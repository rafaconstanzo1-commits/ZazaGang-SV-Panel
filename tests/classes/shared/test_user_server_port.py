from unittest.mock import Mock

import pytest

from app.classes.models.users import HelperUsers
from app.classes.shared.import_helper import ImportHelpers
from app.classes.shared.main_controller import Controller


def _server_payload(create_type, nested_type, monitoring_type, create_data, client_port):
    return {
        "create_type": create_type,
        "monitoring_type": monitoring_type,
        f"{monitoring_type}_monitoring_data": {
            "host": "127.0.0.1",
            "port": client_port,
        },
        f"{create_type}_create_data": {
            "create_type": nested_type,
            f"{nested_type}_create_data": create_data,
        },
    }


def _prepare_server_data(monkeypatch, user, payload):
    monkeypatch.setattr(HelperUsers, "get_user", lambda _user_id: user)
    controller = object.__new__(Controller)
    controller.big_bucket = Mock()
    controller.big_bucket.is_vanilla_type.return_value = False
    return controller.prepare_server_creation_data(payload, user["user_id"])


def test_java_server_uses_profile_port_and_ram(monkeypatch):
    user = {
        "user_id": 7,
        "server_port": 25570,
        "server_ram_gb": 3.0,
        "superuser": False,
    }
    payload = _server_payload(
        "minecraft_java",
        "download_jar",
        "minecraft_java",
        {
            "type": "paper",
            "category": "paper",
            "mem_min": 1.0,
            "mem_max": 2.0,
            "server_properties_port": 12345,
        },
        12345,
    )

    prepared = _prepare_server_data(monkeypatch, user, payload)

    assert prepared["minecraft_java_monitoring_data"]["port"] == 25570
    java_data = prepared["minecraft_java_create_data"]["download_jar_create_data"]
    assert java_data["server_properties_port"] == 25570
    assert java_data["mem_min"] == 3.0
    assert java_data["mem_max"] == 3.0


def test_hytale_monitor_uses_assigned_game_port_and_ram(monkeypatch):
    user = {
        "user_id": 7,
        "server_port": 25570,
        "server_ram_gb": 3.0,
        "superuser": False,
    }
    payload = _server_payload(
        "hytale",
        "download_exe",
        "hytale",
        {
            "mem_min": 1.0,
            "mem_max": 2.0,
            "command": "client supplied command",
        },
        5520,
    )

    prepared = _prepare_server_data(monkeypatch, user, payload)

    assert prepared["hytale_monitoring_data"]["port"] == 25573
    hytale_data = prepared["hytale_create_data"]["download_exe_create_data"]
    assert hytale_data["mem_min"] == 3.0
    assert hytale_data["mem_max"] == 3.0
    assert "command" not in hytale_data


@pytest.mark.parametrize(
    ("create_type", "monitoring_type", "nested_type"),
    [
        ("minecraft_bedrock", "minecraft_bedrock", "download_exe"),
        ("steam_cmd", "steam_cmd", "download"),
    ],
)
def test_other_server_types_use_profile_port(
    monkeypatch, create_type, monitoring_type, nested_type
):
    user = {
        "user_id": 7,
        "server_port": 25570,
        "server_ram_gb": 3.0,
        "superuser": False,
    }
    payload = _server_payload(
        create_type,
        nested_type,
        monitoring_type,
        {},
        12345,
    )

    prepared = _prepare_server_data(monkeypatch, user, payload)

    assert prepared[f"{monitoring_type}_monitoring_data"]["port"] == 25570


@pytest.mark.parametrize(
    ("initial_content", "expected_content"),
    [
        (
            "# server config\nserver-port=12345\nserver-port=12346\nmotd=hello\n",
            "# server config\nserver-port=25570\nmotd=hello\n",
        ),
        (
            "# server config\nmotd=hello",
            "# server config\nmotd=hello\nserver-port=25570\n",
        ),
        ("", "server-port=25570\n"),
    ],
)
def test_import_updates_server_properties_port(
    tmp_path, initial_content, expected_content
):
    properties_file = tmp_path / "server.properties"
    if initial_content:
        properties_file.write_text(initial_content, encoding="utf-8")

    ImportHelpers._set_server_properties_port(str(tmp_path), 25570)

    assert properties_file.read_text(encoding="utf-8") == expected_content
