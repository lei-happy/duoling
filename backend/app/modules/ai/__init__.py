"""
AI 数字员工模块

承载企业数字员工的会话运行时、工具中心、权限隔离与运营管理能力。

子模块说明：
- llm/         : LLM Provider 抽象与 OpenAI 兼容实现
- tools/       : @register_tool 装饰器、注册表、各业务域工具实现
- engine/      : 会话编排器、上下文管理、Prompt 装配、SSE 流式
- security/    : 工具调用权限守卫、高风险动作确认状态机
- models/      : platform/ 跨租户元数据；tenant/ 租户业务数据
- schemas/     : client/ 客户端请求响应；console/ 后台请求响应
- services/    : Service 层业务逻辑
- api/         : client/ 客户端路由；console/ 后台路由
"""
