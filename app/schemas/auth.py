from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: "UserRead"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    organization_id: int | None = None
    employee_id: int | None = None
    is_active: bool
    last_login_at: datetime | None = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=10, max_length=128)
    role: str = "EMPLOYEE"
    organization_id: int | None = None
    employee_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    organization_id: int | None = None
    employee_id: int | None = None
    is_active: bool | None = None


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=10, max_length=128)


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=10, max_length=128)


Token.model_rebuild()
