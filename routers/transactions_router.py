import csv
import io
import datetime
from datetime import date

from fastapi import APIRouter, Response, UploadFile, File
from starlette import status
from sqlalchemy import func

from database import SessionLocal
from models.categories import Category
from models.transactions import TransactionModel, Transaction
from routers.request_helper_classes import TransactionDetails, ChangeTransaction, ListTransations

router = APIRouter(prefix="/transactions", tags=["transactions"])
PAGE_SIZE = 4

def check_transaction_fields(new_transaction: TransactionModel):

    if new_transaction.type not in ("income", "expense"):
        return 1, "Invalid transaction type", None

    if new_transaction.amount <= 0 or new_transaction.amount > 1000000:
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


@router.post("/insert")
def insert(new_transaction: TransactionModel, response: Response):

    stat, message, parsed_date = check_transaction_fields(new_transaction)
    if stat != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": message}

    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.name == new_transaction.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {new_transaction.category} does not exist"}

        transaction = Transaction(
            type=new_transaction.type, amount=new_transaction.amount, description=new_transaction.description,
            date = parsed_date, category = category.id, created_at = datetime.datetime.now())
        db.add(transaction)
        db.commit()
        return {"DONE": f"Transaction created successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.get("/details")
def transaction_details(body: TransactionDetails, response: Response):
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.id == body.id).first()
        if transaction is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": "Transaction does not exist"}

        return {"transaction": transaction}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.put("/change")
def change_transaction(body: ChangeTransaction, response: Response):

    stat, message, parsed_date = check_transaction_fields(body.transaction)

    if stat != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": message}

    db = SessionLocal()
    transaction = body.transaction

    try:
        category = db.query(Category).filter(Category.name == transaction.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {transaction.category} does not exist"}

        existing_transaction = db.query(Transaction).filter(
            Transaction.id == body.id
        ).first()
        if existing_transaction is None:
            response.status_code=status.HTTP_400_BAD_REQUEST
            return {"ERROR": "Transaction does not exist"}

        existing_transaction.category = category.id
        existing_transaction.date = parsed_date
        existing_transaction.amount = transaction.amount
        existing_transaction.description = transaction.description
        existing_transaction.type = transaction.type
        db.commit()
        return {"DONE": "Transaction updated successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.delete("/delete")
def delete_transaction(body: TransactionDetails, response: Response):
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.id == body.id).first()
        if transaction is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": "Transaction does not exist"}
        db.delete(transaction)
        db.commit()
        return {"DONE": "Transaction deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.get("")
def list_transactions(body: ListTransations, response: Response):
    db = SessionLocal()
    offset = (body.page-1) * PAGE_SIZE
    try:
        transactions = db.query(Transaction)

        if body.category is not None:
            category = db.query(Category).filter(Category.name == body.category).first()
            if category is None:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"ERROR": f"Category {body.category} does not exist"}

            transactions = transactions.filter(Transaction.category == category.id)

        if body.type is not None:
            if body.type not in ("expense", "income"):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"ERROR": f"Type {body.type} does not exist"}

            transactions = transactions.filter(Transaction.type == body.type)

        if body.end_date is not None:
            try:
                parsed_date = date.fromisoformat(body.end_date)
                if parsed_date.isoformat() != body.end_date:
                    return {"ERROR": "Invalid date; expected format YYYY-MM-DD"}
            except Exception as e:
                return {"ERROR": "Invalid date; expected format YYYY-MM-DD"}
            transactions = transactions.filter(Transaction.date <= body.end_date)

        if body.start_date is not None:
            try:
                parsed_date = date.fromisoformat(body.start_date)
                if parsed_date.isoformat() != body.start_date:
                    return {"ERROR": "Invalid date; expected format YYYY-MM-DD"}
            except Exception as e:
                return {"ERROR": "Invalid date; expected format YYYY-MM-DD"}
            transactions = transactions.filter(Transaction.date >= body.start_date)

        if body.description is not None:
            transactions = transactions.filter(Transaction.description.ilike(f"%{body.description}%"))

        transactions = (transactions.order_by(Transaction.date.desc(), Transaction.created_at.desc()).
                        offset(offset).limit(PAGE_SIZE).all())
        return {"transactions": transactions}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.post("/import")
async def import_transactions(response: Response, file: UploadFile = File(...)):
    db = SessionLocal()
    data = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(data))

    rows = list(reader)
    errors = []
    successfull = 0

    if len(rows) > 1000000:
        response.status = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Maximum number of rows exceeded"}

    try:

        for i in range(len(rows)):
            transaction = TransactionModel(**rows[i])
            stat, message, parsed_date = check_transaction_fields(transaction)
            if stat != 0:
                errors.append({"line": i, "ERROR": message})
                continue

            category = db.query(Category).filter(
                func.lower(Category.name) == transaction.category.lower()
            ).first()
            if category is None:
                errors.append({"line": i, "ERROR": f"Category {transaction.category} does not exist"})
                continue

            transaction = Transaction(
                type=transaction.type, amount=transaction.amount, description=transaction.description,
                date = parsed_date, category = category.id, created_at = datetime.datetime.now())
            db.add(transaction)
            successfull += 1

        db.commit()
        return {"DONE": f"{successfull} transaction(s) imported successfully", "errors": errors}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}

    finally:
        db.close()
