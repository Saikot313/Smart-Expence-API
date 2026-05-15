import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "smartexpense.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            category_id INTEGER NOT NULL,
            note TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
        )
    """)

    # Seed default categories
    default_categories = [
        ("Food & Dining", "Restaurants, groceries, snacks"),
        ("Transport", "Bus, rickshaw, fuel, ride-sharing"),
        ("Shopping", "Clothing, electronics, household"),
        ("Health", "Medicine, doctor visits, gym"),
        ("Entertainment", "Movies, subscriptions, games"),
        ("Education", "Books, courses, tuition"),
        ("Utilities", "Electricity, internet, water"),
        ("Other", "Miscellaneous expenses"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
        default_categories,
    )

    conn.commit()
    conn.close()
