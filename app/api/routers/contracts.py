from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.contract import (
    ContractAmendment,
    EmploymentContract,
    HrOrder,
    ServiceContract,
)
from app.models.employee import Employee
from app.models.leave import LeaveBalance
from app.models.organization import StaffingTable
from app.models.user import User
from app.services.leave_service import (
    all_balances_for_employee,
    ensure_balances_for_contract,
    final_settlement_preview,
)
from app.services.payroll_calculator import D, q

router = APIRouter(tags=["M03 · Əmək Müqavilələri və Əmrlər"])

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
HR_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER}
PAYROLL_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.ACCOUNTANT}


def _ensure_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and user.organization_id is not None
        and organization_id != user.organization_id
    ):
        raise HTTPException(status_code=404, detail="Qeyd tapılmadı")


def _to_date(value) -> date | None:
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _validate_contract(data: dict, db: Session, user: User) -> dict:
    employee = db.get(Employee, data.get("employee_id"))
    if employee is None:
        raise HTTPException(status_code=400, detail="İşçi tapılmadı")
    staffing = db.get(StaffingTable, data.get("staffing_id"))
    if staffing is None:
        raise HTTPException(status_code=400, detail="Ştat vahidi tapılmadı")
    if employee.organization_id != staffing.organization_id:
        raise HTTPException(status_code=400, detail="İşçi və ştat vahidi eyni təşkilatda olmalıdır")
    _ensure_org(user, employee.organization_id)
    data["organization_id"] = employee.organization_id
    if staffing.harmful_work_bonus_pct and staffing.harmful_work_bonus_pct > 0:
        data.setdefault("notes", "Zərərli iş şəraiti əlavəsi tətbiq olunur")
    return data


def _init_balances(contract: EmploymentContract, db: Session, user: User | None = None) -> None:
    if contract.status == "ACTIVE":
        ensure_balances_for_contract(db, contract)


