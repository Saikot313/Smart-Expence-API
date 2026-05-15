from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date


# ── Category Schemas ──────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Food & Dining")
    description: Optional[str] = Field(None, example="Restaurants and groceries")

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: str


# ── Expense Schemas ───────────────────────────────────────────────
class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Lunch at restaurant")
    amount: float = Field(..., gt=0, example=250.00)
    category_id: int = Field(..., example=1)
    note: Optional[str] = Field(None, example="Team lunch")
    date: str = Field(..., example="2026-05-15")

    @validator("date")
    def validate_date(cls, v):
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")
        return v

class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    note: Optional[str] = None
    date: Optional[str] = None

    @validator("date", pre=True, always=True)
    def validate_date(cls, v):
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")
        return v

class ExpenseOut(BaseModel):
    id: int
    title: str
    amount: float
    category_id: int
    category_name: Optional[str]
    note: Optional[str]
    date: str
    created_at: str


# ── Summary Schemas ───────────────────────────────────────────────
class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    total_amount: float
    expense_count: int
    percentage: float

class MonthlySummary(BaseModel):
    month: str
    total_amount: float
    expense_count: int

class SummaryOut(BaseModel):
    total_expenses: int
    total_amount: float
    average_expense: float
    by_category: list[CategorySummary]
    by_month: list[MonthlySummary]
