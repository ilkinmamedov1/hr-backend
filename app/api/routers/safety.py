from fastapi import APIRouter

from app.api.crud import build_crud_router
from app.core.rbac import Role
from app.models.safety import MedicalExam, PpeIssuance, SafetyBriefing, SafetyIncident

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER}

router = APIRouter(tags=["M13 · SƏTƏM və Əməyin Mühafizəsi"])

router.include_router(
    build_crud_router(
        model=SafetyBriefing,
        prefix="/safety-briefings",
        tags=["M13 · Təlimat Jurnalları"],
        allowed_fields={
            "employee_id", "briefing_type", "briefing_date", "instructor", "topic",
            "signature_ref", "notes",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
        order_by="briefing_date",
    )
)
router.include_router(
    build_crud_router(
        model=MedicalExam,
        prefix="/medical-exams",
        tags=["M13 · Tibbi Müayinə"],
        allowed_fields={
            "employee_id", "exam_date", "next_exam_date", "clinic", "result", "notes",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
        order_by="exam_date",
    )
)
router.include_router(
    build_crud_router(
        model=PpeIssuance,
        prefix="/ppe-issuances",
        tags=["M13 · FMV Uçotu"],
        allowed_fields={
            "employee_id", "item_name", "size", "quantity", "issued_date",
            "useful_life_months", "return_date", "notes",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
        order_by="issued_date",
    )
)
router.include_router(
    build_crud_router(
        model=SafetyIncident,
        prefix="/safety-incidents",
        tags=["M13 · Bədbəxt Hadisələr"],
        allowed_fields={
            "organization_id", "employee_id", "incident_date", "incident_type",
            "description", "severity", "lost_days", "investigation_status",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
        order_by="incident_date",
    )
)
