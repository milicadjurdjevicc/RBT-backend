from sqlalchemy import Column, Integer, Numeric, String
from database import Base


class Budget(Base):
    __tablename__ = "budget"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    month = Column(Integer, nullable=False)
    category = Column(String(30), nullable=False)
    amount = Column(Numeric(2, 0), nullable=False)
