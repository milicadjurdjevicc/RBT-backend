from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def budget():
    return {"message": "Category API"}