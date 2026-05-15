# 企业端 BI 数据分析 · 经营驾驶舱

> **所属阶段**：阶段七 — BI 数据分析模块
>
> **文档状态**：v1.0（首期 · 经营总览）
>
> **优先级**：中
>
> **作者**：智途产研团队
>
> **更新日期**：2026-05-15

---

## 一、功能概述

面向**物流公司老板/高管**，提供以"运单数据"为核心的经营 BI 看板，1 屏看完业务关键指标，并支持多维度筛选钻取。

本期（v1.0）仅交付驾驶舱下的**「经营总览」**子页面，覆盖以下四类视角：

- **钱**：运费总收入、收入趋势、TopN 客户贡献
- **单 / 车**：运单数、发运台数、商品车品牌结构
- **市场**：客户结构、热门起讫点
- **效率**：运单状态分布、运费计算异常率

> **本期边界**：仅做"收入侧"指标，不涉及成本、毛利、利润率（数据库当前无运输成本字段，等成本建模后再扩展）。

---

## 二、业务背景与目标

### 2.1 角色与场景

| 角色 | 关注重点 | 使用频率 |
|------|---------|---------|
| 物流公司老板 | 钱赚了多少、单干了多少、客户结构 | 每日 1–2 次 |
| 运营总监 | 趋势、TopN、异常率 | 每日多次 |
| 业务经理 | 客户/路线/车型贡献 | 每周回顾 |

### 2.2 目标

- 1 屏（首屏）展示老板最关心的 4 个 KPI 卡 + 1 张趋势主图
- 提供 5 个分析视角（趋势 / 客户 / 路线 / 品牌 / 效率）；**无顶栏时间切换**，趋势及以下模块默认按**当月**时间窗拉数（与 KPI 卡独立）
- UI 风格与现有 `运营看板`（`/insight/overview`）一致；顶部 KPI 卡为「当日大数 + 近 30 日迷你折线/柱图 + 周同比/日同比」并排（参考运营看板统计卡）
- 接口聚合查询，单页加载 < 1.5s（百万行运单数据量级）

### 2.3 非目标（本期不做）

- 成本 / 毛利 / 利润率指标
- 司机绩效、车辆利用率（属于运力中心 BI，后续在驾驶舱下另起子页面）
- 地图分布、城市热力图（依赖地理编码完整度，二期）
- 数据下载 / 报表导出（属于"数据报表"菜单职责）

---

## 三、菜单结构

新菜单挂到一级菜单 **数据洞察(id=215)** 下，与"运营看板/数据报表/智能预测"同级。

```text
数据洞察 (id=215)
├── 运营看板 (existing, /insight/overview)
├── 数据报表 (existing, /insight/report)
├── 智能预测 (existing, /insight/prediction)
└── 经营驾驶舱 (NEW · 容器, /insight/cockpit, component=null)
    └── 经营总览 (NEW · 本期叶子, /insight/cockpit/overview)
```

- 父级"**经营驾驶舱**"作为容器（`menu_type=0`、`component=null`），承载未来更多子页面（客户分析、路线分析、车型分析等）
- 子级"**经营总览**"是本期实现的 BI 看板，对应前端组件 `/dashboard/business-cockpit/overview/index`

| 菜单层级 | menu_name | menu_code | path | component | feature_code |
|---------|-----------|-----------|------|-----------|--------------|
| 二级容器 | 经营驾驶舱 | `insight:cockpit` | `/insight/cockpit` | (null) | `bi_cockpit` |
| 三级叶子 | 经营总览 | `insight:cockpit:overview` | `/insight/cockpit/overview` | `/dashboard/business-cockpit/overview/index` | `bi_cockpit_overview` |

---

## 四、数据维度与指标定义

### 4.1 核心 KPI（顶部 4 卡片）

> **与下方图表解耦**：4 张 KPI 卡按**服务端当前时刻**聚合，不随下方图表时间窗变化；便于打开页面即看「今天跑得怎样」。

