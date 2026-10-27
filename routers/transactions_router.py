from fastapi import APIRouter

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("")
def transactions():
    return {"message": "Transactions API"}