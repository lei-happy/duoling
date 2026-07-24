"""接入应用管理服务（平台库）"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.open_platform.models.platform.open_app import OpenApp
from app.modules.open_platform.models.platform.open_credential import OpenCredential


class AppService:
    @staticmethod
    async def list_apps(db: AsyncSession, tenant_code: str) -> list[dict]:
        rows = (
            await db.execute(
                select(OpenApp)
                .where(OpenApp.tenant_code == tenant_code, OpenApp.is_deleted == 0)
                .order_by(OpenApp.id.desc())
            )
        ).scalars().all()

        result = []
        for app in rows:
            cnt = await db.scalar(
                select(func.count())
                .select_from(OpenCredential)
                .where(
                    OpenCredential.app_id == app.id,
                    OpenCredential.is_deleted == 0,
                    OpenCredential.status != "revoked",
                )
            )
            result.append(
                {
                    "id": app.id,
                    "name": app.name,
                    "description": app.description,
                    "status": app.status,
                    "credential_count": int(cnt or 0),
                    "created_at": app.created_at,
                }
            )
        return result

    @staticmethod
    async def get_app(db: AsyncSession, tenant_code: str, app_id: int) -> OpenApp:
        app = await db.scalar(
            select(OpenApp).where(
                OpenApp.id == app_id,
                OpenApp.tenant_code == tenant_code,
                OpenApp.is_deleted == 0,
            )
        )
        if not app:
            raise BizException("接入应用不存在")
        return app

    @staticmethod
    async def create_app(
        db: AsyncSession, tenant_code: str, name: str, description: str, user_id: Optional[int]
    ) -> OpenApp:
        app = OpenApp(
            tenant_code=tenant_code,
            name=name,
            description=description or "",
            status="enabled",
            created_by=user_id,
        )
        db.add(app)
        await db.flush()
        return app

    @staticmethod
    async def update_app(
        db: AsyncSession,
        tenant_code: str,
        app_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> OpenApp:
        app = await AppService.get_app(db, tenant_code, app_id)
        if name is not None:
            app.name = name
        if description is not None:
            app.description = description
        if status is not None:
            if status not in ("enabled", "disabled"):
                raise BizException("应用状态取值不合法")
            app.status = status
        await db.flush()
        return app
