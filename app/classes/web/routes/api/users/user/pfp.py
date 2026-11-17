import io
import logging
import time
import warnings
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from peewee import DoesNotExist

from app.classes.web.base_api_handler import BaseApiHandler
from app.classes.models.users import USER_PROFILE_IMAGE_URL_PREFIX

logger = logging.getLogger(__name__)

MAX_PROFILE_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
PROFILE_IMAGE_UPLOAD_DIRECTORY = (
    "app/frontend/static/assets/images/user-profiles"
)
ALLOWED_PROFILE_IMAGE_FORMATS = {"GIF", "JPEG", "PNG", "WEBP"}


class ApiUsersUserPfpHandler(BaseApiHandler):
    def get(self, user_id):
        auth_data = self.authenticate_user()
        if not auth_data:
            return

        if user_id == "@me":
            user = auth_data[4]
        else:
            user = self.controller.users.get_user_by_id(user_id)

        logger.debug(
            f'User {auth_data[4]["user_id"]} is fetching the pfp for user {user_id}'
        )

        self.finish_json(200, {"status": "ok", "data": user["pfp"]})
        return

    def post(self, user_id):
        auth_data = self.authenticate_user()
        if not auth_data:
            return

        if not self.can_modify_user(auth_data[1], auth_data, user_id):
            return self.finish_json(
                403,
                {
                    "status": "error",
                    "error": "NOT_AUTHORIZED",
                    "error_data": "No tienes permiso para cambiar esta imagen.",
                },
            )

        target_user_id = (
            int(auth_data[4]["user_id"]) if user_id == "@me" else int(user_id)
        )
        try:
            self.controller.users.get_user_by_id(target_user_id)
        except DoesNotExist:
            return self.finish_json(
                404,
                {
                    "status": "error",
                    "error": "USER_NOT_FOUND",
                    "error_data": "No se encontró el usuario.",
                },
            )

        image_data = self.request.body
        if not image_data:
            return self.finish_json(
                400,
                {
                    "status": "error",
                    "error": "EMPTY_IMAGE",
                    "error_data": "Selecciona una imagen para subir.",
                },
            )
        if len(image_data) > MAX_PROFILE_IMAGE_SIZE_BYTES:
            return self.finish_json(
                413,
                {
                    "status": "error",
                    "error": "IMAGE_TOO_LARGE",
                    "error_data": "La imagen no puede superar los 10 MB.",
                },
            )

        try:
            normalized_image = self._normalize_profile_image(image_data)
        except ValueError as error:
            return self.finish_json(
                422,
                {
                    "status": "error",
                    "error": "INVALID_IMAGE",
                    "error_data": str(error),
                },
            )

        image_directory = Path(
            self.controller.project_root, PROFILE_IMAGE_UPLOAD_DIRECTORY
        )
        image_path = image_directory / f"{target_user_id}.png"
        try:
            image_directory.mkdir(parents=True, exist_ok=True)
            self.helper.validate_traversal(
                Path(self.controller.project_root).resolve(), image_path.resolve()
            )
            image_path.write_bytes(normalized_image)
        except OSError as error:
            logger.exception(
                "Unable to save profile image for user %s: %s",
                target_user_id,
                error,
            )
            return self.finish_json(
                500,
                {
                    "status": "error",
                    "error": "IMAGE_SAVE_FAILED",
                    "error_data": "No se pudo guardar la imagen de perfil.",
                },
            )

        image_url = (
            f"{USER_PROFILE_IMAGE_URL_PREFIX}{target_user_id}.png"
            f"?v={time.time_ns()}"
        )
        self.controller.users.raw_update_user(target_user_id, {"pfp": image_url})
        return self.finish_json(
            200,
            {"status": "ok", "data": image_url},
        )

    @staticmethod
    def _normalize_profile_image(image_data):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(image_data)) as image:
                    if image.format not in ALLOWED_PROFILE_IMAGE_FORMATS:
                        raise ValueError(
                            "Usa una imagen PNG, JPG, GIF o WEBP."
                        )
                    image.verify()

                with Image.open(io.BytesIO(image_data)) as image:
                    image.load()
                    image.thumbnail((512, 512))
                    has_alpha = "A" in image.getbands() or "transparency" in image.info
                    profile_image = image.convert("RGBA" if has_alpha else "RGB")
                    output = io.BytesIO()
                    profile_image.save(output, format="PNG", optimize=True)
                    return output.getvalue()
        except (
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            OSError,
            UnidentifiedImageError,
        ) as error:
            raise ValueError("El archivo seleccionado no es una imagen válida.") from error
