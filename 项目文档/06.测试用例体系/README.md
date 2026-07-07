# 智途（ZhiTu）测试用例体系总纲

> **定位**：本目录是智途全平台（后端 + 企业端 + 运营后台 + 驾驶员 H5）的**测试用例、测试脚本、接口测试与缺陷记录**统一归档地。
>
> **判定口径**：以 `backend/app/modules/**`（models/services/api）与 `frontend/*`（views/api）实际代码为准，逐条比对 `项目文档/02.需求文档/**` 需求，只对**已落地模块**做接口测试，未落地模块仅登记为「待测（未开发）」。
>
> **落地状态参考**：`项目文档/05.开发计划/需求-代码落地差距清单.md`

---

## 一、目录结构

```
06.测试用例体系/
├── README.md                     # 本文件：总纲、规范、编号规则
├── _模板/
│   ├── 测试用例模板.md            # 单模块测试用例编写模板
│   └── 缺陷记录模板.md            # 单条缺陷记录模板
├── 00.缺陷台账/
│   └── README.md                 # 全平台缺陷汇总台账（各端登记到此）
├── 01.运营后台端/                 # Console：backend/app/modules/console + ai/console
│   ├── README.md                 # 本端测试范围与执行说明
│   └── <模块>/用例.md
├── 02.企业端/                     # Client Web：backend/app/modules/client + ai/client
│   ├── README.md
│   └── <模块>/用例.md
├── 03.驾驶员H5端/                 # Driver：backend/app/modules/driver
│   ├── README.md
│   └── <模块>/用例.md
└── 04.开放接口与LITE与运力宝/      # Open：backend/app/modules/open
    ├── README.md
    └── <模块>/用例.md
```

**测试脚本**统一放在 `backend/tests/` 下，按端分子目录：

```
backend/tests/
├── conftest.py                   # 共享 fixture（HTTP 测试客户端 / 事务回滚 session / 认证 token）
├── console/                      # 运营后台端接口测试脚本
├── client/                      # 企业端接口测试脚本
├── driver/                      # 驾驶员 H5 端接口测试脚本
└── open/                        # 开放接口测试脚本
```

---

## 二、测试用例编号规范

编号格式：`TC-<端代码>-<模块代码>-<三位序号>`

| 端 | 端代码 |
|---|---|
| 运营后台 Console | `CON` |
| 企业端 Client | `CLI` |
| 驾驶员 H5 Driver | `DRV` |
| 开放接口 Open/LITE/运力宝 | `OPN` |

示例：`TC-CLI-VEHICLE-001`（企业端车辆管理第 1 条用例）。

模块代码用大写英文短名（如 `AUTH` / `VEHICLE` / `DRIVER` / `ORDER` / `BILLING` / `TASK` / `WAYBILL` / `APPROVAL` / `FINANCE` 等），与后端 api 目录保持语义一致。

---

## 三、测试用例编写要求

每条用例至少包含：

- **用例编号**、**用例标题**
- **对应需求文档**（相对路径链接）
- **对应接口**（HTTP 方法 + 路径，如 `POST /api/client/vehicle`）
- **前置条件**（登录角色、依赖数据）
- **测试步骤**
- **测试数据**（关键入参）
- **预期结果**（状态码 + 业务 code + 关键字段/校验点）
- **优先级**：P0（核心链路/阻断）｜P1（重要）｜P2（一般）
- **用例类型**：正向 / 反向（参数校验、权限、边界）
- **自动化状态**：已覆盖脚本 / 仅手工 / 待补
- **执行结果**：通过 ✅ / 失败 ❌ / 阻塞 🚫 / 未执行 ⬜（关联缺陷编号）

---

## 四、测试脚本约定

- 框架：`pytest` + `pytest-asyncio`（`asyncio_mode=auto`），与现有 `backend/tests/` 保持一致。
- **接口测试优先**用 FastAPI `httpx.AsyncClient` + `ASGITransport` 直连 `app.main:app`；无 DB 环境时 `pytest.skip`。
- **不落库**：集成测试统一在外层事务中执行并最终 `rollback`（参考 `tests/test_driver_fund_account.py`）。
- 测试租户固定用 `1001`（开发库 `zt_biz_1001_ci`），平台库 `zt_platform_ci`。
- 每个脚本头部 docstring 注明对应需求文档路径与覆盖的用例编号区间。
- 运行：`cd backend && python -m pytest tests/<端> -v`。

