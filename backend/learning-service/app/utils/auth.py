from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

security = HTTPBearer()


class CurrentUser:
    def __init__(
        self,
        user_id: str,
        role: str,
        exp: datetime,
    ):
        self.user_id = user_id
        self.role = role
        self.exp = exp


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        exp: Optional[int] = payload.get("exp")

        if user_id is None or role is None or exp is None:
            raise credentials_exception

        return CurrentUser(
            user_id=user_id,
            role=role,
            exp=datetime.fromtimestamp(exp),
        )
    except JWTError:
        raise credentials_exception


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[CurrentUser]:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        exp: Optional[int] = payload.get("exp")

        if user_id is None or role is None or exp is None:
            return None

        return CurrentUser(
            user_id=user_id,
            role=role,
            exp=datetime.fromtimestamp(exp),
        )
    except JWTError:
        return None


def require_roles(*roles: str):
    async def role_checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return role_checker


require_teacher = require_roles("teacher", "admin")
require_student = require_roles("student", "teacher", "admin")
require_admin = require_roles("admin")
