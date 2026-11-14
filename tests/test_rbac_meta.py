import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.api.crud import ENTITY_ACL, ensure_org_access
from app.api.routers.meta import ENTITY_DEFS
from app.core.database import SessionLocal
from app.main import app
from app.models.employee import Employee
from app.models.leave import LeaveRequest, LeaveType
from app.models.organization import Organization
from app.models.user import User
from app.services.export_service import _csv_safe

USERS = {
    "admin": ("admin@hr.local", "Admin123!"),
    "hr": ("hr@hr.local", "Hr12345!"),
    "accountant": ("accountant@hr.local", "Acc12345!"),
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


def meta(client: TestClient, role: str) -> dict:
    response = client.get("/api/v1/meta/entities", headers=auth_headers(client, role))
    assert response.status_code == 200, response.text
    return response.json()


def test_acl_registry_covers_all_entities():
    entity_keys = {definition["key"] for definition in ENTITY_DEFS}
    assert entity_keys <= set(ENTITY_ACL)
    for acl in ENTITY_ACL.values():
        assert "SUPERADMIN" in acl["read_roles"]
        assert "SUPERADMIN" in acl["write_roles"]
        assert "SUPERADMIN" in acl["delete_roles"]


def test_meta_requires_authentication(client):
    assert client.get("/api/v1/meta/entities").status_code == 401


def test_admin_sees_every_entity_and_screen(client):
    data = meta(client, "admin")
    assert len(data["entities"]) == len(ENTITY_DEFS)
    assert {screen["key"] for screen in data["screens"]} == {
        "dashboard", "structure", "payroll-runs", "leave-requests", "sick-leaves",
        "timesheets", "production-calendar", "reports", "compliance", "recruitment",
        "onboarding", "approvals", "mss", "users", "audit", "ess",
    }
    employees = next(entity for entity in data["entities"] if entity["key"] == "employees")
    assert "HR_SPECIALIST" in employees["permissions"]["write_roles"]


def test_accountant_reads_payroll_but_not_recruitment(client):
    data = meta(client, "accountant")
    entity_keys = {entity["key"] for entity in data["entities"]}
    screen_keys = {screen["key"] for screen in data["screens"]}
    assert "payroll-runs" in screen_keys
    assert "compliance" in screen_keys
    assert "onboarding" not in screen_keys
    assert "approvals" not in screen_keys
    assert "vacancies" not in entity_keys
    assert "onboarding-tasks" not in entity_keys
    assert "employees" in entity_keys
    employees = next(entity for entity in data["entities"] if entity["key"] == "employees")
    assert "ACCOUNTANT" not in employees["permissions"]["write_roles"]


def test_manager_sees_recruitment_but_not_payroll(client):
    data = meta(client, "manager")
    entity_keys = {entity["key"] for entity in data["entities"]}
    screen_keys = {screen["key"] for screen in data["screens"]}
    assert "onboarding" in screen_keys
    assert "approvals" in screen_keys
    assert "payroll-runs" not in screen_keys
    assert "compliance" not in screen_keys
    assert "vacancies" in entity_keys
    assert "payroll-components" not in entity_keys
    vacancies = next(entity for entity in data["entities"] if entity["key"] == "vacancies")
    assert "DEPT_MANAGER" not in vacancies["permissions"]["write_roles"]


def test_employee_gets_ess_only(client):
    data = meta(client, "employee")
    assert {screen["key"] for screen in data["screens"]} == {"ess"}
    assert "EMPLOYEE" in data["screens"][0]["roles"]


def test_read_only_roles_cannot_manage_screens(client):
    accountant_screens = {screen["key"]: screen for screen in meta(client, "accountant")["screens"]}
    assert "ACCOUNTANT" not in accountant_screens["leave-requests"]["manage_roles"]
    assert "ACCOUNTANT" not in accountant_screens["production-calendar"]["manage_roles"]
    manager_screens = {screen["key"]: screen for screen in meta(client, "manager")["screens"]}
    assert "DEPT_MANAGER" not in manager_screens["onboarding"]["manage_roles"]
    assert "DEPT_MANAGER" in manager_screens["approvals"]["manage_roles"]


def test_org_scoped_access_rejects_foreign_records():
    user = SimpleNamespace(role="HR_DIRECTOR", organization_id=1)
    ensure_org_access(Employee, SimpleNamespace(organization_id=1), user)
    with pytest.raises(HTTPException) as exc_info:
        ensure_org_access(Employee, SimpleNamespace(organization_id=2), user)
    assert exc_info.value.status_code == 404


def test_organization_access_is_scoped():
    user = SimpleNamespace(role="HR_DIRECTOR", organization_id=1)
    ensure_org_access(Organization, SimpleNamespace(id=1), user)
    with pytest.raises(HTTPException) as exc_info:
        ensure_org_access(Organization, SimpleNamespace(id=2), user)
    assert exc_info.value.status_code == 404


def test_superadmin_bypasses_org_scope():
    user = SimpleNamespace(role="SUPERADMIN", organization_id=1)
    ensure_org_access(Employee, SimpleNamespace(organization_id=2), user)
    ensure_org_access(Organization, SimpleNamespace(id=2), user)


def test_security_headers_and_public_info(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    info = client.get("/api/v1/system/info")
    assert info.status_code == 200
    assert {"demo_enabled", "docs_enabled"}.issubset(info.json())
    assert client.get("/health").status_code == 200


def test_protected_endpoints_require_token(client):
    for path in (
        "/api/v1/employees",
        "/api/v1/payroll-runs",
        "/api/v1/audit-logs",
        "/api/v1/meta/entities",
    ):
        assert client.get(path).status_code == 401, path


def test_hr_cannot_escalate_or_reset_superadmin(client):
    hr = auth_headers(client, "hr")
    admin = auth_headers(client, "admin")
    current_admin = client.get("/api/v1/auth/me", headers=admin).json()

    create_privileged = client.post(
        "/api/v1/auth/users",
        headers=hr,
        json={
            "email": "escalate@example.com",
            "full_name": "Escalate User",
            "password": "StrongPass123!",
            "role": "SUPERADMIN",
        },
    )
    assert create_privileged.status_code == 403

    patch_admin = client.patch(
        f"/api/v1/auth/users/{current_admin['id']}",
        headers=hr,
        json={"role": "SUPERADMIN", "is_active": False},
    )
    assert patch_admin.status_code == 404

    reset_admin = client.post(
        f"/api/v1/auth/users/{current_admin['id']}/reset-password",
        headers=hr,
        json={"new_password": "HackedPassword123!"},
    )
    assert reset_admin.status_code == 404

    assert client.get("/api/v1/auth/me", headers=admin).status_code == 200


def test_short_passwords_are_rejected(client):
    admin = auth_headers(client, "admin")
    response = client.post(
        "/api/v1/auth/users",
        headers=admin,
        json={
            "email": f"short-{uuid.uuid4().hex[:8]}@example.com",
            "full_name": "Short Password",
            "password": "short",
            "role": "EMPLOYEE",
        },
    )
    assert response.status_code == 422


def test_password_reset_invalidates_existing_token(client):
    admin = auth_headers(client, "admin")
    email = f"token-{uuid.uuid4().hex[:8]}@example.com"
    password = "InitialPass123!"
    created = client.post(
        "/api/v1/auth/users",
        headers=admin,
        json={
            "email": email,
            "full_name": "Token Test",
            "password": password,
            "role": "EMPLOYEE",
            "organization_id": 1,
        },
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]
    try:
        login = client.post(
            "/api/v1/auth/login", data={"username": email, "password": password}
        )
        assert login.status_code == 200
        old_token = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert client.get("/api/v1/auth/me", headers=old_token).status_code == 200

        reset = client.post(
            f"/api/v1/auth/users/{user_id}/reset-password",
            headers=admin,
            json={"new_password": "ChangedPass123!"},
        )
        assert reset.status_code == 200
        assert client.get("/api/v1/auth/me", headers=old_token).status_code == 401

        new_login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": "ChangedPass123!"},
        )
        assert new_login.status_code == 200
    finally:
        with SessionLocal() as db:
            db.execute(delete(User).where(User.id == user_id))
            db.commit()


def test_cross_org_records_are_hidden(client):
    suffix = uuid.uuid4().hex[:6]
    with SessionLocal() as db:
        org = Organization(
            name=f"Cross Org {suffix}",
            voen=f"9{suffix:0<9}"[:10],
            sector_type="NON_OIL_PRIVATE",
            is_active=True,
        )
        db.add(org)
        db.flush()
        employee = Employee(
            organization_id=org.id,
            pin_code=f"T{suffix[:6]}",
            first_name="Cross",
            last_name=f"Org{suffix}",
            status="ACTIVE",
        )
        db.add(employee)
        db.flush()
        leave_type_id = db.scalar(select(LeaveType.id).limit(1))
        leave = LeaveRequest(
            organization_id=org.id,
            employee_id=employee.id,
            leave_type_id=leave_type_id,
            start_date=date.today(),
            end_date=date.today(),
            calendar_days=1,
            paid_days=1,
            excluded_holidays=0,
            status="PENDING",
        )
        db.add(leave)
        db.commit()
        org_id, employee_id, leave_id = org.id, employee.id, leave.id

    try:
        hr = auth_headers(client, "hr")
        admin = auth_headers(client, "admin")
        assert client.get(f"/api/v1/employees/{employee_id}/profile", headers=hr).status_code == 404
        assert client.get(f"/api/v1/organizations/{org_id}", headers=hr).status_code == 404
        docs = client.get(
            f"/api/v1/employee-documents?employee_id={employee_id}", headers=hr
        )
        assert docs.status_code == 200 and docs.json()["total"] == 0
        create_child = client.post(
            "/api/v1/employee-documents",
            headers=hr,
            json={"employee_id": employee_id, "doc_type": "OTHER", "doc_number": "X"},
        )
        assert create_child.status_code == 400
        assert client.get(f"/api/v1/analytics/dashboard?organization_id={org_id}", headers=hr).status_code == 404
        assert client.get(f"/api/v1/compliance/isb-report?year=2026&month=1&organization_id={org_id}", headers=hr).status_code == 404
        approve_foreign = client.post(
            f"/api/v1/leave-requests/{leave_id}/approve", headers=hr
        )
        assert approve_foreign.status_code == 404
        assert client.get(f"/api/v1/employees/{employee_id}/profile", headers=admin).status_code == 200
    finally:
        with SessionLocal() as db:
            db.execute(delete(LeaveRequest).where(LeaveRequest.id == leave_id))
            db.execute(delete(Employee).where(Employee.id == employee_id))
            db.execute(delete(Organization).where(Organization.id == org_id))
            db.commit()


def test_audit_and_generic_approvals_are_admin_only(client):
    hr = auth_headers(client, "hr")
    admin = auth_headers(client, "admin")
    assert client.get("/api/v1/audit-logs", headers=hr).status_code == 403
    assert client.get("/api/v1/audit-logs", headers=admin).status_code == 200
    assert client.get("/api/v1/approval-workflows", headers=hr).status_code == 403
    assert client.get("/api/v1/approvals", headers=hr).status_code == 200


def test_csv_formula_injection_is_sanitized():
    assert _csv_safe("=cmd|' /C calc'!A0").startswith("'=")
    assert _csv_safe("+1+1").startswith("'+")
    assert _csv_safe("@SUM(A1)").startswith("'@")
    assert _csv_safe("\tformula").startswith("'")
    assert _csv_safe("-900") == "-900"
    assert _csv_safe("-900.50") == "-900.50"
    assert _csv_safe("-1.5") == "-1.5"
    assert _csv_safe("-cmd").startswith("'-")
    assert _csv_safe(42) == 42
