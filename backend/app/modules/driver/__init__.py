"""
驾驶员（user_type=3）H5 / APP / 小程序专用 API 模块

设计要点：
- 与 ``/api/client/*`` 解耦的独立路由树，所有接口在 ``/api/driver/*``
- 复用 ``console.AuthService`` 的登录核心逻辑，仅在企业列表过滤上追加 ``user_type=3``
- 状态推进、签收、装卸等业务**薄层包装** ``client/services/task/*``，确保和企业端
  调度员共享同一份状态机与联动逻辑（task_state_machine / waybill_status_aggregator）
"""
