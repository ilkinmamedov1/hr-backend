from fastapi import APIRouter

from app.api.crud import build_crud_router
from app.core.rbac import Role
from app.models.training import EmployeeCertificate, Training, TrainingParticipant

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER, Role.ACCOUNTANT}

router = APIRouter(tags=["M12 · Təlim və Sertifikatlaşdırma"])

router.include_router(
    build_crud_router(
        model=Training,
        prefix="/trainings",
        tags=["M12 · Təlimlər"],
        allowed_fields={
            "organization_id", "title", "training_type", "provider", "start_date",
            "end_date", "budget", "cost", "status", "description",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
        search_fields=("title", "provider"),
    )
)
router.include_router(
    build_crud_router(
        model=TrainingParticipant,
        prefix="/training-participants",
        tags=["M12 · Təlim İştirakçıları"],
        allowed_fields={
            "training_id", "employee_id", "score", "certificate_number",
            "certificate_expiry", "status",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
    )
)
router.include_router(
    build_crud_router(
        model=EmployeeCertificate,
        prefix="/employee-certificates",
        tags=["M12 · Sertifikatlar"],
        allowed_fields={
            "employee_id", "name", "issuer", "number", "issue_date", "expiry_date", "file_path",
        },
        read_roles=READ,
        write_roles=HR_WRITE,
        order_by="expiry_date",
    )
)
