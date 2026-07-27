# 智途管理员微信小程序

面向租户用户（老板、财务、调度等）的原生微信小程序，承接租户端高频操作与经营数据查看。

与驾驶员端（`frontend/driver-mp`）统一使用 [TDesign 小程序](https://tdesign.tencent.com/miniprogram/getting-started)。

## 技术约定

- **原生小程序**：WXML + WXSS + JS
- **UI**：`tdesign-miniprogram`
- **鉴权**：规划为 `Authorization: Bearer <JWT>`，租户在 JWT 的 `tenant_code` 内
- **API**：规划复用租户 Web 前缀 `/api/client/*`（当前脚手架为演示登录）

## 快速开始

1. 安装依赖并构建 npm 组件：

```bash
cd frontend/admin-mp
npm install
npm run build:npm
```

也可在微信开发者工具中执行：`工具 → 构建 npm`。

2. 用微信开发者工具导入本目录（`frontend/admin-mp`）
3. AppID 可先用测试号；正式环境替换 `project.config.json` 中的 `appid`
4. 开发阶段建议保持 `project.private.config.json` 里 `urlCheck: false`
5. 修改 [`config/env.js`](config/env.js) 中的 `API_BASE`（真机勿用 localhost）

本地设置请勾选：**将 JS 编译成 ES5**（TDesign 需要）。

## 目录结构

```
admin-mp/
├── app.js / app.json / app.wxss
├── config/env.js
├── utils/                 # request / storage / auth
├── api/                   # 接口封装（逐步补齐）
├── pages/                 # home / login / profile
├── scripts/build-npm.js   # 无开发者工具时的 npm 构建
└── assets/icons/          # tabBar 图标
```

## 当前进度

| 能力 | 状态 |
|------|------|
| 工程骨架 + TDesign | ✅ |
| 演示登录 / 工作台 / 我的 | ✅ 占位 |
| 经营数据看板 | ⏳ 待接入 |
| 调度 / 财务高频操作 | ⏳ 待接入 |
| 真实租户鉴权 | ⏳ 待对接 |

## 与驾驶员端关系

| 项目 | 目录 | 用户 | API |
|------|------|------|-----|
| 驾驶员端 | `frontend/driver-mp` | 司机 | `/api/driver` |
| 管理员端 | `frontend/admin-mp` | 老板/财务/调度等 | `/api/client`（规划） |
