from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column(Enum("income", "expense"), nullable=False)
    amount = Column(Numeric(2, 0), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String(200), nullable=True)
    category = Column(String(30), nullable=False)
