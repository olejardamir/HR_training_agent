import os
os.environ["DATABASE_URL"] = "sqlite:///./test_hr.db"

import pytest
from fastapi.testclient import TestClient
from app.database import engine, Base
from app.seed import reset_and_seed
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    reset_and_seed()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
