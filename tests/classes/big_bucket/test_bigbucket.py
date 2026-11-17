import json

from app.classes.big_bucket.bigbucket import BigBucket


class BucketHelper:
    big_bucket_minecraft_cache = ""

    @staticmethod
    def get_setting(key, default):
        return default


def test_bucket_data_filters_vanilla_server_types(tmp_path):
    cache_file = tmp_path / "manifest.json"
    cache_file.write_text(
        json.dumps(
            {
                "categories": {
                    "Mc_java_servers": {
                        "types": {
                            "Paper": {"friendly_name": "Paper"},
                            "Vanilla": {"friendly_name": "Vanilla"},
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    bucket = BigBucket(BucketHelper())

    assert bucket.get_bucket_data(str(cache_file)) == {
        "Mc_java_servers": {"types": {"Paper": {"friendly_name": "Paper"}}}
    }


def test_bucket_rejects_vanilla_download_url():
    bucket = BigBucket(BucketHelper())

    assert bucket.get_fetch_url("Mc_java_servers", "Vanilla", "1.20") is None
