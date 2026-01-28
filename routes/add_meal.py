from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, or_f
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func

from infra import async_session_maker
from models.Meal import Meal
from templates.rendering import render_template

add_meal_router = Router()

@add_meal_router.message(or_f(Command("add"), F.text == "✏️ Добавить блюдо"))
async def add_meal(message: types.Message):
    st = (
        select(Meal)
        .where(Meal.user_telegram_account_id == message.from_user.id)
        .order_by(Meal.updated_at.desc())
        .limit(15)
    )
    async with async_session_maker() as session:
        recent_meals = (await session.execute(st)).scalars()

    button_array = []

    tmp = []
    for i, recent_meal in enumerate(recent_meals, start=1):
        tmp.append(InlineKeyboardButton(
            text=recent_meal.name,
            callback_data=f"add_meal_callback:{recent_meal.id}"
        ))

        if i % 2 == 0:
            button_array.append(tmp)
            tmp = []
    button_array.append(tmp)

    await message.answer(
        render_template("add_meal.html"),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=button_array)
    )

@add_meal_router.callback_query(F.data.startswith("add_meal_callback:"))
async def process_meal(query: types.CallbackQuery):
    meal_id = int(query.data.removeprefix("add_meal_callback:"))
    async with (async_session_maker() as session):
        meal = (await session.execute(
            select(Meal)
            .where(Meal.id == meal_id))
        ).scalar()

        meal.updated_at = func.now()
        await session.commit()

    # TODO: убрать и просто подставить список. Другим коммитом
    formatted_ingredients = [
        f"{ingredient.name} ({ingredient.grams} г, {ingredient.calories} ккал)"
        for ingredient in meal.likely_ingredients
    ]

    await query.message.answer(
        render_template(
            "meal.html",
            meal_name=meal.name,
            calories=meal.calories,
            protein_grams=meal.protein_grams,
            carbs_grams=meal.carbs_grams,
            fat_grams=meal.fat_grams,
            likely_ingredients=formatted_ingredients
        ),
        parse_mode=ParseMode.HTML
    )

    await query.answer()

