# tests/conftest.py
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
import database
import models

# создаём отдельную временную SQLite-БД для тестов
TEST_DB_FD, TEST_DB_PATH = tempfile.mkstemp()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[database.get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    models.Base.metadata.create_all(bind=engine_test)
    yield
    os.close(TEST_DB_FD)
    os.remove(TEST_DB_PATH)


@pytest.fixture
def client():
    return TestClient(app)


def create_todo(client, title="Test todo", description="Some description"):
    payload = {
        "title": title,
        "description": description,
        "completed": False,
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    return response.json()
