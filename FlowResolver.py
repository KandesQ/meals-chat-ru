from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


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
            # TODO: Отправить в нейронку. Проверить еда ли на фото
            return None

        # Команда
        text = msg.text
        if text in TEXT_COMMANDS or text in COMMANDS:
            return await handler(msg, data)

        # Текстовое описание еды (возможен мусорный текст. Возможно оптимизировать запросы к модели)
        # TODO: Отправить в нейронку текст на распознавание