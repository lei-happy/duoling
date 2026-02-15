# 智途(ZhiTu) 管理后台前端（Console）

平台运营团队使用的管理系统前端，基于 EleAdminPlus 模板开发。

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5.x | Composition API + `<script setup>` |
| TypeScript | 5.9.x | 全面类型支持 |
| Element Plus | 2.11.x | UI 组件库 |
| EleAdminPlus | - | 后台管理模板框架 |
| Pinia | 3.0.x | 状态管理 |
| Vue Router | 4.5.x | 路由（动态路由 + 菜单驱动） |
| Vite | 7.1.x | 构建工具 |
| Axios | 1.12.x | HTTP 客户端 |
| ECharts | 5.6.x | 图表 |
| Vue I18n | 11.x | 国际化（zh_CN / zh_TW / en） |

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器（端口 5173）
npm run dev

# 生产构建
npm run build
```

访问地址：http://localhost:5173

## 目录结构

```
src/
├── api/                    # API 接口层
│   ├── login/             # 认证 API
│   ├── layout/            # 布局/用户信息 API
│   ├── tenant/            # 租户管理 API
│   ├── system/            # 系统管理 API（user, role, menu, dict, file 等）
│   └── dashboard/         # 仪表盘 API
├── views/                 # 页面组件
│   ├── login/             # 登录页
│   ├── tenant/            # 租户管理（列表、编辑、产品授权）
│   ├── system/            # 系统管理
│   │   ├── user/          # 用户管理
│   │   ├── role/          # 角色管理
│   │   ├── menu/          # 菜单管理
│   │   ├── organization/  # 组织架构
│   │   ├── dictionary/    # 数据字典
│   │   ├── file/          # 文件管理
│   │   ├── operation-record/ # 操作记录
│   │   └── login-record/  # 登录记录
│   ├── dashboard/         # 仪表盘（analysis, monitor, workplace）
│   ├── user/              # 用户中心（profile, message）
│   └── exception/         # 异常页（403, 404, 500）
├── components/            # 共享组件（24+）
├── layout/                # 布局组件（ele-pro-layout 封装）
├── store/modules/         # Pinia 状态管理
│   ├── user.ts            # 用户信息、菜单、权限
│   ├── theme.ts           # 主题配置（持久化 + 服务端同步）
│   ├── tab.ts             # 标签页管理
│   ├── dict.ts            # 数据字典缓存
│   └── notice.ts          # 通知消息
├── router/                # 路由（动态路由生成）
├── utils/                 # 工具函数
│   ├── request.ts         # Axios 实例（Token 注入、401 处理）
│   ├── permission.ts      # 权限指令（v-role, v-permission）
│   ├── use-permission.ts  # 权限 Hook
│   └── token-util.ts      # Token 管理
├── i18n/                  # 国际化语言包
├── styles/                # 全局样式
└── config/                # 配置文件
```

## 已实现业务页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 登录 | `/login` | 平台管理员登录 |
| 租户管理 | 动态菜单 | 租户列表、搜索、CRUD、状态管理、产品版本授权 |
| 用户管理 | 动态菜单 | 用户列表、搜索、CRUD、状态、密码重置、导入 |
| 角色管理 | 动态菜单 | 角色列表、CRUD、菜单权限分配 |
| 菜单管理 | 动态菜单 | 菜单树、CRUD、图标选择 |
| 组织架构 | 动态菜单 | 组织树管理（后端 API 为 stub） |
| 数据字典 | 动态菜单 | 字典 + 字典项管理 |
| 文件管理 | 动态菜单 | 文件上传记录 |
| 操作记录 | 动态菜单 | 操作日志查看（后端 API 待对接） |
| 登录记录 | 动态菜单 | 登录日志查看（后端 API 待对接） |
| 用户中心 | `/user/profile` | 个人资料、账号设置 |
| 仪表盘 | 动态菜单 | 数据分析、系统监控、工作台 |

## API 对接

- 基路径：`/api/console`（开发环境通过 Vite Proxy 代理到 `http://localhost:8000`）
- 认证：`Authorization: Bearer {token}`
- 响应拦截：401 跳转登录，Token 自动刷新

## 环境变量

| 变量 | 说明 |
|------|------|
| `VITE_API_URL` | API 基路径（默认 `/api/console`） |
| `VITE_API_PROXY_URL` | 开发代理目标（默认 `http://localhost:8000`） |

## 默认账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| admin | admin123 | 超级管理员 |
