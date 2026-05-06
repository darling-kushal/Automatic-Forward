 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/handlers/login.py b/handlers/login.py
index 8b137891791fe96927ad78e64b0aad7bded08bdc..cc9319771d8f46a6d38e576847ac5a37b2f4ff20 100644
--- a/handlers/login.py
+++ b/handlers/login.py
@@ -1 +1,125 @@
+from pyrogram import Client, filters
+from pyrogram.errors import RPCError
+from pyrogram.types import Message
 
+from services.session_manager import create_login_client, save_user_session, complete_sign_in
+
+
+login_states = {}
+
+
+async def cleanup_login_state(user_id: int) -> None:
+    state = login_states.pop(user_id, None)
+    if not state:
+        return
+
+    login_client = state.get("login_client")
+    if login_client:
+        try:
+            await login_client.disconnect()
+        except Exception:
+            pass
+
+
+@Client.on_message(filters.command("login") & filters.private)
+async def login_handler(client: Client, message: Message):
+    if not message.from_user:
+        return
+
+    user_id = message.from_user.id
+
+    if user_id in login_states:
+        await message.reply_text("A login flow is already active. Send /cancel_login to reset it.")
+        return
+
+    login_client = create_login_client(user_id)
+    await login_client.connect()
+
+    login_states[user_id] = {
+        "step": "phone",
+        "login_client": login_client,
+    }
+
+    await message.reply_text("Send your phone number with country code (example: +15551234567).")
+
+
+@Client.on_message(filters.command("cancel_login") & filters.private)
+async def cancel_login_handler(client: Client, message: Message):
+    if not message.from_user:
+        return
+
+    user_id = message.from_user.id
+    if user_id in login_states:
+        await cleanup_login_state(user_id)
+        await message.reply_text("Login flow cancelled.")
+        return
+
+    await message.reply_text("No active login flow.")
+
+
+@Client.on_message(filters.private & ~filters.command(["login", "cancel_login", "start", "broadcast"]))
+async def login_flow_router(client: Client, message: Message):
+    if not message.from_user:
+        return
+
+    user_id = message.from_user.id
+    state = login_states.get(user_id)
+    if not state:
+        return
+
+    if not message.text:
+        await message.reply_text("Please send text input to continue login.")
+        return
+
+    login_client = state["login_client"]
+
+    try:
+        if state["step"] == "phone":
+            phone_number = message.text.strip()
+            sent_code = await login_client.send_code(phone_number)
+            state.update(
+                {
+                    "step": "otp",
+                    "phone_number": phone_number,
+                    "phone_code_hash": sent_code.phone_code_hash,
+                }
+            )
+            await message.reply_text("OTP sent. Enter the code you received.")
+            return
+
+        if state["step"] == "otp":
+            otp = message.text.strip().replace(" ", "")
+            account, needs_password = await complete_sign_in(
+                login_client,
+                state["phone_number"],
+                state["phone_code_hash"],
+                otp,
+            )
+
+            if needs_password:
+                state["step"] = "password"
+                await message.reply_text("Two-step verification is enabled. Send your password.")
+                return
+
+            session_string = await login_client.export_session_string()
+            await save_user_session(user_id, account, session_string, state["phone_number"])
+            await cleanup_login_state(user_id)
+            await message.reply_text("Login completed and session saved.")
+            return
+
+        if state["step"] == "password":
+            password = message.text.strip()
+            account = await login_client.check_password(password)
+
+            session_string = await login_client.export_session_string()
+            await save_user_session(user_id, account, session_string, state["phone_number"])
+            await cleanup_login_state(user_id)
+            await message.reply_text("Login completed with 2FA and session saved.")
+            return
+
+    except RPCError as e:
+        await cleanup_login_state(user_id)
+        await message.reply_text(f"Telegram error: {e}")
+    except Exception as e:
+        await cleanup_login_state(user_id)
+        await message.reply_text(f"Login failed: {e}")
 
EOF
)
