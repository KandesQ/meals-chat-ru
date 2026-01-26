from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, or_f

from templates.rendering import render_template

help_router = Router()


@help_router.message(or_f(Command("help"), F.text == "❓ Помощь"))
async def help(msg: types.Message):
    await msg.answer(
        render_template("help.html"),
        parse_mode=ParseMode.HTML
    )