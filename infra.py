import os

from aiogram import Dispatcher
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async_engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(
    async_engine,
    expire_on_commit=False
)


TEXT_COMMANDS = [
    "📊 Статистика",
    "🎯 Цели",
    "❓ Помощь",
    "⏱️ История",
    "✏️ Добавить блюдо"
]
COMMANDS = [
    "/start",
    "/help",
    "/add",
    "/stats",
    "/goals",
    "/history",
    "/feedback"
]

dp = Dispatcher()