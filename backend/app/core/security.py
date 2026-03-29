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
    phone: str
    user_type: int           # 用户类型（平台管理员/租户管理员/普通用户/驾驶员）
    tenant_code: Optional[str] = None  # 租户编码（平台管理员为 None）
    roles: list[str] = []    # 角色编码列表


class RefreshTokenData(BaseModel):
    """Refresh Token 载荷数据"""
    user_id: int
    user_type: int
    tenant_code: Optional[str] = None
    token_type: str = "refresh"


class TokenResponse(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int          # access_token 过期时间（秒）


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


def create_refresh_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """
    签发 JWT Refresh Token
    仅包含必要信息，使用独立密钥
    """
    settings = get_settings()
    to_encode = RefreshTokenData(
        user_id=data.user_id,
        user_type=data.user_type,
        tenant_code=data.tenant_code,
    ).model_dump()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
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
        if payload.get("token_type") == "refresh":
            return None
        return TokenData(**payload)
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[RefreshTokenData]:
    """
    解析 JWT Refresh Token
    返回 RefreshTokenData 或 None（token无效时）
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("token_type") != "refresh":
            return None
        return RefreshTokenData(**payload)
    except JWTError:
        return None
