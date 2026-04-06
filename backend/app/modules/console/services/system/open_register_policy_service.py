"""
官网自助注册策略（平台配置）
"""

from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.constants.open_register_policy import (
    DEFAULT_TRIAL_DAYS,
    DEFAULT_VERSION_CODE,
    GRANT_TYPE_SELF_REGISTER_TRIAL,
    KEY_OPEN_REGISTER_DEFAULT_VERSION_CODE,
    KEY_OPEN_REGISTER_TRIAL_DAYS,
)
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.system.platform_setting import PlatformSetting


class OpenRegisterPolicyService:
    """自助注册默认版本与试用天数"""

    @staticmethod
    async def _get_value(db: AsyncSession, key: str) -> Optional[str]:
        r = await db.execute(
            select(PlatformSetting.config_value).where(
                PlatformSetting.config_key == key,
                PlatformSetting.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        return row

    @staticmethod
    async def _set_value(
        db: AsyncSession, key: str, value: str, remark: Optional[str] = None
    ) -> None:
        r = await db.execute(
            select(PlatformSetting).where(
                PlatformSetting.config_key == key,
                PlatformSetting.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row:
            row.config_value = value
            if remark is not None:
                row.remark = remark
        else:
            db.add(
                PlatformSetting(
                    config_key=key,
                    config_value=value,
                    remark=remark,
                )
            )
        await db.flush()

    @staticmethod
    async def get_policy_raw(db: AsyncSession) -> Tuple[str, int]:
        """返回 (version_code, trial_days)，trial_days=0 表示不限期"""
        vc = await OpenRegisterPolicyService._get_value(
            db, KEY_OPEN_REGISTER_DEFAULT_VERSION_CODE
        )
        version_code = (vc or "").strip() or DEFAULT_VERSION_CODE
        days_s = await OpenRegisterPolicyService._get_value(
            db, KEY_OPEN_REGISTER_TRIAL_DAYS
        )
        trial_days = DEFAULT_TRIAL_DAYS
        if days_s is not None and str(days_s).strip() != "":
            try:
                trial_days = max(0, int(str(days_s).strip()))
            except ValueError:
                trial_days = DEFAULT_TRIAL_DAYS
        return version_code, trial_days

    @staticmethod
    async def get_resolved_version(
        db: AsyncSession, version_code: str
    ) -> ProductVersion:
        """解析启用中的产品版本，不存在则回退 basic"""
        r = await db.execute(
            select(ProductVersion).where(
                ProductVersion.version_code == version_code,
                ProductVersion.status == 1,
                ProductVersion.is_deleted == 0,
            )
        )
        v = r.scalar_one_or_none()
        if v:
            return v
        r2 = await db.execute(
            select(ProductVersion).where(
                ProductVersion.version_code == DEFAULT_VERSION_CODE,
                ProductVersion.status == 1,
                ProductVersion.is_deleted == 0,
            )
        )
        fb = r2.scalar_one_or_none()
        if fb:
            return fb
        raise BizException("未找到可用的产品版本（basic），请先维护 sys_product_version")

    @staticmethod
    async def save_policy(
        db: AsyncSession, version_code: str, trial_days: int
    ) -> None:
        if trial_days < 0 or trial_days > 3650:
            raise BizException("试用天数需在 0～3650 之间（0 表示不限期）")
        code = (version_code or "").strip()
        if not code:
            raise BizException("请选择版本编码")
        r = await db.execute(
            select(ProductVersion).where(
                ProductVersion.version_code == code,
                ProductVersion.status == 1,
                ProductVersion.is_deleted == 0,
            )
        )
        if not r.scalar_one_or_none():
            raise BizException("版本编码不存在或已停用")

        await OpenRegisterPolicyService._set_value(
            db,
            KEY_OPEN_REGISTER_DEFAULT_VERSION_CODE,
            code,
            "官网自助注册默认开通的产品版本编码",
        )
        await OpenRegisterPolicyService._set_value(
            db,
            KEY_OPEN_REGISTER_TRIAL_DAYS,
            str(trial_days),
            "官网自助注册试用天数，0 表示不限期",
        )

    @staticmethod
    def grant_type_for_self_register() -> str:
        return GRANT_TYPE_SELF_REGISTER_TRIAL
