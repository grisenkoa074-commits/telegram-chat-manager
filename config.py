import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", "chat_manager.db")

MAX_WARNINGS = 3
AUTO_BAN_HOURS = 24
FLOOD_LIMIT = 6
FLOOD_WINDOW_SECONDS = 8

RANKS = {
    0: "Участник",
    1: "Помощник",
    2: "Модератор",
    3: "Администратор",
    4: "Создатель"
}
