from datetime import datetime, timezone
from enum import Enum
from math import ceil
from typing import Optional, List

import humanize.i18n
from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, or_f
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from sqlalchemy import select, func, and_

from infra import async_session_maker
from models.Meal import Meal
from templates.rendering import render_template

history_router = Router()


_HISTORY_PAGE_LIMIT = 10

humanize.i18n.activate("ru_RU")

# TODO: нужно сделать глобальный middleware для проверки
#  не истек ли срок действия любой кнопки. Соответственно для
#  всех кнопок в боте нужно сделать timestamp. Отдельным коммитом
@history_router.message(or_f(Command("history"), F.text == "⏱️ История"))
async def history(msg: types.Message):
    first_page = await _render_first_history_page(msg.from_user.id)

    await msg.answer(
        render_template("history.html"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=first_page),
        parse_mode=ParseMode.HTML,
    )


class HistoryPageCallbackData(CallbackData, prefix="history"):
    """
    Описывает данные предыдущей страницы, с которой пользователь перешел.
    Например, юзер был на 5 странице и нажал на кнопку →. Значит в коллбек
    дате придет информация:
        - page_number = 5
        - total_page_count = {общее кол-во блюд из истории пользователя}
        - first_meal_on_page_id = {id первого блюда на 5 странице}
        - last_meal_on_page_id = {id последнего блюда на 5 странице}

    :param page_number: номер страницы с которой перешел пользователя
    :param total_page_count: общее число блюд из истории этого пользователя
    :param first_meal_on_page_id: id первого блюда на предыдущей страницы
    :param swipe_direction: направление нажатой кнопки
    :param last_meal_on_page_id: id последнего блюда предыдущей страницы

    """
    class SwipeDirection(str, Enum):
        LEFT = "left"
        RIGHT = "right"

    page_number: int
    total_page_count: int
    swipe_direction: SwipeDirection

    first_meal_on_page_id: Optional[int] = None
    # datetime. Aiogram запрещает использовать datetime в callback_data
    first_meal_on_page_updated_at_timestamp: Optional[float] = None

    last_meal_on_page_id: Optional[int] = None
    # datetime. Aiogram запрещает использовать datetime в callback_data
    last_meal_on_page_updated_at_timestamp: Optional[float] = None



@history_router.callback_query(HistoryPageCallbackData.filter(
    F.swipe_direction == HistoryPageCallbackData.SwipeDirection.LEFT
))
async def history_left_btn_callback(
        callback: types.CallbackQuery,
        callback_data: HistoryPageCallbackData
):
    next_meals_st = (
        select(Meal)
        .where(
            and_(
                Meal.updated_at > datetime.fromtimestamp(callback_data.first_meal_on_page_updated_at_timestamp),
                Meal.user_telegram_account_id == callback.from_user.id
            )
        )
        .order_by(Meal.updated_at)
        .limit(_HISTORY_PAGE_LIMIT)
    )

    async with async_session_maker() as session:
        meals = (await session.execute(next_meals_st)).scalars().all()


    # Если пользователь с первой страницы нажимает назад - ничего не происходит
    if callback_data.page_number == 1:
        await callback.answer()
        return

    next_page = _render_history_page(
        page_number=callback_data.page_number - 1,
        meals=meals,
        total_page_count=callback_data.total_page_count
    )

    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=next_page)
    )
    await callback.answer()


@history_router.callback_query(HistoryPageCallbackData.filter(
    F.swipe_direction == HistoryPageCallbackData.SwipeDirection.RIGHT
))
async def history_right_btn_callback(
        callback: types.CallbackQuery,
        callback_data: HistoryPageCallbackData
):
    next_meals_st = (
        select(Meal)
        .where(
            and_(
                Meal.updated_at < datetime.fromtimestamp(callback_data.last_meal_on_page_updated_at_timestamp),
                Meal.user_telegram_account_id == callback.from_user.id
            )
        )
        .order_by(Meal.updated_at.desc())
        .limit(_HISTORY_PAGE_LIMIT)
    )

    async with async_session_maker() as session:
        meals = (await session.execute(next_meals_st)).scalars().all()

    if callback_data.page_number == callback_data.total_page_count:
        await callback.answer()
        return

    next_page = _render_history_page(
        meals,
        callback_data.total_page_count,
        callback_data.page_number + 1
    )

    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=next_page)
    )
    await callback.answer()


# @history_router.callback_query(F.data == "history_meal_callback")
# async def history_meal_callback(callback: types.CallbackQuery):
#     pass


