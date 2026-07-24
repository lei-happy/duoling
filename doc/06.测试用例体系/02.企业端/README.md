# 企业端（Client Web）测试说明

> **端代码**：`CLI` ｜ **缺陷前缀**：`BUG-CLI-xxx`
> **后端范围**：`backend/app/modules/client/**` + `backend/app/modules/ai/**`（client 部分）
> **前端范围**：`frontend/client`
> **测试脚本**：`backend/tests/client/**`
> **测试租户**：`1001`（租户库 `zt_biz_1001_ci`），平台库 `zt_platform_ci`

## 一、范围与分工

企业端是租户业务全域，按 8 个子领域组织用例文档：

| # | 子领域文档 | 覆盖模块 |
|---|---|---|
| 01 | [账号与组织](./01.账号与组织.md) | auth、user、role、organization、business_entity、login_record |
| 02 | [资源管理](./02.资源管理.md) | self_capacity（vehicle/driver/trailer/route/account/fund）、social_capacity、carrier_capacity、compliance |
| 03 | [计费引擎](./03.计费引擎.md) | freight_contract/rate/engine、carrier_*、cost_policy/rule/engine、task_cost、calculate、route |
| 04 | [运营调度与运单](./04.运营调度与运单.md) | task、task_finance、waybill、状态机联动 |
| 05 | [合作伙伴](./05.合作伙伴.md) | partner（customer、carrier、carrier_inbound） |
| 06 | [审批中心](./06.审批中心.md) | approval（flow、center） |
| 07 | [工作台与洞察](./07.工作台与洞察.md) | workbench（activities、todo）、insight（cockpit、profit） |
| 08 | [AI 数字人](./08.AI数字人.md) | ai/client（chat、session、employee、file）+ security 脱敏 |
| 13 | [任务费用单发起节点](./13.任务费用单发起节点.md) | task_finance 发起节点配置（finance_stage_rules、system_config 懒补齐） |
| 14 | [开放平台](./14.开放平台.md) | open_platform（接入应用、API 密钥、MCP 配置、能力目录、调用审计）；脚本在 `backend/tests/open/test_open_platform_*.py` |

缺陷统一登记：[缺陷记录.md](./缺陷记录.md)（不改 `00.缺陷台账/README.md`）。

## 二、执行方式

```powershell
cd backend
python -m pytest tests/client -v
```

- **框架**：pytest + pytest-asyncio（`asyncio_mode=auto`），与项目现有 `backend/tests/` 一致。
- **测试基座**：项目根 `backend/tests/conftest.py` 由「运营后台端」任务统一维护；
  本端在 `backend/tests/client/conftest.py` **自建** fixture（不改根 conftest），提供：
  - `tenant_session`：连接租户库 `zt_biz_1001_ci`，**外层事务执行、结束回滚、不落库**；
  - `platform_session`：连接平台库 `zt_platform_ci`，事务回滚、不落库；
  - `http_client`：httpx AsyncClient 直连 ASGI app（不触发 lifespan / 不启动 worker），
    用于「未登录 / 非法 Token」等鉴权门槛冒烟（不触达 DB）。
- **无 DB 环境**：`tenant_session` / `platform_session` 连接失败时整体 `pytest.skip`（不 fail），
  纯逻辑用例与鉴权冒烟仍照常执行。

## 三、脚本清单

| 脚本 | 层次 | 覆盖 |
|---|---|---|
| `test_auth.py` | 集成(平台库) | 客户端登录反向（未知手机号/错误密码/空手机号） |
| `test_http_auth_guard.py` | 接口(无DB) | 受保护接口未登录/非法 Token 拒绝、健康检查、404 |
| `test_billing_conditions.py` | 纯逻辑 | 条件引擎 v2：compare_scalar、evaluate_tree、各 evaluator、注册表 |
| `test_billing_engine.py` | 纯逻辑 | 运费匹配算法（金额/车型/方向/命中/冲突）+ 成本常量 |
| `test_billing_cost_matcher.py` | 纯逻辑 | 成本引擎舍入、阶梯累进计价 |
| `test_resource_plate.py` | 纯逻辑 | 车牌/挂车号牌规范化与格式校验 |
| `test_resource_vehicle.py` | 集成(租户库) | 车辆核心+扩展双表联写、唯一性、更新 |
| `test_partner_customer.py` | 集成(租户库) | 客户 CRUD、同名/同编码去重、软删 |
| `test_partner_carrier.py` | 集成(租户库) | 承运商 CRUD、编码/电话唯一 |
| `test_task_waybill_state.py` | 纯逻辑 | 任务/运单/明细状态机业务不变量与派生聚合 |
| `test_insight_profit.py` | 纯逻辑+集成 | 利润总览辅助函数 + KPI/趋势/结构/排行聚合 SQL 冒烟 |
| `test_ai_desensitize.py` | 纯逻辑 | AI 工具日志脱敏（手机号/身份证/银行卡/敏感 key） |
| `test_standardize_service.py` | 纯逻辑+集成 | 地名末级后缀扩展（BUG-CLI-001）+ 层级路径解析 |
| `test_system_user.py` | 集成(租户库) | 员工 CRUD、手机号去重、状态变更 |
| `test_system_role.py` | 集成(租户库) | 角色 CRUD、编码唯一、admin 保护 |
| `test_system_organization.py` | 集成(租户库) | 部门树增删改、子部门/员工删除约束 |
| `test_billing_freight_match.py` | 集成(租户库) | 合同+费率创建后 preview 命中（TC-CLI-BILLING-101） |
| `test_task_dispatch.py` | 集成(租户库) | 任务创建+运单挂接、候选 cargo、单号唯一 |
| `test_ai_employee.py` | 集成(平台库) | 启用数字员工列表、按 code 查询、工具绑定 |
| `test_task_finance_stage_rules.py` | 纯逻辑 | 费用单发起节点规则解析/判定/校验（TC-CLI-FINSTAGE-001~018） |
| `test_task_finance_stage_service.py` | 集成(租户库) | 发起节点 create_doc 硬拦截、creatable、懒补齐幂等（TC-CLI-FINSTAGE-101~106） |

## 四、执行结果概览

> 环境：Windows / Python 3.9.13 / pytest 8.4.2；租户库与平台库均可连接。

```
python -m pytest tests/client -v
=> 211 passed
```

- **通过**：211
- **跳过**：0（本机 DB 可用；无 DB 环境下集成用例将 skip）
- **失败**：0

## 五、缺陷概览

| 编号 | 标题 | 级别 | 状态 |
|---|---|---|---|
| BUG-CLI-001 | 地名标准化：以「州」等结尾的地级市省略「市」后缀时层级路径解析失败 | S3 | 已修复 |
| BUG-CLI-002 | AI 日志脱敏：身份证正则反向断言用 `\w` 与手机号/银行卡的 `\d` 不一致 | S4 | 已修复 |

详见 [缺陷记录.md](./缺陷记录.md)。

## 六、待测（未开发）说明

以 `backend/app/modules/client/**` 实际代码为准，比对需求文档。以下财务结算子域**未落地或部分落地**，
本端仅登记为「待测（未开发）」，不编写接口测试（参照 `doc/05.开发计划/需求-代码落地差距清单.md`）：

- 财务结算「应收账单 / 跨任务应付归集 / 对账单」等未开发部分；
- 承运商结算（`carrier_settlement`）仅覆盖随主档联动创建，独立结算流程待开发部分暂不测。

其余已落地模块中，部分接口以文档用例（仅手工 / 待补脚本）形式登记，见各子领域文档「自动化状态」列。
