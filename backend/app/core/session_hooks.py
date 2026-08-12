"""
租户会话提交前钩子

某些派生数据必须与主业务改动**在同一事务里**保持一致，又不应该让每个接口
都记得手动调用一次 —— 典型例子是任务预警：调度员点了派车，工作台的阶段卡
就该立刻正确，而派车的入口散落在企业端、驾驶员端、承运商端十几个接口里。

这里提供一个极薄的注册表：业务模块把「提交前要跑的收尾动作」注册进来，
``db_manager.get_tenant_session`` 在 commit 之前统一执行。

约定：
- 钩子必须是幂等的、无副作用外泄的，且在没有相关改动时应尽快返回。
- 钩子异常不吞：它与主业务同事务，静默失败只会留下不一致的数据。
"""

from __future__ import annotations

from typing import Awaitable, Callable, List

from sqlalchemy.ext.asyncio import AsyncSession

PreCommitHook = Callable[[AsyncSession], Awaitable[None]]

_PRE_COMMIT_HOOKS: List[PreCommitHook] = []


def register_pre_commit_hook(hook: PreCommitHook) -> None:
    """注册租户会话提交前钩子（重复注册同一函数会被忽略）。"""
    if hook not in _PRE_COMMIT_HOOKS:
        _PRE_COMMIT_HOOKS.append(hook)


async def run_pre_commit_hooks(session: AsyncSession) -> None:
    for hook in _PRE_COMMIT_HOOKS:
        await hook(session)
