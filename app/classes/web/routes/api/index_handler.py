from app.classes.web.base_api_handler import BaseApiHandler

PROJECT_SITE_LINK = "https://minecraft.zazagang.beer/"


class ApiIndexHandler(BaseApiHandler):
    def get(self):
        self.finish_json(
            200,
            {
                "status": "ok",
                "data": {
                    "version": self.controller.helper.get_version_string(),
                    "message": f"Zaza Gang project site: {PROJECT_SITE_LINK}",
                },
            },
        )
