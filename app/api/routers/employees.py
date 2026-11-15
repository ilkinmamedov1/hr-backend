from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.contract import EmploymentContract
from app.models.employee import (
    Employee,
    EmployeeDocument,
    EmployeeEducation,
    EmployeeFamilyMember,
    EmployeeMilitary,
    EmployeeMigration,
    EmployeeTaxExemption,
)
from app.models.leave import LeaveBalance
from app.models.organization import Department, Position, StaffingTable
from app.models.user import User
from app.services.export_service import generate_employment_reference_pdf
from app.services.leave_service import final_settlement_preview

router = APIRouter(tags=["M02 · İşçilərin Şəxsi İşləri"])

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
HR_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER}


@router.get("/employees/expiring-documents")
def expiring_documents(
    days: int = Query(60, ge=1, le=365),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    until = date.today() + timedelta(days=days)
    stmt = (
        select(EmployeeDocument, Employee)
        .join(Employee, Employee.id == EmployeeDocument.employee_id)
        .where(
            EmployeeDocument.expiry_date.isnot(None),
            EmployeeDocument.expiry_date <= until,
        )
        .order_by(EmployeeDocument.expiry_date)
    )
    if user.role != Role.SUPERADMIN.value and user.organization_id:
        stmt = stmt.where(Employee.organization_id == user.organization_id)
    rows = db.execute(stmt).all()
    return [
        {
            **serialize(document),
            "employee_name": f"{employee.last_name} {employee.first_name}",
            "pin_code": employee.pin_code,
        }
        for document, employee in rows
    ]


@router.get("/employees/expiring-permits")
def expiring_permits(
    days: int = Query(60, ge=1, le=365),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    until = date.today() + timedelta(days=days)
    stmt = (
        select(EmployeeMigration, Employee)
        .join(Employee, Employee.id == EmployeeMigration.employee_id)
        .where(
            EmployeeMigration.expiry_date.isnot(None),
            EmployeeMigration.expiry_date <= until,
        )
        .order_by(EmployeeMigration.expiry_date)
    )
    if user.role != Role.SUPERADMIN.value and user.organization_id:
        stmt = stmt.where(Employee.organization_id == user.organization_id)
    rows = db.execute(stmt).all()
    return [
        {
            **serialize(migration),
            "employee_name": f"{employee.last_name} {employee.first_name}",
            "pin_code": employee.pin_code,
        }
        for migration, employee in rows
    ]


@router.get("/employees/{employee_id}/profile")
def employee_profile(
    employee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != employee.organization_id:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")

    contract = db.scalar(
        select(EmploymentContract)
        .where(EmploymentContract.employee_id == employee_id)
        .order_by(EmploymentContract.id.desc())
    )
    contract_info = None
    if contract:
        staffing = db.get(StaffingTable, contract.staffing_id)
        department = db.get(Department, staffing.department_id) if staffing else None
        position = db.get(Position, staffing.position_id) if staffing else None
        contract_info = {
            **serialize(contract),
            "department": department.name if department else None,
            "position": position.title if position else None,
        }

    balances = list(
        db.scalars(
            select(LeaveBalance)
            .where(LeaveBalance.employee_id == employee_id)
            .order_by(LeaveBalance.work_year_start.desc())
        )
    )
    documents = list(
        db.scalars(
            select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)
        )
    )
    family = list(
        db.scalars(
            select(EmployeeFamilyMember).where(EmployeeFamilyMember.employee_id == employee_id)
        )
    )
    return {
        "employee": serialize(employee),
        "contract": contract_info,
        "leave_balances": [serialize(balance) for balance in balances],
        "documents": [serialize(document) for document in documents],
        "family_members": [serialize(member) for member in family],
    }


@router.get("/employees/{employee_id}/final-settlement-preview")
def get_final_settlement_preview(
    employee_id: int,
    termination_date: date,
    reason: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*(HR_WRITE | {Role.ACCOUNTANT}))),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != employee.organization_id:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    try:
        return final_settlement_preview(db, employee_id, termination_date, reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/employees/{employee_id}/reference.pdf")
def employee_reference_pdf(
    employee_id: int,
    purpose: str = Query("Tələb olunan yerə"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != employee.organization_id:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    pdf = generate_employment_reference_pdf(db, employee_id, purpose=purpose)
    safe_pin = "".join(c for c in str(employee.pin_code or employee.id) if c.isascii() and (c.isalnum() or c in ("-", "_")))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="arayis-{safe_pin or employee.id}.pdf"'},
    )


router.include_router(
    build_crud_router(
        model=Employee,
        prefix="/employees",
        tags=["M02 · İşçilər"],
        allowed_fields={
            "organization_id", "pin_code", "first_name", "last_name", "father_name",
            "birth_date", "gender", "citizenship", "marital_status", "ssn",
            "individual_voen", "id_card_number", "id_card_issue_date", "id_card_expiry_date",
            "phone", "email", "address", "bank_name", "bank_iban", "photo_path",
            "total_insurance_tenure_years", "status", "notes", "deleted_at",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        search_fields=("first_name", "last_name", "father_name", "pin_code", "ssn", "phone", "email"),
        order_by="last_name",
        soft_delete=True,
    )
)

for child_model, prefix, label in (
    (EmployeeDocument, "/employee-documents", "Sənədlər"),
    (EmployeeTaxExemption, "/employee-tax-exemptions", "Vergi Güzəştləri"),
    (EmployeeFamilyMember, "/employee-family-members", "Ailə Üzvləri"),
    (EmployeeEducation, "/employee-education", "Təhsil və Staj"),
    (EmployeeMilitary, "/employee-military", "Hərbi Uçot"),
    (EmployeeMigration, "/employee-migrations", "Miqrasiya"),
):
    fields = {column.name for column in child_model.__table__.columns} - {
        "id", "created_at", "updated_at"
    }
    router.include_router(
        build_crud_router(
            model=child_model,
            prefix=prefix,
            tags=[f"M02 · {label}"],
            allowed_fields=fields,
            read_roles=HR_READ,
            write_roles=HR_WRITE,
        )
    )
