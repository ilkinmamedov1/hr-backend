from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app

USERS = {
    "admin": ("admin@hr.local", "Admin123!"),
    "hr": ("hr@hr.local", "Hr12345!"),
    "manager": ("manager@hr.local", "Mgr12345!"),
    "employee": ("employee@hr.local", "Emp12345!"),
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient, role: str) -> dict[str, str]:
    email, password = USERS[role]
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_period_endpoints_used_by_workflow_ui(client):
    headers = auth_headers(client, "admin")
    contract = client.get("/api/v1/contracts?limit=1", headers=headers).json()["items"][0]
    contract_id = contract["id"]
    for path in (
        f"/api/v1/contracts/{contract_id}/amendments",
        f"/api/v1/contracts/{contract_id}/leave-balances",
        f"/api/v1/employees/{contract['employee_id']}/final-settlement-preview?termination_date="
        + date.today().isoformat(),
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 200, response.text


def test_offboarding_checklist_is_idempotent_and_cleaned_up(client):
    headers = auth_headers(client, "admin")
    existing = client.get("/api/v1/offboarding/1", headers=headers)
    assert existing.status_code == 200, existing.text

    first = client.post("/api/v1/offboarding/1/checklist", headers=headers, json={})
    assert first.status_code == 201, first.text
    created = first.json()
    assert len(created) >= 1

    second = client.post("/api/v1/offboarding/1/checklist", headers=headers, json={})
    assert second.status_code == 201, second.text
    assert second.json() == []

    for row in created:
        response = client.delete(f"/api/v1/offboarding-clearances/{row['id']}", headers=headers)
        assert response.status_code == 204, response.text


def test_offboarding_requires_hr_write(client):
    manager_headers = auth_headers(client, "manager")
    response = client.post(
        "/api/v1/offboarding/1/checklist", headers=manager_headers, json={}
    )
    assert response.status_code == 403

    employee_headers = auth_headers(client, "employee")
    response = client.get("/api/v1/offboarding/1", headers=employee_headers)
    assert response.status_code == 403


def test_emas_queue_and_sync_flow(client):
    headers = auth_headers(client, "admin")
    queued = client.post(
        "/api/v1/compliance/emas/queue",
        headers=headers,
        json={"entity_type": "EMPLOYEE", "entity_id": 1, "action_type": "SYNC"},
    )
    assert queued.status_code == 201, queued.text
    log = queued.json()
    assert log["emas_status"] == "QUEUED"

    synced = client.post(
        f"/api/v1/compliance/emas/{log['id']}/mark-synced",
        headers=headers,
        json={},
    )
    assert synced.status_code == 200, synced.text
    assert synced.json()["emas_status"] == "SYNCED"
    assert synced.json()["synced_at"]

    deleted = client.delete(f"/api/v1/emas-sync-logs/{log['id']}", headers=headers)
    assert deleted.status_code == 204, deleted.text
