from aiofiles import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from datetime import datetime
import html

TOKEN = "TOKEN"
ACCOUNT_ID = 1234567890
start_command_gif = "https://i.pinimg.com/originals/c0/68/71/c068718af642df631ebc99b209dbf502.gif"
start_Command_text = "🎉 *Hello my dear person*\n\nI'm glad to see you here\nIf you want to ask me a question — write and I will answer"

bot = Bot(token=TOKEN)  # Change to your bot token
dp = Dispatcher()

ADMIN_CHAT_ID = ACCOUNT_ID
users_info: dict = {}
active_replies: dict = {}

CONTENT_ICONS = {
    'text': ('📝', 'Text'),
    'photo': ('📷', 'Photo'),
    'video': ('🎥', 'Video'),
    'document': ('📎', 'Document'),
    'voice': ('🎤', 'Voice'),
    'audio': ('🎵', 'Audio'),
    'animation': ('🎬', 'GIF'),
    'sticker': ('😀', 'Sticker'),
}


def esc_html(s: str) -> str:
    return html.escape(s or "")


def trunc(s: str, n: int = 150) -> str:
    if not s:
        return ""
    return s if len(s) <= n else s[: n - 3] + "..."


def get_name_from_forward(m: types.Message) -> str:
    if m.forward_from:
        fn = m.forward_from.first_name or ""
        ln = m.forward_from.last_name or ""
        return (fn + (" " + ln if ln else "")).strip() or "User"
    if m.forward_sender_name:
        return m.forward_sender_name
    if m.forward_from_chat:
        return m.forward_from_chat.title or "Chat"
    return "User"


def make_keyboard_reply(user_id: int, active: bool = False) -> InlineKeyboardMarkup:
    if active:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Answering", callback_data="active")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_{user_id}")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Reply", callback_data=f"reply_{user_id}")]
    ])


def build_info(display_name: str, user: types.User | None, ctype_emoji: str, ctype_name: str, txt: str | None, cmd: str | None = None, active: bool = False, fw_restricted: bool = False) -> str:
    now = datetime.now().strftime("%H:%M")
    info = f"👤 <b>From:</b> {esc_html(display_name)}"
    if user and user.username:
        info += f" (@{esc_html(user.username)})"
    info += f"\n📱 <b>Type:</b> {ctype_emoji} {ctype_name}"
    info += f"\n⏰ <b>Time:</b> {now}"
    if txt:
        info += f"\n💬 <b>Message:</b> {esc_html(trunc(txt))}"
    if cmd:
        info += f"\n💬 <b>Command:</b> {esc_html(cmd)}"
    if fw_restricted:
        info += "\n\n⚠️ <i>User has restricted message forwarding</i>"
    if active:
        info += "\n\n🟢 <b>You are currently replying to this user</b>"
    return info


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    gif_url = start_command_gif
    await message.answer_animation(
        animation=gif_url,
        caption=start_Command_text,
        parse_mode="Markdown"
    )

    uid = message.from_user.id
    users_info[uid] = {
        "first_name": message.from_user.first_name or "User",
        "last_name": message.from_user.last_name or "",
        "username": message.from_user.username
    }

    forwarded = await message.forward(ADMIN_CHAT_ID)
    display_name = get_name_from_forward(forwarded)
    fw_restricted = not forwarded.forward_from and bool(forwarded.forward_sender_name)

    keyboard = make_keyboard_reply(uid)
    info = build_info(display_name, message.from_user, "📝", "Text", None, cmd="/start", active=False, fw_restricted=fw_restricted)

    await bot.send_message(ADMIN_CHAT_ID, info, parse_mode="HTML", reply_markup=keyboard)


@dp.message(F.chat.id != ADMIN_CHAT_ID)
async def handle_user_message(message: types.Message):
    uid = message.from_user.id
    users_info[uid] = {
        "first_name": message.from_user.first_name or "User",
        "last_name": message.from_user.last_name or "",
        "username": message.from_user.username
    }

    forwarded = await message.forward(ADMIN_CHAT_ID)
    display_name = get_name_from_forward(forwarded)
    fw_restricted = not forwarded.forward_from and bool(forwarded.forward_sender_name)

    is_active = active_replies.get(ADMIN_CHAT_ID) == uid
    emoji, type_name = CONTENT_ICONS.get(message.content_type, ('📦', 'Message'))

    # choose preview text
    preview = message.text or message.caption or None
    info = build_info(display_name, message.from_user, emoji, type_name, preview, active=is_active, fw_restricted=fw_restricted)
    await bot.send_message(ADMIN_CHAT_ID, info, parse_mode="HTML", reply_markup=make_keyboard_reply(uid, active=is_active))


