# 运营后台端（Console）测试说明

> **端代码**：`CON` ｜ **缺陷编号前缀**：`BUG-CON-xxx`
> **对应后端**：`backend/app/modules/console/**`、`backend/app/modules/ai/api/console/**`
> **对应前端**：`frontend/console`
> **测试脚本**：`backend/tests/conftest.py`（共享基座） + `backend/tests/console/**`

## 一、测试范围

运营后台端是平台侧管理后台，操作平台库 `zt_platform_ci`。本轮针对**已落地**接口做接口级测试，覆盖模块：

| 模块 | 用例文档 | 后端 api | 覆盖情况 |
|---|---|---|---|
| 认证 / 鉴权 / 个人配置 | [01.认证与用户角色权限.md](./01.认证与用户角色权限.md) | `console/api/auth`、`system/user`、`system/role` | ✅ 脚本 + 手工 |
| 租户管理 / 产品版本授权 | [02.租户与产品授权.md](./02.租户与产品授权.md) | `console/api/tenant`、`product/product_version` | ✅ 读接口脚本；写接口部分受 BUG-CON-001 阻塞 |
| 基础数据 / 地区 / 字典 | [03.基础数据与地区.md](./03.基础数据与地区.md) | `region`、`dictionary`、`basicdata/*` | ✅ 脚本 + 手工 |
| AI 数字员工 | [04.AI数字员工.md](./04.AI数字员工.md) | `ai/api/console/{employee,provider,prompt,tool,observe}` | ✅ 脚本 |
| 缺陷记录 | [缺陷记录.md](./缺陷记录.md) | — | 见文档 |

> 未列入的模块（`ops/*` 同步、`doc_center`、`log_center`、`changelog`、`sms`、`capacity`、`driver`、`workbench` 等）以读接口鉴权为主，本轮以手工/待补形式登记，未全部脚本化，详见各用例文档「待补」标记。

## 二、测试架构（共享基座）

`backend/tests/conftest.py` 是**全端复用**的共享基座，提供：

1. **HTTP 测试客户端**：`httpx.AsyncClient` + `ASGITransport` 直连 `app.main:app`，无需起端口；`raise_app_exceptions=False` 使 500 以响应形式返回，贴近生产。
2. **平台库事务回滚 Session**：`platform_db` fixture 连接 `zt_platform_ci`，开外层事务并以 `join_transaction_mode="create_savepoint"` 注入 `get_platform_db`，**测试结束整体 rollback，任何写操作都不落库**（已实测 0 残留）。
3. **认证 client**：`auth_client` fixture 走真实登录 `POST /api/console/auth/login`（`13800000000/admin123`）拿 token 注入 `Authorization` 头。
4. **健壮 skip**：无 DB 时依赖 DB 的 fixture 自动 `pytest.skip`；纯逻辑用例（JWT/配置校验）不依赖 DB，恒定可跑。
5. **多端预留**：`login_console` 已实现，`login_client`/`make_console_token` 等辅助供其他端复用。

## 三、执行方式

```bash
cd backend
python -m pytest tests/console tests/conftest.py -v
# 或仅本端
python -m pytest tests/console -v
```

- 测试租户固定 `1001`（`zt_biz_1001_ci`），平台库 `zt_platform_ci`。
- 默认管理员：手机号 `13800000000` / 密码 `admin123`（见 `backend/scripts/seed/seed_data.py`）。

## 四、本轮执行结果概览

> 环境：Windows / Python 3.9.13 / pytest 8.4.2 / httpx 0.28.1，平台库 `zt_platform_ci` 可连接。

| 指标 | 数量 |
|---|---|
| 收集用例（脚本） | 54 |
| 通过 ✅ | 53 |
| 预期失败 XFAIL（关联缺陷） | 1（BUG-CON-001） |
| 失败 ❌ | 0 |
| 跳过 SKIP | 0（本端；DB 可用） |

脚本文件：

| 脚本 | 用例数 | 说明 |
|---|---|---|
| `tests/console/test_auth.py` | 18 | 认证鉴权（含 8 条纯逻辑恒通过） |
| `tests/console/test_tenant_product.py` | 10 | 租户读接口 + 产品版本（1 条 xfail） |
| `tests/console/test_system.py` | 17 | 用户/角色/字典/地区 |
| `tests/console/test_ai_console.py` | 9 | AI 数字员工/Provider/Prompt/Tool |

## 五、关键缺陷

| 编号 | 标题 | 级别 | 状态 |
|---|---|---|---|
| BUG-CON-001 | 创建/更新产品版本接口返回 500（响应序列化触发 `created_at` 懒加载 MissingGreenlet） | S2 严重 | 待确认 |
| BUG-CON-002 | 工作台配置/主题等参数校验失败误用 `AuthException`，返回 401 而非 400 | S3 一般 | 待确认 |

详见 [缺陷记录.md](./缺陷记录.md)。
