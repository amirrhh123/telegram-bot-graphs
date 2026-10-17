"""Register the deployed endpoint: python setup_webhook.py https://your-app.vercel.app"""

import argparse
import os
import re
from urllib.parse import urlparse

from main import bot


def main() -> None:
    """Configure Telegram using the token and webhook secret from the environment."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Public HTTPS origin of your Vercel deployment")
    args = parser.parse_args()
    origin = urlparse(args.url)
    if origin.scheme != "https" or not origin.netloc or origin.path not in ("", "/"):
        parser.error("Pass an HTTPS origin without a path")
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", secret):
        parser.error("Set TELEGRAM_WEBHOOK_SECRET (1-256 letters, digits, underscores or hyphens)")
    try:
        success = bot.set_webhook(
            url=args.url.rstrip("/") + "/webhook",
            secret_token=secret,
            allowed_updates=["message"],
            max_connections=1,
            timeout=20,
        )
        if not success:
            raise RuntimeError("Webhook registration failed")
    except Exception:
        # Telegram API exception messages may contain the bot token.
        raise SystemExit("Webhook registration failed. Check your token and deployment URL.") from None
    print("Webhook registered. Send /start to your bot in Telegram.")


if __name__ == "__main__":
    main()
