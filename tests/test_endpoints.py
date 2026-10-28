import asyncio
import io
import unittest
from datetime import datetime
from unittest.mock import patch

from fastapi import Response, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models.budget import Budget, BudgetModel
from models.categories import Category, CategoryModel
from models.transactions import Transaction, TransactionModel
from main import root
from routers import budget_router, categories_router, summary_router, transactions_router
from routers.request_helper_classes import (
    ChangeBudget,
    ChangeCategoryName,
    ChangeCategoryColor,
    ChangeTransaction,
    DeleteBudget,
    DeleteCategory,
    ListBudget,
    ListTransations,
    TransactionDetails,
    MonthlySummary,
)


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.patches = [
            patch.object(categories_router, "SessionLocal", self.Session),
            patch.object(budget_router, "SessionLocal", self.Session),
            patch.object(transactions_router, "SessionLocal", self.Session),
            patch.object(summary_router, "SessionLocal", self.Session),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        self.addCleanup(self.engine.dispose)

    def add_category(self, name="Food", color="#AABBCC"):
        with self.Session() as db:
            category = Category(name=name, color=color)
            db.add(category)
            db.commit()
            db.refresh(category)
            return category.id

    def test_category_insert_and_duplicate(self):
        response = Response()
        result = categories_router.insert(CategoryModel(name="Food", color="#AABBCC"), response)
        self.assertEqual(response.status_code, 200)
        self.assertIn("created successfully", result["DONE"])

        response = Response()
        result = categories_router.insert(CategoryModel(name="Food", color="#AABBCC"), response)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", result["ERROR"])

    def test_category_names_are_case_insensitive(self):
        self.add_category(name="Food")
        response = Response()
        result = categories_router.insert(
            CategoryModel(name="food", color="#AABBCC"), response
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", result["ERROR"])

    def test_root_category_listing_and_color_change(self):
        self.assertEqual(root(), {"message": "Welcome to Budget Tracker API"})
        self.add_category(name="Zed")
        self.add_category(name="Alpha", color="#112233")

        listed = categories_router.get_categories(Response())
        self.assertEqual([category.name for category in listed["categories"]], ["Alpha", "Zed"])

        result = categories_router.change_color(
            ChangeCategoryColor(name="Alpha", new_color="#ABCDEF"), Response()
        )
        self.assertIn("changed successfully", result["DONE"])

    def test_category_validation_and_delete_with_transactions(self):
        self.add_category()
        response = Response()
        result = categories_router.insert(CategoryModel(name=" ", color="#AABBCC"), response)
        self.assertEqual(response.status_code, 400)
        self.assertIn("between 1 and 30", result["ERROR"])

        response = Response()
        result = categories_router.change_color(
            ChangeCategoryColor(name="Food", new_color="red"), response
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["ERROR"], "Invalid color format")

        transactions_router.insert(
            TransactionModel(
                type="expense", amount=10, date="2026-10-10",
                description="", category="Food",
            ),
            Response(),
        )
        response = Response()
        result = categories_router.delete_category(DeleteCategory(category="Food"), response)
        self.assertEqual(response.status_code, 400)
        self.assertIn("has transactions", result["ERROR"])

    def test_category_rename_and_delete(self):
        self.add_category()
        response = Response()
        categories_router.change_name(ChangeCategoryName(old_name="Food", new_name="Groceries"), response)
        with self.Session() as db:
            self.assertIsNotNone(db.query(Category).filter_by(name="Groceries").first())

        response = Response()
        result = categories_router.delete_category(DeleteCategory(category="Groceries"), response)
        self.assertIn("deleted successfully", result["DONE"])
        with self.Session() as db:
            self.assertIsNone(db.query(Category).filter_by(name="Groceries").first())

    def test_budget_endpoints(self):
        category_id = self.add_category()
        response = Response()
        result = budget_router.insert(BudgetModel(month=9, category="Food", amount=450, year=2026), response)
        self.assertIn("inserted successfully", result["DONE"])

        response = Response()
        budget_router.change_budget(ChangeBudget(month=9, category="Food", amount=500, year=2026), response)
        with self.Session() as db:
            budget = db.query(Budget).filter_by(month=9, category=category_id, year=2026).one()
            self.assertEqual(float(budget.amount), 500.0)

        listed = budget_router.list_budgets(ListBudget(month=9, year=2026), Response())
        self.assertEqual(len(listed["budgets"]), 1)

        response = Response()
        result = budget_router.remove_budget(DeleteBudget(month=9, category="Food", year=2026), response)
        self.assertIn("removed successfully", result["DONE"])

    def test_budget_validation_and_missing_records(self):
        self.add_category()
        response = Response()
        result = budget_router.insert(
            BudgetModel(month=12, category="Food", amount=10, year=2026), response
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["ERROR"], "Invalid month")

        response = Response()
        result = budget_router.change_budget(
            ChangeBudget(month=9, category="Food", amount=10, year=2026), response
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("does not exist", result["ERROR"])

        response = Response()
        result = budget_router.remove_budget(
            DeleteBudget(month=9, category="Food", year=2026), response
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("does not exist", result["ERROR"])

    def test_summary_endpoint(self):
        food_id = self.add_category(name="Food")
        transport_id = self.add_category(name="Transport")
        with self.Session() as db:
            db.add(Budget(month=9, category=food_id, amount=100, year=2026))
            db.add_all([
                Transaction(
                    type="income", amount=250, date=datetime(2026, 10, 1),
                    description="", category=food_id, created_at=datetime(2026, 10, 1, 1),
                ),
                Transaction(
                    type="expense", amount=40, date=datetime(2026, 10, 2),
                    description="Food", category=food_id, created_at=datetime(2026, 10, 2, 1),
                ),
                Transaction(
                    type="expense", amount=60, date=datetime(2026, 10, 3),
                    description="Transport", category=transport_id,
                    created_at=datetime(2026, 10, 3, 1),
                ),
            ])
            db.commit()

        result = summary_router.get_montly_summary(
            MonthlySummary(month=9, year=2026), Response()
        )
        self.assertEqual(result["total income"], 250)
        self.assertEqual(result["total expense"], 100)
        self.assertEqual(result["balance"], 150)
        self.assertEqual(
            result["summary by categories"],
            [
                {"category": "Transport", "spent": 60, "budget": None, "left": None},
                {"category": "Food", "spent": 40, "budget": 100, "left": 60},
            ],
        )

        empty = summary_router.get_montly_summary(
            MonthlySummary(month=0, year=2026), Response()
        )
        self.assertEqual(empty["summary by categories"], [])

    def test_summary_validation(self):
        response = Response()
        result = summary_router.get_montly_summary(
            MonthlySummary(month=12, year=2026), response
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["ERROR"], "Invalid month")

    def test_transaction_insert_details_and_change(self):
        self.add_category()
        transaction = TransactionModel(
            type="expense", amount=25.5, date="2026-10-10", description="Lunch", category="Food"
        )
        response = Response()
        result = transactions_router.insert(transaction, response)
        self.assertIn("created successfully", result["DONE"])
        with self.Session() as db:
            created = db.query(Transaction).one()
            transaction_id = created.id
            self.assertEqual(created.date.isoformat(), "2026-10-10T00:00:00")

        details = transactions_router.transaction_details(TransactionDetails(id=transaction_id), Response())
        self.assertEqual(details["transaction"].description, "Lunch")

        changed = TransactionModel(
            type="income", amount=30, date="2026-10-11", description="Refund", category="Food"
        )
        result = transactions_router.change_transaction(
            ChangeTransaction(id=transaction_id, transaction=changed),
            Response(),
        )
        self.assertIn("updated successfully", result["DONE"])
        with self.Session() as db:
            saved = db.query(Transaction).one()
            self.assertEqual(saved.type, "income")
            self.assertEqual(saved.description, "Refund")
            self.assertEqual(saved.category, 1)

    def test_transaction_delete_and_missing_details(self):
        category_id = self.add_category()
        with self.Session() as db:
            transaction = Transaction(
                type="expense", amount=10, date=datetime(2026, 10, 1),
                description="", category=category_id, created_at=datetime.now(),
            )
            db.add(transaction)
            db.commit()
            transaction_id = transaction.id

        result = transactions_router.delete_transaction(
            TransactionDetails(id=transaction_id), Response()
        )
        self.assertIn("deleted successfully", result["DONE"])
        response = Response()
        result = transactions_router.transaction_details(TransactionDetails(id=transaction_id), response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["ERROR"], "Transaction does not exist")

    def test_transaction_validation_rules(self):
        self.add_category()
        for transaction in [
            TransactionModel(type="other", amount=10, date="2026-10-01", description="", category="Food"),
            TransactionModel(type="expense", amount=0, date="2026-10-01", description="", category="Food"),
            TransactionModel(type="expense", amount=10, date="2026-10-01", description="x" * 201, category="Food"),
        ]:
            response = Response()
            result = transactions_router.insert(transaction, response)
            self.assertEqual(response.status_code, 400)
            self.assertIn("ERROR", result)

        transactions_router.insert(
            TransactionModel(
                type="expense", amount=10.129, date="2026-10-01",
                description="", category="Food",
            ),
            Response(),
        )
        with self.Session() as db:
            self.assertEqual(float(db.query(Transaction).one().amount), 10.13)

    def test_invalid_transaction_date_is_rejected(self):
        response = Response()
        result = transactions_router.insert(
            TransactionModel(
                type="expense", amount=10, date="2026-02-30", description="bad date", category="Food"
            ),
            response,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date", result["ERROR"])


    def test_csv_import_saves_valid_rows_and_reports_invalid_rows(self):
        self.add_category(name="food")
        csv_data = (
            "type,amount,date,description,category\n"
            "expense,12.50,2026-10-28,Coffee,food\n"
            "expense,8.00,2026-02-30,Invalid date,food\n"
            "income,100.00,2026-10-28,Unknown category,missing\n"
        )
        upload = UploadFile(file=io.BytesIO(csv_data.encode("utf-8")), filename="transactions.csv")

        result = asyncio.run(transactions_router.import_transactions(Response(), upload))

        self.assertEqual(result["DONE"], "1 transaction(s) imported successfully")
        self.assertEqual(len(result["errors"]), 2)
        with self.Session() as db:
            imported = db.query(Transaction).one()
            self.assertEqual(imported.description, "Coffee")
            self.assertEqual(imported.category, 1)
            self.assertIsNotNone(imported.created_at)

    def test_transaction_list_filters_sorts_and_paginates(self):
        category_id = self.add_category(name="food")
        rows = [
            ("Lunch old", "2026-10-01", 1),
            ("Lunch same date older", "2026-10-02", 2),
            ("Lunch same date newer", "2026-10-02", 3),
            ("Lunch middle", "2026-10-03", 4),
            ("Lunch newest date older", "2026-10-04", 5),
            ("Lunch newest", "2026-10-04", 6),
        ]
        with self.Session() as db:
            for description, date_text, hour in rows:
                db.add(Transaction(
                    type="expense",
                    amount=10,
                    date=datetime.fromisoformat(date_text),
                    description=description,
                    category=category_id,
                    created_at=datetime(2026, 10, 28, hour),
                ))
            db.commit()

        first_page = transactions_router.list_transactions(
            ListTransations(
                start_date=None, end_date=None, category="food", type="expense",
                description="lunch", page=1,
            ),
            Response(),
        )
        self.assertEqual(
            [tx.description for tx in first_page["transactions"]],
            ["Lunch newest", "Lunch newest date older", "Lunch middle", "Lunch same date newer"],
        )

        second_page = transactions_router.list_transactions(
            ListTransations(
                start_date=None, end_date=None, category="food", type="expense",
                description="lunch", page=2,
            ),
            Response(),
        )
        self.assertEqual(
            [tx.description for tx in second_page["transactions"]],
            ["Lunch same date older", "Lunch old"],
        )


if __name__ == "__main__":
    unittest.main()


