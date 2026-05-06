import asyncio

from pyrogram import Client, filters
from config import OWNER_ID
from database.mongo import users
from services.sender import broadcast_to_groups

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(client, message):

    text = message.text.split(None, 1)[1]

    all_users = users.find()

    total = 0

    async for user in all_users:

        try:
            await broadcast_to_groups(user, text)
            total += 1

        except Exception as e:
            print(e)

        await asyncio.sleep(5)

    await message.reply_text(
        f"Completed for {total} accounts"
    )
