from fastapi import APIRouter, Depends

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, Text, Time

from app.api.crud import ENTITY_ACL
from app.api.deps import get_current_user
from app.core.rbac import Role
from app.models.compliance import EmasSyncLog, GovernmentReport
from app.models.contract import EmploymentContract, HrOrder, ServiceContract
from app.models.employee import (
    Employee,
    EmployeeDocument,
    EmployeeEducation,
    EmployeeFamilyMember,
    EmployeeMigration,
    EmployeeMilitary,
    EmployeeTaxExemption,
)
from app.models.leave import (
    LeaveBalance,
    LeaveRequest,
    LeaveType,
    ShortLeaveRequest,
    SickLeave,
)
from app.models.organization import Department, Organization, Position, StaffingTable
from app.models.payroll import (
    EmployeePayComponent,
    PayrollComponent,
    PayrollRun,
    TaxSocialRateHistory,
)
from app.models.performance import KpiEvaluation
from app.models.recruitment import (
    Application,
    Candidate,
    OffboardingClearance,
    OnboardingTask,
    Vacancy,
)
from app.models.safety import MedicalExam, PpeIssuance, SafetyBriefing, SafetyIncident
from app.models.time import (
    AttendanceLog,
    EmployeeSchedule,
    ProductionCalendar,
    Timesheet,
    WorkSchedule,
)
from app.models.training import EmployeeCertificate, Training, TrainingParticipant
from app.models.trip import BusinessTrip, TripExpenseReport
from app.models.user import User

router = APIRouter(prefix="/meta", tags=["UI Metadata"])

MODULES = [
    {"code": "OVERVIEW", "title": "İcmal"},
    {"code": "M01", "title": "Təşkilat və Ştat"},
    {"code": "M02", "title": "İşçilər"},
    {"code": "M03", "title": "Müqavilələr və Əmrlər"},
    {"code": "M04", "title": "Uyğunluq və Dövlət"},
    {"code": "M05", "title": "İş Vaxtı"},
    {"code": "M06", "title": "Məzuniyyət və İcazə"},
    {"code": "M07", "title": "Əməkhaqqı"},
    {"code": "M08", "title": "Ezamiyyətlər"},
    {"code": "M09", "title": "İşə Qəbul"},
    {"code": "M10", "title": "Onboarding / Offboarding"},
    {"code": "M11", "title": "Performans"},
    {"code": "M12", "title": "Təlim və Sertifikat"},
    {"code": "M13", "title": "SƏTƏM"},
    {"code": "M14", "title": "Sistem və Təhlükəsizlik"},
]

