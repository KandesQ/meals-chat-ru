import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from templates.rendering import render_template

load_dotenv()

dp = Dispatcher()


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