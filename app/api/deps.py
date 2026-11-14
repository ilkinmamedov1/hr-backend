from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.audit import current_user_id
from app.core.database import get_db
from app.core.rbac import Role
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token etibarsızdır",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        token_version = int(payload.get("tv", 0))
    except Exception:
        raise credentials_exception

    user = db.get(User, user_id)
    if (
        user is None
        or not user.is_active
        or token_version != int(user.token_version or 0)
    ):
        raise credentials_exception
    if user.role != Role.SUPERADMIN.value and user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="İstifadəçi heç bir təşkilata bağlı deyil",
        )
    current_user_id.set(user.id)
    return user


def require_roles(*roles) -> Callable:
    allowed = {str(role) for role in roles}
    allowed.add(Role.SUPERADMIN.value)

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu əməliyyat üçün icazəniz yoxdur. Tələb olunan rollar: {sorted(allowed)}",
            )
        return user

    return checker


def user_organization_id(user: User) -> int | None:
    return user.organization_id
