# 驾驶员 H5 端（Driver）测试用例体系

> **端代码**：`DRV` ｜ **缺陷编号**：`BUG-DRV-xxx`
> **后端模块**：`backend/app/modules/driver/**`（+ 交叉只读 `client/.../driver_fund_account`）
> **前端**：`frontend/driver-h5`
> **测试脚本**：`backend/tests/driver/`
> **需求文档**：`项目文档/02.需求文档/03.移动端/02.驾驶员H5端/**`、`项目文档/01.架构设计/驾驶员H5架构设计.md`

本目录归档驾驶员 H5 端的测试用例、缺陷记录，测试脚本位于 `backend/tests/driver/`。
判定口径以 `backend/app/modules/driver/**` 实际代码为准，逐条比对需求文档，只对**已落地模块**做接口/服务测试。

## 一、被测范围与落地状态

| 模块 | 用例文档 | 后端 api / service | 落地状态 |
|---|---|---|---|
| 账号体系与多企业切换 | [01.账号与多企业切换.md](./01.账号与多企业切换.md) | `driver/api/auth.py` + `driver_auth_service.py` + `driver_context.py` | ✅ 已落地 |
| 任务流转与司机动作 | [02.任务流转与司机动作.md](./02.任务流转与司机动作.md) | `driver/api/task.py` + `driver_task_service.py` | ✅ 已落地 |
| 财务与收入查询 | [03.财务与收入查询.md](./03.财务与收入查询.md) | `driver/api/finance.py` + `driver_finance_service.py` | ✅ 已落地 |
| 回单签收与凭证上传 | [04.回单签收与凭证上传.md](./04.回单签收与凭证上传.md) | `driver/api/task_receipt.py` + `driver_receipt_service.py` + `driver/api/file.py` | ⚠️ 代码已落表，但租户库缺表 + 与需求"占位"口径不一致（见 BUG-DRV-002） |
| 个人中心与资质 | [05.个人中心与资质.md](./05.个人中心与资质.md) | `driver/api/profile.py` + `driver_context.py` | ✅ 已落地（资质自助上报：待测(未开发)） |

### 标记「待测（未开发）」的子能力

| 子能力 | 说明 |
|---|---|
| 资质自助上报（驾驶证 / 从业资格证 / 健康证 / 到期提醒） | 需求 `05.个人中心与资质.md §六` 明确一期不实现，无对应 api/model |
| 电子回单 OCR、位置上报 | 需求 `00.模块总览 §五` 远期演进，无代码 |
| 社会运力（`carrier_type=3`）司机操作 | `_build_visibility_condition` 预留 `social_driver_id` 口子，`biz_social_driver` 未落地 |
| `POST /auth/logout` 黑名单登出 | 需求 `01 §五` 标注为"未来接口"，当前仅前端本地清 token |

## 二、接口总览（以 `app/main.py` 挂载 `/api/driver` 为准）

| 前缀 | 方法 路径 | 说明 |
|---|---|---|
| auth | `POST /api/driver/auth/login` | 手机号+密码登录（`user_type=3` 过滤） |
| auth | `POST /api/driver/auth/sms-login` | 手机号+验证码登录 |
| auth | `POST /api/driver/auth/refresh` | 刷新 Token |
| auth | `GET /api/driver/auth/user-tenants` | 可登录企业列表 |
| auth | `POST /api/driver/auth/switch-tenant` | 切换企业（重签 JWT） |
| auth | `PUT /api/driver/auth/password` | 修改密码 |
| auth | `GET /api/driver/auth/user-info` | 司机信息+角色+权限+driverId |
| task | `GET /api/driver/task/my` | 我的任务分页 |
| task | `GET /api/driver/task/{taskId}` | 任务详情 |
| task | `POST /api/driver/task/{taskId}/accept` | 接收调令 |
| task | `POST /api/driver/task/{taskId}/reject` | 拒绝调令（1→0） |
| task | `POST /api/driver/task/{taskId}/confirm-load` | 确认装车（聚合 1→2） |
| task | `POST /api/driver/task/{taskId}/depart` | 确认出发（2→3） |
| task | `POST /api/driver/task/{taskId}/confirm-arrive` | 确认到达（聚合 3→4） |
| task | `POST /api/driver/task/items/{itemId}/sign` | 逐单签收（聚合 4→5） |
| task | `POST /api/driver/task/items/{itemId}/revert-sign` | 撤销签收（受限） |
| finance | `GET /api/driver/finance/my` | 我的费用单分页 |
| finance | `GET /api/driver/finance/summary` | 收入汇总 |
| finance | `GET /api/driver/finance/account` | 我的收款账户 |
| finance | `GET /api/driver/finance/fund-account` | 我的资金账户（往来账） |
| finance | `GET /api/driver/finance/fund-account/transactions` | 我的资金流水 |
| finance | `GET /api/driver/finance/{docId}` | 费用单详情 |
| task-receipt | `POST /api/driver/task-receipt/upload` | 上传回单（落表） |
| task-receipt | `GET /api/driver/task-receipt/my` | 我的回单列表 |
| task-receipt | `DELETE /api/driver/task-receipt/{id}` | 删除回单 |
| profile | `GET /api/driver/profile/me` | 我的资料 |
| profile | `PUT /api/driver/profile/me` | 更新资料（白名单） |
| file | `POST /api/driver/file/upload` | 文件上传（共享路由） |

## 三、测试脚本与执行

脚本位于 `backend/tests/driver/`，本端自建 `conftest.py`（**不修改根 conftest.py**）：

| 脚本 | 覆盖 | 层次 |
|---|---|---|
| `test_driver_schemas.py` | 请求 schema 参数校验（拒单/撤签/回单/资料） | 纯逻辑 |
| `test_driver_context.py` | `get_current_driver` 鉴权与档案锁定 | 纯逻辑 + 集成 |
| `test_driver_auth_service.py` | 登录/切企业反向路径 | 集成（平台库） |
| `test_driver_task_service.py` | 任务可见性、输出裁剪、列表 | 纯逻辑 + 集成 |
| `test_driver_finance_service.py` | 费用单/汇总/账户只读隔离 | 纯逻辑 + 集成 |
| `test_driver_receipt_service.py` | 回单落表/列表/删除越权 | 纯逻辑 + 集成 |

执行：

```bash
cd backend && python -m pytest tests/driver -v
```

- 集成用例统一在**外层事务中执行并 rollback**，不落库；租户库 `1001` / 平台库不可连接时 `skip`。
- `biz_task_receipt` 表缺失时回单集成用例 `skip`（记为 BUG-DRV-002）。

### 最近一次执行结果（2026-07-07）

```
48 passed, 3 skipped, 1 xfailed
```

- **skipped×3**：回单落表集成（租户库缺 `biz_task_receipt` 表）→ BUG-DRV-002
- **xfailed×1**：`test_list_my_tasks_empty`（`GET /task/my` MySQL `NULLS LAST` 语法错误）→ BUG-DRV-001

## 四、缺陷

详见 [缺陷记录.md](./缺陷记录.md)。

| 编号 | 标题 | 级别 | 状态 |
|---|---|---|---|
| BUG-DRV-001 | 我的任务列表 `nullslast()` 在 MySQL 生成非法 SQL，接口 500 | S1 致命 | 待确认 |
| BUG-DRV-002 | 回单表 `biz_task_receipt` 租户库缺失 + 需求"占位不落表"口径与代码不一致 | S2 严重 | 待确认 |
| BUG-DRV-003 | 撤销签收接口未校验 `operation:task:revert-sign` 权限，与需求受限约束不符 | S3 一般 | 待确认 |
