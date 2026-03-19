import os

# ─────────────────────────────────────────────────────
#  Reads from environment variables (set in Railway)
#  For local use, you can also set these in .env file
# ─────────────────────────────────────────────────────

API_KEY       = os.environ.get("KITE_API_KEY",    "wyu8eezesm7r6peu")
API_SECRET    = os.environ.get("KITE_API_SECRET",  "lmez6rv3lg4b4l63z8xj14pxgrhbxvrc")
CAPITAL       = int(os.environ.get("CAPITAL",      "2000"))
TRADING_STYLE = os.environ.get("TRADING_STYLE",    "intraday")
