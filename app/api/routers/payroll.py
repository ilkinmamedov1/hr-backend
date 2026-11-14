from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.employee import Employee
from app.models.payroll import (
    EmployeePayComponent,
    PayrollComponent,
    PayrollItem,
    PayrollItemDetail,
    PayrollRun,
    TaxSocialRateHistory,
)
from app.models.user import User
from app.services.export_service import (
    bank_register_csv,
    generate_payslip_pdf,
    gl_export_csv,
)
from app.services.payroll_service import (
    approve_payroll_run,
    calculate_payroll_run,
    get_rate_rules,
    pay_payroll_run,
)

router = APIRouter(tags=["M07 · Əməkhaqqı və Vergi (Payroll)"])

PAYROLL = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.ACCOUNTANT}
PAYROLL_READ = PAYROLL


def _get_run(db: Session, run_id: int, user: User) -> PayrollRun:
    run = db.get(PayrollRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Hesablama tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != run.organization_id:
        raise HTTPException(status_code=404, detail="Hesablama tapılmadı")
    return run


@router.get("/payroll-runs")
def list_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    year: int | None = None,
    month: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    stmt = select(PayrollRun)
    if user.role != Role.SUPERADMIN.value:
        if not user.organization_id:
            return []
        stmt = stmt.where(PayrollRun.organization_id == user.organization_id)
    if year:
        stmt = stmt.where(PayrollRun.period_year == year)
    if month:
        stmt = stmt.where(PayrollRun.period_month == month)
    if status:
        stmt = stmt.where(PayrollRun.status == status)
    stmt = stmt.order_by(PayrollRun.period_year.desc(), PayrollRun.period_month.desc())
    rows = list(db.scalars(stmt.offset(skip).limit(limit)))
    return [serialize(row) for row in rows]


@router.post("/payroll-runs", status_code=201)
def create_run(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    org_id = payload.get("organization_id") or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    if user.role != Role.SUPERADMIN.value:
        if not user.organization_id or org_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Təşkilat tapılmadı")
        org_id = user.organization_id
    year = payload.get("period_year")
    month = payload.get("period_month")
    run_type = payload.get("run_type", "REGULAR")
    if not year or not month:
        raise HTTPException(status_code=400, detail="period_year və period_month tələb olunur")

    existing = db.scalar(
        select(PayrollRun).where(
            PayrollRun.organization_id == org_id,
            PayrollRun.period_year == year,
            PayrollRun.period_month == month,
            PayrollRun.run_type == run_type,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Bu dövr üçün hesablama artıq mövcuddur")

    run = PayrollRun(
        organization_id=org_id,
        period_year=year,
        period_month=month,
        run_type=run_type,
        status="DRAFT",
        notes=payload.get("notes"),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return serialize(run)


@router.get("/payroll-runs/{run_id}")
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    return serialize(_get_run(db, run_id, user))


@router.post("/payroll-runs/{run_id}/calculate")
def calculate_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    run = _get_run(db, run_id, user)
    try:
        calculate_payroll_run(db, run, user.id)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize(run)


@router.post("/payroll-runs/{run_id}/approve")
def approve_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    run = _get_run(db, run_id, user)
    try:
        approve_payroll_run(db, run, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize(run)


@router.post("/payroll-runs/{run_id}/pay")
def pay_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    run = _get_run(db, run_id, user)
    try:
        pay_payroll_run(db, run)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize(run)


@router.delete("/payroll-runs/{run_id}", status_code=204)
def delete_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    run = _get_run(db, run_id, user)
    if run.status in ("APPROVED", "PAID"):
        raise HTTPException(status_code=400, detail="Təsdiqlənmiş/ödənilmiş hesablama silinə bilməz")
    db.execute(delete(PayrollItem).where(PayrollItem.payroll_run_id == run.id))
    db.delete(run)
    db.commit()
    return None


@router.get("/payroll-runs/{run_id}/items")
def run_items(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    _get_run(db, run_id, user)
    rows = db.execute(
        select(PayrollItem, Employee)
        .join(Employee, Employee.id == PayrollItem.employee_id)
        .where(PayrollItem.payroll_run_id == run_id)
        .order_by(Employee.last_name, Employee.first_name)
    ).all()
    return [
        {
            **serialize(item),
            "employee_name": f"{employee.last_name} {employee.first_name} {employee.father_name or ''}".strip(),
            "pin_code": employee.pin_code,
            "bank_iban": employee.bank_iban,
        }
        for item, employee in rows
    ]


@router.get("/payroll-runs/{run_id}/bank-register.csv")
def bank_register(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    _get_run(db, run_id, user)
    try:
        content = bank_register_csv(db, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="bank-register-{run_id}.csv"'},
    )


@router.get("/payroll-runs/{run_id}/gl-export.csv")
def gl_export(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    _get_run(db, run_id, user)
    try:
        content = gl_export_csv(db, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="gl-export-{run_id}.csv"'},
    )


@router.get("/payroll-items/{item_id}")
def get_payroll_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    item = db.get(PayrollItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Sətir tapılmadı")
    run = db.get(PayrollRun, item.payroll_run_id)
    if user.role != Role.SUPERADMIN.value and user.organization_id != run.organization_id:
        raise HTTPException(status_code=404, detail="Sətir tapılmadı")
    employee = db.get(Employee, item.employee_id)
    details = list(
        db.scalars(
            select(PayrollItemDetail)
            .where(PayrollItemDetail.payroll_item_id == item.id)
            .order_by(PayrollItemDetail.id)
        )
    )
    return {
        **serialize(item),
        "employee_name": f"{employee.last_name} {employee.first_name}",
        "pin_code": employee.pin_code,
        "details": [serialize(detail) for detail in details],
    }


@router.get("/payroll-items/{item_id}/payslip.pdf")
def payslip_pdf(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ, Role.EMPLOYEE)),
):
    item = db.get(PayrollItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Sətir tapılmadı")
    if user.role == Role.EMPLOYEE.value:
        if item.employee_id != user.employee_id:
            raise HTTPException(status_code=403, detail="Bu sənədə giriş icazəniz yoxdur")
    else:
        _get_run(db, item.payroll_run_id, user)
    try:
        pdf = generate_payslip_pdf(db, item_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="payslip-{item_id}.pdf"'},
    )


@router.get("/tax-social-rates/current")
def current_rates(
    sector_type: str = Query(...),
    on_date: date | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL_READ)),
):
    try:
        return get_rate_rules(db, sector_type, on_date or date.today())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


router.include_router(
    build_crud_router(
        model=PayrollComponent,
        prefix="/payroll-components",
        tags=["M07 · Əməkhaqqı Komponentləri"],
        allowed_fields={
            "code", "name", "component_type", "is_taxable", "is_dsmf_base",
            "is_its_base", "is_unemployment_base", "include_in_vacation_avg",
            "include_in_sick_avg", "sort_order",
        },
        read_roles=PAYROLL_READ,
        write_roles=PAYROLL_READ,
        search_fields=("code", "name"),
        org_scoped=False,
    )
)
router.include_router(
    build_crud_router(
        model=EmployeePayComponent,
        prefix="/employee-pay-components",
        tags=["M07 · Fərdi Əlavə/Tutulmalar"],
        allowed_fields={
            "employee_id", "component_id", "amount", "percent", "valid_from", "valid_to", "notes",
        },
        read_roles=PAYROLL_READ | {Role.HR_SPECIALIST},
        write_roles=PAYROLL_READ | {Role.HR_SPECIALIST},
    )
)
router.include_router(
    build_crud_router(
        model=TaxSocialRateHistory,
        prefix="/tax-social-rates",
        tags=["M07 · Vergi və Sosial Dərəcələr"],
        allowed_fields={"sector_type", "effective_from", "effective_to", "rules_json", "note"},
        read_roles=PAYROLL_READ,
        write_roles={Role.SUPERADMIN, Role.HR_DIRECTOR},
        org_scoped=False,
    )
)
