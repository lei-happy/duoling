"""
证照监控 - 预警查询/处理服务（供 API 调用）
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.compliance.compliance_alert import BizComplianceAlert
from app.modules.client.schemas.compliance.compliance_alert import (
    ComplianceAlertOut,
    ComplianceAlertSummary,
)


class ComplianceAlertService:
    """证照监控预警查询/处理"""

    @staticmethod
    async def page(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        subject_type: Optional[str] = None,
        doc_type: Optional[str] = None,
        level: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        conditions = [BizComplianceAlert.is_deleted == 0]
        # 默认只看待处理；显式传 status 则按传入过滤
        if status:
            conditions.append(BizComplianceAlert.status == status)
        else:
            conditions.append(BizComplianceAlert.status == "open")
        if subject_type:
            conditions.append(BizComplianceAlert.subject_type == subject_type)
        if doc_type:
            conditions.append(BizComplianceAlert.doc_type == doc_type)
        if level:
            conditions.append(BizComplianceAlert.level == level)
        if keyword:
            like = f"%{keyword}%"
            conditions.append(BizComplianceAlert.subject_name.like(like))

        total = (
            await db.execute(
                select(func.count())
                .select_from(BizComplianceAlert)
                .where(*conditions)
            )
        ).scalar() or 0

        rows = (
            await db.execute(
                select(BizComplianceAlert)
                .where(*conditions)
                # 已过期优先、其次按剩余天数升序
                .order_by(BizComplianceAlert.days_left.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()

        return {
            "list": [ComplianceAlertOut.from_model(r).model_dump() for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def summary(db: AsyncSession) -> dict:
        """合规看板汇总（仅统计 open 状态）"""
        rows = (
            await db.execute(
                select(
                    BizComplianceAlert.level,
                    BizComplianceAlert.subject_type,
                    BizComplianceAlert.doc_type,
                    func.count().label("cnt"),
                )
                .where(
                    BizComplianceAlert.is_deleted == 0,
                    BizComplianceAlert.status == "open",
                )
                .group_by(
                    BizComplianceAlert.level,
                    BizComplianceAlert.subject_type,
                    BizComplianceAlert.doc_type,
                )
            )
        ).all()

        summary = ComplianceAlertSummary()
        by_subject: dict = {}
        by_doc: dict = {}
        for level, subject_type, doc_type, cnt in rows:
            summary.total += cnt
            if level == "expired":
                summary.expired += cnt
            elif level == "critical":
                summary.critical += cnt
            elif level == "warning":
                summary.warning += cnt
            by_subject[subject_type] = by_subject.get(subject_type, 0) + cnt
            by_doc[doc_type] = by_doc.get(doc_type, 0) + cnt
        summary.bySubjectType = by_subject
        summary.byDocType = by_doc
        return summary.model_dump()

    @staticmethod
    async def dismiss(
        db: AsyncSession, *, alert_id: int, operator_user_id: int
    ) -> dict:
        alert = (
            await db.execute(
                select(BizComplianceAlert).where(
                    BizComplianceAlert.id == alert_id,
                    BizComplianceAlert.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if alert is None:
            raise BizException("预警不存在或已删除")
        alert.status = "dismissed"
        alert.dismissed_user_id = operator_user_id
        alert.dismissed_at = datetime.now()
        await db.commit()
        return ComplianceAlertOut.from_model(alert).model_dump()