| 指标 | 主数值口径 | 迷你图 | 单位（主数值 / 接口） | 数据源 |
|------|------------|--------|----------------------|--------|
| 运费总收入 | 当日 0 点至今 `SUM(freight_amount)` | 近 30 个自然日、按日 `SUM`（折线面积图） | **万元** / 元 | `biz_waybill.freight_amount` |
| 总运单数 | 当日 0 点至今 `COUNT(*)` | 近 30 日按日单量（柱图） | 单 | `biz_waybill.id` |
| 总发运台数 | 当日 0 点至今 `SUM(quantity)` | 近 30 日按日台数（折线面积图） | 台 | `biz_waybill.quantity` |
| 服务客户数 | 当日 0 点至今有运单的去重客户 | 近 30 日按日 `COUNT(DISTINCT customer_id)`（柱图） | 个 | `biz_waybill.customer_id` |

每个卡片统一结构：

- **主区**：标题 + 指标说明（问号 tooltip）+ **当日**累计（运费卡主数值以**万元**展示，保留 2 位小数）
- **中区**：ECharts 迷你图（高度约 36px），展示**近 30 个自然日**（含当日；当日桶为 0 点至今，与主数值一致）
- **底部**：**周同比**与**日同比**并排（参考运营看板统计卡），均用「箭头图标 + 百分比」；对照期为 0 无法计算时显示「—」
  - **周同比**：本周一 0 点～当前时刻，对比上周一 0 点～（上周一 0 点 + 与本周已过的**相同时长**）
  - **日同比**：今天 0 点～当前时刻，对比昨天 0 点～**昨天与当前同一时刻**（即与今天等长的「昨日同时段」）

### 4.2 主体图表（6 个分析模块）

| 模块 | 图表类型 | 维度 | 度量 | 备注 |
|------|---------|------|------|------|
| 收入与单量趋势 | 双 Y 轴折/柱 | 时间（日/周/月） | 收入、单量 | 默认统计**当月**（无顶栏时间切换；由前端传入本月 `start`/`end`） |
| TopN 客户运费贡献 | 横向柱状 + 排行列表 | 客户 | 收入、占比、单量 | 默认 Top10 |
| 客户类型分布 | 环形图 | `customer_type` | 收入、单量 | 主机厂/贸易商/经销商/个人/其他 |
| 热门起讫点 | 双柱状（左右分栏） | 出发地省 / 目的地省 | 单量、收入 | 默认 Top10 |
| 商品车品牌排行 | 横向柱状 + 词云 | 品牌 | 台数、收入 | 默认 Top20 |
| 运营效率 | 环形 + 进度条 | 运单状态 / 计算状态 | 占比 | 状态环形 + 异常率 |

### 4.3 指标-数据源映射

```sql
-- 主表：biz_waybill（含 freight_amount/quantity/status/calc_status/created_at）
-- JOIN：
--   biz_customer ON biz_waybill.customer_id   →  customer_type
--   biz_region   ON biz_waybill.origin_region_id / destination_region_id  →  province/city
--   biz_waybill_cargo ON biz_waybill.id        →  brand_id/series_id
--   biz_vehicle_brand ON biz_waybill_cargo.brand_id  →  brand_name_cn
```

| 字段 | 取值规则 | 兜底策略 |
|------|---------|---------|
| 时间口径 | `biz_waybill.created_at` | 默认本月 |
| 收入 | `freight_amount`（可为 NULL） | NULL 视为 0 |
| 客户类型 | `biz_customer.customer_type`（0/1/2/3/4） | 客户已删/未匹配 → "未知" |
| 起讫地省份 | `biz_region.name` (level=1) | `origin_region_id` 为空时取 `biz_waybill.origin` 文本 |
| 品牌 | `biz_waybill_cargo.brand_id → biz_vehicle_brand.brand_name_cn` | 无标准化时回退 `biz_waybill_cargo.vehicle_brand` 文本 |
| 状态 | `biz_waybill.status`（0–6 七态） | — |
| 计算状态 | `biz_waybill.calc_status`（pending/calculating/calculated/exception/locked） | 异常率分子取 `exception` |

### 4.4 时间窗与对比口径

**下方图表与分析模块**

- 经营总览页**无**顶栏「经营总览」标题行，**无**本月/本年或自定义时间切换。
- 时间窗由前端 `provide` **当月**起止（自然月 1 日 0 点～月末结束）作为各图表接口的 `start` / `end`；与 KPI 卡独立。
- 时间字段：本期固定使用 `biz_waybill.created_at`。

**顶部 KPI 4 卡片**

- `GET /kpi-summary` **不使用**上述 `start` / `end`；按服务端「当前时刻」计算当日累计、近 30 日序列及周/日同比（见 4.1 底部说明）。
- 周同比、日同比分母为 0 时增长率置空（前端「—」）。

