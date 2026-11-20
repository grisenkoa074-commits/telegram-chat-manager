from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

router = Router()


async def is_admin(message: Message) -> bool:
    member = await message.bot.get_chat_member(
        message.chat.id,
        message.from_user.id
    )
    return member.status in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    )


@router.message(Command("ban"))
async def ban_user(message: Message):
    if not await is_admin(message):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой /ban на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    try:
        await message.bot.ban_chat_member(message.chat.id, user.id)
        await message.answer(f"🚫 Пользователь {user.full_name} заблокирован.")
    except TelegramBadRequest:
        await message.answer("Не удалось заблокировать пользователя.")


@router.message(Command("unban"))
async def unban_user(message: Message):
    if not await is_admin(message):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой /unban на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    try:
        await message.bot.unban_chat_member(
            message.chat.id,
            user.id,
            only_if_banned=True
        )
        await message.answer(f"Пользователь {user.full_name} разблокирован.")
    except TelegramBadRequest:
        await message.answer("Не удалось разблокировать пользователя.")


@router.message(Command("mute"))
async def mute_user(message: Message):
    if not await is_admin(message):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой /mute на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    try:
        await message.bot.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions={
                "can_send_messages": False,
                "can_send_audios": False,
                "can_send_documents": False,
                "can_send_photos": False,
                "can_send_videos": False,
                "can_send_video_notes": False,
                "can_send_voice_notes": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
            }
        )
        await message.answer(f"🔇 Пользователь {user.full_name} получил мут.")
    except TelegramBadRequest:
        await message.answer("Не удалось выдать мут.")


@router.message(Command("unmute"))
async def unmute_user(message: Message):
    if not await is_admin(message):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой /unmute на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    try:
        await message.bot.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions={
                "can_send_messages": True,
                "can_send_audios": True,
                "can_send_documents": True,
                "can_send_photos": True,
                "can_send_videos": True,
                "can_send_video_notes": True,
                "can_send_voice_notes": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
            }
        )
        await message.answer(f"🔊 Мут с пользователя {user.full_name} снят.")
    except TelegramBadRequest:
        await message.answer("Не удалось снять мут.")


@router.message(Command("kick"))
async def kick_user(message: Message):
    if not await is_admin(message):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой /kick на сообщение пользователя.")
        return

    user = message.reply_to_message.from_user

    try:
        await message.bot.ban_chat_member(message.chat.id, user.id)
        await message.bot.unban_chat_member(
            message.chat.id,
            user.id,
            only_if_banned=True
        )
        await message.answer(f"👢 Пользователь {user.full_name} исключён.")
    except TelegramBadRequest:
        await message.answer("Не удалось исключить пользователя.")
