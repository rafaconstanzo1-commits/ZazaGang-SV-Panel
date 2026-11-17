import json

from app.classes.helpers.helpers import Helpers


def test_language_setting_is_fixed_to_spanish(tmp_path):
    settings_file = tmp_path / "config.json"
    settings_file.write_text(json.dumps({"language": "en_EN"}), encoding="utf-8")
    helper = Helpers.__new__(Helpers)
    helper.settings_file = str(settings_file)

    assert helper.get_setting("language") == "es_ES"
    assert helper.get_all_settings()["language"] == "es_ES"

    helper.set_setting("language", "en_EN")
    assert json.loads(settings_file.read_text(encoding="utf-8"))["language"] == "es_ES"
