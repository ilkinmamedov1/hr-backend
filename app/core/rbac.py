try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class Role(StrEnum):
    SUPERADMIN = "SUPERADMIN"
    HR_DIRECTOR = "HR_DIRECTOR"
    HR_SPECIALIST = "HR_SPECIALIST"
    ACCOUNTANT = "ACCOUNTANT"
    DEPT_MANAGER = "DEPT_MANAGER"
    EMPLOYEE = "EMPLOYEE"


ALL_ROLES = {r.value for r in Role}
HR_ROLES = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
PAYROLL_ROLES = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.ACCOUNTANT}
MANAGEMENT_ROLES = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.DEPT_MANAGER}
