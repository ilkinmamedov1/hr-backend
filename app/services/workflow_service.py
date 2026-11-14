from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import Role
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.organization import Department, StaffingTable
from app.models.trip import BusinessTrip
from app.models.user import User
from app.models.workflow import ApprovalWorkflow
from app.services.leave_service import approve_leave_request, release_leave_request


def pick_approver(db: Session, organization_id: int, employee_id: int | None) -> User | None:
    if employee_id:
        contract = db.scalar(
            select(EmploymentContract).where(
                EmploymentContract.employee_id == employee_id,
                EmploymentContract.status == "ACTIVE",
            )
        )
        if contract:
            staffing = db.get(StaffingTable, contract.staffing_id)
            if staffing:
                department = db.get(Department, staffing.department_id)
                if department and department.head_employee_id:
                    head_user = db.scalar(
                        select(User).where(
                            User.employee_id == department.head_employee_id, User.is_active.is_(True)
                        )
                    )
                    if head_user:
                        return head_user

    for role in (Role.HR_DIRECTOR.value, Role.HR_SPECIALIST.value, Role.SUPERADMIN.value):
        user = db.scalar(
            select(User).where(
                User.organization_id == organization_id,
                User.role == role,
                User.is_active.is_(True),
            )
        )
        if user:
            return user
    return None


def create_step(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    organization_id: int,
    employee_id: int | None,
    comment: str | None = None,
) -> ApprovalWorkflow | None:
    existing = db.scalar(
        select(ApprovalWorkflow).where(
            ApprovalWorkflow.entity_type == entity_type,
            ApprovalWorkflow.entity_id == entity_id,
        )
    )
    if existing:
        return existing
    approver = pick_approver(db, organization_id, employee_id)
    if approver is None:
        return None
    step = ApprovalWorkflow(
        entity_type=entity_type,
        entity_id=entity_id,
        step_order=1,
        approver_id=approver.id,
        decision="PENDING",
        comment=comment,
    )
    db.add(step)
    db.flush()
    return step


def apply_entity_decision(db: Session, entity_type: str, entity_id: int, decision: str) -> None:
    if entity_type == "LEAVE_REQUEST":
        request = db.get(LeaveRequest, entity_id)
        if request is None:
            return
        contract = db.scalar(
            select(EmploymentContract).where(
                EmploymentContract.employee_id == request.employee_id,
                EmploymentContract.status == "ACTIVE",
            )
        )
        if decision == "APPROVED":
            if request.status != "APPROVED":
                approve_leave_request(db, request, None)
        elif decision == "REJECTED":
            release_leave_request(db, request, "REJECTED")
    elif entity_type == "BUSINESS_TRIP":
        trip = db.get(BusinessTrip, entity_id)
        if trip:
            trip.status = decision

    db.flush()


def decide(
    db: Session,
    step: ApprovalWorkflow,
    user: User,
    decision: str,
    comment: str | None = None,
) -> ApprovalWorkflow:
    if decision not in ("APPROVED", "REJECTED"):
        raise ValueError("Qərar APPROVED və ya REJECTED olmalıdır")
    if step.approver_id != user.id and user.role not in (
        Role.SUPERADMIN.value,
        Role.HR_DIRECTOR.value,
    ):
        raise PermissionError("Bu addım üzrə qərar vermək səlahiyyətiniz yoxdur")
    if step.decision != "PENDING":
        raise ValueError("Bu addım üzrə artıq qərar verilib")

    step.decision = decision
    step.comment = comment
    step.decided_at = datetime.now(timezone.utc)

    entity_type, entity_id = step.entity_type, step.entity_id
    if decision == "REJECTED":
        apply_entity_decision(db, entity_type, entity_id, "REJECTED")
        return step

    pending = db.scalar(
        select(ApprovalWorkflow).where(
            ApprovalWorkflow.entity_type == entity_type,
            ApprovalWorkflow.entity_id == entity_id,
            ApprovalWorkflow.decision == "PENDING",
            ApprovalWorkflow.id != step.id,
        )
    )
    if pending is None:
        apply_entity_decision(db, entity_type, entity_id, "APPROVED")
    return step


def close_all_steps(db: Session, entity_type: str, entity_id: int, decision: str) -> None:
    steps = list(
        db.scalars(
            select(ApprovalWorkflow).where(
                ApprovalWorkflow.entity_type == entity_type,
                ApprovalWorkflow.entity_id == entity_id,
                ApprovalWorkflow.decision == "PENDING",
            )
        )
    )
    for step in steps:
        step.decision = decision
        step.decided_at = datetime.now(timezone.utc)
