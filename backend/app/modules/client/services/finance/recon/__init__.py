"""对账一致性核对包

- ``diff_constants``：差异类型 / 严重度 / 处置状态常量。
- ``consistency_checker``：核对器本体，客户侧与承运商侧共用。
- ``workbench_service``：对账工作台的 KPI 与候选池读聚合（直接 import 模块，不在此
  重导出——它依赖 ``linkage`` 包，经包初始化重导出会与 ``linkage`` 形成导入环）。

两侧对账 service 在启动时通过 ``ConsistencyChecker.register_binding`` 注册自己的
表结构（对账主表 + 桥接表 + 列名），核对器据此完成置脏、重挂检测与差异留痕，
无需为每一侧各写一份。
"""

from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
    DiffCandidate,
    ReconBinding,
    ReconCheckReport,
)

__all__ = [
    "ConsistencyChecker",
    "DiffCandidate",
    "ReconBinding",
    "ReconCheckReport",
]
