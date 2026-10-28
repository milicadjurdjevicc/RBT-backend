import datetime
import traceback

from fastapi import APIRouter, Response
from sqlalchemy import func, extract
from starlette import status

from database import SessionLocal
from models.budget import Budget
from models.categories import Category
from models.transactions import Transaction
from routers.request_helper_classes import MonthlySummary

router = APIRouter(prefix="/summary", tags=["summary"])

@router.get("")
def get_montly_summary(body: MonthlySummary, response: Response):

    total_income = 0
    total_expense = 0
    budgets = []

    if body.month < 0 or body.month > 11:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid month"}
    if body.year < 0 or body.year > datetime.datetime.now().year:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid year"}
    db = SessionLocal()

    try:
        categories = db.query(Category).all()

        for category in categories:

            budget = db.query(Budget).filter(
                Budget.category == category.id, Budget.month == body.month, Budget.year == body.year).first()

            expenses = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.category == category.id,
                Transaction.type == "expense",
                extract("month", Transaction.date) == body.month + 1,
                extract("year", Transaction.date) == body.year,
            ).scalar()

            incomes = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.category == category.id,
                Transaction.type == "income",
                extract("month", Transaction.date) == body.month + 1,
                extract("year", Transaction.date) == body.year,
            ).scalar()

            total_income += incomes
            total_expense += expenses

            if budget is not None:
                budget_amount = budget.amount
                budget_left = budget_amount - expenses
            else:
                budget_amount = None
                budget_left = None

            if budget or expenses:
                budgets.append({
                    "category": category.name,
                    "spent": expenses,
                    "budget": budget_amount,
                    "left": budget_left
                })

        budgets.sort(key=lambda budget: (budget["spent"], budget["category"]), reverse=True)
        return {"total income": total_income, "total expense": total_expense, "balance": total_income - total_expense,
                "summary by categories": budgets}


    except Exception as e:
        db.rollback()
        print(f"Database Error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database Error"}

    finally:
        db.close()