@router.get("/contracts/{contract_id}/leave-balances")
def contract_leave_balances(
    contract_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    contract = db.get(EmploymentContract, contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Müqavilə tapılmadı")
    _ensure_org(user, contract.organization_id)
    balances = list(
        db.scalars(
            select(LeaveBalance)
            .where(LeaveBalance.contract_id == contract_id)
            .order_by(LeaveBalance.work_year_start.desc())
        )
    )
    return [serialize(balance) for balance in balances]


@router.get("/contracts/{contract_id}/amendments")
def list_amendments(
    contract_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    contract = db.get(EmploymentContract, contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Müqavilə tapılmadı")
    _ensure_org(user, contract.organization_id)
    rows = list(
        db.scalars(
            select(ContractAmendment)
            .where(ContractAmendment.contract_id == contract_id)
            .order_by(ContractAmendment.effective_date.desc())
        )
    )
    return [serialize(row) for row in rows]


@router.post("/contracts/{contract_id}/amendments", status_code=201)
def create_amendment(
    contract_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    contract = db.get(EmploymentContract, contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Müqavilə tapılmadı")
    _ensure_org(user, contract.organization_id)

    amendment = ContractAmendment(
        contract_id=contract.id,
        amendment_no=payload.get("amendment_no", f"RA-{contract.id}-{date.today():%Y%m%d}"),
        effective_date=_to_date(payload.get("effective_date")) or date.today(),
        old_salary=contract.gross_salary,
        new_salary=Decimal(str(payload["new_salary"])) if payload.get("new_salary") is not None else None,
        old_staffing_id=contract.staffing_id,
        new_staffing_id=payload.get("new_staffing_id"),
        old_end_date=contract.end_date,
        new_end_date=_to_date(payload.get("new_end_date")),
        reason=payload.get("reason"),
        status="ACTIVE",
    )
    if payload.get("new_salary") is not None:
        contract.gross_salary = Decimal(str(payload["new_salary"]))
    if payload.get("new_staffing_id") is not None:
        staffing = db.get(StaffingTable, payload["new_staffing_id"])
        if staffing is None or staffing.organization_id != contract.organization_id:
            raise HTTPException(status_code=400, detail="Yeni ştat vahidi tapılmadı")
        contract.staffing_id = staffing.id
    if payload.get("new_end_date") is not None:
        contract.end_date = _to_date(payload["new_end_date"])
    db.add(amendment)
    db.commit()
    db.refresh(amendment)
    return serialize(amendment)


@router.post("/contracts/{contract_id}/terminate")
def terminate_contract(
    contract_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    contract = db.get(EmploymentContract, contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Müqavilə tapılmadı")
    _ensure_org(user, contract.organization_id)
    if contract.status == "TERMINATED":
        raise HTTPException(status_code=400, detail="Müqavilə artıq xitam edilib")

    termination_date = _to_date(payload.get("termination_date")) or date.today()
    reason = payload.get("reason")
    preview = final_settlement_preview(db, contract.employee_id, termination_date, reason)

    contract.status = "TERMINATED"
    contract.termination_date = termination_date
    contract.termination_article = payload.get("labor_code_article")

    order = HrOrder(
        organization_id=contract.organization_id,
        order_number=payload.get("order_number", f"XITAM-{contract.id}-{termination_date:%Y%m%d}"),
        order_type="TERMINATE",
        employee_id=contract.employee_id,
        labor_code_article=payload.get("labor_code_article"),
        order_date=date.today(),
        effective_date=termination_date,
        payload_json={
            "reason": reason,
            "contract_id": contract.id,
            "settlement": preview,
        },
        status="SIGNED",
        created_by=user.id,
    )
    db.add(order)
    employee = db.get(Employee, contract.employee_id)
    if employee:
        employee.status = "TERMINATED"
    db.commit()
    return {"contract_id": contract.id, "status": contract.status, "settlement": preview, "order_id": order.id}


@router.get("/service-contracts/{contract_id}/tax-preview")
def service_contract_tax_preview(
    contract_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*(PAYROLL_READ | {Role.HR_SPECIALIST}))),
):
    contract = db.get(ServiceContract, contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Xidməti müqavilə tapılmadı")
    _ensure_org(user, contract.organization_id)
    amount = D(contract.amount)
    withholding = q(amount * D(contract.withholding_tax_pct) / Decimal("100"))
    dsmf = q(amount * D(contract.dsmf_pct) / Decimal("100"))
    return {
        "contract_id": contract.id,
        "amount": float(amount),
        "withholding_tax": float(withholding),
        "dsmf": float(dsmf),
        "net_to_contractor": float(amount - withholding - dsmf),
    }


router.include_router(
    build_crud_router(
        model=EmploymentContract,
        prefix="/contracts",
        tags=["M03 · Əmək Müqavilələri"],
        allowed_fields={
            "employee_id", "staffing_id", "contract_number", "contract_type", "work_type",
            "start_date", "end_date", "probation_end_date", "gross_salary", "salary_type",
            "annual_leave_days", "signed_date", "termination_date", "termination_article",
            "status", "notes", "organization_id",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        search_fields=("contract_number",),
        before_create=_validate_contract,
        after_create=_init_balances,
    )
)
router.include_router(
    build_crud_router(
        model=HrOrder,
        prefix="/hr-orders",
        tags=["M03 · Kadr Əmrləri"],
        allowed_fields={
            "organization_id", "order_number", "order_type", "employee_id",
            "labor_code_article", "order_date", "effective_date", "payload_json",
            "status", "created_by",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        search_fields=("order_number",),
        order_by="order_date",
    )
)
router.include_router(
    build_crud_router(
        model=ServiceContract,
        prefix="/service-contracts",
        tags=["M03 · Xidməti Müqavilələr"],
        allowed_fields={
            "organization_id", "contractor_name", "contractor_voen", "contract_number",
            "start_date", "end_date", "amount", "service_description",
            "withholding_tax_pct", "dsmf_pct", "status", "payment_details",
        },
        read_roles=PAYROLL_READ | {Role.HR_SPECIALIST},
        write_roles=PAYROLL_READ | {Role.HR_SPECIALIST},
        search_fields=("contractor_name", "contract_number"),
    )
)
