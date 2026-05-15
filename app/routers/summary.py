from fastapi import APIRouter, Query
from app.database.db import get_connection
from app.schemas.schemas import SummaryOut, CategorySummary, MonthlySummary
from typing import Optional

router = APIRouter()


@router.get("/", response_model=SummaryOut, summary="Get expense summary")
def get_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
):
    conn = get_connection()
    base_filter = " WHERE 1=1"
    params = []

    if start_date:
        base_filter += " AND e.date >= ?"
        params.append(start_date)
    if end_date:
        base_filter += " AND e.date <= ?"
        params.append(end_date)
    if category_id:
        base_filter += " AND e.category_id = ?"
        params.append(category_id)

    # Overall totals
    totals = conn.execute(
        f"SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total FROM expenses e{base_filter}",
        params,
    ).fetchone()

    total_count = totals["cnt"]
    total_amount = totals["total"]
    average = round(total_amount / total_count, 2) if total_count > 0 else 0.0

    # By category
    cat_rows = conn.execute(
        f"""
        SELECT c.id, c.name, COUNT(*) as cnt, COALESCE(SUM(e.amount), 0) as total
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        {base_filter}
        GROUP BY e.category_id
        ORDER BY total DESC
        """,
        params,
    ).fetchall()

    by_category = [
        CategorySummary(
            category_id=r["id"],
            category_name=r["name"] or "Unknown",
            total_amount=round(r["total"], 2),
            expense_count=r["cnt"],
            percentage=round((r["total"] / total_amount * 100) if total_amount > 0 else 0, 2),
        )
        for r in cat_rows
    ]

    # By month
    month_rows = conn.execute(
        f"""
        SELECT strftime('%Y-%m', e.date) as month, COUNT(*) as cnt, SUM(e.amount) as total
        FROM expenses e
        {base_filter}
        GROUP BY month
        ORDER BY month DESC
        """,
        params,
    ).fetchall()

    by_month = [
        MonthlySummary(
            month=r["month"],
            total_amount=round(r["total"], 2),
            expense_count=r["cnt"],
        )
        for r in month_rows
    ]

    conn.close()

    return SummaryOut(
        total_expenses=total_count,
        total_amount=round(total_amount, 2),
        average_expense=average,
        by_category=by_category,
        by_month=by_month,
    )


@router.get("/top-expenses", summary="Get top N most expensive items")
def top_expenses(
    limit: int = Query(5, ge=1, le=50),
    category_id: Optional[int] = Query(None),
):
    conn = get_connection()
    query = """
        SELECT e.*, c.name as category_name
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE 1=1
    """
    params = []
    if category_id:
        query += " AND e.category_id = ?"
        params.append(category_id)
    query += " ORDER BY e.amount DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "amount": r["amount"],
            "category": r["category_name"],
            "date": r["date"],
        }
        for r in rows
    ]
