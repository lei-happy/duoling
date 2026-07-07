# 开放接口 / LITE 端 / 运力宝（Open）测试范围与执行说明

> **端代码**：`OPN` ｜ **缺陷编号前缀**：`BUG-OPN-xxx`
>
> **后端范围**：`backend/app/modules/open/**`（无需认证）；运力宝相关的证照监控扫描服务、承运商运力建档（落地在 `backend/app/modules/client/**`，因功能属运力宝需求纳入本端）。
>
> **前端范围**：`frontend/website`（官网，若相关）。
>
> **测试脚本**：`backend/tests/open/`

---

## 一、模块与落地状态

| # | 模块 | 后端代码 | 路径前缀 | 落地状态 | 用例文档 |
|---|------|---------|---------|---------|---------|
| 01 | 企业自助注册 | `open/api/register.py` + `services/register_service.py` | `/api/open/register` | 已落地 | [01.企业自助注册.md](01.企业自助注册.md) |
| 02 | 公开产品版本 / 版本功能矩阵 / 更新日志 | `open/api/product.py`、`open/api/changelog.py` | `/api/open/product`、`/api/open/changelog` | 已落地 | [02.公开产品与更新日志.md](02.公开产品与更新日志.md) |
| 03 | 短信验证码 | `open/api/sms.py` + `services/sms_service.py` | `/api/open/sms` | 已落地 | [03.短信验证码.md](03.短信验证码.md) |
| 04 | LITE 承运商运力上报 | `open/api/lite_carrier_dispatch.py` | `/api/open/lite/carrier` | **契约占位**（前端未建，接口占位实现存在缺陷） | [04.LITE承运商运力上报.md](04.LITE承运商运力上报.md) |
| 05 | 承运商邀请着陆页 / 激活 | `open/api/carrier_invite.py` + `client/services/partner/carrier_invite_service.py` | `/api/open/carrier-invite` | 已落地（路径 B） | [05.运力宝证照监控与承运商建档.md](05.运力宝证照监控与承运商建档.md) |
| 05 | 运力宝-证照监控扫描 | `client/services/compliance/compliance_scan_service.py` | worker（无 HTTP 触发） | 已落地（v1） | [05.运力宝证照监控与承运商建档.md](05.运力宝证照监控与承运商建档.md) |

> LITE 端前端（承运商运力上报页）未开发，前端整体登记为「待测（未开发）」，参见 `项目文档/05.开发计划/需求-代码落地差距清单.md`。

---

## 二、接口清单（以 `backend/app/main.py` 注册为准，前缀 `/api/open`）

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/open/register/phone-available` | 手机号是否已关联企业 | 无 |
| POST | `/api/open/register` | 提交企业自助注册（异步任务） | 无 |
| GET | `/api/open/register/progress/{task_id}` | 注册任务进度 | 无 |
| GET | `/api/open/product/versions` | 产品版本列表 | 无 |
| GET | `/api/open/product/version-features` | 版本×功能矩阵 | 无 |
| GET | `/api/open/changelog` | 更新日志列表（仅已发布） | 无 |
| POST | `/api/open/sms/send` | 发送短信验证码 | 无 |
| POST | `/api/open/sms/reset-password` | 验证码重置密码 | 无 |
| GET | `/api/open/carrier-invite/{invite_code}` | 邀请着陆页信息 | 无 |
| POST | `/api/open/carrier-invite/activate` | 邀请激活（路径 B 建 lite 租户） | 无 |
| POST | `/api/open/lite/carrier/task/{task_id}/dispatch` | LITE 承运商上报运力（占位） | X-Lite-Token（占位） |

---

## 三、测试脚本与执行

脚本目录：`backend/tests/open/`

| 脚本 | 覆盖 |
|---|---|
| `conftest.py` | 本端 fixture：`platform_client`（HTTP，DB 不可达 skip）、`platform_session` / `tenant_session`（外层事务回滚不落库） |
| `test_register.py` | 手机号正则、注册 schema、phone-available / register / progress HTTP |
| `test_sms.py` | 用途/常量/schema、send / reset-password HTTP |
| `test_product_changelog.py` | 版本列表 / 功能矩阵 / 更新日志分页 HTTP |
| `test_carrier_invite.py` | 脱敏 / 邀请码 / URL / 激活 schema、着陆页 / 激活 HTTP |
| `test_lite_carrier_dispatch.py` | 上报 schema、租户上下文缺陷（BUG-OPN-001） |
| `test_compliance_scan.py` | 证照分级 `_level_of`、阈值环境变量（纯逻辑） |

执行：

```bash
cd backend && python -m pytest tests/open -v
```

**约定**：
- 无 DB / 服务时 HTTP 集成用例 `pytest.skip`，纯逻辑用例始终通过。
- 集成用例统一走外层事务并最终 `rollback`，不落库；`sms/send` 的 HTTP 用例例外（无事务包裹，会向 CI 库落一条 `sms_code`，属预期副作用）。
- 测试租户固定 `1001`，平台库 `zt_platform`（开发库 `_ci` 后缀）。

---

## 四、最近一次执行结果

- 环境：本地无平台库 / 租户库连接。
- 结果：**68 passed, 9 skipped**（9 条 skip 均为需平台库的 HTTP 集成用例）。
- 纯逻辑 / schema 用例全部通过，脚本可正常收集、无导入错误。

---

## 五、缺陷

见 [缺陷记录.md](缺陷记录.md)。关键：`BUG-OPN-001`（S2）LITE 运力上报占位接口因开放路径无租户上下文而永远不可用。
