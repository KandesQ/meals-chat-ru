from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    grams: int
    calories: int
