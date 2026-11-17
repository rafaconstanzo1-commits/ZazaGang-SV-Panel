from unittest.mock import Mock

import pytest

from app.classes.shared.server import ServerInstance


@pytest.fixture
def reset_start_reservations(monkeypatch):
    monkeypatch.setattr(ServerInstance, "_starting_owner_ids", set())


def _server(server_id, owner_id, running=False):
    server = object.__new__(ServerInstance)
    server.server_id = server_id
    server.settings = {"created_by": owner_id}
    server.check_running = Mock(return_value=running)
    server.server_instances = []
    server._notify_account_start_error = Mock()
    return server


def test_account_start_slot_blocks_another_running_owned_server(
    reset_start_reservations,
):
    active_server = _server("active", 7, running=True)
    server_to_start = _server("next", 7)
    server_to_start.server_instances = [
        {"server_obj": active_server},
        {"server_obj": server_to_start},
    ]

    assert not server_to_start._claim_account_server_slot(7, 7)
    server_to_start._notify_account_start_error.assert_called_once()


def test_account_start_slot_blocks_concurrent_starts_for_same_owner(
    reset_start_reservations,
):
    first_server = _server("first", 7)
    second_server = _server("second", 7)

    assert first_server._claim_account_server_slot(7, 7)
    assert not second_server._claim_account_server_slot(7, 7)

    first_server._release_account_server_slot(7)
    assert second_server._claim_account_server_slot(7, 7)
    second_server._release_account_server_slot(7)


def test_account_start_slot_does_not_block_another_owner(
    reset_start_reservations,
):
    first_server = _server("first", 7)
    second_server = _server("second", 8)

    assert first_server._claim_account_server_slot(7, 7)
    assert second_server._claim_account_server_slot(8, 8)

    first_server._release_account_server_slot(7)
    second_server._release_account_server_slot(8)
