import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from routes.history import history_router
from usecases.FlowResolver import FlowResolver
from routes.add_meal import add_meal_router
from routes.feedback import feedback_router
from routes.help import help_router
from templates.rendering import render_template

load_dotenv()


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )



dp = Dispatcher()

dp.message.outer_middleware(FlowResolver())


dp.include_router(help_router)
dp.include_router(add_meal_router)
dp.include_router(feedback_router)
dp.include_router(history_router)


kb_builder = ReplyKeyboardBuilder()
kb_builder.row(
    types.KeyboardButton(text="📊 Статистика"),
    types.KeyboardButton(text="🎯 Цели"),
    types.KeyboardButton(text="❓ Помощь")
)
kb_builder.row(
types.KeyboardButton(text="⏱️ История"),
    types.KeyboardButton(text="✏️ Добавить блюдо")
)
keyboard = kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        render_template("start.txt"),
        reply_markup=keyboard
    )


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())