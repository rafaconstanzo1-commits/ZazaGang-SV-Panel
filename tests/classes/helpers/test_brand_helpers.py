from app.classes.helpers.brand_helpers import (
    STOCK_FULL,
    STOCK_SQUARE,
    resolve_brand_paths,
)


def test_brand_paths_ignore_saved_logo_choices():
    assert resolve_brand_paths({"full": "custom.png", "square": "custom.png"}) == {
        "full": STOCK_FULL,
        "square": STOCK_SQUARE,
    }
