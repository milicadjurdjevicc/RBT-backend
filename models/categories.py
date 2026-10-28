from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(30), unique=True, nullable=False)
    color = Column(String(7), nullable=False)

class CategoryModel(BaseModel):
    name: str
    color: str