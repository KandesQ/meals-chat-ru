import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.types import Message, Update
from dotenv import load_dotenv
from langsmith.utils import with_cache
from sqlalchemy.util import await_only

from infra import async_session_maker, TEXT_COMMANDS, COMMANDS, dp
from usecases.add_meal_by_photo import add_meal_by_photo
from usecases.add_meal_by_photo_and_caption import add_meal_by_photo_and_caption
from usecases.add_meal_by_text import add_meal_by_text

load_dotenv()


# TODO: need total rework. Now FSM can't catch input because
#  this middleware assumes any text as text input of
#  food. This middleware should be only responsible for routing user inputs. There should
#  not be any logic invocation. But such behavior is decent for MVP
class FlowResolver(BaseMiddleware):
    """
    Бот не ждет ответа фото или текста от пользователя, если тот ввел
    команду. Вместо этого он всегда проверяет тип сообщения. И на его основе
    выбирает нужный способ обработки
    """

    def __init__(self):
        pass

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            msg: Message,
            data: Dict[str, Any]
    ) -> Any:

        # Временное решение. Если задействуется FSM - то дальше не идем.
        state = data.get("state")
        if state and await state.get_state() is not None:

            # Если установлен стейт, но юзер решил вызвать команду или текстовую команду,
            # то стейт надо очистить и переотправить в бота сообщение
            if msg.text in COMMANDS or msg.text in TEXT_COMMANDS:
                await state.clear()

                await dp.feed_update(
                    msg.bot,
                    Update(
                        update_id=msg.message_id,
                        message=msg
                    )
                )

                return None

            return await handler(msg, data)

        # Фото + caption
        caption = msg.caption
        photo = msg.photo
        if caption and photo:
            largest_image_id = photo[-1].file_id
            image = await msg.bot.get_file(largest_image_id)
            image_url = f"https://api.telegram.org/file/bot{os.getenv("BOT_TOKEN")}/{image.file_path}"

            analyzing_msg = await msg.answer("🧠 Анализирую...")

            async with async_session_maker() as session:
                template = add_meal_by_photo_and_caption(
                    msg.from_user.id,
                    image_url,
                    caption,
                    session
                )
                await session.commit()

            await analyzing_msg.delete()

            # TODO: добавить кнопки: "👎 Выглядит неправильно", "🚫 удали это"
            await msg.answer(
                template,
                parse_mode=ParseMode.HTML
            )
            return None

        # TODO: If set goals FSM receives a command or a text command, handler should interrupt FSM setting and send feed_update to dp through dp.feed_update()
        # Только фото
        photo = msg.photo
        if photo:
            largest_image_id = photo[-1].file_id
            image = await msg.bot.get_file(largest_image_id)
            image_url = f"https://api.telegram.org/file/bot{os.getenv("BOT_TOKEN")}/{image.file_path}"

            analyzing_msg = await msg.answer("🧠 Анализирую...")

            async with async_session_maker() as session:
                template = add_meal_by_photo(
                    msg.from_user.id,
                    image_url,
                    session
                )
                await session.commit()

            await analyzing_msg.delete()

            # TODO: добавить кнопки: "👎 Выглядит неправильно", "🚫 удали это"
            await msg.answer(
                template,
                parse_mode=ParseMode.HTML,
            )
            return None

        # Команда
        text = msg.text
        if text in TEXT_COMMANDS or text in COMMANDS:
            return await handler(msg, data)


        meal_description = msg.text

        analyzing_msg = await msg.answer("🧠 Анализирую...")

        async with async_session_maker() as session:
            template = add_meal_by_text(
                msg.from_user.id,
                meal_description,
                session)
            await session.commit()

        await analyzing_msg.delete()

        await msg.answer(
            template,
            parse_mode=ParseMode.HTML
        )

        return None
