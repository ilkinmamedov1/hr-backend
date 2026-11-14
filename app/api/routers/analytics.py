from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.organization import Department, StaffingTable
from app.models.user import User
from app.models.workflow import AuditLog
from app.services import analytics_service
from app.api.crud import serialize

router = APIRouter(tags=["M14 · Analitika"])

ANALYTICS_ROLES = {
    Role.SUPERADMIN,
    Role.HR_DIRECTOR,
    Role.HR_SPECIALIST,
    Role.ACCOUNTANT,
    Role.DEPT_MANAGER,
}


def _org(user: User, organization_id: int | None) -> int:
    if (
        organization_id is not None
        and user.role != Role.SUPERADMIN.value
        and user.organization_id != organization_id
    ):
        raise HTTPException(status_code=404, detail="Təşkilat tapılmadı")
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    return org_id


@router.get("/analytics/dashboard")
def dashboard(
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ANALYTICS_ROLES)),
):
    return analytics_service.dashboard(db, _org(user, organization_id))


@router.get("/analytics/payroll-trend")
def payroll_trend(
    months: int = Query(12, ge=1, le=36),
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ANALYTICS_ROLES)),
):
    return analytics_service.payroll_fund_trend(db, _org(user, organization_id), months)


@router.get("/analytics/department-payroll")
def department_payroll(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ANALYTICS_ROLES)),
):
    return analytics_service.department_payroll(db, _org(user, organization_id), year, month)


@router.get("/analytics/attendance")
def attendance(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ANALYTICS_ROLES)),
):
    return analytics_service.attendance_summary(db, _org(user, organization_id), year, month)


@router.get("/mss/team")
def my_team(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ANALYTICS_ROLES)),
):
    if user.employee_id is None:
        raise HTTPException(status_code=400, detail="İstifadəçi işçi ilə əlaqələndirilməyib")
    departments = list(
        db.scalars(select(Department).where(Department.head_employee_id == user.employee_id))
    )
    dept_ids = [department.id for department in departments]
    if not dept_ids:
        return []
    rows = list(
        db.scalars(
            select(Employee)
            .join(EmploymentContract, EmploymentContract.employee_id == Employee.id)
            .join(StaffingTable, EmploymentContract.staffing_id == StaffingTable.id)
            .where(
                StaffingTable.department_id.in_(dept_ids),
                EmploymentContract.status == "ACTIVE",
                Employee.deleted_at.is_(None),
            )
        )
    )
    return [
        {
            "employee_id": employee.id,
            "name": f"{employee.last_name} {employee.first_name}",
            "pin_code": employee.pin_code,
            "phone": employee.phone,
            "email": employee.email,
        }
        for employee in rows
    ]


@router.get("/audit-logs")
def audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    table_name: str | None = None,
    record_id: int | None = None,
    user_id: int | None = None,
    action: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.SUPERADMIN)),
):
    from sqlalchemy import select

    stmt = select(AuditLog)
    if table_name:
        stmt = stmt.where(AuditLog.table_name == table_name)
    if record_id:
        stmt = stmt.where(AuditLog.record_id == record_id)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    rows = list(db.scalars(stmt.order_by(AuditLog.id.desc()).offset(skip).limit(limit)))
    return [serialize(row) for row in rows]
