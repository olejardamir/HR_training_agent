from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base
from app.seed import reset_and_seed


def setup_database():
    Base.metadata.drop_all(bind=engine)
    reset_and_seed()


def teardown_database():
    Base.metadata.drop_all(bind=engine)


def get_client():
    return TestClient(app)
