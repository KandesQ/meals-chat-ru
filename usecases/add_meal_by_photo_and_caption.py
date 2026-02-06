from sqlalchemy.ext.asyncio import AsyncSession

from models.Meal import Meal
from templates.rendering import render_template
from usecases.AI_requests import recognize_meal_by_photo_and_caption


def add_meal_by_photo_and_caption(
        user_telegram_account_id: int,
        image_url: str,
        image_caption: str,
        db_session: AsyncSession
) -> str:
    meal_result = recognize_meal_by_photo_and_caption(image_url, image_caption)

    if not meal_result.is_food:
        return render_template(
            "not_meal.txt",
            reason=meal_result.reason.lower()
        )

    if meal_result.confidence <= 0.5:
        return render_template("not_enough_details.txt")

    meal = Meal(
        name=meal_result.meal_name,
        calories=meal_result.total_calories,
        protein_grams=meal_result.total_protein,
        carbs_grams=meal_result.total_carbs,
        fat_grams=meal_result.total_fat,
        likely_ingredients=meal_result.likely_ingredients,
        user_telegram_account_id=user_telegram_account_id,
    )
    db_session.add(meal)

    return render_template(
        "meal.html",
        meal_name=meal_result.meal_name,
        calories=meal_result.total_calories,
        protein_grams=meal_result.total_protein,
        carbs_grams=meal_result.total_carbs,
        fat_grams=meal_result.total_fat,
        likely_ingredients=meal_result.likely_ingredients
    )