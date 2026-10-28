from fastapi import APIRouter, Response
from starlette import status

from database import SessionLocal
from models.budget import BudgetModel, Budget
from models.categories import Category
from routers.request_helper_classes import ChangeBudget, DeleteBudget, ListBudget

router = APIRouter(prefix="/budget", tags=["budget"])

@router.post("/insert")
def insert(new_budget: BudgetModel, response:Response):

    if new_budget.month < 0 or new_budget.month > 11:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid month"}

    if new_budget.amount < 0 or new_budget.amount > 1000000:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Transaction amount must be between 0 and 1000000"}

    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.name == new_budget.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {new_budget.category} does not exist"}

        budget = db.query(Budget).filter(Budget.category == category.id, Budget.month == new_budget.month, Budget.year == new_budget.year).first()
        if budget is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Budget for category {new_budget.category} for {new_budget.month+1}/{new_budget.year} already exists"}
        budget = Budget(month=new_budget.month, amount=new_budget.amount, category=category.id, year=new_budget.year)
        db.add(budget)
        db.commit()
        return {"DONE": "Budget inserted successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}

    finally:
        db.close()

@router.put("/change")
def change_budget(body: ChangeBudget, response:Response):
    if body.month < 0 or body.month > 11:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid month"}

    if body.amount < 0 or body.amount > 1000000:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Transaction amount must be between 0 and 1000000"}

    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name == body.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {body.category} does not exist"}

        updated = db.query(Budget).filter(Budget.category == category.id, Budget.month == body.month, Budget.year == body.year).update(
            {Budget.amount: body.amount}
        )
        if updated == 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Budget for category {body.category} for {body.month + 1}/{body.year} does not exist"}
        elif updated != 1:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": "Error updating budget"}

        db.commit()
        return {"DONE": "Budget updated successfully"}


    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.delete("/remove")
def remove_budget(body: DeleteBudget, response: Response):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name == body.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {body.category} does not exist"}

        budget = db.query(Budget).filter(Budget.category == category.id, Budget.month == body.month, Budget.year == body.year).first()
        if budget is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Budget for category {body.category} for {body.month+1}/{body.year} does not exist"}

        db.delete(budget)
        db.commit()
        return {"DONE": "Budget removed successfully"}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.get("/month")
def list_budgets(body: ListBudget, response: Response):
    db = SessionLocal()
    try:
        budgets = db.query(Budget).filter(Budget.month == body.month, Budget.year == body.year).all()
        return {"budgets": budgets}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

