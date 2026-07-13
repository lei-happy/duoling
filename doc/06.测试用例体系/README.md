# 智途（ZhiTu）测试用例体系总纲

> **定位**：本目录是智途全平台（后端 + 企业端 + 运营后台 + 驾驶员 H5）的**测试用例、测试脚本、接口测试与缺陷记录**统一归档地。
>
> **判定口径**：以 `backend/app/modules/**`（models/services/api）与 `frontend/*`（views/api）实际代码为准，逐条比对 `doc/02.需求文档/**` 需求，只对**已落地模块**做接口测试，未落地模块仅登记为「待测（未开发）」。
>
> **落地状态参考**：`doc/05.开发计划/需求-代码落地差距清单.md`

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

## 七、执行总览

### 首轮测试（2026-07-07）

| 端 | 用例文档 | 测试脚本 | pytest 结果 | 缺陷 |
|---|---|---|---|---|
| 运营后台 Console | 5 份 | `tests/conftest.py` + `tests/console/` 4 个 | 53 passed / 1 xfailed | BUG-CON-001(S2)、BUG-CON-002(S3) |
| 企业端 Client | 10 份 | `tests/client/` 13 个 | 188 passed | BUG-CLI-001(S3)、BUG-CLI-002(S4) |
| 驾驶员 H5 Driver | 6 份 | `tests/driver/` 7 个 | 48 passed / 3 skipped / 1 xfailed | BUG-DRV-001(S1)、BUG-DRV-002(S2)、BUG-DRV-003(S3) |
| 开放接口 Open | 6 份 | `tests/open/` 7 个 | 68 passed / 9 skipped | BUG-OPN-001(S2)、BUG-OPN-002/003(S3) |
| **合计** | **27 份** | **~31 个** | **357 passed / 12 skipped / 2 xfailed** | **10 个** |

### 修复轮次（2026-07-07）— 10/10 缺陷已修复

| 端 | 修复内容 | 修复后 pytest | 新增/增强测试 |
|---|---|---|---|
| 运营后台 | BUG-CON-001 `refresh`；BUG-CON-002 `BizException` | 63 passed | +`test_basicdata.py`（品牌/车系/经销商/role-menu） |
| 企业端 | BUG-CLI-001 地名变体；BUG-CLI-002 脱敏边界 | 211 passed | +7 脚本（组织/角色/运价命中/调度/AI员工等） |
| 驾驶员 H5 | BUG-DRV-001 排序；BUG-DRV-002 回单表迁移；BUG-DRV-003 权限 | 57 passed | 全链路/改密/回单 CRUD 集成 |
| 开放接口 | BUG-OPN-001 显式切库；BUG-OPN-002/003 短信校验与节流 | 79 passed / 9 skipped | LITE/短信反向用例 |
| **合计（全量 `pytest tests`）** | **10 缺陷全部关闭** | **~640+ passed / 9 skipped / 0 failed** | 脚本增至 ~40 个 |

> skip 均为无平台库 `zt_platform_ci` 时的 HTTP 集成用例，按规范 skip 而非 fail。

### 第三轮：全平台回归 + 覆盖增强（2026-07-09）

> 环境：Windows / Python 3.9.13 / pytest 8.4.2；平台库 `zt_platform_ci`、租户库 `zt_biz_1001_ci` 均可连接。
> 详见 [测试质量报告_2026-07-09.md](./测试质量报告_2026-07-09.md)。

| 端 | 用例数 | 结果 | 变化 |
|---|---|---|---|
| 运营后台 Console | 63 | 全通过 | — |
| 企业端 Client | 260 | 全通过 | **+49**（审批中心核心逻辑单测，从 0 补齐） |
| 驾驶员 H5 Driver | 57 | 全通过 | — |
| 开放接口 Open | 88 | 全通过 | **9 个 HTTP 集成用例由「误跳过」转真正执行**（修复 BUG-TEST-001） |
| 跨端（状态机/资金账） | 252 | 全通过 | — |
| **合计（`pytest tests`）** | **720** | **720 passed / 0 failed / 0 skipped** | 全绿、零跳过 |

**本轮两项质量提升**：

1. **BUG-TEST-001**：修复 open 端 `conftest.py` 中 `db_manager` 全局单例异步引擎跨事件循环污染，导致 9 个 HTTP 集成用例被静默 skip（假绿）的测试基座缺陷 → 现真正执行并通过。
2. **审批中心补覆盖**：新增 `tests/client/test_approval_flow.py`（49 用例），覆盖条件 DSL 求值、画布树展开、条件分支选择、流程结构校验、审批人解析。

### 待办（后续补测）

- **仍待脚本化**：多企业登录/切租户、角色菜单授权后 menu-version、运单批量导入+地名、SSE 对话/配额守卫（见各端 README「待补」节）。
- **异步 Worker / 外部依赖**：计费/成本 worker、双引擎回归、证照预警 worker、AI 工具编排（依赖 LLM）→ 仅手工。
- **待测（未开发）**：财务结算「应收/跨任务应付/对账单」、承运商独立结算、移动端 BI、LITE 前端、资质自助上报/OCR → 按差距清单登记，暂不编接口测试。
- **文档口径待对齐**：回单签收需求文档仍写「占位不落表」，与已落表实现不一致（见驾驶员 H5 缺陷记录）。