ENTITY_DEFS = [
    {
        "key": "organizations",
        "model": Organization,
        "module": "M01",
        "label": "Təşkilatlar",
        "icon": "building",
        "list_fields": ["id", "name", "voen", "sector_type", "phone", "email", "is_active"],
    },
    {
        "key": "departments",
        "model": Department,
        "module": "M01",
        "label": "Departamentlər",
        "icon": "tree",
        "list_fields": ["id", "code", "name", "parent_id", "head_employee_id", "is_active"],
    },
    {
        "key": "positions",
        "model": Position,
        "module": "M01",
        "label": "Vəzifələr",
        "icon": "briefcase",
        "list_fields": ["id", "title", "grade_level", "min_salary", "max_salary", "annual_leave_days"],
    },
    {
        "key": "staffing",
        "model": StaffingTable,
        "module": "M01",
        "label": "Ştat cədvəli",
        "icon": "grid",
        "list_fields": [
            "id", "department_id", "position_id", "approved_headcount",
            "base_salary", "effective_from", "is_active",
        ],
    },
    {
        "key": "employees",
        "model": Employee,
        "module": "M02",
        "label": "İşçilər",
        "icon": "users",
        "list_fields": ["id", "pin_code", "last_name", "first_name", "phone", "email", "status"],
        "form_exclude": {"deleted_at"},
    },
    {
        "key": "employee-documents",
        "model": EmployeeDocument,
        "module": "M02",
        "label": "Sənədlər",
        "icon": "file",
        "list_fields": ["id", "employee_id", "doc_type", "doc_number", "issue_date", "expiry_date"],
    },
    {
        "key": "employee-tax-exemptions",
        "model": EmployeeTaxExemption,
        "module": "M02",
        "label": "Vergi güzəştləri",
        "icon": "percent",
        "list_fields": ["id", "employee_id", "exemption_code", "monthly_amount", "valid_from", "valid_to"],
    },
    {
        "key": "employee-family-members",
        "model": EmployeeFamilyMember,
        "module": "M02",
        "label": "Ailə üzvləri",
        "icon": "family",
        "list_fields": ["id", "employee_id", "full_name", "relation", "birth_date", "is_dependent"],
    },
    {
        "key": "employee-education",
        "model": EmployeeEducation,
        "module": "M02",
        "label": "Təhsil və staj",
        "icon": "graduation",
        "list_fields": ["id", "employee_id", "institution", "degree_level", "start_year", "end_year"],
    },
    {
        "key": "employee-military",
        "model": EmployeeMilitary,
        "module": "M02",
        "label": "Hərbi uçot",
        "icon": "shield",
        "list_fields": ["id", "employee_id", "military_ticket_number", "rank", "is_liable"],
    },
    {
        "key": "employee-migrations",
        "model": EmployeeMigration,
        "module": "M02",
        "label": "Miqrasiya",
        "icon": "globe",
        "list_fields": ["id", "employee_id", "permit_type", "permit_number", "expiry_date", "country"],
    },
    {
        "key": "contracts",
        "model": EmploymentContract,
        "module": "M03",
        "label": "Əmək müqavilələri",
        "icon": "contract",
        "list_fields": [
            "id", "contract_number", "employee_id", "staffing_id", "contract_type",
            "gross_salary", "start_date", "status",
        ],
        "form_exclude": {"termination_date", "termination_article"},
    },
    {
        "key": "service-contracts",
        "model": ServiceContract,
        "module": "M03",
        "label": "Xidməti müqavilələr",
        "icon": "contract",
        "list_fields": ["id", "contract_number", "contractor_name", "amount", "start_date", "status"],
    },
    {
        "key": "hr-orders",
        "model": HrOrder,
        "module": "M03",
        "label": "Kadr əmrləri",
        "icon": "stamp",
        "list_fields": [
            "id", "order_number", "order_type", "employee_id", "order_date",
            "effective_date", "status",
        ],
        "form_exclude": {"created_by"},
    },
    {
        "key": "government-reports",
        "model": GovernmentReport,
        "module": "M04",
        "label": "Dövlət hesabatları",
        "icon": "report",
        "list_fields": [
            "id", "report_type", "period_year", "period_month", "headcount",
            "fund_total", "status",
        ],
    },
    {
        "key": "emas-sync-logs",
        "model": EmasSyncLog,
        "module": "M04",
        "label": "ƏMAS sync logları",
        "icon": "sync",
        "list_fields": ["id", "entity_type", "entity_id", "action_type", "emas_status", "synced_at"],
    },
    {
        "key": "attendance",
        "model": AttendanceLog,
        "module": "M05",
        "label": "Turniket davamiyyəti",
        "icon": "clock",
        "list_fields": ["id", "employee_id", "punch_time", "direction", "device_id", "is_manual"],
    },
    {
        "key": "work-schedules",
        "model": WorkSchedule,
        "module": "M05",
        "label": "İş qrafikləri",
        "icon": "calendar-grid",
        "list_fields": ["id", "name", "schedule_type", "weekly_hours", "is_default"],
    },
    {
        "key": "employee-schedules",
        "model": EmployeeSchedule,
        "module": "M05",
        "label": "Fərdi qrafiklər",
        "icon": "calendar-user",
        "list_fields": ["id", "employee_id", "work_schedule_id", "effective_from", "effective_to"],
    },
    {
        "key": "timesheets",
        "model": Timesheet,
        "module": "M05",
        "label": "Tabel sətirləri",
        "icon": "clock",
        "list_fields": [
            "id", "employee_id", "year", "month", "worked_days",
            "overtime_hours", "status",
        ],
        "form_exclude": {
            "planned_days", "worked_days", "planned_hours", "regular_hours",
            "overtime_hours", "night_hours", "holiday_hours", "vacation_days",
            "sick_days", "trip_days", "absent_days", "approved_by",
        },
    },
    {
        "key": "leave-types",
        "model": LeaveType,
        "module": "M06",
        "label": "Məzuniyyət növləri",
        "icon": "palmtree",
        "list_fields": ["id", "code", "name", "is_paid", "affects_balance", "max_days_per_year"],
    },
    {
        "key": "leave-balances",
        "model": LeaveBalance,
        "module": "M06",
        "label": "Məzuniyyət balansı",
        "icon": "scale",
        "list_fields": [
            "id", "employee_id", "contract_id", "work_year_start", "work_year_end",
            "remaining_days",
        ],
    },
    {
        "key": "short-leaves",
        "model": ShortLeaveRequest,
        "module": "M06",
        "label": "Saatlıq icazələr",
        "icon": "hourglass",
        "list_fields": ["id", "employee_id", "leave_date", "start_time", "end_time", "hours", "status"],
        "form_exclude": {"approved_by"},
    },
    {
        "key": "payroll-components",
        "model": PayrollComponent,
        "module": "M07",
        "label": "Əməkhaqqı komponentləri",
        "icon": "coins",
        "list_fields": ["id", "code", "name", "component_type", "is_taxable", "sort_order"],
    },
    {
        "key": "employee-pay-components",
        "model": EmployeePayComponent,
        "module": "M07",
        "label": "Fərdi əlavə/tutulmalar",
        "icon": "coins",
        "list_fields": ["id", "employee_id", "component_id", "amount", "percent", "valid_from", "valid_to"],
    },
    {
        "key": "tax-social-rates",
        "model": TaxSocialRateHistory,
        "module": "M07",
        "label": "Vergi və sosial dərəcələr",
        "icon": "percent",
        "list_fields": ["id", "sector_type", "effective_from", "effective_to", "note"],
    },
    {
        "key": "trips",
        "model": BusinessTrip,
        "module": "M08",
        "label": "Ezamiyyətlər",
        "icon": "plane",
        "list_fields": [
            "id", "employee_id", "destination_city", "start_date", "end_date",
            "daily_allowance", "status",
        ],
    },
    {
        "key": "trip-expense-reports",
        "model": TripExpenseReport,
        "module": "M08",
        "label": "Xərc hesabatları",
        "icon": "receipt",
        "list_fields": ["id", "trip_id", "total_amount", "advance_amount", "balance", "status"],
    },
    {
        "key": "vacancies",
        "model": Vacancy,
        "module": "M09",
        "label": "Vakansiyalar",
        "icon": "megaphone",
        "list_fields": [
            "id", "title", "department_id", "openings", "salary_min", "salary_max", "status",
        ],
        "form_exclude": {"created_by", "closed_at"},
    },
    {
        "key": "candidates",
        "model": Candidate,
        "module": "M09",
        "label": "Namizədlər",
        "icon": "user-search",
        "list_fields": [
            "id", "full_name", "phone", "email", "experience_years",
            "current_position", "source",
        ],
    },
    {
        "key": "applications",
        "model": Application,
        "module": "M09",
        "label": "Müraciətlər",
        "icon": "inbox",
        "list_fields": ["id", "vacancy_id", "candidate_id", "stage", "score", "applied_at"],
        "form_exclude": {"hired_employee_id"},
    },
    {
        "key": "onboarding-tasks",
        "model": OnboardingTask,
        "module": "M10",
        "label": "Onboarding tapşırıqları",
        "icon": "checklist",
        "list_fields": ["id", "employee_id", "title", "category", "due_date", "status"],
    },
    {
        "key": "offboarding-clearances",
        "model": OffboardingClearance,
        "module": "M10",
        "label": "Offboarding clearance",
        "icon": "logout",
        "list_fields": ["id", "employee_id", "department", "item", "status"],
    },
    {
        "key": "kpi-evaluations",
        "model": KpiEvaluation,
        "module": "M11",
        "label": "KPI qiymətləndirmə",
        "icon": "target",
        "list_fields": [
            "id", "employee_id", "period_code", "final_score",
            "bonus_multiplier", "is_synced_to_payroll",
        ],
        "form_exclude": {"evaluated_by"},
    },
    {
        "key": "trainings",
        "model": Training,
        "module": "M12",
        "label": "Təlimlər",
        "icon": "presentation",
        "list_fields": ["id", "title", "training_type", "provider", "start_date", "end_date", "status"],
    },
    {
        "key": "training-participants",
        "model": TrainingParticipant,
        "module": "M12",
        "label": "Təlim iştirakçıları",
        "icon": "users",
        "list_fields": ["id", "training_id", "employee_id", "score", "status"],
    },
    {
        "key": "employee-certificates",
        "model": EmployeeCertificate,
        "module": "M12",
        "label": "Sertifikatlar",
        "icon": "certificate",
        "list_fields": ["id", "employee_id", "name", "issuer", "issue_date", "expiry_date"],
    },
    {
        "key": "safety-briefings",
        "model": SafetyBriefing,
        "module": "M13",
        "label": "Təlimat jurnalları",
        "icon": "safety",
        "list_fields": ["id", "employee_id", "briefing_type", "briefing_date", "instructor", "topic"],
    },
    {
        "key": "medical-exams",
        "model": MedicalExam,
        "module": "M13",
        "label": "Tibbi müayinə",
        "icon": "health",
        "list_fields": ["id", "employee_id", "exam_date", "next_exam_date", "clinic", "result"],
    },
    {
        "key": "ppe-issuances",
        "model": PpeIssuance,
        "module": "M13",
        "label": "Fərdi mühafizə vasitələri",
        "icon": "helmet",
        "list_fields": ["id", "employee_id", "item_name", "size", "quantity", "issued_date", "return_date"],
    },
    {
        "key": "safety-incidents",
        "model": SafetyIncident,
        "module": "M13",
        "label": "Bədbəxt hadisələr",
        "icon": "alert",
        "list_fields": [
            "id", "employee_id", "incident_date", "incident_type", "severity",
            "lost_days", "investigation_status",
        ],
    },
]

