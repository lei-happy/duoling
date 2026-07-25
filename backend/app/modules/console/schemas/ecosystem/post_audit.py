"""运营端审核入参 Schemas（camelCase，对齐前端）

这一层只做「形状校验」：必填、长度、取值范围。业务判定（这条挂牌在不在待审
队列里、这家企业够不够资格免审）全部留给 Service——那些规则要在批量、
定时任务、事件回调等没有 HTTP 入口的路径上同样生效。

驳回原因编码的合法性也放 Service（``_resolve_reject_reason``）：
选了「其他」必须补充说明这条规则和编码取值是同一件事的两面，
拆到两层会出现「Schema 放过、Service 拦下」的错位提示。
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.console.models.ecosystem.constants import MAX_BATCH_APPROVE


class AuditApproveRequest(BaseModel):
    """审核通过

    ``remark`` 是给平台内部留痕的，不展示给租户（通过时租户只需要知道
    「已上架」，不需要读运营的备注）。
    """

    remark: Optional[str] = Field(None, max_length=255)


class AuditRejectRequest(BaseModel):
    """驳回

    ``reason`` 会**原样展示给租户**，所以留空时由后端套用原因模板，
    而不是把「信息不真实」这种没有下一步的短语甩过去。
    """

    reasonCode: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=500)


class BatchApproveRequest(BaseModel):
    """批量通过"""

    postIds: List[int] = Field(..., min_length=1, max_length=MAX_BATCH_APPROVE)


class ForceDelistRequest(BaseModel):
    """强制下架

    ``reason`` 必填且会展示给租户：强制下架是平台单方面的处置，
    不给理由租户只会反复重新发布同样的内容。
    ``revokeWhitelist`` 默认 True——下架一条却留着免审，下一条照样直通上架。
    """

    reason: str = Field(..., min_length=1, max_length=500)
    reasonCode: Optional[int] = Field(None, gt=0)
    revokeWhitelist: bool = True


class SpotCheckPassRequest(BaseModel):
    """抽检通过"""

    remark: Optional[str] = Field(None, max_length=255)


class SpotCheckFailRequest(BaseModel):
    """抽检不通过"""

    reason: str = Field(..., min_length=1, max_length=500)
    reasonCode: Optional[int] = Field(None, gt=0)


class WhitelistGrantRequest(BaseModel):
    """授予免审白名单"""

    tenantCode: str = Field(..., min_length=1, max_length=32)
    remark: Optional[str] = Field(None, max_length=255)


class WhitelistRevokeRequest(BaseModel):
    """移出免审白名单

    原因必填：30 天后运营看到一条「曾被移出」却不知道当初发生了什么，
    既无法判断该不该恢复，也无法向租户解释。
    """

    reason: str = Field(..., min_length=1, max_length=255)
