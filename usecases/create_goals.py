from sqlalchemy.ext.asyncio import AsyncSession

from models.Goals import Goals

def create_goals(
        user_telegram_id: int,
        protein_percent: int,
        carbs_percent: int,
        fat_percent: int,
        db_session: AsyncSession
) -> None:
    db_session.add(
        Goals(
            user_telegram_id=user_telegram_id,
            protein_percent=protein_percent,
            carbs_percent=carbs_percent,
            fat_percent=fat_percent
        )
    )
