from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import RANKS

router = Router()

# ВАЖНО: сюда позже добавим твой Telegram ID.
OWNER_ID = 0


def is_owner(user_id: int) -> bool:
    return OWNER_ID != 0 and user_id == OWNER_ID


@router.message(Command("owner"))
async def owner_panel(message: Message):
    if not is_owner(message.from_user.id):
        return

    await message.answer(
        "<b>ПАНЕЛЬ ВЛАДЕЛЬЦА</b>\n\n"
        "📊 /globalstats — статистика бота\n"
        "👮 /moderators — статистика модераторов\n"
        "📨 /broadcast — рассылка сообщений\n"
        "👥 /groups — список подключённых групп\n"
        "⚙️ /botsettings — настройки бота"
    )


@router.message(Command("globalstats"))
async def global_stats(message: Message):
    if not is_owner(message.from_user.id):
        return

    await message.answer(
        "📊 <b>Общая статистика</b>\n"
        "Сбор статистики будет подключён следующим этапом."
    )


@router.message(Command("moderators"))
async def moderators_stats(message: Message):
    if not is_owner(message.from_user.id):
        return

    await message.answer(
        "👮 <b>Статистика модераторов</b>\n"
        "Здесь будут отображаться действия каждого модератора."
    )


@router.message(Command("broadcast"))
async def broadcast_help(message: Message):
    if not is_owner(message.from_user.id):
        return

    await message.answer(
        "📨 Для рассылки позже будет добавлен отдельный мастер "
        "с подтверждением отправки."
    )
