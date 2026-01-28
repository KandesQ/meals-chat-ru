from typing import Optional

from pydantic import BaseModel

from models.Ingredient import Ingredient


class MealResult(BaseModel):
    is_food: bool
    confidence: Optional[float]
    reason: Optional[str]  # Если is_food = False

    meal_name: Optional[str]
    total_calories: Optional[int]
    total_protein: Optional[float]
    total_carbs: Optional[float]
    total_fat: Optional[float]
    likely_ingredients: Optional[list[Ingredient]]
