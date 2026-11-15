from datetime import date
import logging
from sqlalchemy import delete, func, select, text, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    Application,
    ApprovalWorkflow,
    AttendanceLog,
    BusinessTrip,
    Candidate,
    ContractAmendment,
    Department,
    EmasSyncLog,
    Employee,
    EmployeeCertificate,
    EmployeeDocument,
    EmployeeEducation,
    EmployeeFamilyMember,
    EmployeeMigration,
    EmployeeMilitary,
    EmployeePayComponent,
    EmployeeSchedule,
    EmployeeTaxExemption,
    EmploymentContract,
    GovernmentReport,
    HrOrder,
    KpiEvaluation,
    LeaveBalance,
    LeaveRequest,
    MedicalExam,
    OffboardingClearance,
    OnboardingTask,
    Organization,
    PayrollItem,
    PayrollItemDetail,
    PayrollRun,
    PpeIssuance,
    SafetyBriefing,
    SafetyIncident,
    ServiceContract,
    ShortLeaveRequest,
    SickLeave,
    Timesheet,
    Training,
    TrainingParticipant,
    TripExpenseReport,
    User,
    Vacancy,
    WorkSchedule,
)

logger = logging.getLogger(__name__)


def wipe_demo_data(db: Session, current_user_id: int) -> dict:
    """Safely wipes all operational demo data while preserving reference catalogs and superadmin."""
    logger.info("Starting demo data wipe initiated by user_id=%s", current_user_id)
    summary = {}

    # 1. Sever circular / foreign-key pointers to Employee before deleting Employees
    db.execute(update(Organization).values(director_id=None))
    db.execute(update(Department).values(head_employee_id=None))
    db.execute(update(User).values(employee_id=None))
    db.flush()

    # 2. Delete transactional and child tables in strict reverse-dependency order
    table_deletions = [
        ("payroll_item_details", PayrollItemDetail),
        ("payroll_items", PayrollItem),
        ("payroll_runs", PayrollRun),
        ("employee_pay_components", EmployeePayComponent),
        ("trip_expense_reports", TripExpenseReport),
        ("business_trips", BusinessTrip),
        ("timesheets", Timesheet),
        ("attendance_logs", AttendanceLog),
        ("employee_schedules", EmployeeSchedule),
        ("leave_balances", LeaveBalance),
        ("leave_requests", LeaveRequest),
        ("sick_leaves", SickLeave),
        ("short_leave_requests", ShortLeaveRequest),
        ("contract_amendments", ContractAmendment),
        ("hr_orders", HrOrder),
        ("employment_contracts", EmploymentContract),
        ("applications", Application),
        ("vacancies", Vacancy),
        ("candidates", Candidate),
        ("safety_briefings", SafetyBriefing),
        ("safety_incidents", SafetyIncident),
        ("ppe_issuances", PpeIssuance),
        ("training_participants", TrainingParticipant),
        ("trainings", Training),
        ("kpi_evaluations", KpiEvaluation),
        ("approval_workflows", ApprovalWorkflow),
        ("onboarding_tasks", OnboardingTask),
        ("offboarding_clearances", OffboardingClearance),
        ("medical_exams", MedicalExam),
        ("employee_tax_exemptions", EmployeeTaxExemption),
        ("employee_military", EmployeeMilitary),
        ("employee_migrations", EmployeeMigration),
        ("employee_family_members", EmployeeFamilyMember),
        ("employee_education", EmployeeEducation),
        ("employee_documents", EmployeeDocument),
        ("employee_certificates", EmployeeCertificate),
        ("service_contracts", ServiceContract),
        ("government_reports", GovernmentReport),
        ("emas_sync_logs", EmasSyncLog),
        ("employees", Employee),
    ]

    for label, model_cls in table_deletions:
        try:
            count = db.query(model_cls).delete(synchronize_session=False)
            summary[label] = count
        except Exception as exc:
            logger.warning("Error deleting %s: %s", label, exc)
            summary[label] = 0

    # 3. Clean custom non-default work schedules (keep default one if exists)
    try:
        deleted_schedules = db.query(WorkSchedule).filter(WorkSchedule.is_default.is_(False)).delete(synchronize_session=False)
        summary["custom_work_schedules"] = deleted_schedules
    except Exception as exc:
        logger.warning("Error deleting custom work schedules: %s", exc)

    # 4. Delete demo users (keep current user and all other SUPERADMIN users)
    try:
        demo_users_deleted = db.query(User).filter(
            User.role != "SUPERADMIN",
            User.id != current_user_id
        ).delete(synchronize_session=False)
        summary["demo_users"] = demo_users_deleted
    except Exception as exc:
        logger.warning("Error deleting demo users: %s", exc)
        summary["demo_users"] = 0

    # 5. Update Organization settings to explicitly disable demo mode
    orgs = list(db.scalars(select(Organization)))
    for org in orgs:
        settings_dict = dict(org.settings_json or {})
        settings_dict["demo_enabled"] = False
        org.settings_json = settings_dict
    db.flush()

    # 6. Reset sequences so any new records start from 1
    sequences = [
        "candidates_id_seq",
        "vacancies_id_seq",
        "applications_id_seq",
        "employees_id_seq",
        "employment_contracts_id_seq",
        "contract_amendments_id_seq",
        "hr_orders_id_seq",
        "timesheets_id_seq",
        "payroll_runs_id_seq",
        "payroll_items_id_seq",
        "payroll_item_details_id_seq",
        "employee_pay_components_id_seq",
        "attendance_logs_id_seq",
        "leave_requests_id_seq",
        "leave_balances_id_seq",
        "sick_leaves_id_seq",
        "short_leave_requests_id_seq",
        "business_trips_id_seq",
        "trip_expense_reports_id_seq",
        "employee_schedules_id_seq",
        "employee_documents_id_seq",
        "trainings_id_seq",
        "safety_incidents_id_seq",
        "approval_workflows_id_seq",
    ]
    for seq in sequences:
        try:
            db.execute(text(f"ALTER SEQUENCE IF EXISTS {seq} RESTART WITH 1"))
        except Exception:
            pass

    db.commit()
    logger.info("Demo data wipe completed successfully. Summary: %s", summary)

    return {
        "status": "ok",
        "demo_enabled": False,
        "message": "Demo məlumatları tam təmizləndi və sistem real rejimə keçirildi",
        "summary": summary,
    }


def set_demo_mode(db: Session, enabled: bool) -> bool:
    """Updates the demo_enabled flag in organization settings."""
    orgs = list(db.scalars(select(Organization)))
    for org in orgs:
        settings_dict = dict(org.settings_json or {})
        settings_dict["demo_enabled"] = enabled
        org.settings_json = settings_dict
    db.commit()
    return enabled
