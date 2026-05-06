import os
from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in your deployment environment before starting the app."
        )
    return value


def _required_int_env(name: str) -> int:
    raw = _required_env(name)
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be an integer, got: {raw!r}"
        ) from exc


def _optional_int_env(name: str, default: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be an integer, got: {raw!r}"
        ) from exc


API_ID = _required_int_env("API_ID")
API_HASH = _required_env("API_HASH")
BOT_TOKEN = _required_env("BOT_TOKEN")
MONGO_URI = _required_env("MONGO_URI")
OWNER_ID = _optional_int_env("OWNER_ID", default=0)
