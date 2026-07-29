# 智途移动端微信小程序 · 高保真原型设计规范（v2）

> 本规范在 v1（pt-head 文档壳 + TDesign 色板）基础上，融合 [apple-design](.cursor/skills/apple-design) 的物理交互与材质语言，以及 [frontend-design](.cursor/skills/frontend-design) 的业务扎根审美要求。  
> 实现载体：`assets/mp.css` + `assets/mp.js`，双端通过 `body[data-app="driver|admin"]` 换肤。

---

## 1. 设计前提

| 维度 | 驾驶员端 | 后台人员端 |
|------|----------|------------|
| 用户 | 户外作业的司机，单手、强光、网络不稳 | 老板/调度/财务/车队长，碎片时间移动办公 |
| 页面唯一任务 | **现在最该处理的那一件事**（接调令、装车、看钱） | **按角色看最痛的三指标 + 一键进深页** |
| 气质关键词 | 可靠、清晰、行动导向、不花哨 | 专业、克制、数据可信、权限可理解 |

---

## 2. 设计 Token

### 2.1 色彩 Color

**驾驶员端（driver）** — 公路与调度蓝 + 暖橙 urgency

| Token | 色值 | 用途 |
|-------|------|------|
| `--brand` | `#1d4ed8` | 主操作、导航、链接（对齐 `driver-mp/app.json`） |
| `--brand-deep` | `#1e3a8a` | Hero 渐变深部 |
| `--accent-warm` | `#e8871e` | **记忆点**：待办置顶、紧急调令、需立即处理 |
| `--accent-warm-soft` | `#fef3e2` | 暖色提示背景 |
| `--page` | `#f1f4f9` | 页面底色（微冷灰，户外可读） |
| `--card` | `#ffffff` | 卡片表面 |
| `--line` | `rgba(15,23,42,0.06)` | 发丝分割线 |

**后台人员端（admin）** — TDesign 企业蓝 + 中性办公灰

| Token | 色值 | 用途 |
|-------|------|------|
| `--brand` | `#0052d9` | 主色（对齐 TDesign / admin-mp） |
| `--page` | `#f3f3f3` | 页面底 |
| KPI 正/警示 | `--success` / `--warning` / `--danger` | 角色首屏指标语义色 |

**共用语义色**：success / warning / danger / info 仅用于状态，不做装饰渐变。

### 2.2 字体 Type

| 角色 | 字体 | 字号 | 字距 | 行高 |
|------|------|------|------|------|
| 展示（金额、大 KPI） | `--mono`（DIN Alternate / SF Mono） | 28–32px | `-0.02em` | 1.1 |
| 标题（任务名、模块 hd） | `--font` PingFang SC | 16–18px | `-0.015em` | 1.25 |
| 正文 | `--font` | 14px | `0` | 1.55 |
| 标签/Tab/chip | `--font` | 11–12px | `+0.02em` | 1.35 |

原则（apple-design §15）：**大字收紧、小字略放**，禁止全局统一 `letter-spacing`。

### 2.3 间距与圆角

| Token | 值 | 说明 |
|-------|-----|------|
| `--r` | 14px | 卡片 |
| `--r-s` | 10px | 按钮、输入 |
| `--r-xs` | 6px | chip |
| 页面水平边距 | 12px | 与微信小程序惯例一致 |
| 卡片间距 | 10px | 列表密度适中 |

### 2.4 阴影与材质（apple-design §12）

| 层级 | 样式 |
|------|------|
| 卡片 | 轻阴影 + 1px 发丝描边，避免「重 SaaS 阴影」 |
| tabBar / action-bar | **半透明材质**：`backdrop-filter: blur(20px) saturate(180%)` + 白色 78% 透明度 |
| Hero | 165deg 渐变 + 径向深部，内容滚动于其下时 tabBar 仍可读 |
| Sheet / Modal | 背景 dim +  sheet 从底部同路径进出（spatial consistency） |

### 2.5 动效 Motion

| 场景 | 实现 | 参数 |
|------|------|------|
| 按钮/Cell 按下 | `transform: scale(0.97)` | 120ms，`ease-out`，**pointer-down 即反馈** |
| 默认过渡 | opacity / transform | 280ms，`cubic-bezier(0.16,1,0.3,1)` 近似 critically damped |
| 抽屉/Sheet | translateY | 禁止仅 end-state 动画；原型用 CSS 示意 |
| 画廊切屏 | `scrollIntoView smooth` | 键盘 ← → |
| 减少动效 | `@media (prefers-reduced-motion: reduce)` | 改 cross-fade，去掉 scale |

