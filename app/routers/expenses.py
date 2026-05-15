from fastapi import APIRouter, HTTPException, Query
from app.database.db import get_connection
from app.schemas.schemas import ExpenseCreate, ExpenseUpdate, ExpenseOut
from typing import List, Optional

router = APIRouter()


def row_to_expense(row) -> ExpenseOut:
    return ExpenseOut(
        id=row["id"],
        title=row["title"],
        amount=row["amount"],
        category_id=row["category_id"],
        category_name=row["category_name"] if "category_name" in row.keys() else None,
        note=row["note"],
        date=row["date"],
        created_at=row["created_at"],
    )


EXPENSE_SELECT = """
    SELECT e.*, c.name as category_name
    FROM expenses e
    LEFT JOIN categories c ON e.category_id = c.id
"""


@router.get("/", response_model=List[ExpenseOut], summary="List expenses with filters")
def list_expenses(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    search: Optional[str] = Query(None, description="Search in title or note"),
    limit: int = Query(50, ge=1, le=500, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    conn = get_connection()
    query = EXPENSE_SELECT + " WHERE 1=1"
    params = []

    if category_id is not None:
        query += " AND e.category_id = ?"
        params.append(category_id)
    if start_date:
        query += " AND e.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND e.date <= ?"
        params.append(end_date)
    if min_amount is not None:
        query += " AND e.amount >= ?"
        params.append(min_amount)
    if max_amount is not None:
        query += " AND e.amount <= ?"
        params.append(max_amount)
    if search:
        query += " AND (e.title LIKE ? OR e.note LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY e.date DESC, e.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [row_to_expense(r) for r in rows]


@router.post("/", response_model=ExpenseOut, status_code=201, summary="Add a new expense")
def create_expense(body: ExpenseCreate):
    conn = get_connection()
    # Validate category exists
    cat = conn.execute(
        "SELECT id FROM categories WHERE id = ?", (body.category_id,)
    ).fetchone()
    if not cat:
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        cursor = conn.execute(
            "INSERT INTO expenses (title, amount, category_id, note, date) VALUES (?, ?, ?, ?, ?)",
            (body.title, body.amount, body.category_id, body.note, body.date),
        )
        conn.commit()
        row = conn.execute(
            EXPENSE_SELECT + " WHERE e.id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_expense(row)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/{expense_id}", response_model=ExpenseOut, summary="Get a single expense")
def get_expense(expense_id: int):
    conn = get_connection()
    row = conn.execute(
        EXPENSE_SELECT + " WHERE e.id = ?", (expense_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Expense not found.")
    return row_to_expense(row)


@router.put("/{expense_id}", response_model=ExpenseOut, summary="Update an expense")
def update_expense(expense_id: int, body: ExpenseUpdate):
    conn = get_connection()
    row = conn.execute(
        EXPENSE_SELECT + " WHERE e.id = ?", (expense_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found.")

    if body.category_id:
        cat = conn.execute(
            "SELECT id FROM categories WHERE id = ?", (body.category_id,)
        ).fetchone()
        if not cat:
            conn.close()
            raise HTTPException(status_code=404, detail="Category not found.")

    title = body.title or row["title"]
    amount = body.amount or row["amount"]
    category_id = body.category_id or row["category_id"]
    note = body.note if body.note is not None else row["note"]
    date = body.date or row["date"]

    try:
        conn.execute(
            "UPDATE expenses SET title=?, amount=?, category_id=?, note=?, date=? WHERE id=?",
            (title, amount, category_id, note, date, expense_id),
        )
        conn.commit()
        updated = conn.execute(
            EXPENSE_SELECT + " WHERE e.id = ?", (expense_id,)
        ).fetchone()
        return row_to_expense(updated)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.delete("/{expense_id}", status_code=204, summary="Delete an expense")
def delete_expense(expense_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found.")
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
