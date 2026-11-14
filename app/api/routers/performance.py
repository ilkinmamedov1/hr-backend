from fastapi import APIRouter

from app.api.crud import build_crud_router
from app.core.rbac import Role
from app.models.performance import KpiEvaluation

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER}
HR_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER, Role.ACCOUNTANT}

router = APIRouter(tags=["M11 · Performans və KPI / OKR"])

router.include_router(
    build_crud_router(
        model=KpiEvaluation,
        prefix="/kpi-evaluations",
        tags=["M11 · KPI Qiymətləndirmə"],
        allowed_fields={
            "employee_id", "period_code", "kpi_items_json", "final_score",
            "bonus_multiplier", "is_synced_to_payroll", "evaluated_by", "notes",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        order_by="id",
    )
)
