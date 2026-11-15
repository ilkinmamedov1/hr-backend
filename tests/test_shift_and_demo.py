from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.main import app
from app.core.database import SessionLocal
from app.models.employee import Employee
from app.models.contract import EmploymentContract, HrOrder
from app.models.payroll import PayrollRun
from app.models.time import AttendanceLog, EmployeeSchedule, ProductionCalendar, Timesheet, WorkSchedule
from app.models.user import User


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient, email: str = "admin@hr.local", password: str = "Admin123!") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_work_schedule_presets(client):
    headers = auth_headers(client)
    res = client.get("/api/v1/work-schedules/presets", headers=headers)
    assert res.status_code == 200, res.text
    presets = res.json()
    assert len(presets) >= 6
    preset_keys = [p["key"] for p in presets]
    assert "SHIFT_3_STANDARD" in preset_keys
    assert "SHIFT_12_STANDARD" in preset_keys
    assert "SHIFT_24_STANDARD" in preset_keys
    assert "SHIFT_2_STANDARD" in preset_keys
    assert "STANDARD_5_DAYS" in preset_keys

    # Check shift 3 rules
    shift3 = next(p for p in presets if p["key"] == "SHIFT_3_STANDARD")
    assert shift3["schedule_type"] == "SHIFT_3"
    assert len(shift3["shift_rules_json"]["shifts"]) == 3


def test_work_schedule_crud_and_assignments(client):
    headers = auth_headers(client)

    # 1. Create a 12-hour shift schedule
    payload = {
        "organization_id": 1,
        "name": "12 Saatlıq Mühafizə Test",
        "schedule_type": "SHIFT_12",
        "weekly_hours": 40.0,
        "is_default": False,
        "shift_rules_json": {
            "rotation_pattern": "1 gün gündüz, 1 gün gecə, 2 gün ev",
            "shifts": [
                {"name": "Gündüz", "start": "08:00", "end": "20:00", "break_minutes": 60, "night_hours": 0},
                {"name": "Gecə", "start": "20:00", "end": "08:00", "break_minutes": 60, "night_hours": 8},
            ]
        }
    }
    create_res = client.post("/api/v1/work-schedules", json=payload, headers=headers)
    assert create_res.status_code in (200, 201), create_res.text
    schedule_data = create_res.json()
    schedule_id = schedule_data["id"]

    # 2. Get overview
    overview_res = client.get("/api/v1/work-schedules/overview", headers=headers)
    assert overview_res.status_code == 200
    items = overview_res.json()
    found = next((item for item in items if item["id"] == schedule_id), None)
    assert found is not None
    assert found["name"] == "12 Saatlıq Mühafizə Test"
    assert len(found["shifts"]) == 2

    # 3. Assign an employee
    emp_res = client.get("/api/v1/employees?limit=1", headers=headers)
    assert emp_res.status_code == 200
    emp_list = emp_res.json().get("items", [])
    if emp_list:
        emp_id = emp_list[0]["id"]
        assign_res = client.post(
            f"/api/v1/work-schedules/{schedule_id}/assign",
            json={"employee_ids": [emp_id], "effective_from": str(date.today())},
            headers=headers
        )
        assert assign_res.status_code == 200, assign_res.text
        assert assign_res.json()["assigned_count"] == 1

        # 4. View assignments
        get_assigns = client.get(f"/api/v1/work-schedules/{schedule_id}/assignments", headers=headers)
        assert get_assigns.status_code == 200
        assignments = get_assigns.json()
        assert len(assignments) >= 1
        assign_id = assignments[0]["id"]

        # 5. Delete assignment
        del_assign = client.delete(f"/api/v1/work-schedules/{schedule_id}/assignments/{assign_id}", headers=headers)
        assert del_assign.status_code == 200

    # 6. Delete the test schedule
    del_res = client.delete(f"/api/v1/work-schedules/{schedule_id}", headers=headers)
    assert del_res.status_code in (200, 204)


def test_toggle_demo_mode(client):
    headers = auth_headers(client)

    # Disable demo mode
    res = client.post("/api/v1/system/toggle-demo-mode", json={"enabled": False}, headers=headers)
    assert res.status_code == 200
    assert res.json()["demo_enabled"] is False

    info_res = client.get("/api/v1/system/info")
    assert info_res.status_code == 200
    assert info_res.json()["demo_enabled"] is False

    # Re-enable demo mode
    res2 = client.post("/api/v1/system/toggle-demo-mode", json={"enabled": True}, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["demo_enabled"] is True

    info_res2 = client.get("/api/v1/system/info")
    assert info_res2.status_code == 200
    assert info_res2.json()["demo_enabled"] is True


def test_wipe_demo_data(client):
    headers = auth_headers(client)

    # Call wipe demo data
    res = client.post("/api/v1/system/wipe-demo-data", headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "ok"
    assert data["demo_enabled"] is False

    # Check system info reflects demo_enabled == False
    info_res = client.get("/api/v1/system/info")
    assert info_res.status_code == 200
    assert info_res.json()["demo_enabled"] is False

    # Verify database state
    db = SessionLocal()
    try:
        # All employees and contracts wiped
        assert db.scalar(select(func.count(Employee.id))) == 0
        assert db.scalar(select(func.count(EmploymentContract.id))) == 0
        assert db.scalar(select(func.count(HrOrder.id))) == 0
        assert db.scalar(select(func.count(Timesheet.id))) == 0
        assert db.scalar(select(func.count(AttendanceLog.id))) == 0
        assert db.scalar(select(func.count(PayrollRun.id))) == 0

        # Reference tables still intact!
        assert db.scalar(select(func.count(ProductionCalendar.cal_date))) > 0

        # Superadmin user still intact!
        superadmin = db.scalar(select(User).where(User.email == "admin@hr.local"))
        assert superadmin is not None
        assert superadmin.role == "SUPERADMIN"
    finally:
        from app.seed import seed_demo
        seed_demo(db)
        db.close()

