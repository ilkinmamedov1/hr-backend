from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, ensure_org_access, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.employee import Employee
from app.models.trip import BusinessTrip, TripExpenseReport
from app.models.user import User
from app.services.workflow_service import close_all_steps, create_step

router = APIRouter(tags=["M08 · Ezamiyyətlər və Xərclər"])

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
TRIP_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER}


def _check_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and user.organization_id is not None
        and organization_id != user.organization_id
    ):
        raise HTTPException(status_code=404, detail="Qeyd tapılmadı")


from app.services.export_service import calculate_trip_advance_norms


def _validate_trip(data: dict, db: Session, user: User) -> dict:
    employee = db.get(Employee, data.get("employee_id"))
    if employee is None:
        raise HTTPException(status_code=400, detail="İşçi tapılmadı")
    _check_org(user, employee.organization_id)
    data["organization_id"] = employee.organization_id

    if "start_date" in data and "end_date" in data:
        try:
            start = date.fromisoformat(str(data["start_date"]))
            end = date.fromisoformat(str(data["end_date"]))
            days = max((end - start).days + 1, 1)
            norms = calculate_trip_advance_norms(
                data.get("destination_city", ""),
                bool(data.get("is_foreign", False)),
                days,
            )
            if not data.get("daily_allowance"):
                data["daily_allowance"] = norms["daily_allowance"]
            if not data.get("hotel_limit"):
                data["hotel_limit"] = norms["hotel_limit"]
            if not data.get("total_advance"):
                data["total_advance"] = norms["total_advance"]
        except Exception:
            pass
    return data


@router.post("/trips/calculate-advance")
def calculate_advance_endpoint(
    payload: dict = Body(...),
    user: User = Depends(require_roles(*TRIP_READ)),
):
    try:
        start_date = date.fromisoformat(str(payload["start_date"]))
        end_date = date.fromisoformat(str(payload["end_date"]))
        days = max((end_date - start_date).days + 1, 1)
    except Exception:
        raise HTTPException(status_code=400, detail="Tarix formatı düzgün deyil (YYYY-MM-DD)")
    norms = calculate_trip_advance_norms(
        payload.get("destination_city", ""),
        bool(payload.get("is_foreign", False)),
        days,
    )
    return {
        "days": days,
        "daily_allowance": float(norms["daily_allowance"]),
        "hotel_limit": float(norms["hotel_limit"]),
        "total_advance": float(norms["total_advance"]),
    }


def _validate_trip_update(row: BusinessTrip, data: dict, db: Session, user: User) -> dict:
    if "employee_id" in data and data["employee_id"] != row.employee_id:
        return _validate_trip(data, db, user)
    return data


def _trip_workflow(trip: BusinessTrip, db: Session, user: User) -> None:
    create_step(
        db,
        entity_type="BUSINESS_TRIP",
        entity_id=trip.id,
        organization_id=trip.organization_id,
        employee_id=trip.employee_id,
    )


def _prepare_expense(data: dict, db: Session, user: User) -> dict:
    trip = db.get(BusinessTrip, data.get("trip_id"))
    if trip is None:
        raise HTTPException(status_code=400, detail="Ezamiyyət tapılmadı")
    _check_org(user, trip.organization_id)
    total = Decimal(str(data.get("total_amount", 0)))
    advance = Decimal(str(trip.total_advance))
    data["advance_amount"] = advance
    data["balance"] = total - advance
    trip.actual_expenses = total
    return data


@router.post("/trips/{trip_id}/approve")
def approve_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*TRIP_READ)),
):
    trip = db.get(BusinessTrip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Ezamiyyət tapılmadı")
    ensure_org_access(BusinessTrip, trip, user)
    trip.status = "APPROVED"
    close_all_steps(db, "BUSINESS_TRIP", trip.id, "APPROVED")
    db.commit()
    return serialize(trip)


@router.post("/trips/{trip_id}/complete")
def complete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.ACCOUNTANT)),
):
    trip = db.get(BusinessTrip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Ezamiyyət tapılmadı")
    ensure_org_access(BusinessTrip, trip, user)
    trip.status = "COMPLETED"
    db.commit()
    return serialize(trip)


router.include_router(
    build_crud_router(
        model=BusinessTrip,
        prefix="/trips",
        tags=["M08 · Ezamiyyətlər"],
        allowed_fields={
            "organization_id", "employee_id", "destination_city", "is_foreign",
            "start_date", "end_date", "purpose", "daily_allowance", "hotel_limit",
            "total_advance", "actual_expenses", "order_id", "status", "notes",
        },
        read_roles=TRIP_READ,
        write_roles=HR_WRITE | {Role.ACCOUNTANT},
        search_fields=("destination_city",),
        order_by="start_date",
        before_create=_validate_trip,
        before_update=_validate_trip_update,
        after_create=_trip_workflow,
    )
)
router.include_router(
    build_crud_router(
        model=TripExpenseReport,
        prefix="/trip-expense-reports",
        tags=["M08 · Avans Hesabatları"],
        allowed_fields={
            "trip_id", "submitted_at", "total_amount", "advance_amount",
            "balance", "items_json", "status", "notes",
        },
        read_roles=TRIP_READ,
        write_roles=HR_WRITE | {Role.ACCOUNTANT},
        before_create=_prepare_expense,
        org_relation=(BusinessTrip, "trip_id"),
    )
)
