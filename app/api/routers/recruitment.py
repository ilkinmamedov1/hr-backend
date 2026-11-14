from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.organization import Department, StaffingTable
from app.models.recruitment import (
    Application,
    Candidate,
    OffboardingClearance,
    OnboardingTask,
    Vacancy,
)
from app.models.user import User
from app.services.leave_service import ensure_balances_for_contract

router = APIRouter(tags=["M09 · İşə Qəbul (ATS)"])

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
RECRUIT_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER}

STAGES = {"NEW", "CALL", "INTERVIEW", "TASK", "OFFER", "HIRED", "REJECTED"}

DEFAULT_OFFBOARDING_TASKS = [
    ("İşdən çıxma ərizəsi", "HR"),
    ("Əmək müqaviləsinin xitamı", "HR"),
    ("Təhvil-təslim aktı", "ADMIN"),
    ("İT avadanlıqlarının qaytarılması", "IT"),
    ("Giriş kartının qaytarılması", "SECURITY"),
    ("Maddi sərvətlərin təhvili", "FINANCE"),
    ("Son əməkhaqqı hesablaması", "FINANCE"),
]


def _ensure_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and user.organization_id is not None
        and organization_id != user.organization_id
    ):
        raise HTTPException(status_code=404, detail="Qeyd tapılmadı")


@router.patch("/applications/{application_id}/stage")
def move_stage(
    application_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.DEPT_MANAGER)),
):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Müraciət tapılmadı")
    vacancy = db.get(Vacancy, application.vacancy_id)
    _ensure_org(user, vacancy.organization_id if vacancy else None)
    stage = payload.get("stage")
    if stage not in STAGES:
        raise HTTPException(status_code=400, detail=f"Yanlış mərhələ. Mümkün: {sorted(STAGES)}")
    application.stage = stage
    if payload.get("score") is not None:
        application.score = payload["score"]
    if payload.get("notes") is not None:
        application.notes = payload["notes"]
    db.commit()
    return serialize(application)


