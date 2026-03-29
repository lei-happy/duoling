"""
短信验证码服务
负责验证码的生成、落表、校验，以及通过验证码重置密码
"""

import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.common.exceptions import BizException
from app.common.sms_client import AliyunSmsClient
from app.common.utils import hash_password
from app.core.config import get_settings
from app.core.database import db_manager
from app.modules.console.models.sms.sms_code import SmsCode
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.client.models.user.biz_user import BizUser

SMS_CODE_LENGTH = 6
SMS_CODE_EXPIRE_MINUTES = 5
SMS_CODE_RESEND_SECONDS = 60

PURPOSE_LOGIN = 1
PURPOSE_RESET_PASSWORD = 2


class SmsService:
    """短信验证码服务"""

    @staticmethod
    async def _check_phone_exists(
        db: AsyncSession, phone: str, purpose: int, app_type: str,
    ) -> None:
        """
        校验手机号是否存在，根据 app_type 和 purpose 使用不同策略：
        - console + 登录: sys_user WHERE user_type=0
        - client + 登录: sys_user + 至少一条有效的 sys_user_tenant
        - 重置密码: sys_user 存在即可
        """
        if purpose == PURPOSE_LOGIN and app_type == "console":
            result = await db.execute(
                select(User).where(
                    User.phone == phone,
                    User.user_type == 0,
                    User.is_deleted == 0,
                )
            )
            if not result.scalar_one_or_none():
                raise BizException("该手机号未注册")
        elif purpose == PURPOSE_LOGIN and app_type == "client":
            result = await db.execute(
                select(User).where(
                    User.phone == phone,
                    User.is_deleted == 0,
                )
            )
            user = result.scalar_one_or_none()
            if not user:
                raise BizException("该手机号未注册")
            ut_result = await db.execute(
                select(UserTenant).where(
                    UserTenant.user_id == user.id,
                    UserTenant.status == 1,
                    UserTenant.is_deleted == 0,
                )
            )
            if not ut_result.first():
                raise BizException("该手机号未关联任何企业")
        else:
            result = await db.execute(
                select(User).where(
                    User.phone == phone,
                    User.is_deleted == 0,
                )
            )
            if not result.scalar_one_or_none():
                raise BizException("该手机号尚未注册")

    @staticmethod
    async def send_code(
        db: AsyncSession,
        phone: str,
        purpose: int,
        app_type: str = "client",
        client_ip: Optional[str] = None,
    ) -> dict:
        """
        生成并存储验证码，通过阿里云短信认证服务发送到用户手机。
        SMS_ENABLED 关闭时仅落表不发送，返回明文验证码便于开发调试。
        """
        if purpose not in (PURPOSE_LOGIN, PURPOSE_RESET_PASSWORD):
            raise BizException("无效的验证码用途")

        await SmsService._check_phone_exists(db, phone, purpose, app_type)

        last = await db.execute(
            select(SmsCode).where(
                SmsCode.phone == phone,
                SmsCode.purpose == purpose,
                SmsCode.status == 0,
            ).order_by(SmsCode.created_at.desc()).limit(1)
        )
        last_record = last.scalar_one_or_none()
        if last_record:
            elapsed = (datetime.now() - last_record.created_at).total_seconds()
            if elapsed < SMS_CODE_RESEND_SECONDS:
                remaining = int(SMS_CODE_RESEND_SECONDS - elapsed)
                raise BizException(f"发送过于频繁，请 {remaining} 秒后再试")

        code = "".join([str(random.randint(0, 9)) for _ in range(SMS_CODE_LENGTH)])
        expire_at = datetime.now() + timedelta(minutes=SMS_CODE_EXPIRE_MINUTES)

        sms_code = SmsCode(
            phone=phone,
            code=code,
            purpose=purpose,
            status=0,
            expire_at=expire_at,
            client_ip=client_ip,
        )
        db.add(sms_code)
        await db.flush()

        purpose_text = "登录" if purpose == PURPOSE_LOGIN else "重置密码"
        logger.info(
            f"验证码已生成 | phone={phone} purpose={purpose_text} "
            f"code={code} expire_at={expire_at}"
        )

        settings = get_settings()
        if settings.ALIYUN_SMS_ENABLED:
            try:
                AliyunSmsClient.send_verify_code(phone, code, purpose)
            except Exception as e:
                logger.error(f"短信发送失败，验证码已落表 | phone={phone} error={e}")
                raise BizException("短信发送失败，请稍后重试")
            return {"message": "验证码已发送"}
        else:
            return {"message": "验证码已发送", "code": code}

    @staticmethod
    async def verify_code(
        db: AsyncSession,
        phone: str,
        code: str,
        purpose: int,
    ) -> SmsCode:
        """
        校验验证码：匹配手机号 + 验证码 + 用途，检查有效期和使用状态。
        校验通过后标记为已使用。
        """
        result = await db.execute(
            select(SmsCode).where(
                and_(
                    SmsCode.phone == phone,
                    SmsCode.code == code,
                    SmsCode.purpose == purpose,
                    SmsCode.status == 0,
                )
            ).order_by(SmsCode.created_at.desc()).limit(1)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise BizException("验证码错误或已失效")

        if datetime.now() > record.expire_at:
            record.status = 2
            await db.flush()
            raise BizException("验证码已过期，请重新获取")

        record.status = 1
        await db.flush()
        return record

    @staticmethod
    async def reset_password_by_sms(
        platform_db: AsyncSession,
        phone: str,
        code: str,
        new_password: str,
    ) -> None:
        """
        通过短信验证码重置密码。
        1. 校验验证码
        2. 更新 sys_user.password
        3. 反向同步所有关联租户库的 biz_user.password
        """
        await SmsService.verify_code(
            platform_db, phone, code, PURPOSE_RESET_PASSWORD
        )

        result = await platform_db.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")

        hashed = hash_password(new_password)
        user.password = hashed
        user.force_change_pwd = 0
        await platform_db.flush()

        tenant_result = await platform_db.execute(
            select(UserTenant.tenant_code).where(
                UserTenant.user_id == user.id,
                UserTenant.is_deleted == 0,
            )
        )
        tenant_codes = [row[0] for row in tenant_result.all()]

        for tc in tenant_codes:
            try:
                async for tenant_db in db_manager.get_tenant_session(tc):
                    biz_result = await tenant_db.execute(
                        select(BizUser).where(
                            BizUser.phone == phone,
                            BizUser.is_deleted == 0,
                        )
                    )
                    biz_user = biz_result.scalar_one_or_none()
                    if biz_user:
                        biz_user.password = hashed
                        await tenant_db.flush()
                    logger.info(f"密码已同步至租户库: {tc}")
            except Exception as e:
                logger.warning(f"同步租户 {tc} 密码失败: {e}")

        logger.info(f"密码重置成功 | phone={phone} synced_tenants={len(tenant_codes)}")
