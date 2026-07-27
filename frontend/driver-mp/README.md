# 智途驾驶员微信小程序

面向驾驶员（`user_type=3`）的原生微信小程序，与 H5（`frontend/driver-h5`）共用后端 `/api/driver/*`。

## 技术约定

- **原生小程序**：WXML + WXSS + JS，无 uni-app / Taro
- **UI**：[TDesign 小程序](https://tdesign.tencent.com/miniprogram/getting-started)（`tdesign-miniprogram`）
  - 全局组件见 `app.json` → `usingComponents`（button / input / cell / tabs / dialog / upload 等）
  - 业务组件（`task-card`、`status-tag`、`empty-state`、`bottom-action-bar`）内部已基于 TDesign
- **鉴权**：`Authorization: Bearer <JWT>`，租户在 JWT 的 `tenant_code` 内
- **打开方式**：用[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)导入本目录

## 快速开始

1. 安装并打开微信开发者工具
2. 在本目录安装依赖并构建 npm 组件：

```bash
cd frontend/driver-mp
npm install
npm run build:npm
```

也可在开发者工具中执行：`工具 → 构建 npm`。

3. 「导入项目」→ 选择 `frontend/driver-mp`
4. AppID 可先用测试号；正式环境替换 `project.config.json` 中的 `appid`
5. 开发阶段建议保持 `project.private.config.json` 里 `urlCheck: false`（不校验合法域名）
6. 修改 [`config/env.js`](config/env.js) 中的 `API_BASE`：
   - 模拟器可用 `http://localhost:8000/api/driver`
   - 真机请改为电脑局域网 IP，例如 `http://192.168.1.8:8000/api/driver`
7. 确保后端已启动（默认 `http://localhost:8000`）
8. 本地设置请勾选：**将 JS 编译成 ES5**（TDesign 需要）

## 常见问题

### 真机调试报 `Cannot find module 'tslib'`

**根因（已核实）**：微信开发者工具 `2.01.2510260` 安装目录里的编译器一加载就会 `require('tslib')`，但  
`C:\Program Files (x86)\Tencent\微信web开发者工具\code\package.nw\node_modules\`  
下**缺少 `tslib` 包**。这是工具安装不完整/损坏，不是小程序业务代码问题。关「增强编译」、清缓存都解决不了。

**推荐修复（补装到工具目录，需管理员权限）**：

1. 先在本目录执行：`npm install` 与 `npm run build:npm`
2. **右键以管理员身份运行** [`scripts/fix-devtools-tslib.bat`](scripts/fix-devtools-tslib.bat)  
   （或管理员 PowerShell 执行 `scripts/fix-devtools-tslib.ps1`）
3. **完全退出**微信开发者工具（托盘图标也退出）后重新打开
4. 再点真机调试

手动复制也可以：把 `frontend/driver-mp/node_modules/tslib` 整个文件夹复制到上述 `node_modules` 下。

**临时绕过**：用顶部「预览」扫码真机看效果（不走同一条真机调试编译链路）。

### 构建 npm 后组件找不到

确认已生成 `miniprogram_npm/tdesign-miniprogram/`。若仍报错，在开发者工具中再执行一次「构建 npm」，并勾选「将 JS 编译成 ES5」。

### 模拟器启动失败 / `EMFILE: too many open files`

**原因**：项目根目录同时存在完整 `node_modules`（TDesign 文件极多）时，开发者工具监听文件过多，句柄耗尽。

**处理**：

1. **完全退出**微信开发者工具（托盘图标也退出）
2. 确保已执行过 `npm run build:npm`（存在 `miniprogram_npm/`）
3. 删除本目录下的 `node_modules`（运行时只用 `miniprogram_npm`，可不保留）
4. 重新打开项目 → 清缓存 → 编译

```bash
cd frontend/driver-mp
npm run build:npm
# 然后删除 node_modules 再打开开发者工具
Remove-Item -Recurse -Force node_modules
```

需要重新安装/构建组件时再执行：`npm install && npm run build:npm`。

## 目录结构

```
driver-mp/
├── app.js / app.json / app.wxss
├── config/env.js           # 环境基地址
├── utils/                  # request / storage / auth / format / constants
├── api/                    # 与 H5 对齐的接口封装
├── services/session.js     # 登录会话
├── components/             # 业务组件（内部已用 TDesign）
├── pages/                  # 业务页面
├── scripts/build-npm.js    # 无开发者工具时的 npm 构建
└── assets/icons/           # tabBar 图标
```

## 功能范围（与 H5 对等）

- 登录：手机号+密码 / 短信验证码 / 多企业选择 / 强制改密 / 切换企业
- 工作台：KPI、快捷入口、近期任务
- 任务：列表、详情、接拒调令、装车/出发/到达、逐单签收、回单上传
- 财务：费用单、详情、收入汇总、收款账户、资金往来账
- 个人中心：资料查看与白名单编辑

## 上线清单

1. 微信公众平台配置 **request 合法域名**、**uploadFile 合法域名**（HTTPS）
2. 将 `config/env.js` 的 trial / release 地址改为正式 API
3. 关闭开发工具「不校验合法域名」后做一轮真机验收

## 与后端关系

| 能力 | 说明 |
|------|------|
| 业务 API | 直接复用 `/api/driver/*`，无需新建小程序专用树 |
| 短信 | `/api/open/sms/send`（与 H5 相同） |
| 微信一键登录 | 未做；后续可加 openid 绑定，业务接口不变 |
