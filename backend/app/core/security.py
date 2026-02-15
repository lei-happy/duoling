"""
认证鉴权模块
JWT Token 签发与校验
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings


class TokenData(BaseModel):
    """Token 载荷数据"""
    user_id: int
    username: str
    user_type: int           # 用户类型（平台管理员/租户管理员/普通用户/驾驶员）
    tenant_code: Optional[str] = None  # 租户编码（平台管理员为 None）
    roles: list[str] = []    # 角色编码列表


class TokenResponse(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int          # 过期时间（秒）


def create_access_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """
    签发 JWT Access Token
    """
    settings = get_settings()
    to_encode = data.model_dump()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    解析 JWT Access Token
    返回 TokenData 或 None（token无效时）
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenData(**payload)
    except JWTError:
        return None
