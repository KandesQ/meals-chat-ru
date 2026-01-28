import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.types import Message
from dotenv import load_dotenv

from infra import async_session_maker
from usecases.add_meal_by_photo import add_meal_by_photo

load_dotenv()


TEXT_COMMANDS = [
    "📊 Статистика",
    "🎯 Цели",
    "❓ Помощь",
    "⏱️ История",
    "✏️ Добавить блюдо"
]
COMMANDS = [
    "/start",
    "/help",
    "/add",
    "/stats",
    "/goals",
    "/history",
    "/feedback"
]

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
        # Фото + caption
        caption = msg.caption
        photo = msg.photo
        if caption and photo:
            # TODO: Отправить в нейронку. Проверить еда ли на фото
            return None

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

        # Текстовое описание еды (возможен мусорный текст. Возможно оптимизировать запросы к модели)
        # TODO: Отправить в нейронку текст на распознавание