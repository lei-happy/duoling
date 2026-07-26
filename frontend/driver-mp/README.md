# 智途驾驶员微信小程序

面向驾驶员（`user_type=3`）的原生微信小程序，与 H5（`frontend/driver-h5`）共用后端 `/api/driver/*`。

## 技术约定

- **原生小程序**：WXML + WXSS + JS，无 uni-app / Taro / Vant Weapp
- **鉴权**：`Authorization: Bearer <JWT>`，租户在 JWT 的 `tenant_code` 内
- **打开方式**：用[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)导入本目录

## 快速开始

1. 安装并打开微信开发者工具
2. 「导入项目」→ 选择 `frontend/driver-mp`
3. AppID 可先用测试号；正式环境替换 `project.config.json` 中的 `appid`
4. 开发阶段建议保持 `project.private.config.json` 里 `urlCheck: false`（不校验合法域名）
5. 修改 [`config/env.js`](config/env.js) 中的 `API_BASE`：
   - 模拟器可用 `http://localhost:8000/api/driver`
   - 真机请改为电脑局域网 IP，例如 `http://192.168.1.8:8000/api/driver`
6. 确保后端已启动（默认 `http://localhost:8000`）

## 目录结构

```
driver-mp/
├── app.js / app.json / app.wxss
├── config/env.js           # 环境基地址
├── utils/                  # request / storage / auth / format / constants
├── api/                    # 与 H5 对齐的接口封装
├── services/session.js     # 登录会话
├── components/             # 自研组件
├── pages/                  # 业务页面
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
