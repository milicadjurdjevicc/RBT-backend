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
    year: int

class DeleteBudget(BaseModel):
    month: int
    category: str
    year: int

class ListBudget(BaseModel):
    month: int
    year: int

class TransactionDetails(BaseModel):
    id : int

class ChangeTransaction(BaseModel):
    id : int
    transaction: TransactionModel

class ListTransations(BaseModel):
    start_date: str | None
    end_date: str | None
    category: str | None
    type: str | None
    description: str | None
    page: int

class MonthlySummary(BaseModel):
    month: int
    year: int