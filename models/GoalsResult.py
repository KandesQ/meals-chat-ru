from typing import Optional

from pydantic import BaseModel


class GoalsResult(BaseModel):
    conclusion_text: str

    not_enough_details: bool = False
    not_enough_details_text: Optional[str] = None

    protein_percent: Optional[int]
    carbs_percent: Optional[int]
    fat_percent: Optional[int]
