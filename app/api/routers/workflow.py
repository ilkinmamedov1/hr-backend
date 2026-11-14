from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.leave import LeaveRequest
from app.models.trip import BusinessTrip
from app.models.user import User
from app.models.workflow import ApprovalWorkflow
from app.services.workflow_service import decide

router = APIRouter(tags=["M14 · Təsdiq Zənciri"])

APPROVAL_ROLES = {
    Role.SUPERADMIN,
    Role.HR_DIRECTOR,
    Role.HR_SPECIALIST,
    Role.DEPT_MANAGER,
}


def _entity_org(db: Session, entity_type: str, entity_id: int) -> int | None:
    if entity_type == "LEAVE_REQUEST":
        row = db.get(LeaveRequest, entity_id)
    elif entity_type == "BUSINESS_TRIP":
        row = db.get(BusinessTrip, entity_id)
    else:
        return None
    return row.organization_id if row else None


def _can_access(user: User, organization_id: int | None) -> bool:
    return (
        user.role == Role.SUPERADMIN.value
        or (organization_id is not None and organization_id == user.organization_id)
    )


@router.get("/approvals/pending")
def pending_approvals(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*APPROVAL_ROLES)),
):
    stmt = select(ApprovalWorkflow).where(ApprovalWorkflow.decision == "PENDING")
    if user.role not in (Role.SUPERADMIN.value, Role.HR_DIRECTOR.value):
        stmt = stmt.where(ApprovalWorkflow.approver_id == user.id)
    rows = list(db.scalars(stmt.order_by(ApprovalWorkflow.id)))
    if user.role != Role.SUPERADMIN.value:
        rows = [
            row for row in rows
            if _can_access(user, _entity_org(db, row.entity_type, row.entity_id))
        ]
    return [serialize(row) for row in rows]


@router.get("/approvals")
def list_approvals(
    entity_type: str | None = None,
    entity_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*APPROVAL_ROLES)),
):
    stmt = select(ApprovalWorkflow)
    if entity_type:
        stmt = stmt.where(ApprovalWorkflow.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(ApprovalWorkflow.entity_id == entity_id)
    rows = list(db.scalars(stmt.order_by(ApprovalWorkflow.id)))
    if user.role != Role.SUPERADMIN.value:
        rows = [
            row for row in rows
            if _can_access(user, _entity_org(db, row.entity_type, row.entity_id))
        ]
    return [serialize(row) for row in rows]


@router.post("/approvals/{approval_id}/decide")
def decide_approval(
    approval_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*APPROVAL_ROLES)),
):
    step = db.get(ApprovalWorkflow, approval_id)
    if step is None:
        raise HTTPException(status_code=404, detail="Təsdiq addımı tapılmadı")
    if not _can_access(user, _entity_org(db, step.entity_type, step.entity_id)):
        raise HTTPException(status_code=404, detail="Təsdiq addımı tapılmadı")
    try:
        decide(
            db,
            step,
            user,
            decision=payload.get("decision"),
            comment=payload.get("comment"),
        )
        db.commit()
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(step)
    return serialize(step)


router.include_router(
    build_crud_router(
        model=ApprovalWorkflow,
        prefix="/approval-workflows",
        tags=["M14 · Təsdiq Zənciri"],
        allowed_fields={
            "entity_type", "entity_id", "step_order", "approver_id",
            "decision", "comment", "decided_at",
        },
        read_roles={Role.SUPERADMIN},
        write_roles={Role.SUPERADMIN},
        order_by="id",
        org_scoped=False,
    )
)
