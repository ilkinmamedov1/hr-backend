from datetime import date
import pytest
from fastapi.testclient import TestClient

from app.main import app

USERS = {
    "superadmin": ("admin@hr.local", "Admin123!"),
    "hr_director": ("hr@hr.local", "Hr12345!"),
    "accountant": ("accountant@hr.local", "Acc12345!"),
    "dept_manager": ("manager@hr.local", "Mgr12345!"),
    "employee": ("employee@hr.local", "Emp12345!"),
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def get_headers(client: TestClient, role_key: str) -> dict[str, str]:
    email, password = USERS[role_key]
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {role_key}: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# =========================================================================
# 1. SECURITY AUDIT TESTS (SQL Injection, Auth Bypass, Headers)
# =========================================================================

def test_sql_injection_in_login(client):
    """SQL injection payloads in login must never bypass authentication."""
    malicious_inputs = [
        "admin@hr.local' OR '1'='1",
        "admin@hr.local' OR '1'='1' --",
        "' OR ''='",
        "\" OR \"\"=\"",
        "admin' UNION SELECT 1, 'hacked', 'pass'--",
    ]
    for username in malicious_inputs:
        resp = client.post("/api/v1/auth/login", data={"username": username, "password": "wrongpassword"})
        assert resp.status_code in (400, 401), f"Unexpected status {resp.status_code} for payload: {username}"


def test_sql_injection_in_search_and_filtering(client):
    """SQL injection in generic search query (?q=), filters and sorting must be safely parameterized."""
    headers = get_headers(client, "superadmin")
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT NULL, NULL, NULL, NULL --",
        "1; SELECT pg_sleep(5); --",
        "admin' AND 1=1 --",
    ]

    for payload in sqli_payloads:
        # Search query parameter
        resp = client.get(f"/api/v1/employees?q={payload}", headers=headers)
        assert resp.status_code == 200, f"Search failed with payload: {payload}"
        data = resp.json()
        assert "items" in data

        # Generic entity filter
        resp2 = client.get(f"/api/v1/contracts?status={payload}", headers=headers)
        assert resp2.status_code == 200, f"Filter failed with payload: {payload}"

        # Sorting injection attempt
        resp3 = client.get(f"/api/v1/employees?sort={payload}", headers=headers)
        assert resp3.status_code in (200, 400), f"Sort failed with payload: {payload}"


def test_sql_injection_in_path_parameters(client):
    """Path parameters (e.g. /{id}) must validate integer types and not execute injection strings."""
    headers = get_headers(client, "superadmin")
    malicious_paths = [
        "/api/v1/employees/1' OR '1'='1/profile",
        "/api/v1/hr-orders/1;DROP TABLE users;--/order.pdf",
        "/api/v1/applications/1' UNION SELECT 1--/offer-letter.pdf",
    ]
    for path in malicious_paths:
        resp = client.get(path, headers=headers)
        # Should return 422 Unprocessable Entity (type error) or 404, never 500 Internal Server Error
        assert resp.status_code in (404, 422), f"Expected 404/422 on {path}, got {resp.status_code}"


def test_security_headers_present(client):
    """Verify essential defensive HTTP security headers are set on responses."""
    resp = client.get("/api/v1/system/info")
    assert resp.status_code == 200
    headers = resp.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("referrer-policy") == "no-referrer"
    assert "default-src" in headers.get("content-security-policy", "")


# =========================================================================
# 2. ROLE-BASED ACCESS CONTROL (RBAC) BOUNDARY VERIFICATIONS
# =========================================================================

