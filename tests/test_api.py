import pytest
import os
import tempfile


@pytest.fixture(scope="session")
def client():
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_file.close()
    os.environ["DB_PATH"] = db_file.name

    from app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    os.unlink(db_file.name)


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "SmartExpense" in r.json()["message"]


def test_list_categories(client):
    r = client.get("/categories/")
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_create_category(client):
    r = client.post("/categories/", json={"name": "Test Category", "description": "For testing"})
    assert r.status_code == 201
    assert r.json()["name"] == "Test Category"


def test_create_duplicate_category(client):
    client.post("/categories/", json={"name": "Duplicate Cat"})
    r = client.post("/categories/", json={"name": "Duplicate Cat"})
    assert r.status_code == 409


def test_create_and_get_expense(client):
    cats = client.get("/categories/").json()
    cat_id = cats[0]["id"]
    payload = {"title": "Test Lunch", "amount": 150.0, "category_id": cat_id, "date": "2026-05-15"}
    r = client.post("/expenses/", json=payload)
    assert r.status_code == 201
    eid = r.json()["id"]
    r2 = client.get(f"/expenses/{eid}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Test Lunch"


def test_expense_not_found(client):
    r = client.get("/expenses/99999")
    assert r.status_code == 404


def test_filter_expenses_by_category(client):
    cats = client.get("/categories/").json()
    cat_id = cats[0]["id"]
    r = client.get(f"/expenses/?category_id={cat_id}")
    assert r.status_code == 200


def test_update_expense(client):
    cats = client.get("/categories/").json()
    cat_id = cats[0]["id"]
    r = client.post("/expenses/", json={"title": "Old Title", "amount": 100.0, "category_id": cat_id, "date": "2026-05-10"})
    eid = r.json()["id"]
    r2 = client.put(f"/expenses/{eid}", json={"title": "New Title", "amount": 200.0})
    assert r2.status_code == 200
    assert r2.json()["title"] == "New Title"


def test_delete_expense(client):
    cats = client.get("/categories/").json()
    cat_id = cats[0]["id"]
    r = client.post("/expenses/", json={"title": "To Delete", "amount": 50.0, "category_id": cat_id, "date": "2026-05-01"})
    eid = r.json()["id"]
    assert client.delete(f"/expenses/{eid}").status_code == 204
    assert client.get(f"/expenses/{eid}").status_code == 404


def test_summary(client):
    r = client.get("/summary/")
    assert r.status_code == 200
    data = r.json()
    assert "total_expenses" in data
    assert "by_category" in data
    assert "by_month" in data


def test_top_expenses(client):
    r = client.get("/summary/top-expenses?limit=3")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_expenses(client):
    cats = client.get("/categories/").json()
    cat_id = cats[0]["id"]
    client.post("/expenses/", json={"title": "Special Coffee", "amount": 80.0, "category_id": cat_id, "date": "2026-05-15"})
    r = client.get("/expenses/?search=Special")
    assert r.status_code == 200
    assert any("Special" in e["title"] for e in r.json())
