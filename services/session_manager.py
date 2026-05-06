from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import User

from config import API_ID, API_HASH
from database.mongo import users


def create_login_client(user_id: int) -> Client:
    return Client(
        name=f"login_{user_id}",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    )


async def save_user_session(user_id: int, account: User, session_string: str, phone_number: str) -> None:
    await users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "account_id": account.id,
                "account_name": f"{account.first_name or ''} {account.last_name or ''}".strip(),
                "phone_number": phone_number,
                "username": account.username,
                "session": session_string,
            }
        },
        upsert=True,
    )


async def complete_sign_in(login_client: Client, phone_number: str, phone_code_hash: str, otp: str):
    try:
        account = await login_client.sign_in(
            phone_number=phone_number,
            phone_code_hash=phone_code_hash,
            phone_code=otp,
        )
        return account, False
    except SessionPasswordNeeded:
        return None, True