async def _render_first_history_page(
        user_telegram_account_id: int,
) -> List[List[InlineKeyboardButton]]:
    total_meals_count_st = (
        select(func.count())
        .where(Meal.user_telegram_account_id == user_telegram_account_id)
    )

    get_meals_page_st = (
        select(Meal)
        .order_by(Meal.updated_at.desc())
        .limit(_HISTORY_PAGE_LIMIT)
    )

    async with async_session_maker() as session:
        meals = (await session.execute(get_meals_page_st)).scalars().all()
        total_meals_count = (await session.execute(total_meals_count_st)).scalar()

    page = []
    navigation_buttons = []
    for i in range(len(meals)):
        meal = meals[i]

        if i == 0:
            total_page_count = ceil(total_meals_count / _HISTORY_PAGE_LIMIT)

            first_meal_on_page = meal
            left_arrow_btn_callback_data = HistoryPageCallbackData(
                page_number=1,
                total_page_count=total_page_count,
                swipe_direction=HistoryPageCallbackData.SwipeDirection.LEFT,
                first_meal_on_page_id=first_meal_on_page.id,
                first_meal_on_page_updated_at_timestamp=first_meal_on_page.updated_at.timestamp()
            )

            navigation_buttons.append(
                InlineKeyboardButton(
                    text="←",
                    callback_data=left_arrow_btn_callback_data.pack()
                )
            )

            # Сразу же добавляю отображение номера страницы
            navigation_buttons.append(
                InlineKeyboardButton(
                    text=f"1/{total_page_count}",
                    callback_data="None"
                )
            )

        if i == len(meals) - 1:
            total_page_count = ceil(total_meals_count / _HISTORY_PAGE_LIMIT)

            last_meal_on_page = meal
            right_arrow_btn_callback_data = HistoryPageCallbackData(
                total_page_count=total_page_count,
                last_meal_on_page_id=last_meal_on_page.id,
                last_meal_on_page_updated_at_timestamp=last_meal_on_page.updated_at.timestamp(),
                page_number=1,
                swipe_direction=HistoryPageCallbackData.SwipeDirection.RIGHT
            )

            navigation_buttons.append(
                InlineKeyboardButton(
                    text="→",
                    callback_data=right_arrow_btn_callback_data.pack()
                )
            )

        time_ago = humanize.naturaltime(datetime.now(tz=timezone.utc) - meal.updated_at.replace(tzinfo=timezone.utc))
        page.append(
            [InlineKeyboardButton(text=f"{time_ago} - {meal.name}", callback_data=f"history_meal_callback:")]
        )

    page.append(navigation_buttons)

    return page


def _render_history_page(
        meals: List[Meal],
        total_page_count: int,
        page_number: int
) -> List[List[InlineKeyboardButton]]:
    page = []
    navigation_buttons = []
    for i in range(len(meals)):
        meal = meals[i]

        if i == 0:
            first_meal_on_page = meal
            left_arrow_btn_callback_data = HistoryPageCallbackData(
                total_page_count=total_page_count,
                first_meal_on_page_id=first_meal_on_page.id,
                page_number=page_number,
                swipe_direction=HistoryPageCallbackData.SwipeDirection.LEFT,
                first_meal_on_page_updated_at_timestamp=first_meal_on_page.updated_at.timestamp()
            )

            navigation_buttons.append(
                InlineKeyboardButton(
                    text="←",
                    callback_data=left_arrow_btn_callback_data.pack()
                )
            )

            # Сразу же добавляю отображение номера страницы
            navigation_buttons.append(
                InlineKeyboardButton(
                    text=f"{page_number}/{total_page_count}",
                    callback_data="None"
                )
            )

        if i == len(meals) - 1:
            last_meal_on_page = meal
            right_arrow_btn_callback_data = HistoryPageCallbackData(
                total_page_count=total_page_count,
                last_meal_on_page_id=last_meal_on_page.id,
                last_meal_on_page_updated_at_timestamp=last_meal_on_page.updated_at.timestamp(),
                page_number=page_number,
                swipe_direction=HistoryPageCallbackData.SwipeDirection.RIGHT
            )
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="→",
                    callback_data=right_arrow_btn_callback_data.pack()
                )
            )

        time_ago = humanize.naturaltime(datetime.now(tz=timezone.utc) - meal.updated_at.replace(tzinfo=timezone.utc))
        page.append(
            [InlineKeyboardButton(text=f"{time_ago} - {meal.name}", callback_data=f"history_meal_callback:")]
        )

    page.append(navigation_buttons)

    return page