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
5. 真机调试：复制 [`config/env.local.example.js`](config/env.local.example.js) 为 `config/env.local.js`，把地址改成电脑局域网 IP（不要写 `localhost`）
6. 确保后端已启动并监听 `0.0.0.0:8000`

本地设置请勾选：**将 JS 编译成 ES5**（TDesign 需要）。

## 常见问题

### 模拟器能访问后端，真机调试不行

手机上的 `localhost` 是手机自己，不是你的电脑。

1. 复制 `config/env.local.example.js` → `config/env.local.js`，填电脑局域网 IP（`ipconfig` 看 WLAN 的 IPv4）
2. 手机和电脑连**同一 Wi-Fi**（不要用手机热点的另一段网，也不要用 VPN 的 `10.x` 地址）
3. 后端必须监听 `0.0.0.0`，例如：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4. 开发者工具勾选：**不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**
5. Windows 防火墙放行 8000 端口；改完 `env.local.js` 后重新编译再点真机调试

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
