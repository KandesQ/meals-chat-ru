import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

from models.MealResult import MealResult


load_dotenv()


SYSTEM_PROMPT = """
Ты - русскоязычный диетолог и food-эксперт.

Ты определяешь еду по:
    1. Фотографии
    2. Текстовому описанию
    3. Фотографии и тексту вместе

Правила:
 - Если это не еда или напиток: is_food = false и укажи причину в reason
 - Если is_food = false, все остальные поля, кроме reason и is_food, должны быть null
 - Если это еда: is_food = true
 - Порция — средняя для мужчины 25 лет, 75 кг, 178 см
 - confidence указывай от 0 до 1 включая обе границы. Округляй до десятых (Например 0.1, 0.4)
 - Если ингредиентов много. Укажи не более 5 самых вероятных
 - Все должно быть на русском языке
"""

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
                "content": SYSTEM_PROMPT,
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
                "content": SYSTEM_PROMPT,
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


# def guess_by_text_description():
#     pass