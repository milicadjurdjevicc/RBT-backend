from pydantic import BaseModel

from models.transactions import TransactionModel


class ChangeCategoryName(BaseModel):
    new_name: str
    old_name:str

class ChangeCategoryColor(BaseModel):
    new_color: str
    name: str

class DeleteCategory(BaseModel):
    category: str

class ChangeBudget(BaseModel):
    month: int
    category: str
    amount: float

class DeleteBudget(BaseModel):
    month: int
    category: str

class ListBudget(BaseModel):
    month: int

class TransactionDetails(BaseModel):
    id : int

class ChangeTransaction(BaseModel):
    id : int
    transaction: TransactionModel