---

## 五、数据模型与依赖表

### 5.1 依赖表清单

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `biz_waybill` | 主表（运单） | `customer_id`、`origin_region_id`、`destination_region_id`、`freight_amount`、`quantity`、`status`、`calc_status`、`created_at`、`is_deleted` |
| `biz_waybill_cargo` | 货物明细（品牌/台数） | `waybill_id`、`brand_id`、`vehicle_brand`、`quantity` |
| `biz_customer` | 客户类型 | `id`、`customer_type`、`customer_name` |
| `biz_region` | 行政区域 | `id`、`code`、`name`、`parent_code`、`level` |
| `biz_vehicle_brand` | 品牌字典 | `brand_id`、`brand_name_cn` |

### 5.2 查询性能与索引建议

- `biz_waybill(created_at, is_deleted)`：复合索引（如已存在则跳过；本期不强制新增，依赖 `id` 自增近似单调可走主键反向扫描）
- `biz_waybill(customer_id, is_deleted)`：客户聚合查询走该索引
- 单租户百万级数据下，所有聚合接口需保证 ≤ 500ms（聚合查询走 MySQL 索引扫描）

### 5.3 多租户与权限

- 所有查询通过 `get_tenant_db` 注入租户库 Session，与现有运单接口口径一致
- 接口默认要求登录态（`get_current_user`），不做菜单级细粒度按钮权限（首期）
- 后续可基于 `feature_code = bi_cockpit_overview` 做版本灰度

---

## 六、API 接口设计

### 6.1 公共约定

- **前缀**：`/insight/cockpit/*`
- **公共参数**：
  - `start`（可选，ISO 日期，默认本月 1 号 00:00）
  - `end`（可选，ISO 日期，默认现在）
  - **例外**：`GET /insight/cockpit/kpi-summary` 的 `start` / `end` 为兼容保留，**不参与**本期顶部 KPI 卡计算（见 6.2.1）。
  - 所有接口返回 `{code, message, data}` 标准结构

### 6.2 接口列表

#### 6.2.1 核心 KPI（顶部卡片专用）

```http
GET /insight/cockpit/kpi-summary?start=...&end=...
```

> `start` / `end` 为历史兼容保留，**本期响应不依赖该窗口**，卡片数据均按服务端**当前自然日**与近 30 日计算。

**响应**：

```jsonc
{
  "code": 0,
  "data": {
    "revenue": {
      "todayValue": 1234567.89,
      "weekOverWeekRate": 0.05,
      "dayOverDayRate": 0.1223,
      "trend30d": [{ "date": "2026-04-16", "value": 92000.0 }, { "date": "2026-04-17", "value": 88000.0 }]
    },
    "waybillCount": {
      "todayValue": 32,
      "weekOverWeekRate": -0.02,
      "dayOverDayRate": 0.1428,
      "trend30d": [{ "date": "2026-04-16", "value": 5 }, ...]
    },
    "vehicleQuantity": { "todayValue": 128, "weekOverWeekRate": null, "dayOverDayRate": 0.1636, "trend30d": [...] },
    "customerCount": { "todayValue": 8, "weekOverWeekRate": 0.1, "dayOverDayRate": 0.1428, "trend30d": [...] }
  }
}
```

说明：`revenue.trend30d[].value` 与 `todayValue` 均为**元**；前端「运费总收入」主数值展示为**万元**。`weekOverWeekRate` / `dayOverDayRate` 为小数增长率；分母为 0 时为 `null`。其余指标 `value` / `todayValue` 为整数计数。

#### 6.2.2 收入与单量趋势

```http
GET /insight/cockpit/revenue-trend?start=...&end=...&granularity=day|week|month
```

**响应**：

```jsonc
{
  "code": 0,
  "data": [
    { "date": "2026-05-01", "revenue": 92000.00, "waybillCount": 24, "vehicleQuantity": 96 },
    ...
  ]
}
```

#### 6.2.3 TopN 客户

```http
GET /insight/cockpit/customer-rank?start=...&end=...&limit=10
```

```jsonc
{
  "code": 0,
  "data": [
    { "customerId": 1, "customerName": "比亚迪", "revenue": 320000, "waybillCount": 45, "share": 0.26 },
    ...
  ]
}
```

#### 6.2.4 客户类型分布

```http
GET /insight/cockpit/customer-type-dist?start=...&end=...
```

