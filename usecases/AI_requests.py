import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

from models.GoalsResult import GoalsResult
from models.MealResult import MealResult


load_dotenv()


MEAL_RECOGNITION_SYSTEM_PROMPT = """
Ты - русскоязычный диетолог и food-эксперт.

Ты определяешь еду по:
    1. Фотографии
    2. Текстовому описанию
    3. Фотографии и тексту вместе

Правила:
 - Если это не еда или напиток: is_food = false и укажи причину в reason. Причина будет использоваться в формате "Я не смог провести анализ, потому что {причина}", но тебе просто нужно написать причину, чтобы она естественно подходила после "потому что". 
 - Если is_food = false, все остальные поля, кроме reason и is_food, должны быть null
 - Если это еда: is_food = true
 - Порция — средняя для мужчины 25 лет, 75 кг, 178 см
 - confidence указывай от 0 до 1 включая обе границы. Округляй до десятых (Например 0.1, 0.4)
 - Если ингредиентов много. Укажи не более 5 самых вероятных
 - Все должно быть на русском языке
"""

# TODO: Replace with AsyncOpenAI()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def recognize_meal_by_photo(image_url: str) -> MealResult:
    response = client.responses.parse(
        model="o4-mini",
        text_format=MealResult,
        input=[
            {
                "role": "system",
                "content": MEAL_RECOGNITION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Определи блюдо по фото"
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ],
    )

    return response.output_parsed


def recognize_meal_by_photo_and_caption(
        image_url: str,
        caption: str,
):
    response = client.responses.parse(
        model="o4-mini",
        text_format=MealResult,
        input=[
            {
                "role": "system",
                "content": MEAL_RECOGNITION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Определи блюдо по фото и тексту к нему"
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    },
                    {
                        "type": "input_text",
                        "text": f"Текст пользователя: {caption}"
                    }
                ]
            }
        ],
    )

    return response.output_parsed


def recognize_meal_by_text_description(meal_description: str) -> MealResult:
    response = client.responses.parse(
        model="o4-mini",
        text_format=MealResult,
        input=[
            {
                "role": "system",
                "content": MEAL_RECOGNITION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Определи блюдо по тексту пользователя"
                    },
                    {
                        "type": "input_text",
                        "text": f"Текст пользователя: {meal_description}"
                    }
                ]
            }
        ],
    )

    return response.output_parsed


GOAlS_SYSTEM_PROMPT = """
Ты профессиональный нутрициолог и спортивный диетолог.

Твоя задача:
1. Проанализировать пользовательский ввод.
2. Определить цель (набор массы, похудение, поддержание, рекомпозиция).
3. Предложить распределение БЖУ в процентах.
4. Написать краткое профессиональное заключение (1-2 предложения).

Для ответа не нужно знать полную инфомацию о юзере (например, рост, физ активность, желаемые результы). Определи
все что нужно по тому что вводит юзер 

Если данных НЕДОСТАТОЧНО:
- Установи "not_enough_details": true
- В "not_enough_details_text" кратко укажи, какой информации не хватает
- НЕ указывай проценты БЖУ (оставь их null)
- "conclusion_text" должен быть коротким пояснением

Если данных ДОСТАТОЧНО:
- "not_enough_details": false
- "not_enough_details_text": null
- Укажи проценты белков, жиров и углеводов
- Проценты должны быть целыми числами
- Сумма процентов должна равняться 100

ВАЖНО:
- Ответ строго в формате JSON
- Никакого текста вне JSON
- Не используй markdown
- Не жди от пользователя полного ввода. Попытайся вывести итог по введенным данным. Не нагнетай информацией 
"""


def determine_goals(goals_input: str) -> GoalsResult:
    response = client.responses.parse(
        model="o4-mini",
        text_format=GoalsResult,
        input=[
            {
                "role": "system",
                "content": GOAlS_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Ввод пользователя: {goals_input}"
                    }
                ]
            }
        ],
    )

    return response.output_parsed
