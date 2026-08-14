"""业务 <-> 财务联动闸口（候选生成、锁定编排、置脏中转）

业务模块只依赖本包，不直接 import 财务内部实现：

- ``waybill_to_finance``：运单 → 客户应收（候选池、签收台数口径、编辑拦截、置脏）
- ``task_to_finance``：任务单 → 承运商对账 / 司机工资（候选池、扣减额口径、互斥）
- ``lock_orchestrator``：财务终态 → 业务对象 ``is_locked`` 编排
- ``driver_fund_orchestrator``：预付单 ↔ 驾驶员资金账户
"""
