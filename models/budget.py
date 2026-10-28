from pydantic import BaseModel
from sqlalchemy import Column, Integer, Numeric, String
from database import Base


class Budget(Base):
    __tablename__ = "budget"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    month = Column(Integer, nullable=False)
    category = Column(Integer, nullable=False)
    amount = Column(Numeric(9, 2), nullable=False)
    year = Column(Integer, nullable=False)


class BudgetModel(BaseModel):

    month: int
    category: str
    amount: float
    year: int