from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.rbac import ALL_ROLES, HR_ROLES, PAYROLL_ROLES, Role
from app.models.contract import EmploymentContract
from app.models.organization import Department, Organization, Position, StaffingTable
from app.models.user import User

router = APIRouter(tags=["M01 · Təşkilati Struktur və Ştat"])

ORG_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR}
HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
ORG_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER}


def _check_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and user.organization_id is not None
        and organization_id != user.organization_id
    ):
        raise HTTPException(status_code=404, detail="Təşkilat tapılmadı")


@router.get("/departments/tree")
def department_tree(
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ORG_READ)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)
    rows = list(
        db.scalars(select(Department).where(Department.organization_id == org_id).order_by(Department.name))
    )
    nodes = {row.id: {**serialize(row), "children": []} for row in rows}
    roots = []
    for row in rows:
        node = nodes[row.id]
        if row.parent_id and row.parent_id in nodes:
            nodes[row.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


@router.get("/staffing/vacancies")
def staffing_vacancies(
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ORG_READ)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)
    rows = db.execute(
        select(StaffingTable, Department.name, Position.title, func.count(EmploymentContract.id))
        .join(Department, Department.id == StaffingTable.department_id)
        .join(Position, Position.id == StaffingTable.position_id)
        .outerjoin(
            EmploymentContract,
            (EmploymentContract.staffing_id == StaffingTable.id)
            & (EmploymentContract.status == "ACTIVE"),
        )
        .where(StaffingTable.organization_id == org_id, StaffingTable.is_active.is_(True))
        .group_by(StaffingTable.id, Department.name, Position.title)
        .order_by(Department.name, Position.title)
    ).all()
    result = []
    for staffing, department_name, position_title, filled in rows:
        approved = Decimal(str(staffing.approved_headcount))
        result.append(
            {
                **serialize(staffing),
                "department_name": department_name,
                "position_title": position_title,
                "filled_headcount": filled,
                "vacant_headcount": float(approved - Decimal(filled)),
            }
        )
    return result


@router.get("/organizations/{org_id}/summary")
def organization_summary(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    organization = db.get(Organization, org_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Təşkilat tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Təşkilat tapılmadı")
    departments = db.scalar(select(func.count(Department.id)).where(Department.organization_id == org_id)) or 0
    positions = db.scalar(select(func.count(Position.id)).where(Position.organization_id == org_id)) or 0
    staffing = db.scalar(select(func.count(StaffingTable.id)).where(StaffingTable.organization_id == org_id)) or 0
    active_contracts = db.scalar(
        select(func.count(EmploymentContract.id)).where(
            EmploymentContract.organization_id == org_id, EmploymentContract.status == "ACTIVE"
        )
    ) or 0
    return {
        "organization": serialize(organization),
        "departments": departments,
        "positions": positions,
        "staffing_units": staffing,
        "active_contracts": active_contracts,
    }


router.include_router(
    build_crud_router(
        model=Organization,
        prefix="/organizations",
        tags=["M01 · Təşkilati Struktur"],
        allowed_fields={
            "name", "short_name", "voen", "sun_code", "legal_address", "actual_address",
            "bank_name", "bank_iban", "bank_swift", "director_id", "phone", "email",
            "sector_type", "settings_json", "is_active",
        },
        read_roles=ORG_READ,
        write_roles=ORG_WRITE,
        search_fields=("name", "voen"),
    )
)
router.include_router(
    build_crud_router(
        model=Department,
        prefix="/departments",
        tags=["M01 · Departamentlər"],
        allowed_fields={
            "organization_id", "parent_id", "code", "name", "cost_center_code",
            "head_employee_id", "path", "is_active",
        },
        read_roles=ALL_ROLES,
        write_roles=HR_WRITE,
        search_fields=("name", "code"),
    )
)
router.include_router(
    build_crud_router(
        model=Position,
        prefix="/positions",
        tags=["M01 · Vəzifələr"],
        allowed_fields={
            "organization_id", "title", "occupation_code", "grade_level",
            "min_salary", "max_salary", "annual_leave_days",
        },
        read_roles=ALL_ROLES,
        write_roles=HR_WRITE,
        search_fields=("title", "occupation_code"),
    )
)
router.include_router(
    build_crud_router(
        model=StaffingTable,
        prefix="/staffing",
        tags=["M01 · Ştat Cədvəli"],
        allowed_fields={
            "organization_id", "department_id", "position_id", "approved_headcount",
            "base_salary", "harmful_work_bonus_pct", "effective_from", "effective_to", "is_active",
        },
        read_roles=ORG_READ | PAYROLL_ROLES,
        write_roles=HR_WRITE,
    )
)