```jsonc
{
  "code": 0,
  "data": [
    { "customerType": 0, "label": "主机厂", "revenue": 650000, "waybillCount": 180 },
    { "customerType": 1, "label": "贸易商", ... },
    { "customerType": -1, "label": "未知", ... }
  ]
}
```

#### 6.2.5 区域排行（起讫地）

```http
GET /insight/cockpit/region-rank?start=...&end=...&type=origin|destination&limit=10
```

```jsonc
{
  "code": 0,
  "data": [
    { "regionName": "广东省", "regionCode": "440000", "revenue": 280000, "waybillCount": 96, "vehicleQuantity": 384 },
    ...
  ]
}
```

聚合策略：通过 `biz_waybill.origin_region_id → biz_region` 回溯到 `level=1` 的省。`origin_region_id` 为 NULL 时聚合到"未知"分组（取 `biz_waybill.origin` 文本字段保底，按文本相同聚合）。

#### 6.2.6 商品车品牌排行

```http
GET /insight/cockpit/vehicle-brand-rank?start=...&end=...&limit=20
```

聚合源：`biz_waybill_cargo` JOIN `biz_waybill`（继承筛选条件），按 `brand_id` 或回退 `vehicle_brand` 文本聚合。

```jsonc
{
  "code": 0,
  "data": [
    { "brandId": 1, "brandName": "比亚迪", "vehicleQuantity": 1200, "revenueShare": 0.18 },
    ...
  ]
}
```

> 注：`revenueShare` 为该品牌对应运单（biz_waybill）的 freight 占比；多品牌运单按 `quantity` 等比例分摊。

#### 6.2.7 运营效率

```http
GET /insight/cockpit/operation-efficiency?start=...&end=...
```

```jsonc
{
  "code": 0,
  "data": {
    "statusDist": [
      { "status": 0, "label": "待确认", "count": 12 },
      { "status": 1, "label": "已确认", "count": 38 },
      { "status": 2, "label": "已调度", "count": 24 },
      { "status": 3, "label": "运输中", "count": 56 },
      { "status": 4, "label": "已送达", "count": 30 },
      { "status": 5, "label": "已完成", "count": 120 },
      { "status": 6, "label": "已取消", "count": 8 }
    ],
    "calcExceptionRate": 0.034,
    "calcExceptionCount": 12,
    "lockedCount": 56,
    "totalCount": 288
  }
}
```

### 6.3 错误码

- `0`：成功
- 复用全局：`401`（未登录）、`403`（无租户）、`500`（服务异常）
- 业务侧：无特殊错误码（聚合查询不抛业务异常，空时返回空数组/0 值）

---

## 七、前端页面设计

### 7.1 页面布局（栅格 16-gutter，仿 analysis 风格）

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  ┌─KPI 1─┐ ┌─KPI 2─┐ ┌─KPI 3─┐ ┌─KPI 4─┐  ← 顶部 4 KPI 卡（el-col 6）   │
│  │收入   │ │运单数 │ │发运台 │ │客户数 │   迷你图 + 周同比 / 日同比   │
│  └───────┘ └───────┘ └───────┘ └───────┘                                 │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─收入与单量趋势 (md=18)─────────────────┐ ┌─客户运费排行 (md=6)─┐   │
│  │ 双 Y 轴折/柱组合图 + 粒度切换 day/week  │ │ Top10 列表          │   │
│  └─────────────────────────────────────────┘ └─────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─客户类型分布 (md=16) 环形+表格─────────┐ ┌─运营效率 (md=8)─────┐   │
│  │                                           │ │ 状态环形 + 异常率 │   │
│  └───────────────────────────────────────────┘ └─────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─出发地 Top10 (md=12)──────────┐ ┌─目的地 Top10 (md=12)──────┐       │
│  │   横向柱状                     │ │   横向柱状                  │       │
│  └────────────────────────────────┘ └─────────────────────────────┘       │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─品牌台数排行 (md=16) 横向柱状─┐ ┌─品牌词云 (md=8)──────────┐       │
│  │                                  │ │                            │       │
│  └──────────────────────────────────┘ └────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.2 文件清单

