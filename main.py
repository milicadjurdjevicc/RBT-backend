from fastapi import FastAPI

from routers.budget_router import router as budget_router
from routers.categories_router import router as categories_router
from routers.transactions_router import router as transactions_router

app = FastAPI()

app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(budget_router)


@app.get("/")
def root():
    return {"message": "Welcome to Budget Tracker API"}