@router.post("/applications/{application_id}/hire", status_code=201)
def hire_candidate(
    application_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Müraciət tapılmadı")
    vacancy = db.get(Vacancy, application.vacancy_id)
    candidate = db.get(Candidate, application.candidate_id)
    if vacancy is None or candidate is None:
        raise HTTPException(status_code=400, detail="Vakansiya və ya namizəd tapılmadı")
    _ensure_org(user, vacancy.organization_id)
    staffing = db.get(StaffingTable, payload.get("staffing_id") or vacancy.staffing_id)
    if staffing is None or staffing.organization_id != vacancy.organization_id:
        raise HTTPException(status_code=400, detail="Ştat vahidi tələb olunur")

    def parse_optional_date(value):
        if value is None or isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

    org_id = vacancy.organization_id
    pin_code = payload.get("pin_code")
    if not pin_code:
        raise HTTPException(status_code=400, detail="pin_code (FİN) tələb olunur")
    existing = db.scalar(
        select(Employee).where(Employee.organization_id == org_id, Employee.pin_code == pin_code)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Bu FİN ilə işçi artıq mövcuddur")

    names = candidate.full_name.split(" ", 1)
    employee = Employee(
        organization_id=org_id,
        pin_code=pin_code,
        first_name=payload.get("first_name") or names[0],
        last_name=payload.get("last_name") or (names[1] if len(names) > 1 else ""),
        father_name=payload.get("father_name"),
        birth_date=parse_optional_date(payload.get("birth_date")),
        gender=payload.get("gender"),
        citizenship=payload.get("citizenship", "AZ"),
        phone=payload.get("phone") or candidate.phone,
        email=payload.get("email") or candidate.email,
        bank_name=payload.get("bank_name"),
        bank_iban=payload.get("bank_iban"),
        status="ACTIVE",
    )
    db.add(employee)
    db.flush()

    contract = EmploymentContract(
        organization_id=org_id,
        employee_id=employee.id,
        staffing_id=staffing.id,
        contract_number=payload.get("contract_number", f"EM-{employee.id:05d}"),
        contract_type=payload.get("contract_type", "INDEFINITE"),
        work_type=payload.get("work_type", "MAIN"),
        start_date=parse_optional_date(payload.get("start_date")) or date.today(),
        end_date=parse_optional_date(payload.get("end_date")),
        probation_end_date=parse_optional_date(payload.get("probation_end_date")),
        gross_salary=Decimal(str(payload.get("gross_salary", staffing.base_salary))),
        salary_type=payload.get("salary_type", "MONTHLY"),
        status="ACTIVE",
    )
    db.add(contract)
    db.flush()
    ensure_balances_for_contract(db, contract)

    application.stage = "HIRED"
    application.hired_employee_id = employee.id

    hired_count = db.scalar(
        select(func.count(Application.id)).where(
            Application.vacancy_id == vacancy.id, Application.stage == "HIRED"
        )
    ) or 0
    if hired_count >= vacancy.openings:
        vacancy.status = "CLOSED"
        vacancy.closed_at = date.today()

    standard_tasks = [
        ("Əmək müqaviləsinin imzalanması", "HR"),
        ("Şirkət emailinin yaradılması", "IT"),
        ("İş yeri və texnikanın hazırlanması", "IT"),
        ("Daxili təlimlərin təyin edilməsi", "TRAINING"),
        ("Mentorun təyin edilməsi", "HR"),
    ]
    for title, category in standard_tasks:
        db.add(
            OnboardingTask(
                employee_id=employee.id,
                title=title,
                category=category,
                due_date=contract.start_date,
                status="PENDING",
            )
        )

    db.commit()
    db.refresh(employee)
    db.refresh(contract)
    db.refresh(application)
    return {
        "employee": serialize(employee),
        "contract": serialize(contract),
        "application": serialize(application),
    }


@router.get("/onboarding/{employee_id}")
def onboarding_status(
    employee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*RECRUIT_READ)),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    _ensure_org(user, employee.organization_id)
    tasks = list(
        db.scalars(
            select(OnboardingTask)
            .where(OnboardingTask.employee_id == employee_id)
            .order_by(OnboardingTask.id)
        )
    )
    return [serialize(task) for task in tasks]


@router.post("/onboarding/{employee_id}/checklist", status_code=201)
def create_onboarding_checklist(
    employee_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    _ensure_org(user, employee.organization_id)
    tasks = payload.get("tasks") or [
        {"title": "Əmək müqaviləsinin imzalanması", "category": "HR"},
        {"title": "Şirkət emailinin yaradılması", "category": "IT"},
        {"title": "İş yeri və texnikanın hazırlanması", "category": "IT"},
        {"title": "Mentorun təyin edilməsi", "category": "HR"},
    ]
    created = []
    for task in tasks:
        row = OnboardingTask(
            employee_id=employee_id,
            title=task["title"],
            category=task.get("category", "HR"),
            assignee=task.get("assignee"),
            due_date=task.get("due_date"),
            status="PENDING",
        )
        db.add(row)
        created.append(row)
    db.commit()
    return [serialize(row) for row in created]


def _employee_department_name(db: Session, employee: Employee) -> str:
    contract = db.scalar(
        select(EmploymentContract).where(
            EmploymentContract.employee_id == employee.id,
            EmploymentContract.status == "ACTIVE",
        )
    )
    if contract is None:
        return "Ümumi"
    staffing = db.get(StaffingTable, contract.staffing_id)
    if staffing is None or staffing.department_id is None:
        return "Ümumi"
    department = db.get(Department, staffing.department_id)
    return department.name if department else "Ümumi"


@router.get("/offboarding/{employee_id}")
def offboarding_status(
    employee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*RECRUIT_READ)),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    _ensure_org(user, employee.organization_id)
    rows = list(
        db.scalars(
            select(OffboardingClearance)
            .where(OffboardingClearance.employee_id == employee_id)
            .order_by(OffboardingClearance.id)
        )
    )
    return [serialize(row) for row in rows]


@router.post("/offboarding/{employee_id}/checklist", status_code=201)
def create_offboarding_checklist(
    employee_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    _ensure_org(user, employee.organization_id)
    department_name = _employee_department_name(db, employee)
    tasks = payload.get("tasks") or [
        {"item": title, "department": department}
        for title, department in DEFAULT_OFFBOARDING_TASKS
    ]
    existing = set(
        db.scalars(
            select(OffboardingClearance.item).where(
                OffboardingClearance.employee_id == employee_id
            )
        )
    )
    created = []
    for task in tasks:
        item = str(task.get("item") or task.get("title") or "").strip()
        if not item or item in existing:
            continue
        row = OffboardingClearance(
            employee_id=employee_id,
            department=task.get("department") or department_name,
            item=item,
            status="PENDING",
            notes=task.get("notes"),
        )
        db.add(row)
        created.append(row)
        existing.add(item)
    db.commit()
    return [serialize(row) for row in created]


router.include_router(
    build_crud_router(
        model=Vacancy,
        prefix="/vacancies",
        tags=["M09 · Vakansiyalar"],
        allowed_fields={
            "organization_id", "staffing_id", "department_id", "title", "openings",
            "description", "requirements", "salary_min", "salary_max", "status",
            "created_by", "closed_at",
        },
        read_roles=RECRUIT_READ,
        write_roles=HR_WRITE,
        search_fields=("title", "description"),
        order_by="id",
    )
)
router.include_router(
    build_crud_router(
        model=Candidate,
        prefix="/candidates",
        tags=["M09 · Namizədlər"],
        allowed_fields={
            "full_name", "phone", "email", "cv_url", "skills_json",
            "experience_years", "current_position", "source", "notes",
        },
        read_roles=RECRUIT_READ,
        write_roles=HR_WRITE,
        search_fields=("full_name", "phone", "email", "current_position"),
        org_scoped=False,
    )
)
router.include_router(
    build_crud_router(
        model=Application,
        prefix="/applications",
        tags=["M09 · Müraciətlər / Kanban"],
        allowed_fields={
            "vacancy_id", "candidate_id", "stage", "score", "notes", "applied_at", "hired_employee_id",
        },
        read_roles=RECRUIT_READ,
        write_roles=HR_WRITE,
        org_relation=(Vacancy, "vacancy_id"),
    )
)
router.include_router(
    build_crud_router(
        model=OnboardingTask,
        prefix="/onboarding-tasks",
        tags=["M10 · Onboarding"],
        allowed_fields={
            "employee_id", "title", "category", "assignee", "due_date", "status", "notes",
        },
        read_roles=RECRUIT_READ,
        write_roles=HR_WRITE,
    )
)
router.include_router(
    build_crud_router(
        model=OffboardingClearance,
        prefix="/offboarding-clearances",
        tags=["M10 · Offboarding"],
        allowed_fields={"employee_id", "department", "item", "status", "notes"},
        read_roles=RECRUIT_READ,
        write_roles=HR_WRITE,
    )
)
