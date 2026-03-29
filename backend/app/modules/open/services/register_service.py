"""
企业自助注册服务（异步任务 + 进度）
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import BackgroundTasks
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.common.exceptions import BizException
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.schemas.tenant.tenant import TenantCreate
from app.modules.console.services.tenant.tenant_service import TenantService
from app.modules.open.models.open_register_task import OpenRegisterTask
from app.modules.open.schemas.register import (
    RegisterRequest,
    RegisterResponse,
    RegisterStartResponse,
    RegisterProgressOut,
)


class RegisterService:
    """企业自助注册服务"""

    _TASK_TTL_MINUTES = 30

    @staticmethod
    async def _update_task_fields(task_id: str, **fields) -> None:
        factory = db_manager._platform_session_factory
        if not factory:
            return
        if "updated_at" not in fields:
            fields["updated_at"] = datetime.now()
        async with factory() as session:
            await session.execute(
                update(OpenRegisterTask)
                .where(OpenRegisterTask.id == task_id)
                .values(**fields)
            )
            await session.commit()

    @staticmethod
    def _build_response(data: RegisterRequest, tenant, is_existing_user: bool) -> RegisterResponse:
        if is_existing_user:
            message = "注册成功，该手机号已注册过账号，请使用已有密码登录"
        else:
            message = "注册成功，默认密码为 123456，首次登录后请修改密码"
        return RegisterResponse(
            tenant_code=tenant.tenant_code,
            tenant_name=tenant.tenant_name,
            admin_phone=data.contact_phone,
            is_existing_user=is_existing_user,
            message=message,
        )

    @staticmethod
    async def start_register(
        db: AsyncSession,
        data: RegisterRequest,
        background_tasks: BackgroundTasks,
    ) -> RegisterStartResponse:
        """校验后创建任务并投递后台执行"""
        existing = await db.execute(
            select(Tenant).where(
                Tenant.tenant_name == data.tenant_name,
                Tenant.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException("企业名称已存在")

        one_hour_ago = datetime.now() - timedelta(hours=1)
        dup_task = await db.execute(
            select(OpenRegisterTask)
            .where(
                OpenRegisterTask.contact_phone == data.contact_phone,
                OpenRegisterTask.status.in_(["pending", "running"]),
                OpenRegisterTask.is_deleted == 0,
                OpenRegisterTask.created_at >= one_hour_ago,
            )
            .order_by(OpenRegisterTask.created_at.desc())
            .limit(1)
        )
        existing_task = dup_task.scalar_one_or_none()
        if existing_task:
            logger.info(
                f"同一手机号存在进行中注册任务，返回已有 task_id={existing_task.id}"
            )
            return RegisterStartResponse(task_id=existing_task.id)

        task_id = str(uuid.uuid4())
        task = OpenRegisterTask(
            id=task_id,
            status="pending",
            current_step="queued",
            message="即将开始初始化企业基础数据…",
            percent=0,
            contact_phone=data.contact_phone,
            payload_json=data.model_dump_json(),
        )
        db.add(task)
        await db.flush()
        # 必须先提交：BackgroundTasks 会在依赖注入里的 session.commit() 之前执行，
        # 否则后台任务与首次轮询都读不到未提交的行（任务不存在 / 永远 pending）。
        await db.commit()

        background_tasks.add_task(RegisterService.run_register_job, task_id)
        return RegisterStartResponse(task_id=task_id)

    @staticmethod
    async def run_register_job(task_id: str) -> None:
        """后台执行开户（独立 Session）"""
        factory = db_manager._platform_session_factory
        if not factory:
            logger.error("平台库未初始化，无法执行注册任务")
            return

        data: Optional[RegisterRequest] = None
        try:
            async with factory() as session:
                tr = await session.execute(
                    select(OpenRegisterTask).where(
                        OpenRegisterTask.id == task_id,
                        OpenRegisterTask.is_deleted == 0,
                    )
                )
                task = tr.scalar_one_or_none()
                if not task or task.is_deleted:
                    logger.error(
                        "注册后台任务未读到任务行 task_id=%s（"
                        "请确认 POST /register 在调度后台前已 commit）",
                        task_id,
                    )
                    return
                if task.status in ("success", "failed"):
                    return
                data = RegisterRequest.model_validate_json(task.payload_json)
                task.status = "running"
                task.current_step = "start"
                task.message = "正在处理…"
                task.percent = 5
                await session.commit()
        except Exception as e:
            logger.exception(f"注册任务启动失败 task_id={task_id}: {e}")
            await RegisterService._update_task_fields(
                task_id,
                status="failed",
                error_message=str(e)[:2000],
                message="开户失败",
                percent=0,
            )
            return

        if data is None:
            return

        async def on_progress(step_key: str, message: str, percent: int) -> None:
            await RegisterService._update_task_fields(
                task_id,
                status="running",
                current_step=step_key,
                message=message,
                percent=percent,
            )

        source_channel = "referral" if data.referrer_code else "website"
        tenant_data = TenantCreate(
            tenantName=data.tenant_name,
            contactPerson=data.contact_person,
            contactPhone=data.contact_phone,
            contactEmail=data.contact_email,
            province=data.province,
            city=data.city,
            remark="官网自助注册 - 免费版",
            sourceChannel=source_channel,
            referrerCode=data.referrer_code,
        )

        try:
            async with factory() as db:
                tenant, is_existing_user = await TenantService.create_tenant(
                    db, tenant_data, on_progress=on_progress
                )
                tenant.status = 1
                await db.flush()

                logger.info(
                    f"企业自助注册成功: {tenant.tenant_code} - {data.tenant_name} "
                    f"(渠道: {source_channel}, 已有用户: {is_existing_user})"
                )

                result = RegisterService._build_response(data, tenant, is_existing_user)
                await db.commit()

            await RegisterService._update_task_fields(
                task_id,
                status="success",
                current_step="done",
                message="注册成功",
                percent=100,
                result_json=result.model_dump_json(),
                error_message=None,
            )
        except BizException as e:
            logger.warning(f"注册任务业务失败 task_id={task_id}: {e.message}")
            await RegisterService._update_task_fields(
                task_id,
                status="failed",
                error_message=e.message,
                message="开户失败",
                percent=0,
            )
        except Exception as e:
            logger.exception(f"注册任务异常 task_id={task_id}: {e}")
            await RegisterService._update_task_fields(
                task_id,
                status="failed",
                error_message=str(e)[:2000],
                message="开户失败",
                percent=0,
            )

    @staticmethod
    async def get_progress(db: AsyncSession, task_id: str) -> RegisterProgressOut:
        """查询注册任务进度"""
        try:
            uuid.UUID(task_id)
        except ValueError:
            raise BizException("无效的任务 ID")

        result = await db.execute(
            select(OpenRegisterTask).where(
                OpenRegisterTask.id == task_id,
                OpenRegisterTask.is_deleted == 0,
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            raise BizException("任务不存在")

        expire_before = datetime.now() - timedelta(
            minutes=RegisterService._TASK_TTL_MINUTES
        )
        if task.status in ("pending", "running") and task.created_at < expire_before:
            return RegisterProgressOut(
                status="failed",
                current_step=task.current_step,
                message="任务已超时，请重新提交注册",
                percent=task.percent,
                error_message="timeout",
            )

        out = RegisterProgressOut(
            status=task.status,
            current_step=task.current_step,
            message=task.message,
            percent=task.percent,
            error_message=task.error_message,
        )
        if task.status == "success" and task.result_json:
            out.result = RegisterResponse.model_validate_json(task.result_json)
        return out
