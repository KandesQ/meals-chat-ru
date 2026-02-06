from sys import prefix

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, or_f
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from sqlalchemy import select, delete

from infra import async_session_maker
from models.Goals import Goals
from templates.rendering import render_template
from usecases.AI_requests import determine_goals
from usecases.create_goals import create_goals

goals_router = Router()



@goals_router.message(
    or_f(
        Command("goals"),
        F.text == "🎯 Цели"
    )
)
async def set_goals(msg: types.Message):
    kb = [
        [InlineKeyboardButton(text="🎯 Установить цель", callback_data="set_goal")]
    ]
    bot_text = render_template("current_goals.html")

    async with async_session_maker() as session:
        goals = (await session.execute(
            select(Goals)
                .where(Goals.user_telegram_id == msg.from_user.id)
        )).scalar()

    if goals:
        bot_text = render_template("current_goals.html", goals=goals)
        kb[0].append(
            InlineKeyboardButton(text="Очистить все", callback_data="clear_goals")
        )

    await msg.answer(
        bot_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        ),
        parse_mode=ParseMode.HTML
    )


@goals_router.callback_query(F.data == "clear_goals")
async def clear_goals(callback: types.CallbackQuery):
    async with async_session_maker() as session:
        await session.execute(
            delete(Goals)
            .where(Goals.user_telegram_id == callback.from_user.id)
        )
        await session.commit()

    await callback.message.answer(
        "✅ Удалил все цели."
    )

    await callback.answer()


class _SetGoal(StatesGroup):
    goal_text = State()


class _GoalsDto(CallbackData, prefix="goals"):
    protein_percent: int
    carbs_percent: int
    fat_percent: int


@goals_router.message(_SetGoal.goal_text)
async def process_text_goal(msg: types.Message, state: FSMContext):
    goal_input = ((await state.update_data(goal_text=msg.text))
                  .get("goal_text"))


    process_message=  await msg.answer(
        "🧠 Определяю цели..."
    )

    goals_result = determine_goals(goal_input)

    await process_message.delete()

    if goals_result.not_enough_details:
        await msg.answer(goals_result.not_enough_details_text)
        return

    kb = [
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=_GoalsDto(
                protein_percent=goals_result.protein_percent,
                carbs_percent=goals_result.carbs_percent,
                fat_percent=goals_result.fat_percent
            ).pack()),
            InlineKeyboardButton(text="Отменить", callback_data="cancel_set_goal")
        ]
    ]

    await msg.answer(
        render_template(
            "suggest_goals.html",
            goals=goals_result
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode=ParseMode.HTML
    )


@goals_router.callback_query(_GoalsDto.filter())
async def accept_goals(query: types.CallbackQuery, callback_data: _GoalsDto):
    async with async_session_maker() as session:
        goals_exist = (await session.execute(
            select(Goals.id)
            .where(Goals.user_telegram_id == query.from_user.id)
        ))

        if goals_exist:
            await session.execute(
                delete(Goals)
                .where(Goals.user_telegram_id == query.from_user.id)
            )

        create_goals(
            query.from_user.id,
            callback_data.protein_percent,
            callback_data.carbs_percent,
            callback_data.fat_percent,
            session
        )
        await session.commit()

    await query.message.answer(
        "✅ Новые цели поставлены."
    )

    await query.answer()

    # TODO: print today stats. Send feed_update() to bot



@goals_router.callback_query(F.data == "set_goal")
async def set_goal(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(
        render_template("set_goal.html"),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_set_goal")]
        ])
    )

    await state.set_state(_SetGoal.goal_text)

    await query.answer()


@goals_router.callback_query(F.data == "cancel_set_goal")
async def cancel_goal(query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await query.message.answer(
        render_template("cancel_goal.txt")
    )

    await query.answer()
