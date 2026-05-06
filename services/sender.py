import asyncio

from pyrogram import Client
from config import API_ID, API_HASH

async def broadcast_to_groups(user_data, text):

    session = user_data["session"]

    app = Client(
        name=f"sessions/{user_data['user_id']}",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session,
        in_memory=False
    )

    await app.start()

    async for dialog in app.get_dialogs():

        try:
            chat = dialog.chat

            if str(chat.type) in ["ChatType.GROUP", "ChatType.SUPERGROUP"]:

                await app.send_message(
                    chat.id,
                    text
                )

                print(chat.title)

                await asyncio.sleep(10)

        except Exception as e:
            print(e)

    await app.stop()
