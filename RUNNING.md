# Running the project

## Requirements

- Python 3.10 or newer
- MySQL 8.x
- MySQL command-line client

## Install dependencies

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn sqlalchemy pymysql python-multipart
```

If PowerShell activation is unavailable:

```powershell
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy pymysql python-multipart
```

## Initialize MySQL

The default connection is configured in `database.py`:

```text
mysql+pymysql://root:123@localhost:3306/rbt_backend_api
```

Create the database and tables:

```powershell
mysql -u root -p < database\database_dump.sql
```

This resets the application tables. If the schema already exists, load optional development seed data instead:

```powershell
mysql -u root -p rbt_backend_api < database\seed_data.sql
```

Update `DATABASE_URL` in `database.py` if your MySQL credentials or connection details differ.

## Start the API

```powershell
python -m uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

## Manual requests

Send requests from Postman. The OpenAPI document is available at `http://127.0.0.1:8000/openapi.json`.

## Run automated tests

The tests use an in-memory SQLite database and do not require MySQL:

```powershell
python -m unittest discover -s tests -v
```
