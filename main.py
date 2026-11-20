
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from config import BOT_TOKEN, DATABASE_PATH
from database import Database

from handlers.user import router as user_router
from handlers.admin import router as admin_router
from handlers.owner import router as owner_router


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN в переменных окружения!")

    logging.basicConfig(level=logging.INFO)

    db = Database(DATABASE_PATH)
    await db.connect()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp["db"] = db

    # Подсчёт активности участников
    @dp.message()
    async def count_messages(message: Message):
        if message.from_user and not message.from_user.is_bot:
            await db.save_user(
                message.chat.id,
                message.from_user.id,
                message.from_user.full_name
            )
            await db.record_activity(
                message.chat.id,
                message.from_user.id
            )

    dp.include_router(owner_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Telegram Chat Manager запущен!")
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

