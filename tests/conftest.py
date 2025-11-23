# tests/conftest.py

import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from main import app
import database
import models

TEST_DB_FD, TEST_DB_PATH = tempfile.mkstemp()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
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
    database.Base.metadata.create_all(bind=engine_test)
    yield
    try:
        os.close(TEST_DB_FD)
        os.remove(TEST_DB_PATH)
    except PermissionError:
        pass



@pytest.fixture
def client():
    return TestClient(app)
