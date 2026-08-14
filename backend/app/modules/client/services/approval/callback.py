"""审批中心 - 业务回调注册表

项目无全局事件总线，模块间通信靠 Service 直调。为避免引擎反向依赖各业务模块，
采用「回调注册表」模式（与 AI 工具注册思路一致）：

  - 业务模块实现 ApprovalCallback 协议并在启动时注册到 registry
  - 引擎在实例终态时按 biz_type 查表回调，引擎不 import 任何业务模块

详见《08.审批中心/02.业务接入规范》§三。
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, runtime_checkable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class ApprovalCallback(Protocol):
    """业务模块实现并注册的回调协议。

    引擎在实例终态时**同事务**调用对应方法；回调内只用传入的 db，
    禁止自行 commit / 新开事务；实现需幂等。
    """

    biz_type: str

    async def build_summary(self, db: AsyncSession, biz_id: int) -> Dict[str, Any]:
        """（可选）由业务侧构建展示摘要快照。"""
        ...

    async def on_approved(self, db: AsyncSession, instance: Any) -> None:
        """审批通过：业务侧推进自身状态机。"""
        ...

    async def on_rejected(self, db: AsyncSession, instance: Any) -> None:
        """审批拒绝：业务侧退回。"""
        ...

    async def on_cancelled(self, db: AsyncSession, instance: Any) -> None:
        """发起人撤回：业务侧恢复可编辑。"""
        ...


class _Registry:
    def __init__(self) -> None:
        self._callbacks: Dict[str, ApprovalCallback] = {}

    def register(self, callback: ApprovalCallback) -> None:
        biz_type = getattr(callback, "biz_type", None)
        if not biz_type:
            raise ValueError("ApprovalCallback 必须声明 biz_type")
        if biz_type in self._callbacks:
            logger.warning(f"[审批中心] biz_type={biz_type} 的回调被重复注册，后者覆盖前者")
        self._callbacks[biz_type] = callback

    def get(self, biz_type: str) -> Optional[ApprovalCallback]:
        return self._callbacks.get(biz_type)

    def all(self) -> Dict[str, ApprovalCallback]:
        return dict(self._callbacks)


_registry = _Registry()


def register_callback(callback: ApprovalCallback) -> None:
    _registry.register(callback)


def get_callback(biz_type: str) -> Optional[ApprovalCallback]:
    return _registry.get(biz_type)


def get_registry() -> _Registry:
    return _registry
