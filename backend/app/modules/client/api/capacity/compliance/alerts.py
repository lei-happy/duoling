"""
证照监控 - 预警 API（运力宝核心能力）

  - GET  /            分页查询预警（默认只看待处理 open）
  - GET  /summary     合规看板汇总
  - PUT  /{id}/dismiss 忽略预警

预警数据由独立的「证照监控 worker」周期扫描生成，本接口只读结果 + 处理状态。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_code, get_tenant_db
from app.core.database import db_manager
from app.core.security import TokenData
from app.modules.client.services.compliance.compliance_alert_service import (
    ComplianceAlertService,
)

router = APIRouter()


async def _ensure_alert_table(tenant_code: str = Depends(get_tenant_code)) -> None:
    """老租户库可能缺 biz_compliance_alert，首次访问时幂等补建。"""
    await db_manager.ensure_tenant_tables(tenant_code, ["biz_compliance_alert"])


@router.get("")
async def page_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    subjectType: Optional[str] = None,
    docType: Optional[str] = None,
    level: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _table: None = Depends(_ensure_alert_table),
    _=Depends(get_current_user),
):
    """证照到期预警分页列表"""
    data = await ComplianceAlertService.page(
        db,
        page=page,
        page_size=page_size,
        subject_type=subjectType,
        doc_type=docType,
        level=level,
        status=status,
        keyword=keyword,
    )
    return success(data=data)


@router.get("/summary")
async def alert_summary(
    db: AsyncSession = Depends(get_tenant_db),
    _table: None = Depends(_ensure_alert_table),
    _=Depends(get_current_user),
):
    """合规看板汇总（按级别/主体/证照分组的待处理数量）"""
    data = await ComplianceAlertService.summary(db)
    return success(data=data)


@router.put("/{alert_id}/dismiss")
async def dismiss_alert(
    request: Request,
    alert_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _table: None = Depends(_ensure_alert_table),
):
    """忽略一条预警（人工确认，扫描不再覆盖其状态）"""
    data = await ComplianceAlertService.dismiss(
        db, alert_id=alert_id, operator_user_id=current_user.user_id
    )
    return success(data=data)
