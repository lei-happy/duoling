"""
通用工具函数
"""

import hashlib
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional


def generate_uuid() -> str:
    """生成 UUID"""
    return str(uuid.uuid4()).replace("-", "")


def generate_tenant_code() -> str:
    """
    生成租户编码
    格式：年份后两位 + 5位自增序号，如 260001
    实际使用时序号由数据库自增控制，此处生成基于时间的临时编码
    """
    now = datetime.now()
    return now.strftime("%y") + generate_uuid()[:4].upper()


def hash_password(password: str) -> str:
    """密码哈希（使用 bcrypt）"""
    import bcrypt
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import bcrypt
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def now_utc() -> datetime:
    """当前 UTC 时间"""
    return datetime.now(timezone.utc)


def md5(text: str) -> str:
    """MD5 哈希"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def to_decimal(val) -> Optional[Decimal]:
    """将值安全地转换为 Decimal，无效值返回 None"""
    if val is None:
        return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError, TypeError):
        return None
