from types import SimpleNamespace
from unittest.mock import Mock, call

from app.classes.controllers.roles_controller import RolesController
from app.classes.controllers.servers_controller import ServersController
from app.classes.models.roles import HelperRoles
from app.classes.models.server_permissions import PermissionsServers
from app.classes.models.users import HelperUsers


def test_removing_server_deletes_only_its_generated_role(monkeypatch):
    server_id = "server-123"
    roles = {
        1: {
            "role_name": f"creator of server with id={server_id}",
            "servers": [server_id],
        },
        2: {"role_name": "operators", "servers": [server_id]},
        3: {
            "role_name": f"creator of server with id={server_id}",
            "servers": [server_id, "server-456"],
        },
    }
    server_controller = object.__new__(ServersController)
    server_controller.management_helper = Mock()
    server_controller.servers_helper = Mock()

    monkeypatch.setattr(
        PermissionsServers,
        "get_roles_from_server",
        lambda _server_id: [
            SimpleNamespace(role_id=role_id) for role_id in roles
        ],
    )
    monkeypatch.setattr(
        RolesController, "get_role_with_servers", lambda role_id: roles[role_id]
    )
    delete_permissions = Mock()
    remove_roles = Mock()
    remove_user_memberships = Mock()
    remove_role = Mock()
    monkeypatch.setattr(
        PermissionsServers, "delete_roles_permissions", delete_permissions
    )
    monkeypatch.setattr(PermissionsServers, "remove_roles_of_server", remove_roles)
    monkeypatch.setattr(
        HelperUsers, "remove_roles_from_role_id", remove_user_memberships
    )
    monkeypatch.setattr(HelperRoles, "remove_role", remove_role)

    server_controller.remove_server(server_id)

    remove_role.assert_called_once_with(1)
    remove_user_memberships.assert_called_once_with(1)
    assert delete_permissions.call_args_list == [
        call(1, [server_id]),
        call(2, {server_id}),
        call(3, {server_id}),
    ]
    remove_roles.assert_called_once_with(server_id)
    server_controller.management_helper.remove_all_server_backups.assert_called_once_with(
        server_id
    )
    server_controller.servers_helper.remove_server.assert_called_once_with(server_id)
