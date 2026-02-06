from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import mapped_column

from models.Base import Base


class Goals(Base):
    __tablename__ = "user_goals"

    id = mapped_column(BigInteger, primary_key=True)
    user_telegram_id = mapped_column(BigInteger, nullable=False)

    protein_percent = mapped_column(Integer, nullable=False)
    carbs_percent = mapped_column(Integer, nullable=False)
    fat_percent = mapped_column(Integer, nullable=False)