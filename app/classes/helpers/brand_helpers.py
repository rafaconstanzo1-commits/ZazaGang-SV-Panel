"""Helpers for resolving the bundled ZazaGang brand assets.

Kept free of Tornado/DB imports so it can be unit-tested in isolation.
"""

STOCK_FULL = "/static/assets/images/brand/zazagang-logo.png"
STOCK_SQUARE = "/static/assets/images/brand/zaza-icon.png"
DEFAULT_LOGIN_BACKGROUND = "zazagang-background.jpeg"


def resolve_brand_paths(_settings):
    """Return the fixed wide and square brand asset paths."""
    return {"full": STOCK_FULL, "square": STOCK_SQUARE}
