from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.contract import EmploymentContract
from app.models.employee import Employee, EmployeeDocument, EmployeeMigration
from app.models.leave import LeaveRequest
from app.models.organization import Department, StaffingTable
from app.models.payroll import PayrollItem, PayrollRun
from app.models.time import AttendanceLog


def dashboard(db: Session, organization_id: int) -> dict:
    headcount = db.scalar(
        select(func.count(Employee.id)).where(
            Employee.organization_id == organization_id,
            Employee.status == "ACTIVE",
            Employee.deleted_at.is_(None),
        )
    ) or 0

    gender_rows = db.execute(
        select(Employee.gender, func.count(Employee.id))
        .where(
            Employee.organization_id == organization_id,
            Employee.status == "ACTIVE",
            Employee.deleted_at.is_(None),
        )
        .group_by(Employee.gender)
    ).all()

    today = date.today()
    age_buckets = {"<25": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55+": 0}
    for birth_date in db.scalars(
        select(Employee.birth_date).where(
            Employee.organization_id == organization_id,
            Employee.status == "ACTIVE",
            Employee.birth_date.isnot(None),
        )
    ):
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 25:
            age_buckets["<25"] += 1
        elif age < 35:
            age_buckets["25-34"] += 1
        elif age < 45:
            age_buckets["35-44"] += 1
        elif age < 55:
            age_buckets["45-54"] += 1
        else:
            age_buckets["55+"] += 1

    latest_run = db.scalar(
        select(PayrollRun)
        .where(PayrollRun.organization_id == organization_id, PayrollRun.status != "DRAFT")
        .order_by(PayrollRun.period_year.desc(), PayrollRun.period_month.desc())
        .limit(1)
    )

    pending_leaves = db.scalar(
        select(func.count(LeaveRequest.id)).where(
            LeaveRequest.organization_id == organization_id,
            LeaveRequest.status == "PENDING",
        )
    ) or 0

    expiring_documents = db.scalar(
        select(func.count(EmployeeDocument.id))
        .join(Employee, Employee.id == EmployeeDocument.employee_id)
        .where(
            Employee.organization_id == organization_id,
            EmployeeDocument.expiry_date.isnot(None),
            EmployeeDocument.expiry_date >= today,
            EmployeeDocument.expiry_date <= today + timedelta(days=60),
        )
    ) or 0

    expiring_permits = db.scalar(
        select(func.count(EmployeeMigration.id))
        .join(Employee, Employee.id == EmployeeMigration.employee_id)
        .where(
            Employee.organization_id == organization_id,
            EmployeeMigration.expiry_date.isnot(None),
            EmployeeMigration.expiry_date >= today,
            EmployeeMigration.expiry_date <= today + timedelta(days=60),
        )
    ) or 0

    terminated = db.scalar(
        select(func.count(EmploymentContract.id)).where(
            EmploymentContract.organization_id == organization_id,
            EmploymentContract.status == "TERMINATED",
            EmploymentContract.termination_date >= today - timedelta(days=365),
        )
    ) or 0
    turnover = round((terminated / headcount) * 100, 2) if headcount else 0

    department_rows = db.execute(
        select(Department.name, func.count(Employee.id))
        .join(StaffingTable, StaffingTable.department_id == Department.id)
        .join(EmploymentContract, EmploymentContract.staffing_id == StaffingTable.id)
        .join(Employee, Employee.id == EmploymentContract.employee_id)
        .where(
            Department.organization_id == organization_id,
            EmploymentContract.status == "ACTIVE",
            Employee.deleted_at.is_(None),
        )
        .group_by(Department.name)
        .order_by(func.count(Employee.id).desc())
    ).all()

    return {
        "headcount": headcount,
        "gender_distribution": {g or "NAMƏLUM": c for g, c in gender_rows},
        "age_distribution": age_buckets,
        "departments": [{"name": name, "headcount": count} for name, count in department_rows],
        "latest_payroll": (
            {
                "period": f"{latest_run.period_year}-{latest_run.period_month:02d}",
                "status": latest_run.status,
                "total_gross": float(latest_run.total_gross),
                "total_net": float(latest_run.total_net),
            }
            if latest_run
            else None
        ),
        "pending_leave_requests": pending_leaves,
        "expiring_documents_60d": expiring_documents,
        "expiring_permits_60d": expiring_permits,
        "annual_turnover_pct": turnover,
        "attendance_logs_last_30d_note": "Ətraflı hesabat üçün /analytics/attendance endpointindən istifadə edin",
    }


def payroll_fund_trend(db: Session, organization_id: int, months: int = 12) -> list[dict]:
    rows = db.execute(
        select(
            PayrollRun.period_year,
            PayrollRun.period_month,
            func.sum(PayrollItem.gross_total),
            func.sum(PayrollItem.net_payable),
            func.count(PayrollItem.id),
        )
        .join(PayrollItem, PayrollItem.payroll_run_id == PayrollRun.id)
        .where(
            PayrollRun.organization_id == organization_id,
            PayrollRun.run_type == "REGULAR",
            PayrollRun.status.in_(["CALCULATED", "APPROVED", "PAID"]),
        )
        .group_by(PayrollRun.period_year, PayrollRun.period_month)
        .order_by(PayrollRun.period_year.desc(), PayrollRun.period_month.desc())
        .limit(months)
    ).all()
    return [
        {
            "period": f"{year}-{month:02d}",
            "gross": float(gross or 0),
            "net": float(net or 0),
            "headcount": count,
        }
        for year, month, gross, net, count in reversed(rows)
    ]


def department_payroll(db: Session, organization_id: int, year: int, month: int) -> list[dict]:
    run = db.scalar(
        select(PayrollRun).where(
            PayrollRun.organization_id == organization_id,
            PayrollRun.period_year == year,
            PayrollRun.period_month == month,
            PayrollRun.run_type == "REGULAR",
        )
    )
    if run is None:
        return []
    rows = db.execute(
        select(
            Department.name,
            func.count(PayrollItem.id),
            func.sum(PayrollItem.gross_total),
            func.sum(PayrollItem.net_payable),
        )
        .join(EmploymentContract, EmploymentContract.id == PayrollItem.contract_id)
        .join(StaffingTable, StaffingTable.id == EmploymentContract.staffing_id)
        .join(Department, Department.id == StaffingTable.department_id)
        .where(PayrollItem.payroll_run_id == run.id)
        .group_by(Department.name)
        .order_by(func.sum(PayrollItem.gross_total).desc())
    ).all()
    return [
        {"department": name, "headcount": count, "gross": float(gross or 0), "net": float(net or 0)}
        for name, count, gross, net in rows
    ]


def attendance_summary(db: Session, organization_id: int, year: int, month: int) -> list[dict]:
    rows = db.execute(
        select(
            Employee.id,
            Employee.first_name,
            Employee.last_name,
            func.count(AttendanceLog.id),
            func.min(AttendanceLog.punch_time),
            func.max(AttendanceLog.punch_time),
        )
        .join(AttendanceLog, AttendanceLog.employee_id == Employee.id)
        .where(
            Employee.organization_id == organization_id,
            func.extract("year", AttendanceLog.punch_time) == year,
            func.extract("month", AttendanceLog.punch_time) == month,
        )
        .group_by(Employee.id, Employee.first_name, Employee.last_name)
    ).all()
    return [
        {
            "employee_id": emp_id,
            "employee": f"{last_name} {first_name}",
            "punch_count": count,
            "first_punch": first.isoformat() if first else None,
            "last_punch": last.isoformat() if last else None,
        }
        for emp_id, first_name, last_name, count, first, last in rows
    ]