def test_employee_role_boundaries(client):
    """Regular employee must only access ESS and cannot access admin/payroll/other employees."""
    emp_headers = get_headers(client, "employee")

    # 1. Allowed ESS operations
    me_resp = client.get("/api/v1/ess/me", headers=emp_headers)
    assert me_resp.status_code == 200
    assert "employee" in me_resp.json()

    ref_resp = client.get("/api/v1/ess/reference.pdf", headers=emp_headers)
    assert ref_resp.status_code == 200
    assert ref_resp.headers["content-type"] == "application/pdf"

    payslips_resp = client.get("/api/v1/ess/payslips", headers=emp_headers)
    assert payslips_resp.status_code == 200

    # 2. Forbidden admin and payroll operations (403 Forbidden)
    forbidden_paths = [
        "/api/v1/payroll-runs",
        "/api/v1/auth/users",
        "/api/v1/audit-logs",
        "/api/v1/compliance/unified-declaration?year=2026&month=1",
        "/api/v1/compliance/military-report",
        "/api/v1/employees/1/reference.pdf",  # Cannot download other employee's reference
    ]
    for path in forbidden_paths:
        resp = client.get(path, headers=emp_headers)
        assert resp.status_code == 403, f"Employee should be forbidden from {path}, got {resp.status_code}"


def test_accountant_role_boundaries(client):
    """Accountant can view and run payroll, but cannot manage users or system audit."""
    acc_headers = get_headers(client, "accountant")

    # Allowed: Payroll and compliance reports
    pr_resp = client.get("/api/v1/payroll-runs", headers=acc_headers)
    assert pr_resp.status_code == 200

    comp_resp = client.get("/api/v1/compliance/unified-declaration?year=2026&month=1", headers=acc_headers)
    assert comp_resp.status_code == 200

    # Forbidden: Users and system config
    assert client.get("/api/v1/auth/users", headers=acc_headers).status_code == 403
    assert client.get("/api/v1/audit-logs", headers=acc_headers).status_code == 403


def test_dept_manager_role_boundaries(client):
    """Department manager can view timesheets, approve leaves, but cannot see payroll runs."""
    mgr_headers = get_headers(client, "dept_manager")

    # Allowed
    assert client.get("/api/v1/timesheets", headers=mgr_headers).status_code == 200
    assert client.get("/api/v1/leave-requests", headers=mgr_headers).status_code == 200
    assert client.get("/api/v1/mss/team", headers=mgr_headers).status_code == 200

    # Forbidden: Company payroll and system users
    assert client.get("/api/v1/payroll-runs", headers=mgr_headers).status_code == 403
    assert client.get("/api/v1/auth/users", headers=mgr_headers).status_code == 403
    assert client.get("/api/v1/audit-logs", headers=mgr_headers).status_code == 403


def test_hr_director_and_superadmin_operations(client):
    """HR Director and Superadmin can perform HR management, order PDFs, offer letters, reports."""
    hr_headers = get_headers(client, "hr_director")
    admin_headers = get_headers(client, "superadmin")

    for h in (hr_headers, admin_headers):
        # Employees and profile
        assert client.get("/api/v1/employees", headers=h).status_code == 200
        assert client.get("/api/v1/employees/1/profile", headers=h).status_code == 200
        assert client.get("/api/v1/employees/1/reference.pdf", headers=h).status_code == 200

        # HR Orders
        assert client.get("/api/v1/hr-orders", headers=h).status_code == 200
        assert client.get("/api/v1/hr-orders/1/order.pdf", headers=h).status_code == 200

        # Recruitment and Offer Letter
        assert client.get("/api/v1/vacancies", headers=h).status_code == 200
        assert client.get("/api/v1/applications/1/offer-letter.pdf", headers=h).status_code == 200

        # Business trip advance calculation
        trip_calc = client.post(
            "/api/v1/trips/calculate-advance",
            headers=h,
            json={
                "destination_city": "Bakı",
                "start_date": "2026-06-01",
                "end_date": "2026-06-05",
                "transport_cost": 50.0,
            },
        )
        assert trip_calc.status_code == 200
        assert trip_calc.json()["total_advance"] > 0

        # Military Accounting CSV report
        mil_rep = client.get("/api/v1/compliance/military-report", headers=h)
        assert mil_rep.status_code == 200
        assert "text/csv" in mil_rep.headers["content-type"]

    # Only superadmin can access system audit and users
    assert client.get("/api/v1/audit-logs", headers=admin_headers).status_code == 200
    assert client.get("/api/v1/auth/users", headers=admin_headers).status_code == 200
