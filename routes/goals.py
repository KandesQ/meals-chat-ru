from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.util import await_only
from urllib3.util.util import reraise

from infra import COMMANDS, TEXT_COMMANDS
from templates.rendering import render_template

goals_router = Router()



@goals_router.message(
    or_f(
        Command("goals"),
        F.text == "🎯 Цели"
    )
)
async def set_goals(msg: types.Message):

    await msg.answer(
        render_template("no_goal.txt"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎯 Установить цель", callback_data="set_goal")]
            ]
        )
    )

    # Set FSM. If user press CANCEL or enter cmd or text cmd, then unset FSM and proceed that action


    # If there's goal for the user in db
    # await msg.answer(
    #     render_template("current_goal.html"), # TODO: add macros
    #     parse_mode=ParseMode.HTML,
    #     reply_markup=InlineKeyboardMarkup(
    #         inline_keyboard=[
    #             [InlineKeyboardButton(text="Отменить", callback_data="cancel_set_goals")]
    #         ]
    #     )
    # )


class _SetGoal(StatesGroup):
    goal_text = State()


@goals_router.message(_SetGoal.goal_text)
async def process_text_goal(msg: types.Message, state: FSMContext):
    goal_input = ((await state.update_data(goal_text=msg.text))
                  .get("goal_text"))


    # TODO: process goal



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