---

## 五、缺陷记录规范

- 发现的缺陷：① 在对应端目录写详细缺陷记录（用 `_模板/缺陷记录模板.md`）；② 在 `00.缺陷台账/README.md` 登记一行汇总。
- 缺陷编号：`BUG-<端代码>-<三位序号>`，如 `BUG-CLI-001`。
- 严重级别：**S1 致命**（主流程不可用/数据错误）｜**S2 严重**（重要功能缺陷）｜**S3 一般**（次要功能/体验）｜**S4 轻微**（文案/边界）。
- 状态：待确认 / 已确认 / 修复中 / 已修复 / 不修复 / 无法复现。

---

## 六、执行分工（并行任务）

| 任务 | 负责范围 | 后端模块 | 前端 |
|---|---|---|---|
| 运营后台端 | 平台管理后台 | `modules/console`、`modules/ai/console` | `frontend/console` |
| 企业端 | 租户业务全域 | `modules/client`、`modules/ai/client` | `frontend/client` |
| 驾驶员 H5 端 | 司机移动端 | `modules/driver` | `frontend/driver-h5` |
| 开放接口/LITE/运力宝 | 无认证/自助/上报 | `modules/open` | `frontend/website` |

---

## 七、首轮执行总览（2026-07-07）

### 用例与脚本产出

| 端 | 用例文档 | 测试脚本 | pytest 结果 | 缺陷 |
|---|---|---|---|---|
| 运营后台 Console | 5 份（`01.运营后台端/`） | `tests/conftest.py`（共享基座）+ `tests/console/` 4 个 | 53 passed / 1 xfailed | BUG-CON-001(S2)、BUG-CON-002(S3) |
| 企业端 Client | 10 份（`02.企业端/`） | `tests/client/` 13 个 | 188 passed | BUG-CLI-001(S3)、BUG-CLI-002(S4) |
| 驾驶员 H5 Driver | 6 份（`03.驾驶员H5端/`） | `tests/driver/` 7 个 | 48 passed / 3 skipped / 1 xfailed | BUG-DRV-001(S1)、BUG-DRV-002(S2)、BUG-DRV-003(S3) |
| 开放接口 Open | 6 份（`04.开放接口与LITE与运力宝/`） | `tests/open/` 7 个 | 68 passed / 9 skipped | BUG-OPN-001(S2)、BUG-OPN-002/003(S3) |
| **合计** | **27 份** | **~31 个脚本** | **357 passed / 12 skipped / 2 xfailed / 0 failed** | **10（S1×1,S2×3,S3×5,S4×1）** |

> 说明：skip 均为需真实 DB/建表/外部依赖的集成用例，本地环境缺失时按规范 skip 而非 fail；xfailed 为已挂缺陷号、修复后自动转 xpass 的用例。全部脚本可被 pytest 收集、无导入错误、纯逻辑用例全通过。

### 待办（后续补测）

- **需登录 Token/种子数据的写链路**：租户创建与产品授权（建真实库不可回滚）、员工/角色/组织增改、运价合同命中、任务全链路调度、承运商结算联动等 → 需一套可复用的种子/登录夹具后脚本化。
- **异步 Worker / 外部依赖**：计费与成本引擎 worker、双引擎回归、证照预警 worker、AI 对话 SSE 与工具编排（依赖 LLM Provider）→ 仅手工/待补。
- **待测（未开发）**：财务结算「应收/跨任务应付/对账单」、承运商独立结算、移动端 BI 看板与管理侧、LITE 前端、资质自助上报/OCR/位置上报 → 按差距清单仅登记，暂不编接口测试。

### 优先修复建议

1. `BUG-DRV-001`（S1）司机端"我的任务"MySQL `NULLS LAST` 语法 → 生产阻断，优先修复（`driver_task_service.py` 去掉 `.nullslast()`）。
2. `BUG-CON-001`（S2）产品版本创建/更新 500 → 返回前 `await db.refresh(version)`。
3. `BUG-OPN-001`（S2）LITE 上报接口开放路径无租户上下文 → 需重设计鉴权/租户注入。
4. `BUG-DRV-002`（S2）回单表缺失与需求口径不一致 → 补迁移或对齐需求。
