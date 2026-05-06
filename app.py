import os
import threading

from flask import Flask

from pyrogram import Client

from config import API_ID, API_HASH, BOT_TOKEN

web_app = Flask(__name__)


@web_app.get("/")
def home():
    return {"status": "ok", "service": "automatic-forward-bot"}, 200


@web_app.get("/health")
def health():
    return {"status": "healthy"}, 200


def run_web_server() -> None:
    port = int(os.getenv("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)

bot = Client(
    "promo_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers"),
)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    bot.run()