---

## 3. 记忆点 Signature（frontend-design §2.1）

### 驾驶员端：**「待办置顶卡」**

- 左侧 4px `--accent-warm` 竖条 + 白卡片
- 文案直接说业务动作：「新调令待接 · TK031」「回单还没传」
- 不是四个 KPI 数字墙——**一件事比四个数更重要**

### 后台端：**「角色玻璃 KPI 带」**

- Hero 内 KPI 使用半透明白底 + blur（`.kpis .kpi`）
- 调度/老板/财务/车队长四套首屏，同一 tabBar、不同信息优先级
- 老板看风险清单，财务看金额队列，调度看待派与异常

---

## 4. 组件规范

### 4.1 导航

- **tabBar**：4 项固定；未授权 tab 置灰（opacity 0.35），不可进入空白页
- **二级页**：浅色导航 `wx-head.onpage`，返回 ‹ + 标题居中
- **wx-body**：可滚动区；内容与 floating tabBar 之间留 safe-area

### 4.2 反馈四类型（apple-design §16）

| 类型 | 示例 |
|------|------|
| status | 正在确认装车，请稍候… |
| completion | 已成功签收 3 单 |
| warning | 余额为负，请联系财务核对 |
| error | 登记失败，请稍后重试（无 HTTP/字段名） |

### 4.3 任务卡 / 列表

- 状态 chip + 任务号（mono）+ 路线 meta 同行
- 列表默认「进行中」Tab；空态给下一步行动

### 4.4 Sheet / ActionSheet

- 从底弹出，带 handle；驳回/拒单原因必填
- 背景内容 dim + blur，mask 可点关闭

---

## 5. 避免的模板化倾向（frontend-design §3.1）

- ❌ 大渐变 + 三栏统计 + 玻璃拟态到处滥用
- ❌ 纯英文/技术错误码直出
- ❌ 所有模块同一套 KPI 四宫格
- ❌ 无来源的装饰编号
- ✅ 每个模块 `pt-intent` 写清**设计判断**
- ✅ P0/P1/P2 badge 标注与代码差距
- ✅ 演示数据统一：TK031、王建军、皖通汽车物流、李敏/张总/赵倩/陈队

---

## 6. 模块与文件

```text
prototype/移动端/
├── DESIGN.md          ← 本文件
├── 驾驶员微信小程序/   ← 14 × HTML + assets
└── 后台人员微信小程序/ ← 12 × HTML + assets
```

HTML 结构不变：`pt-head` → `pt-gallery`（board × N）→ `pt-rules` → `assets/mp.js`。

---

## 7. 自检清单（交付前）

1. 首屏是否有明确视觉重心？
2. tabBar / action-bar 是否材质化（blur）？
3. 按钮是否有按下缩放反馈？
4. 大字 KPI 是否 negative tracking？
5. 是否支持 `prefers-reduced-motion`？
6. 26 个 HTML 是否均可引用 `assets/mp.css|js`？
7. 驾驶员待办卡是否有暖色左条记忆点？
8. 后台四套角色首屏是否信息优先级不同？

---

## 8. 参考

- 产品需求：`doc/02.需求文档/03.移动端/02.驾驶员H5端/`
- 实现对照：`frontend/driver-mp/`、`frontend/admin-mp/`
- 交互技能：`.cursor/skills/apple-design/SKILL.md`
- 视觉技能：`.cursor/skills/frontend-design/SKILL.md`

---

## 9. 设备壳 v3（iPhone 15 + 微信官方顶栏）

| 组件 | 规格 |
|------|------|
| 外框 | 钛金属渐变 bezel，54px 圆角，侧键/电源键伪元素 |
| 内屏 | 375×812，46px 圆角 |
| Dynamic Island | 122×34px，居中，含摄像头点缀 |
| Home Indicator | 134×5px 底部横条 |
| 状态栏 | 高 47px，SF Pro 时间 + 信号/WiFi/电池 SVG |
| 微信胶囊 | 87×32px，0.5px 描边，三点 + 分隔 + 关闭圆环 |
| 导航栏 | 高 44px，标题 17px/600，返回 ‹ 左对齐 |

运行时由 `assets/mp.js` 的 `wrapDevices()` + `buildChrome()` 自动注入，HTML 只需保留：

```html
<div class="dev">
  <div class="wx-head onpage">
    <div class="wx-nav" data-back><span class="ttl">页面标题</span></div>
  </div>
  <div class="wx-body scroll">...</div>
</div>
```
