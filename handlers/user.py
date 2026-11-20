from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я Telegram Chat Manager 🤖\n\n"
        "Добавь меня в группу и выдай права администратора.\n"
        "В группе доступны команды:\n"
        "/help — список команд\n"
        "/rules — правила чата\n"
        "/me — твой профиль"
    )


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "<b>Команды бота</b>\n\n"
        "/rules — правила группы\n"
        "/me — твой профиль и активность\n"
        "/help — список команд"
    )


@router.message(Command("rules"))
async def rules_command(message: Message):
    db = message.bot.get("db")
    rules = await db.get_rules(message.chat.id)

    if not rules:
        await message.answer("Правила пока не установлены.")
        return

    await message.answer(f"<b>📜 Правила чата</b>\n\n{rules}")


@router.message(Command("me"))
async def profile_command(message: Message):
    db = message.bot.get("db")
    user = message.from_user
    chat_id = message.chat.id

    total = await db.get_total_activity(chat_id, user.id)
    weekly = await db.get_activity(chat_id, user.id, 7)
    rank = await db.get_rank(chat_id, user.id)
    warnings = await db.warning_count(chat_id, user.id)

    await message.answer(
        f"<b>👤 Твой профиль</b>\n\n"
        f"Имя: {user.full_name}\n"
        f"Ранг: {rank}\n"
        f"Сообщений всего: {total}\n"
        f"За 7 дней: {weekly}\n"
        f"Предупреждений: {warnings}"
    )
