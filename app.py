import os
import threading
import traceback

from flask import Flask
from pyrogram import Client

web_app = Flask(__name__)
_bot_status = {"running": False, "error": None}

@web_app.get("/")
def home():
    return {
        "status": "ok",
        "service": "automatic-forward-bot",
        "bot_running": _bot_status["running"],
        "bot_error": _bot_status["error"],
    }, 200


@web_app.get("/health")
def health():
    code = 200 if _bot_status["running"] else 503
    return {
        "status": "healthy" if _bot_status["running"] else "degraded",
        "bot_error": _bot_status["error"],
    }, code


def run_web_server() -> None:
    port = int(os.getenv("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)


def run_bot() -> None:
    try:
        from config import API_ID, API_HASH, BOT_TOKEN

        bot = Client(
            "promo_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="handlers"),
        )

        _bot_status["running"] = True
        bot.run()
    except Exception as exc:
        _bot_status["running"] = False
        _bot_status["error"] = str(exc)
        print("Bot failed to start:")
        traceback.print_exc()

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    run_bot()

    # Keep process alive so deployment logs are visible even if bot startup fails.
    web_thread.join()
