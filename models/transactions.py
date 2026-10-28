from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column(Enum("income", "expense"), nullable=False)
    amount = Column(Numeric(9, 2), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String(200), nullable=True)
    category = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

class TransactionModel(BaseModel):

    type:str
    amount:float
    date:str
    description: str = ""
    category:str