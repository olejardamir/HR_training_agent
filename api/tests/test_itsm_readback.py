from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_itsm_ticket_get_unknown_ticket_returns_404():
    resp = client.get("/mock/itsm/tickets/some_ticket_id")
    assert resp.status_code == 404


def test_itsm_ticket_list_all_returns_list():
    resp = client.get("/mock/itsm/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
