from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from templates.rendering import render_template

feedback_router = Router()


@feedback_router.message(Command("feedback"))
async def feedback(message: types.Message):
    await message.answer(
        render_template("feedback.html"),
        parse_mode=ParseMode.HTML
    )