def _roles(*roles) -> list[str]:
    return sorted({str(role) for role in roles} | {Role.SUPERADMIN.value})


_HR_READ = _roles(
    Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER
)
_HR_WRITE = _roles(Role.HR_DIRECTOR, Role.HR_SPECIALIST)
_PAYROLL = _roles(Role.HR_DIRECTOR, Role.ACCOUNTANT)
_RECRUIT_READ = _roles(Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER)
_APPROVAL = _roles(Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER)
_ADMIN = _roles(Role.HR_DIRECTOR)
_ALL = _roles(*Role)

SCREENS = [
    {"key": "dashboard", "title": "İcmal", "module": "OVERVIEW", "icon": "dashboard", "roles": _HR_READ, "manage_roles": []},
    {"key": "payroll-runs", "title": "Əməkhaqqı hesablamaları", "module": "M07", "icon": "wallet", "roles": _PAYROLL, "manage_roles": _PAYROLL},
    {"key": "leave-requests", "title": "Məzuniyyət sorğuları", "module": "M06", "icon": "palmtree", "roles": _HR_READ, "manage_roles": _APPROVAL},
    {"key": "sick-leaves", "title": "Xəstəlik vərəqələri", "module": "M06", "icon": "health", "roles": _HR_READ, "manage_roles": _HR_WRITE},
    {"key": "timesheets", "title": "Tabel (T-13)", "module": "M05", "icon": "clock", "roles": _HR_READ, "manage_roles": _HR_WRITE},
    {"key": "attendance", "title": "Turniket və Davamiyyət", "module": "M05", "icon": "log-in", "roles": _HR_READ, "manage_roles": _HR_WRITE},
    {"key": "work-schedules", "title": "İş qrafikləri (Növbəli)", "module": "M05", "icon": "calendar", "roles": _HR_READ, "manage_roles": _HR_WRITE},
    {"key": "production-calendar", "title": "İstehsalat təqvimi", "module": "M05", "icon": "calendar-grid", "roles": _HR_READ, "manage_roles": _HR_WRITE},
    {"key": "structure", "title": "Təşkilat strukturu", "module": "M01", "icon": "tree", "roles": _HR_READ, "manage_roles": []},
    {"key": "reports", "title": "Müddət xəbərdarlıqları", "module": "M02", "icon": "alert", "roles": _HR_READ, "manage_roles": []},
    {"key": "compliance", "title": "Dövlət hesabatları", "module": "M04", "icon": "report", "roles": _PAYROLL, "manage_roles": _PAYROLL},
    {"key": "recruitment", "title": "İşə qəbul lövhəsi", "module": "M09", "icon": "user-search", "roles": _RECRUIT_READ, "manage_roles": _RECRUIT_READ},
    {"key": "onboarding", "title": "Onboarding idarəsi", "module": "M10", "icon": "checklist", "roles": _RECRUIT_READ, "manage_roles": _HR_WRITE},
    {"key": "approvals", "title": "Təsdiq mərkəzi", "module": "M14", "icon": "check", "roles": _APPROVAL, "manage_roles": _APPROVAL},
    {"key": "mss", "title": "MSS · Komandam", "module": "M14", "icon": "users", "roles": _APPROVAL, "manage_roles": []},
    {"key": "users", "title": "İstifadəçilər", "module": "M14", "icon": "shield", "roles": _ADMIN, "manage_roles": _ADMIN},
    {"key": "audit", "title": "Audit jurnalı", "module": "M14", "icon": "list", "roles": _ADMIN, "manage_roles": []},
    {"key": "system-settings", "title": "Sistem və Demo İdarəsi", "module": "M14", "icon": "settings", "roles": _ADMIN, "manage_roles": _ADMIN},
    {"key": "ess", "title": "ESS · Şəxsi kabinet", "module": "M14", "icon": "user", "roles": _ALL, "manage_roles": _ALL},
]

