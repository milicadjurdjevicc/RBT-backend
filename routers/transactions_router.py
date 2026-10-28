from datetime import date

from fastapi import APIRouter, Response
from starlette import status

from database import SessionLocal
from models.categories import Category
from models.transactions import TransactionModel, Transaction
from routers.request_helper_classes import TransactionDetails, ChangeTransaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

def check_transaction_fields(new_transaction: TransactionModel):

    if new_transaction.type not in ("income", "expense"):
        return 1, "Invalid transaction type", None

    if new_transaction.amount < 0 or new_transaction.amount > 1000000:
        return 1, "Transaction amount must be between 0 and 1000000", None
    try:
        parsed_date = date.fromisoformat(new_transaction.date)
        if parsed_date.isoformat() != new_transaction.date:
            return 1, "Invalid date; expected format YYYY-MM-DD", None
    except Exception as e:
        return 1, "Invalid date; expected format YYYY-MM-DD", None

    if new_transaction.description and len(new_transaction.description) > 200:
        return 1, "Transaction description must be less than 200 characters", parsed_date

    return 0, "", parsed_date

@router.get("")
def transactions():
    return {"message": "Transactions API"}


@router.post("/insert")
def insert(new_transaction: TransactionModel, response: Response):

    stat, message, parsed_date = check_transaction_fields(new_transaction)
    if stat != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": message}

    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.name == new_transaction.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Category {new_transaction.category} does not exist"}

        transaction = Transaction(
            type=new_transaction.type, amount=new_transaction.amount, description=new_transaction.description,
            date = parsed_date, category = category.id)
        db.add(transaction)
        db.commit()
        return {"message": f"Transaction created successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}
    finally:
        db.close()

@router.get("/details")
def transaction_details(body: TransactionDetails, response: Response):
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.id == body.id).first()
        if transaction is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Transaction does not exist"}

        return {"transaction": transaction}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}
    finally:
        db.close()

@router.put("/change")
def change_transaction(body: ChangeTransaction, response: Response):

    stat, message, parsed_date = check_transaction_fields(body.transaction)

    if stat != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": message}

    db = SessionLocal()
    transaction = body.transaction

    try:
        category = db.query(Category).filter(Category.name == transaction.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Category {transaction.category} does not exist"}

        updated = db.query(Transaction).filter(Transaction.id == body.id).update(
            {Transaction.category: transaction.category, Transaction.date: parsed_date, Transaction.amount: transaction.amount,
             Transaction.description: transaction.description, Transaction.type: transaction.type}
        )

        if updated == 0:
            response.status_code=status.HTTP_400_BAD_REQUEST
            return {"message": "Transaction does not exist"}
        elif updated != 1:
            response.status_code=status.HTTP_400_BAD_REQUEST
            return {"message": "Error updating transaction"}

        db.commit()
        return {"message": "Transaction updated successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Database error"}
    finally:
        db.close()

