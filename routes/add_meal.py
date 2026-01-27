from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, or_f

from templates.rendering import render_template

add_meal_router = Router()

@add_meal_router.message(or_f(Command("add"), F.text == "✏️ Добавить блюдо"))
async def add_meal(message: types.Message):
    # Просто отправить сообщение. Любое сообщение, которое не команда или не текст команды
    # должно рассматриваться как блюдо. Если оно не блюдо (нейронка не распознала), то
    # кидается Please ✏️ write a food or drink or send me a 📸 photo.
    # recent_meals = select from db

    # kb = клавиатура с 15 последними блюдами

    await message.answer(
        render_template("add_meal.html"),
        parse_mode=ParseMode.HTML
    )