TABLE_TO_ENTITY = {
    "organizations": "organizations",
    "departments": "departments",
    "positions": "positions",
    "staffing_table": "staffing",
    "employees": "employees",
    "employment_contracts": "contracts",
    "leave_types": "leave-types",
    "payroll_components": "payroll-components",
    "payroll_runs": "payroll-runs",
    "timesheets": "timesheets",
    "work_schedules": "work-schedules",
    "business_trips": "trips",
    "vacancies": "vacancies",
    "candidates": "candidates",
    "trainings": "trainings",
    "hr_orders": "hr-orders",
    "users": "users",
}

FIELD_LABELS = {
    "id": "ID",
    "organization_id": "Təşkilat",
    "parent_id": "Üst bölmə",
    "employee_id": "İşçi",
    "contract_id": "Müqavilə",
    "staffing_id": "Ştat vahidi",
    "department_id": "Departament",
    "position_id": "Vəzifə",
    "leave_type_id": "Məzuniyyət növü",
    "component_id": "Komponent",
    "training_id": "Təlim",
    "trip_id": "Ezamiyyət",
    "vacancy_id": "Vakansiya",
    "candidate_id": "Namizəd",
    "hired_employee_id": "İşə qəbul edilən işçi",
    "head_employee_id": "Bölmə rəhbəri",
    "approver_id": "Təsdiqləyən",
    "approved_by": "Təsdiqləyən",
    "created_by": "Yaradan",
    "evaluated_by": "Qiymətləndirən",
    "user_id": "İstifadəçi",
    "first_name": "Ad",
    "last_name": "Soyad",
    "father_name": "Ata adı",
    "full_name": "Ad Soyad",
    "pin_code": "FİN",
    "ssn": "SSN",
    "individual_voen": "Fərdi VÖEN",
    "birth_date": "Doğum tarixi",
    "gender": "Cins",
    "citizenship": "Vətəndaşlıq",
    "marital_status": "Ailə vəziyyəti",
    "id_card_number": "Şəxsiyyət vəsiqəsi",
    "id_card_issue_date": "ŞV verilmə tarixi",
    "id_card_expiry_date": "ŞV bitmə tarixi",
    "phone": "Telefon",
    "email": "E-poçt",
    "address": "Ünvan",
    "bank_name": "Bank",
    "bank_iban": "IBAN",
    "bank_swift": "SWIFT",
    "photo_path": "Foto",
    "total_insurance_tenure_years": "Sığorta stajı (il)",
    "status": "Status",
    "notes": "Qeydlər",
    "deleted_at": "Silinmə tarixi",
    "created_at": "Yaradılma tarixi",
    "updated_at": "Yenilənmə tarixi",
    "name": "Ad",
    "short_name": "Qısa ad",
    "voen": "VÖEN",
    "sun_code": "SUN kod",
    "legal_address": "Hüquqi ünvan",
    "actual_address": "Faktiki ünvan",
    "director_id": "Direktor",
    "sector_type": "Sektor",
    "settings_json": "Parametrlər (JSON)",
    "is_active": "Aktiv",
    "code": "Kod",
    "cost_center_code": "Xərc mərkəzi",
    "path": "İerarxiya",
    "title": "Ad",
    "occupation_code": "Peşə kodu",
    "grade_level": "Dərəcə",
    "min_salary": "Min. əməkhaqqı",
    "max_salary": "Maks. əməkhaqqı",
    "annual_leave_days": "İllik məzuniyyət (gün)",
    "approved_headcount": "Təsdiqlənmiş ştat",
    "base_salary": "Baza əməkhaqqı",
    "harmful_work_bonus_pct": "Zərərli şərait əlavəsi (%)",
    "effective_from": "Qüvvəyə minmə",
    "effective_to": "Qüvvədən düşmə",
    "doc_type": "Sənəd növü",
    "doc_number": "Sənəd nömrəsi",
    "issue_date": "Verilmə tarixi",
    "expiry_date": "Bitmə tarixi",
    "file_path": "Fayl",
    "exemption_code": "Güzəşt kodu",
    "monthly_amount": "Aylıq məbləğ",
    "doc_reference": "Sənəd istinadı",
    "valid_from": "Qüvvəyə minmə",
    "valid_to": "Qüvvədən düşmə",
    "relation": "Qohumluq",
    "is_dependent": "Asılı şəxs",
    "document_number": "Sənəd nömrəsi",
    "institution": "Təhsil müəssisəsi",
    "degree_level": "Təhsil pilləsi",
    "specialty": "İxtisas",
    "diploma_number": "Diplom nömrəsi",
    "start_year": "Başlama ili",
    "end_year": "Bitirmə ili",
    "is_primary": "Əsas",
    "military_ticket_number": "Hərbi bileti",
    "rank": "Rütbə",
    "registration_office": "Qeydiyyat orqanı",
    "is_liable": "Hərbi mükəlləfiyyət",
    "permit_type": "İcazə növü",
    "permit_number": "İcazə nömrəsi",
    "country": "Ölkə",
    "contract_number": "Müqavilə nömrəsi",
    "contract_type": "Müqavilə növü",
    "work_type": "İş növü",
    "start_date": "Başlama tarixi",
    "end_date": "Bitmə tarixi",
    "probation_end_date": "Sınaq müddəti bitişi",
    "gross_salary": "Brutto əməkhaqqı",
    "salary_type": "Əməkhaqqı növü",
    "signed_date": "İmzalanma tarixi",
    "termination_date": "Xitam tarixi",
    "termination_article": "Xitam maddəsi",
    "contractor_name": "Podratçı",
    "contractor_voen": "Podratçı VÖEN",
    "amount": "Məbləğ",
    "service_description": "Xidmətin təsviri",
    "withholding_tax_pct": "Vergi tutulması (%)",
    "dsmf_pct": "DSMF (%)",
    "payment_details": "Ödəniş detalları (JSON)",
    "order_number": "Əmr nömrəsi",
    "order_type": "Əmr növü",
    "labor_code_article": "ƏM maddəsi",
    "order_date": "Əmr tarixi",
    "effective_date": "Qüvvəyə minmə tarixi",
    "payload_json": "Məlumat (JSON)",
    "report_type": "Hesabat növü",
    "period_year": "İl",
    "period_month": "Ay",
    "period_quarter": "Rüb",
    "headcount": "İşçi sayı",
    "fund_total": "Fond (cəmi)",
    "entity_type": "Obyekt növü",
    "entity_id": "Obyekt ID",
    "action_type": "Əməliyyat növü",
    "request_payload": "Sorğu (JSON)",
    "response_payload": "Cavab (JSON)",
    "emas_status": "ƏMAS statusu",
    "retry_count": "Təkrar sayı",
    "synced_at": "Sinxronlaşma vaxtı",
    "punch_time": "Keçid vaxtı",
    "direction": "İstiqamət",
    "device_id": "Cihaz",
    "is_manual": "Əl ilə",
    "raw_payload": "Xam məlumat (JSON)",
    "schedule_type": "Qrafik növü",
    "weekly_hours": "Həftəlik saat",
    "shift_rules_json": "Növbə qaydaları (JSON)",
    "is_default": "Standart",
    "work_schedule_id": "İş qrafiki",
    "year": "İl",
    "month": "Ay",
    "planned_days": "Plan gün",
    "worked_days": "İşlənmiş gün",
    "planned_hours": "Plan saat",
    "regular_hours": "Normal saat",
    "overtime_hours": "Əlavə iş saatı",
    "night_hours": "Gecə saatı",
    "holiday_hours": "Bayram saatı",
    "vacation_days": "Məzuniyyət günü",
    "sick_days": "Xəstəlik günü",
    "trip_days": "Ezamiyyət günü",
    "absent_days": "Gəlmədiyi gün",
    "is_paid": "Ödənişli",
    "affects_balance": "Balansa təsir",
    "max_days_per_year": "İllik maks. gün",
    "labor_code_ref": "ƏM istinadı",
    "description": "Təsvir",
    "work_year_start": "İş ili başlanğıcı",
    "work_year_end": "İş ili sonu",
    "entitled_base_days": "Baza gün hüququ",
    "entitled_extra_days": "Əlavə gün hüququ",
    "used_days": "İstifadə olunan gün",
    "remaining_days": "Qalıq gün",
    "leave_date": "İcazə tarixi",
    "start_time": "Başlama vaxtı",
    "end_time": "Bitmə vaxtı",
    "hours": "Saat",
    "reason": "Səbəb",
    "component_type": "Komponent növü",
    "is_taxable": "Vergiyə cəlb olunur",
    "is_dsmf_base": "DSMF bazası",
    "is_its_base": "İTS bazası",
    "is_unemployment_base": "İşsizlik bazası",
    "include_in_vacation_avg": "Məzuniyyət ortalamasına daxil",
    "include_in_sick_avg": "Xəstəlik ortalamasına daxil",
    "sort_order": "Sıralama",
    "percent": "Faiz",
    "rules_json": "Qaydalar (JSON)",
    "note": "Qeyd",
    "destination_city": "Şəhər",
    "is_foreign": "Xarici",
    "purpose": "Məqsəd",
    "daily_allowance": "Gündəlik kasa",
    "hotel_limit": "Otel limiti",
    "total_advance": "Avans",
    "actual_expenses": "Faktiki xərc",
    "order_id": "Əmr",
    "submitted_at": "Təqdim edilmə vaxtı",
    "total_amount": "Cəmi məbləğ",
    "advance_amount": "Avans məbləği",
    "balance": "Balans",
    "items_json": "Xərc sətirləri (JSON)",
    "openings": "Vakansiya sayı",
    "requirements": "Tələblər",
    "salary_min": "Min. əməkhaqqı",
    "salary_max": "Maks. əməkhaqqı",
    "closed_at": "Bağlanma tarixi",
    "cv_url": "CV linki",
    "skills_json": "Bacarıqlar (JSON)",
    "experience_years": "Təcrübə (il)",
    "current_position": "Cari vəzifə",
    "source": "Mənbə",
    "stage": "Mərhələ",
    "score": "Bal",
    "applied_at": "Müraciət tarixi",
    "category": "Kateqoriya",
    "assignee": "Məsul şəxs",
    "due_date": "Son tarix",
    "item": "Element",
    "period_code": "Dövr",
    "kpi_items_json": "KPI göstəriciləri (JSON)",
    "final_score": "Yekun bal",
    "bonus_multiplier": "Bonus əmsalı",
    "is_synced_to_payroll": "Payroll-a sync",
    "training_type": "Təlim növü",
    "provider": "Təşkilatçı",
    "budget": "Büdcə",
    "cost": "Xərc",
    "certificate_number": "Sertifikat nömrəsi",
    "certificate_expiry": "Sertifikat bitmə tarixi",
    "issuer": "Veren qurum",
    "number": "Nömrə",
    "briefing_type": "Təlimat növü",
    "briefing_date": "Təlimat tarixi",
    "instructor": "Təlimatçı",
    "topic": "Mövzu",
    "signature_ref": "İmza istinadı",
    "exam_date": "Müayinə tarixi",
    "next_exam_date": "Növbəti müayinə",
    "clinic": "Klinika",
    "result": "Nəticə",
    "item_name": "Vasitə adı",
    "size": "Ölçü",
    "quantity": "Miqdar",
    "issued_date": "Verilmə tarixi",
    "return_date": "Qaytarılma tarixi",
    "useful_life_months": "İstifadə müddəti (ay)",
    "incident_date": "Hadisə tarixi",
    "incident_type": "Hadisə növü",
    "severity": "Ağırlıq",
    "lost_days": "İtirilmiş gün",
    "investigation_status": "Araşdırma statusu",
}

