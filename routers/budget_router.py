from fastapi import APIRouter

router = APIRouter(prefix="/budget", tags=["budget"])

@router.get("")
def budget():
    return {"message": "Budget API"}