| 文件路径 | 说明 |
|---------|------|
| `frontend/client/src/views/dashboard/business-cockpit/overview/index.vue` | 经营总览页面入口 |
| `business-cockpit/overview/composables/use-cockpit-filter.ts` | 注入当月时间窗（供趋势及以下图表） |
| `business-cockpit/overview/components/kpi-card.vue` | 顶部 4 KPI 卡 |
| `business-cockpit/overview/components/trend-card.vue` | 收入/单量趋势 + 客户排行 |
| `business-cockpit/overview/components/customer-analysis.vue` | 客户类型分布 + Top 客户 |
| `business-cockpit/overview/components/route-analysis.vue` | 起讫点双柱状 |
| `business-cockpit/overview/components/vehicle-brand-analysis.vue` | 品牌柱状 + 词云 |
| `business-cockpit/overview/components/efficiency-card.vue` | 状态环形 + 异常率 |
| `frontend/client/src/api/dashboard/cockpit/index.ts` | API 客户端 |
| `frontend/client/src/api/dashboard/cockpit/model/index.ts` | 类型定义 |

### 7.3 交互规则

- **时间窗**：页面无顶栏筛选；由 `provideCockpitFilter()` 注入**当月** `start`/`end`，子组件 `watch` 后拉数
- **加载态**：每个卡片独立 loading，加载失败用 `EleMessage.error`
- **空数据**：图表展示"暂无数据"占位（参考 ele-admin-plus 默认）
- **配色**：主色 `#5b8ff9`（蓝），辅色 `#975fe5`（紫）/ `#61ddaa`（绿）/ `#ff9c6e`（橙），与现有 analysis 一致

### 7.4 复用要点

- 图表组件：`vue-echarts` + 按需 `echarts/core` 引入（参考 sale-card.vue 的 `use([...])` 写法）
- 词云：`echarts-wordcloud`（已在 hot-search 中使用）
- 卡片容器：`ele-card`
- 排行列表样式：复用 `.sale-rank-item` 类（来自 sale-card.vue）

---

## 八、性能与缓存策略

- **聚合查询索引**：依赖 `biz_waybill` 主键 + `created_at`，单租户百万级数据下控制 < 500ms
- **服务端缓存**：本期不做缓存；预留扩展点（可在 Service 层加 5 min Redis 缓存，key 含 tenant_code + start + end + endpoint）
- **前端节流**：日期范围变化时 debounce 300ms 再触发请求，避免快速切换造成抖动
- **接口并发**：页面加载时 7 个接口并发请求（前端 `Promise.all`），不串行

---

## 九、测试要点

### 9.1 接口正确性

- 时间筛选边界：`start` ≥ `end` 时 KPI 全部为 0
- 空数据态：新租户无运单时所有接口返回空数组/0 值（不报错）
- KPI 周/日同比：对照段为 0 → 对应 `weekOverWeekRate` / `dayOverDayRate` = null（前端显示 "—"）；有值时为小数增长率
- NULL 处理：`freight_amount` 为 NULL 的运单计为 0；`customer_id` 为 NULL 计为"未知客户"
- 软删过滤：`is_deleted=1` 的运单 / 客户 / 区域 不参与聚合

### 9.2 UI 一致性

- 卡片间距、字号、配色与 `/insight/overview` 视觉一致
- 浏览器宽度 1280/1440/1920 三档无异常
- 浅色/深色主题切换正常（依赖 ele-admin-plus 主题）

### 9.3 多租户隔离

- 切换租户后所有数据重新加载
- 接口不返回跨租户数据

---

## 十、后续迭代规划

| 版本 | 内容 | 备注 |
|------|------|------|
| v1.1 | 接入运输成本字段（油费/路费/外协费） | 依赖成本建模 |
| v1.2 | 毛利与毛利率 KPI 与趋势 | 基于 v1.1 |
| v1.3 | 地图分布（省/市热力） | 依赖 region 经纬度完整度 |
| v2.0 | 增加客户分析/路线分析/车型分析三个独立子页面（驾驶舱兄弟节点） | 钻取与导出 |
| v2.1 | 与智能预测（`/insight/prediction`）联动，预测线与实际线对比 | 依赖预测模块 |

---

## 附录 A：菜单 SQL（幂等）

参见 [backend/scripts/fix/sql/insight_cockpit_menu.sql](../../../backend/scripts/fix/sql/insight_cockpit_menu.sql)，使用 `INSERT ... WHERE NOT EXISTS` 写法，可重复执行。

## 附录 B：UI 参考

UI 风格与现有 [运营看板](../../../frontend/client/src/views/dashboard/analysis/index.vue) 保持一致（统计卡 + 趋势 + 排行 + 词云）。