CHOICES = {
    ("employees", "gender"): ["M", "F"],
    ("employees", "status"): ["ACTIVE", "ON_LEAVE", "SUSPENDED", "TERMINATED"],
    ("employees", "marital_status"): ["SINGLE", "MARRIED", "DIVORCED", "WIDOWED"],
    ("organizations", "sector_type"): ["NON_OIL_PRIVATE", "OIL_PUBLIC"],
    ("employment_contracts", "contract_type"): ["INDEFINITE", "FIXED_TERM", "PART_TIME"],
    ("employment_contracts", "work_type"): ["MAIN", "PART_TIME", "CONTRACT"],
    ("employment_contracts", "salary_type"): ["MONTHLY", "HOURLY"],
    ("employment_contracts", "status"): ["ACTIVE", "SUSPENDED", "TERMINATED"],
    ("service_contracts", "status"): ["ACTIVE", "COMPLETED", "CANCELLED"],
    ("hr_orders", "order_type"): [
        "HIRE", "TRANSFER", "TERMINATE", "LEAVE", "BONUS", "DISCIPLINARY", "OTHER",
    ],
    ("hr_orders", "status"): ["DRAFT", "SIGNED", "CANCELLED"],
    ("leave_requests", "status"): ["PENDING", "APPROVED", "REJECTED", "CANCELLED"],
    ("short_leave_requests", "status"): ["PENDING", "APPROVED", "REJECTED", "CANCELLED"],
    ("sick_leaves", "status"): ["ACTIVE", "CANCELLED"],
    ("production_calendar", "day_type"): [
        "WORKDAY", "WEEKEND", "HOLIDAY", "MOURNING", "SHORT_WORKDAY",
    ],
    ("work_schedules", "schedule_type"): ["STANDARD_5", "SHIFT", "FLEXIBLE"],
    ("timesheets", "status"): ["OPEN", "APPROVED", "LOCKED"],
    ("business_trips", "status"): ["PENDING", "APPROVED", "REJECTED", "COMPLETED", "CANCELLED"],
    ("trip_expense_reports", "status"): ["SUBMITTED", "APPROVED", "REJECTED"],
    ("vacancies", "status"): ["OPEN", "CLOSED", "ON_HOLD"],
    ("applications", "stage"): ["NEW", "CALL", "INTERVIEW", "TASK", "OFFER", "HIRED", "REJECTED"],
    ("onboarding_tasks", "status"): ["PENDING", "IN_PROGRESS", "DONE"],
    ("onboarding_tasks", "category"): ["HR", "IT", "TRAINING", "SECURITY", "OTHER"],
    ("offboarding_clearances", "status"): ["PENDING", "DONE", "WAIVED"],
    ("payroll_runs", "run_type"): ["REGULAR", "BONUS", "FINAL"],
    ("payroll_runs", "status"): ["DRAFT", "CALCULATED", "APPROVED", "PAID"],
    ("payroll_components", "component_type"): ["EARNING", "DEDUCTION"],
    ("government_reports", "report_type"): ["UNIFIED_DECLARATION", "ISB", "STATISTICS", "OTHER"],
    ("government_reports", "status"): ["DRAFT", "SUBMITTED", "ACCEPTED"],
    ("emas_sync_logs", "emas_status"): ["QUEUED", "SENT", "SYNCED", "FAILED"],
    ("emas_sync_logs", "action_type"): ["SYNC", "CREATE", "UPDATE", "DELETE"],
    ("employee_documents", "doc_type"): [
        "ID_CARD", "PASSPORT", "MILITARY", "DIPLOMA", "MEDICAL", "OTHER",
    ],
    ("employee_family_members", "relation"): ["CHILD", "SPOUSE", "PARENT", "SIBLING", "OTHER"],
    ("employee_migrations", "permit_type"): [
        "WORK_PERMIT", "RESIDENCE_PERMIT", "TEMPORARY",
    ],
    ("employee_education", "degree_level"): [
        "SECONDARY", "BACHELOR", "MASTER", "PHD",
    ],
    ("safety_briefings", "briefing_type"): ["INTRO", "REPEAT", "TARGETED"],
    ("safety_incidents", "incident_type"): [
        "MINOR_INJURY", "SERIOUS_INJURY", "FATALITY", "NEAR_MISS", "PROPERTY_DAMAGE",
    ],
    ("safety_incidents", "severity"): ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    ("safety_incidents", "investigation_status"): ["OPEN", "IN_PROGRESS", "CLOSED"],
    ("medical_exams", "result"): ["FIT", "RESTRICTED", "UNFIT"],
    ("trainings", "training_type"): ["INTERNAL", "EXTERNAL", "ONLINE"],
    ("trainings", "status"): ["PLANNED", "ONGOING", "COMPLETED", "CANCELLED"],
    ("training_participants", "status"): ["REGISTERED", "ATTENDED", "COMPLETED", "ABSENT"],
    ("attendance_logs", "direction"): ["IN", "OUT"],
    ("tax_social_rates_history", "sector_type"): ["NON_OIL_PRIVATE", "OIL_PUBLIC"],
}

