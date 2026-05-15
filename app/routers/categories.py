from fastapi import APIRouter, HTTPException
from app.database.db import get_connection
from app.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryOut
from typing import List

router = APIRouter()


def row_to_category(row) -> CategoryOut:
    return CategoryOut(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        created_at=row["created_at"],
    )


@router.get("/", response_model=List[CategoryOut], summary="List all categories")
def list_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return [row_to_category(r) for r in rows]


@router.post("/", response_model=CategoryOut, status_code=201, summary="Create a category")
def create_category(body: CategoryCreate):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (body.name, body.description),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM categories WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_category(row)
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=409, detail=f"Category '{body.name}' already exists.")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/{category_id}", response_model=CategoryOut, summary="Get a category")
def get_category(category_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Category not found.")
    return row_to_category(row)


@router.put("/{category_id}", response_model=CategoryOut, summary="Update a category")
def update_category(category_id: int, body: CategoryUpdate):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found.")

    name = body.name or row["name"]
    description = body.description if body.description is not None else row["description"]

    try:
        conn.execute(
            "UPDATE categories SET name = ?, description = ? WHERE id = ?",
            (name, description, category_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        return row_to_category(updated)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.delete("/{category_id}", status_code=204, summary="Delete a category")
def delete_category(category_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Cannot delete category with existing expenses. Reassign expenses first.",
            )
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
