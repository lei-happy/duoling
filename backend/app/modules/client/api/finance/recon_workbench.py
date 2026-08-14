"""对账工作台 API（文档 08 §3.2）

接口前缀：``/api/client/finance/recon-workbench``

只读聚合。工作台不做单据 CRUD：候选池选完客户后跳到客户对账单台账建单，差异处置
调的也是对账单下的差异接口——这里只负责「今天该干哪几件事」。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.recon_diff import ReconDiffOut
from app.modules.client.services.finance.customer.customer_recon_service import (
    CustomerReconService,
)
from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
)
from app.modules.client.services.finance.recon.workbench_service import (
    ReconWorkbenchService as Svc,
)

router = APIRouter()


@router.get("/summary")
async def workbench_summary(
    enterpriseId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """KPI 卡与四个 Tab 的角标，一次给全。"""
    return success(data=await Svc.summary(db, enterprise_id=enterpriseId))


@router.get("/pending-waybills")
async def pending_waybills(
    keyword: Optional[str] = None,
    enterpriseId: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=300),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """候选池 Tab：待对账运单按客户归堆。"""
    rows = await Svc.pending_waybill_groups(
        db, keyword=keyword, enterprise_id=enterpriseId, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("/diffs")
async def pending_diffs(
    onlyBlocking: bool = False,
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """差异待办 Tab：跨对账单的未处置差异，带上所属对账单编号便于跳转。"""
    rows = await ConsistencyChecker.list_diffs(
        db,
        recon_kind=Svc.recon_kind,
        only_open=True,
        severity=2 if onlyBlocking else None,
        limit=limit,
    )
    recon_ids = {int(x.recon_id) for x in rows if x.recon_id}
    doc_no_map = await CustomerReconService.doc_no_map(db, recon_ids)
    out = []
    for x in rows:
        item = ReconDiffOut.from_model(x).model_dump()
        item["reconDocNo"] = doc_no_map.get(int(x.recon_id or 0))
        out.append(item)
    return success(data={"list": out, "count": len(out)})
