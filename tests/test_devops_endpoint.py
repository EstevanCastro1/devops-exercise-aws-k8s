import pytest
from fastapi.testclient import TestClient
from app.main import app, API_KEY

client = TestClient(app)


def _headers(jwt: str = "dummy-jwt"):
    return {
        "X-Parse-REST-API-Key": API_KEY,
        "X-JWT-KWY": jwt,
        "Content-Type": "application/json",
    }


def test_post_devops_ok():
    payload = {
        "message": "This is a test",
        "to": "Juan Perez",
        "from": "Rita Asturia",
        "timeToLifeSec": 45,
    }

    response = client.post("/DevOps", json=payload, headers=_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello Juan Perez your message will be send"


@pytest.mark.parametrize("method", ["get", "put", "delete", "patch"])
def test_other_methods_return_error(method):
    func = getattr(client, method)
    response = func("/DevOps", headers=_headers())
    assert response.status_code == 200
    assert response.text == "ERROR"


def test_invalid_api_key():
    payload = {
        "message": "This is a test",
        "to": "Juan Perez",
        "from": "Rita Asturia",
        "timeToLifeSec": 45,
    }
    headers = _headers()
    headers["X-Parse-REST-API-Key"] = "wrong-key"

    response = client.post("/DevOps", json=payload, headers=headers)
    assert response.status_code == 401
