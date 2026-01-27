from dataclasses import dataclass

from sqlalchemy import BigInteger, Integer, Numeric, JSON, String, DateTime, func, TypeDecorator, Dialect
from sqlalchemy.orm import mapped_column

from models.Base import Base


class _LikelyIngredients(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, likely_ingredients, dialect):
        if likely_ingredients is None:
            return None

        return [
            {
                "name": likely_ingredient.name,
                "grams": likely_ingredient.grams,
                "calories": likely_ingredient.calories
            }
            for likely_ingredient in likely_ingredients
        ]

    def process_result_value(self, likely_ingredients_row, dialect):
        if likely_ingredients_row is None:
            return None

        return [
            LikelyIngredient(**likely_ingredient)
            for likely_ingredient in likely_ingredients_row
        ]


@dataclass
class LikelyIngredient:
    name: str
    grams: float
    calories: int


class Meal(Base):
    __tablename__ = "meals"

    id = mapped_column(BigInteger, primary_key=True)
    name = mapped_column(String(150), nullable=False)
    calories = mapped_column(Integer, nullable=False)
    protein_grams = mapped_column(Numeric(6, 2), nullable=False)
    carbs_grams = mapped_column(Numeric(6, 2), nullable=False)
    fat_grams = mapped_column(Numeric(6, 2), nullable=False)
    likely_ingredients = mapped_column(_LikelyIngredients, nullable=False)

    user_telegram_account_id = mapped_column(BigInteger, nullable=False)

    created_at = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
