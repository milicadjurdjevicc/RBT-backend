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
        return {"message": "Invalid month"}

    if new_budget.amount < 0 or new_budget.amount > 1000000:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Transaction amount must be between 0 and 1000000"}

    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.name == new_budget.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Category {new_budget.category} does not exist"}

        budget = db.query(Budget).filter(Budget.category == category.id, Budget.month == new_budget.month).first()
        if budget is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Budget for category {new_budget.category} for {new_budget.month+1} month already exists"}
        budget = Budget(month=new_budget.month, amount=new_budget.amount, category=category.id)
        db.add(budget)
        db.commit()
        return {"message": "Budget inserted successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}

    finally:
        db.close()

@router.put("/change")
def change_budget(body: ChangeBudget, response:Response):
    if body.month < 0 or body.month > 11:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Invalid month"}

    if body.amount < 0 or body.amount > 1000000:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Transaction amount must be between 0 and 1000000"}

    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name == body.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Category {body.category} does not exist"}

        updated = db.query(Budget).filter(Budget.category == category.id, Budget.month == body.month).update(
            {Budget.amount: body.amount}
        )
        if updated == 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Budget for category {body.category} for {body.month + 1} month does not exist"}
        elif updated != 1:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Error updating budget"}

        db.commit()
        return {"message": "Budget updated successfully"}


    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}
    finally:
        db.close()

@router.delete("/remove")
def remove_budget(body: DeleteBudget, response: Response):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name == body.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Category {body.category} does not exist"}

        budget = db.query(Budget).filter(Budget.category == category.id, Budget.month == body.month).first()
        if budget is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Budget for category {body.category} for {body.month+1} month does not exist"}

        db.delete(budget)
        db.commit()
        return {"message": "Budget removed successfully"}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}
    finally:
        db.close()

@router.get("/month")
def list_budgets(body: ListBudget, response: Response):
    db = SessionLocal()
    try:
        budgets = db.query(Budget).filter(Budget.month == body.month).all()
        return {"budgets": budgets}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}
    finally:
        db.close()