from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.compliance import EmasSyncLog
from app.models.contract import EmploymentContract, HrOrder
from app.models.employee import Employee
from app.models.time import ProductionCalendar
from app.services.calendar_service import generate_year_calendar

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


def test_mourning_calendar_and_pre_mourning_short_day():
    with SessionLocal() as db:
        generate_year_calendar(db, 2026)
        jan20 = db.scalar(
            select(ProductionCalendar).where(ProductionCalendar.cal_date == date(2026, 1, 20))
        )
        assert jan20 is not None
        assert jan20.day_type == "MOURNING"
        assert float(jan20.norm_hours_40) == 0.0

        jan19 = db.scalar(
            select(ProductionCalendar).where(ProductionCalendar.cal_date == date(2026, 1, 19))
        )
        assert jan19 is not None
        assert jan19.day_type == "SHORT_WORKDAY"
        assert float(jan19.norm_hours_40) == 7.00
        assert float(jan19.norm_hours_36) == 6.20
        assert "Hüznqabağı" in (jan19.description or "")


def test_hr_order_pdf_endpoint(client):
    headers = auth_headers(client, "admin")
    orders = client.get("/api/v1/hr-orders?limit=1", headers=headers).json()
    if orders.get("items"):
        order_id = orders["items"][0]["id"]
        res = client.get(f"/api/v1/hr-orders/{order_id}/order.pdf", headers=headers)
        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF-")


def test_offer_letter_pdf_endpoint(client):
    headers = auth_headers(client, "admin")
    apps = client.get("/api/v1/applications?limit=1", headers=headers).json()
    if apps.get("items"):
        app_id = apps["items"][0]["id"]
        res = client.get(f"/api/v1/applications/{app_id}/offer-letter.pdf", headers=headers)
        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF-")


def test_employment_reference_pdf_endpoints(client):
    admin_hdr = auth_headers(client, "admin")
    emp_hdr = auth_headers(client, "employee")

    employees = client.get("/api/v1/employees?limit=1", headers=admin_hdr).json()
    if employees.get("items"):
        emp_id = employees["items"][0]["id"]
        res = client.get(f"/api/v1/employees/{emp_id}/reference.pdf?purpose=Bank", headers=admin_hdr)
        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF-")

    ess_res = client.get("/api/v1/ess/reference.pdf?purpose=Viza", headers=emp_hdr)
    assert ess_res.status_code == 200, ess_res.text
    assert ess_res.headers["content-type"] == "application/pdf"
    assert ess_res.content.startswith(b"%PDF-")


def test_military_report_forma_t2_endpoint(client):
    headers = auth_headers(client, "admin")
    res = client.get("/api/v1/compliance/military-report?organization_id=1", headers=headers)
    assert res.status_code == 200, res.text
    assert "text/csv" in res.headers["content-type"]
    assert "Hərbi mükəlləfiyyət" in res.text
    assert "SHXÇDX" in res.text


def test_trip_advance_norms_calculation(client):
    headers = auth_headers(client, "admin")

    baku_res = client.post(
        "/api/v1/trips/calculate-advance",
        headers=headers,
        json={"destination_city": "Bakı", "is_foreign": False, "start_date": "2026-06-01", "end_date": "2026-06-03"},
    )
    assert baku_res.status_code == 200, baku_res.text
    baku_data = baku_res.json()
    assert baku_data["days"] == 3
    assert baku_data["daily_allowance"] == 90.0

    foreign_res = client.post(
        "/api/v1/trips/calculate-advance",
        headers=headers,
        json={"destination_city": "İstanbul", "is_foreign": True, "start_date": "2026-06-01", "end_date": "2026-06-05"},
    )
    assert foreign_res.status_code == 200, foreign_res.text
    foreign_data = foreign_res.json()
    assert foreign_data["days"] == 5
    assert foreign_data["daily_allowance"] == 150.0


def test_short_leave_monthly_limit_validation(client):
    headers = auth_headers(client, "admin")
    employees = client.get("/api/v1/employees?limit=1", headers=headers).json()
    emp_id = employees["items"][0]["id"]

    res_excess = client.post(
        "/api/v1/short-leaves",
        headers=headers,
        json={
            "employee_id": emp_id,
            "leave_date": "2026-08-10",
            "start_time": "10:00",
            "end_time": "19:00",
            "hours": 9.0,
            "reason": "Artıq saat",
        },
    )
    assert res_excess.status_code == 400
    assert "8 saatdan çox ola bilməz" in res_excess.json()["detail"]
