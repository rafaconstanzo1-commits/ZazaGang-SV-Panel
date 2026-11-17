from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image

from app.classes.web.routes.api.users.user.pfp import ApiUsersUserPfpHandler


def _encoded_image(image_format):
    buffer = BytesIO()
    mode, color = (
        ("RGB", (20, 120, 40))
        if image_format == "JPEG"
        else ("RGBA", (20, 120, 40, 128))
    )
    Image.new(mode, (600, 300), color).save(buffer, format=image_format)
    return buffer.getvalue()


def test_profile_image_is_normalized_and_resized_to_png():
    result = ApiUsersUserPfpHandler._normalize_profile_image(_encoded_image("JPEG"))

    with Image.open(BytesIO(result)) as image:
        assert image.format == "PNG"
        assert image.size == (512, 256)
        assert image.mode == "RGB"


def test_profile_image_rejects_non_raster_formats():
    with pytest.raises(ValueError, match="no es una imagen válida"):
        ApiUsersUserPfpHandler._normalize_profile_image(b"<svg></svg>")


def test_profile_image_rejects_supported_but_disallowed_raster_format():
    with pytest.raises(ValueError, match="Usa una imagen PNG, JPG, GIF o WEBP"):
        ApiUsersUserPfpHandler._normalize_profile_image(_encoded_image("BMP"))


def test_profile_image_upload_rejects_files_over_ten_mib():
    handler = Mock()
    handler.authenticate_user.return_value = (None, [], None, None, {"user_id": 3})
    handler.can_modify_user.return_value = True
    handler.controller.users.get_user_by_id.return_value = {}
    handler.request = SimpleNamespace(body=b"x" * (10 * 1024 * 1024 + 1))

    ApiUsersUserPfpHandler.post(handler, "3")

    response = handler.finish_json.call_args.args
    assert response[0] == 413
    assert response[1]["error"] == "IMAGE_TOO_LARGE"
    handler.controller.users.raw_update_user.assert_not_called()


def test_profile_image_upload_saves_png_and_updates_user(tmp_path):
    handler = Mock()
    handler.authenticate_user.return_value = (None, [], None, None, {"user_id": 3})
    handler.can_modify_user.return_value = True
    handler.controller.users.get_user_by_id.return_value = {}
    handler.controller.project_root = tmp_path
    handler.request = SimpleNamespace(body=_encoded_image("PNG"))
    handler._normalize_profile_image.side_effect = (
        ApiUsersUserPfpHandler._normalize_profile_image
    )

    ApiUsersUserPfpHandler.post(handler, "3")

    saved_image = (
        tmp_path
        / "app"
        / "frontend"
        / "static"
        / "assets"
        / "images"
        / "user-profiles"
        / "3.png"
    )
    with Image.open(saved_image) as image:
        assert image.format == "PNG"
        assert image.size == (512, 256)
    assert handler.finish_json.call_args.args[0] == 200
    handler.controller.users.raw_update_user.assert_called_once()
    assert handler.controller.users.raw_update_user.call_args.args[0] == 3
    assert handler.controller.users.raw_update_user.call_args.args[1]["pfp"].startswith(
        "/static/assets/images/user-profiles/3.png?v="
    )
