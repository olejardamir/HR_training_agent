import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base
from app.seed import reset_and_seed


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    reset_and_seed()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
