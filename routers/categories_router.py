import re
import traceback

from fastapi import APIRouter, Response, status
from sqlalchemy import func

from database import SessionLocal
from models.budget import Budget
from models.categories import CategoryModel, Category
from models.transactions import Transaction
from routers.request_helper_classes import ChangeCategoryName, ChangeCategoryColor, DeleteCategory

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/insert")
def insert(new_category: CategoryModel, response: Response):

    new_category.name = new_category.name.strip()
    if len(new_category.name) > 30 or len(new_category.name) < 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Category name must be between 1 and 30 characters"}

    color_regex = re.compile(r"^#([A-Fa-f0-9]{6})$")
    if color_regex.fullmatch(new_category.color) is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid color format"}

    db = SessionLocal()
    try:
        cat = db.query(Category).filter(
            func.lower(Category.name) == new_category.name.lower()
        ).first()
        if cat is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {new_category.name} already exists"}

        cat = Category(name=new_category.name, color=new_category.color)
        db.add(cat)
        db.commit()
        return {"DONE": f"Category {new_category.name} created successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}

    finally:
        db.close()


@router.put("/change/name")
def change_name(body: ChangeCategoryName, response: Response):
    new_name = body.new_name.strip()
    old_name = body.old_name.strip()

    if len(new_name) > 30 or len(new_name) < 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Category name must be between 1 and 30 characters"}

    db = SessionLocal()
    try:
        cat = db.query(Category).filter(Category.name == old_name).first()
        if cat is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {old_name} does not exist"}

        cat = db.query(Category).filter(
            func.lower(Category.name) == new_name.lower()
        ).first()
        if cat is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {new_name} already exists"}

        category = db.query(Category).filter(Category.name == old_name).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Error updating category"}

        category.name = new_name
        db.commit()
        return{"DONE": f"Category {new_name} changed successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}

@router.put("/change/color")
def change_color(body: ChangeCategoryColor, response: Response):
    color_regex = re.compile(r"^#([A-Fa-f0-9]{6})$")
    if color_regex.fullmatch(body.new_color) is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid color format"}

    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name == body.name).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {body.name} does not exist"}

        category.color = body.new_color
        db.commit()
        return {"DONE": f"Category {body.name} changed successfully"}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}

    finally:
        db.close()

@router.get("")
def get_categories(response: Response):
    db = SessionLocal()
    try:
        categories = db.query(Category).order_by(Category.name.asc()).all()
        return {"categories": categories}
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()

@router.delete("/delete")
def delete_category(body: DeleteCategory, response: Response):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name == body.category).first()
        if category is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {body.category} does not exist"}

        transactions = db.query(Transaction).filter(Transaction.category == category.id).all()
        if transactions:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"ERROR": f"Category {category.name} has transactions and cannot be deleted"}

        db.query(Budget).filter(Budget.category == category.id).delete(synchronize_session=False)
        db.delete(category)

        db.commit()
        return {"DONE": f"Category {category.name} deleted successfully"}

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ERROR": "Database error"}
    finally:
        db.close()