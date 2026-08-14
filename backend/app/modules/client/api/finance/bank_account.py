"""银行账户 API

接口前缀：``/api/client/finance/bank-account``

余额只能通过「校准」接口改（``/calibrate``），编辑接口里没有 balance 字段：账面余额被
人随手改过是查账时最难受的情况，必须留下原因。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.bank_account import (
    BalanceCalibrateRequest,
    BankAccountCreateRequest,
    BankAccountListItem,
    BankAccountOption,
    BankAccountStatusRequest,
    BankAccountUpdateRequest,
)
from app.modules.client.services.finance.cashier.bank_account_service import (
    BankAccountService,
)

router = APIRouter()

_MODULE = "银行账户"
_SVC = BankAccountService


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


@router.get("")
async def page_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    enterpriseId: Optional[int] = None,
    accountType: Optional[int] = None,
    usageScope: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        enterprise_id=enterpriseId, account_type=accountType,
        usage_scope=usageScope, status=status,
    )
    return success(data={
        "list": [BankAccountListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/options")
async def account_options(
    enterpriseId: Optional[int] = None,
    forPay: Optional[bool] = Query(
        default=None, description="true-付款账户 false-收款账户",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """下拉用：启用中的账户，并按收付用途过滤。"""
    rows = await _SVC.options(db, enterprise_id=enterpriseId, for_pay=forPay)
    return success(data=[BankAccountOption.from_model(m).model_dump() for m in rows])


@router.get("/summary")
async def balance_summary(
    enterpriseId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _SVC.balance_summary(db, enterprise_id=enterpriseId))


@router.post("")
@operation_log(module=_MODULE, action="新增账户", description="新增企业银行账户")
async def create_account(
    request: Request,
    data: BankAccountCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    account = await _SVC.create(
        db,
        enterprise_id=data.enterpriseId,
        account_name=data.accountName,
        account_no=data.accountNo,
        bank_name=data.bankName,
        bank_branch=data.bankBranch,
        account_type=data.accountType,
        currency=data.currency,
        usage_scope=data.usageScope,
        balance=data.balance,
        is_default_receive=data.isDefaultReceive,
        is_default_pay=data.isDefaultPay,
        sort_order=data.sortOrder,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(
        data=BankAccountListItem.from_model(account).model_dump(),
        message="账户已添加",
    )


@router.get("/{account_id}")
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    account = await _SVC.get_or_404(db, account_id)
    return success(data=BankAccountListItem.from_model(account).model_dump())


@router.put("/{account_id}")
@operation_log(module=_MODULE, action="编辑账户", description="编辑银行账户信息")
async def update_account(
    request: Request,
    account_id: int,
    data: BankAccountUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    account = await _SVC.update(
        db, account_id,
        account_name=data.accountName,
        account_no=data.accountNo,
        bank_name=data.bankName,
        bank_branch=data.bankBranch,
        account_type=data.accountType,
        currency=data.currency,
        usage_scope=data.usageScope,
        is_default_receive=data.isDefaultReceive,
        is_default_pay=data.isDefaultPay,
        status=data.status,
        sort_order=data.sortOrder,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=BankAccountListItem.from_model(account).model_dump())


@router.put("/{account_id}/status")
@operation_log(module=_MODULE, action="启停账户", description="启用或停用银行账户")
async def set_status(
    request: Request,
    account_id: int,
    data: BankAccountStatusRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    account = await _SVC.set_status(
        db, account_id, data.status, current_user.user_id,
    )
    return success(
        data=BankAccountListItem.from_model(account).model_dump(),
        message=("账户已启用" if account.status == 1 else "账户已停用"),
    )


@router.post("/{account_id}/calibrate")
@operation_log(module=_MODULE, action="余额校准", description="校准银行账户账面余额")
async def calibrate(
    request: Request,
    account_id: int,
    data: BalanceCalibrateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    account = await _SVC.calibrate(
        db, account_id,
        balance=data.balance, reason=data.reason,
        operator_id=current_user.user_id,
    )
    return success(
        data=BankAccountListItem.from_model(account).model_dump(),
        message="余额已校准，本次调整已记录",
    )


@router.delete("/{account_id}")
@operation_log(module=_MODULE, action="删除账户", description="删除银行账户")
async def delete_account(
    request: Request,
    account_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.soft_delete(db, account_id)
    return success()


@router.get("/{account_id}/events")
async def list_events(
    account_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """账户的资金变动与校准留痕。"""
    events = await _SVC.list_events(db, account_id)
    return success(data=[
        {
            "id": e.id,
            "eventType": e.event_type,
            "occurredAmount": (
                float(e.occurred_amount) if e.occurred_amount is not None else None
            ),
            "operatorId": e.operator_id,
            "operatorName": e.operator_name,
            "reason": e.reason,
            "payload": e.payload_snapshot,
            "eventTime": e.event_time,
        }
        for e in events
    ])