FORM_EXCLUDE_DEFAULT = {
    "id", "created_at", "updated_at", "deleted_at",
}


def _field_type(column) -> str:
    ctype = column.type
    if isinstance(ctype, Boolean):
        return "boolean"
    if isinstance(ctype, DateTime):
        return "datetime"
    if isinstance(ctype, Date):
        return "date"
    if isinstance(ctype, Time):
        return "time"
    if isinstance(ctype, (Integer,)):
        return "integer"
    if isinstance(ctype, (Numeric, Float)):
        return "number"
    if "JSON" in type(ctype).__name__.upper():
        return "json"
    if isinstance(ctype, Text) or getattr(ctype, "length", 0) is None or (ctype.length or 0) > 500:
        return "text"
    return "string"


def _field_label(name: str) -> str:
    if name in FIELD_LABELS:
        return FIELD_LABELS[name]
    return name.replace("_", " ").strip().capitalize()


def _field_default(column):
    default = column.default
    if default is not None and not default.is_callable and not default.is_scalar:
        value = default.arg
        if isinstance(value, (str, int, float, bool)):
            return value
    return None


def _entity_meta(defn: dict) -> dict:
    model = defn["model"]
    table = model.__table__
    form_exclude = FORM_EXCLUDE_DEFAULT | defn.get("form_exclude", set())
    fields = []
    for column in table.columns:
        fk_target = None
        for fk in column.foreign_keys:
            fk_target = TABLE_TO_ENTITY.get(fk.column.table.name)
        required = (
            not column.nullable
            and column.default is None
            and column.server_default is None
            and not column.primary_key
        )
        choices = CHOICES.get((table.name, column.name))
        fields.append(
            {
                "name": column.name,
                "label": _field_label(column.name),
                "type": _field_type(column),
                "required": required,
                "readonly": column.primary_key or column.name in form_exclude,
                "max_length": getattr(column.type, "length", None),
                "choices": choices,
                "ref": fk_target,
                "default": _field_default(column),
            }
        )
    return {
        "key": defn["key"],
        "path": f"/{defn['key']}",
        "module": defn["module"],
        "label": defn["label"],
        "icon": defn.get("icon", "dot"),
        "list_fields": defn["list_fields"],
        "fields": fields,
        "permissions": ENTITY_ACL.get(defn["key"], {
            "read_roles": [],
            "write_roles": [],
            "delete_roles": [],
        }),
    }


@router.get("/entities")
def entities(user: User = Depends(get_current_user)):
    entities_meta = []
    for defn in ENTITY_DEFS:
        permissions = ENTITY_ACL.get(defn["key"], {})
        if user.role not in permissions.get("read_roles", []):
            continue
        entities_meta.append(_entity_meta(defn))
    screens = [screen for screen in SCREENS if user.role in screen["roles"]]
    return {
        "modules": MODULES,
        "screens": screens,
        "entities": entities_meta,
    }
