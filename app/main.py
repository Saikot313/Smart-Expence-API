from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.routers import expenses, categories, summary

app = FastAPI(
    title="SmartExpense API",
    description="A personal finance REST API with CRUD operations, category-based filtering, and expense summary.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(summary.router, prefix="/summary", tags=["Summary"])

@app.get("/", tags=["Health"])
def root():
    return {"message": "Welcome to SmartExpense API 💰", "docs": "/docs"}
