# Budget Tracker API

The API is built with FastAPI. Endpoints are registered at the root path with no version prefix. JSON request bodies are used unless an endpoint is marked as a multipart upload.

## Endpoint index

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Welcome message |
| POST | `/categories/insert` | Create a category |
| GET | `/categories` | List categories |
| PUT | `/categories/change/name` | Rename a category |
| PUT | `/categories/change/color` | Change a category color |
| DELETE | `/categories/delete` | Delete a category |
| POST | `/budget/insert` | Create a monthly budget |
| PUT | `/budget/change` | Update a monthly budget |
| DELETE | `/budget/remove` | Remove a monthly budget |
| GET | `/budget/month` | List budgets for a month |
| POST | `/transactions/insert` | Create a transaction |
| GET | `/transactions/details` | Get one transaction |
| PUT | `/transactions/change` | Update a transaction |
| DELETE | `/transactions/delete` | Delete a transaction |
| GET | `/transactions` | Filter and page transactions |
| POST | `/transactions/import` | Import transactions from CSV |
| GET | `/summary` | Get a monthly summary |

## Root

### `GET /`

Response:

```json
{"message":"Welcome to Budget Tracker API"}
```

## Categories

Category names are trimmed, must contain 1–30 characters, and are unique regardless of letter case.
Colors use six-digit hexadecimal format.

### `POST /categories/insert`

```json
{"name":"Food","color":"#12ABCF"}
```

Returns `200` with `{"DONE":"Category Food created successfully"}`.

### `GET /categories`

Returns `{"categories":[...]}`. Categories are sorted by name ascending.

### `PUT /categories/change/name`

```json
{"old_name":"Food","new_name":"Groceries"}
```

### `PUT /categories/change/color`

```json
{"name":"Food","new_color":"#12ABCF"}
```

Both update endpoints return a `DONE` message on success.

### `DELETE /categories/delete`

```json
{"category":"Food"}
```

Categories with transactions cannot be deleted. Associated budgets are deleted with the category.

## Budgets

Months are zero-based: `0` is January and `11` is December. Budget amounts range from `0` to `1,000,000`. 
Values are stored with two decimal places by the database.

### `POST /budget/insert`

```json
{"month":2,"category":"Food","amount":700,"year":2025}
```

### `PUT /budget/change`

Uses the same request body as `/budget/insert`.

### `DELETE /budget/remove`

```json
{"month":2,"category":"Food","year":2025}
```

### `GET /budget/month`

This endpoint expects a JSON body:

```json
{"month":2,"year":2025}
```

Returns `{"budgets":[...]}`.

## Transactions

Transaction fields:

```json
{
  "type":"expense",
  "amount":24.5,
  "date":"2025-03-14",
  "description":"Lunch",
  "category":"Food"
}
```

`type` must be `income` or `expense`; amounts must be greater than `0` and at most `1,000,000`; 
dates use `YYYY-MM-DD`; descriptions are optional and may contain up to 200 characters; 
categories must already exist. Values are stored with two decimal places by the database.

### `POST /transactions/insert`

Accepts one transaction object and returns a success message.

### `GET /transactions/details`

```json
{"id":1}
```

Returns `{"transaction":{...}}`.

### `PUT /transactions/change`

```json
{
  "id":1,
  "transaction":{
    "type":"expense",
    "amount":26.5,
    "date":"2025-03-14",
    "description":"Lunch",
    "category":"Food"
  }
}
```

### `DELETE /transactions/delete`

```json
{"id":1}
```

### `GET /transactions`

This endpoint expects a JSON body. All fields are required; unused filters should be `null`.

```json
{
  "start_date":null,
  "end_date":null,
  "category":null,
  "type":null,
  "description":null,
  "page":1
}
```

Dates are inclusive. Results are ordered newest first, with four transactions per page. 
Description matching is case-insensitive.

### `POST /transactions/import`

Upload a `multipart/form-data` file using the field name `file`. The CSV header must be:

```text
type,amount,date,description,category
```

The response reports the number of imported rows and any invalid rows:

```json
{
  "DONE":"2 transaction(s) imported successfully",
  "errors":[]
}
```

## Monthly summary

### `GET /summary`

This endpoint expects a JSON body:

```json
{"month":2,"year":2025}
```

The response contains total income, total expense, balance, and category summaries:

```json
{
  "total income":4200.0,
  "total expense":1350.0,
  "balance":2850.0,
  "summary by categories":[
    {"category":"Food","spent":500.0,"budget":700.0,"left":200.0}
  ]
}
```

Category summaries include categories with spending or a budget and are ordered by spending descending, then category name descending.

## Errors

Invalid input, missing records, duplicate categories, and broken business rules return an `ERROR` message. 
Database failures return HTTP `500`.