@dp.callback_query(F.data.startswith("reply_"))
async def handle_reply_button(callback: types.CallbackQuery):
    if callback.message.chat.id != ADMIN_CHAT_ID:
        await callback.answer("Only for admin")
        return

    try:
        user_id = int(callback.data.split("_", 1)[1])
    except:
        await callback.answer("ERROR")
        return

    user_data = users_info.get(user_id, {"first_name": "User", "username": None})
    user_name = user_data["first_name"] + (f" {user_data['last_name']}" if user_data.get("last_name") else "")
    active_replies[ADMIN_CHAT_ID] = user_id

    try:
        await callback.message.edit_reply_markup(reply_markup=make_keyboard_reply(user_id, active=True))
    except:
        pass

    full_name = esc_html(user_name)
    if user_data.get("username"):
        full_name += f" (@{esc_html(user_data['username'])})"

    await callback.message.answer(
        f"✅ <b>Reply mode enabled!</b>\n\nNow all your messages will be sent to <b>{full_name}</b>\nWrite a message to send.\n\n<b>To exit reply mode:</b>\n• Press ❌ Cancel\n• Or send the /cancel command",
        parse_mode="HTML"
    )
    await callback.answer(f"Replying to {user_name}")


@dp.callback_query(F.data.startswith("cancel_"))
async def handle_cancel_reply(callback: types.CallbackQuery):
    if callback.message.chat.id != ADMIN_CHAT_ID:
        return
    try:
        user_id = int(callback.data.split("_", 1)[1])
    except:
        await callback.answer("Error")
        return

    active_replies.pop(ADMIN_CHAT_ID, None)
    try:
        await callback.message.edit_reply_markup(reply_markup=make_keyboard_reply(user_id, active=False))
    except:
        pass

    await callback.message.answer("❌ <b>Reply mode canceled</b>", parse_mode="HTML")
    await callback.answer("Reply mode canceled")


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    if message.chat.id != ADMIN_CHAT_ID:
        return
    active_replies.pop(ADMIN_CHAT_ID, None)
    await message.answer("❌ <b>Reply mode canceled</b>", parse_mode="HTML")


@dp.message(F.chat.id == ADMIN_CHAT_ID)
async def handle_admin_message(message: types.Message):
    if message.text and message.text.startswith('/'):
        return

    if ADMIN_CHAT_ID not in active_replies:
        await message.answer("ℹ️ <b>You are not in reply mode</b>\n\nPress the \"💬 Reply\" button under the user's message.", parse_mode="HTML")
        return

    target = active_replies[ADMIN_CHAT_ID]
    user_data = users_info.get(target, {"first_name": "User"})
    user_name = user_data["first_name"] + (f" {user_data['last_name']}" if user_data.get("last_name") else "")
    safe_user = esc_html(user_name)

    try:
        if message.text:
            await bot.send_message(target, message.text)
            action = "Text sent"
        elif message.photo:
            await bot.send_photo(target, message.photo[-1].file_id, caption=message.caption)
            action = "Photo sent"
        elif message.video:
            await bot.send_video(target, message.video.file_id, caption=message.caption)
            action = "Video sent"
        elif message.document:
            await bot.send_document(target, message.document.file_id, caption=message.caption)
            action = "Document sent"
        elif message.voice:
            await bot.send_voice(target, message.voice.file_id)
            action = "Voice message sent"
        elif message.animation:
            await bot.send_animation(target, message.animation.file_id, caption=message.caption)
            action = "GIF sent"
        elif message.sticker:
            await bot.send_sticker(target, message.sticker.file_id)
            action = "Sticker sent"
        else:
            await message.copy_to(target)
            action = "Message sent"

        now = datetime.now().strftime("%H:%M")
        await message.answer(f"✅ <b>{action} to {safe_user}</b> at {now}", parse_mode="HTML")

    except Exception as e:
        msg = str(e).lower()
        if "bot was blocked" in msg:
            await message.answer(f"❌ <b>{safe_user} blocked the bot</b>", parse_mode="HTML")
        elif "chat not found" in msg:
            await message.answer(f"❌ <b>Chat with {safe_user} not found</b>", parse_mode="HTML")
        else:
            await message.answer(f"❌ <b>Sending error:</b> {esc_html(str(e)[:200])}", parse_mode="HTML")
        active_replies.pop(ADMIN_CHAT_ID, None)


async def main():
    print("🤖 Bot started!")
    print("─" * 40)
    print(f"🆔 Admin: {ADMIN_CHAT_ID}")
    print("📩 Messages are forwarded with a 'Reply' button")
    print("🛡️ Using HTML formatting (safe)")
    print("─" * 40)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
