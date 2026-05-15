#  SmartExpense API

A personal finance REST API built with **FastAPI**, **SQLite**, and **Python**.

## Features

- ✅ Full CRUD for **Expenses** and **Categories**
- ✅ **Category-based filtering** + date range + amount range + search
- ✅ **Summary endpoints** — totals, by-category breakdown, monthly trends
- ✅ **Top expenses** endpoint
- ✅ Input validation via Pydantic
- ✅ Auto-seeded default categories
- ✅ Interactive docs at `/docs`

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn app.main:app --reload

# 3. Open docs
# http://127.0.0.1:8000/docs
```

---

## API Endpoints

### 🏷️ Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/categories/` | List all categories |
| POST | `/categories/` | Create a category |
| GET | `/categories/{id}` | Get one category |
| PUT | `/categories/{id}` | Update a category |
| DELETE | `/categories/{id}` | Delete a category |

### 💸 Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/expenses/` | List expenses (with filters) |
| POST | `/expenses/` | Add an expense |
| GET | `/expenses/{id}` | Get one expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

#### Query Filters for `GET /expenses/`
| Param | Type | Description |
|-------|------|-------------|
| `category_id` | int | Filter by category |
| `start_date` | string | YYYY-MM-DD |
| `end_date` | string | YYYY-MM-DD |
| `min_amount` | float | Minimum amount |
| `max_amount` | float | Maximum amount |
| `search` | string | Search title/note |
| `limit` | int | Max results (default 50) |
| `offset` | int | Pagination offset |

### 📊 Summary
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/summary/` | Full summary (totals, by-category, by-month) |
| GET | `/summary/top-expenses` | Top N most expensive items |

---

## Example Requests

```bash
# Add an expense
curl -X POST http://localhost:8000/expenses/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":250,"category_id":1,"date":"2026-05-15"}'

# Filter by category and date
curl "http://localhost:8000/expenses/?category_id=1&start_date=2026-05-01"

# Get summary
curl http://localhost:8000/summary/

# Top 5 expenses
curl "http://localhost:8000/summary/top-expenses?limit=5"
```

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## Project Structure

```
SmartExpense/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database/
│   │   └── db.py            # SQLite connection & schema init
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response models
│   └── routers/
│       ├── expenses.py      # Expense CRUD + filtering
│       ├── categories.py    # Category CRUD
│       └── summary.py       # Summary & analytics
├── tests/
│   └── test_api.py          # Pytest test suite
├── requirements.txt
└── README.md
```
