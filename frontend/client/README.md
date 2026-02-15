# 智途(ZhiTu) 客户端前端（Client）

企业客户使用的业务系统前端，基于 EleAdminPlus 模板开发。

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

# 启动开发服务器（端口 5174）
npm run dev

# 生产构建
npm run build
```

访问地址：http://localhost:5174

> 注意：Client 登录需要先通过 Console 管理后台创建企业和企业超管账号。

## 目录结构

```
src/
├── api/                    # API 接口层
│   ├── login/             # 认证 API
│   ├── layout/            # 布局/用户信息 API
│   ├── system/            # 系统管理 API（user, role, menu, dict, file 等）
│   └── dashboard/         # 仪表盘 API
├── views/                 # 页面组件
│   ├── login/             # 登录页（支持多租户选择）
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
├── components/            # 共享组件
├── layout/                # 布局组件（ele-pro-layout 封装）
├── store/modules/         # Pinia 状态管理
│   ├── user.ts            # 用户信息、菜单、权限
│   ├── theme.ts           # 主题配置
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

## 已实现页面

### 已对接后端的业务页面

| 页面 | 说明 | 后端 API 状态 |
|------|------|--------------|
| 登录 | 支持多租户选择，手机号关联多企业时显示企业列表 | ✅ 已对接 |

### 前端就绪、待对接后端的页面

以下页面前端 UI 已就绪（基于 EleAdminPlus 模板），后端 Client CRUD API 尚未实现：

| 页面 | 说明 |
|------|------|
| 用户管理 | 用户列表、搜索、CRUD、状态、密码重置、导入 |
| 角色管理 | 角色列表、CRUD、菜单权限分配 |
| 菜单管理 | 菜单树、CRUD |
| 组织架构 | 组织树管理 |
| 数据字典 | 字典 + 字典项管理 |
| 文件管理 | 文件上传记录 |
| 操作记录 | 操作日志查看 |
| 登录记录 | 登录日志查看 |
| 用户中心 | 个人资料、账号设置 |
| 仪表盘 | 数据分析、系统监控、工作台 |

### 待开发的业务页面

以下为核心业务页面，后端已有 ORM 模型但 API 和前端页面均未开发：

| 页面 | 后端模型 | 说明 |
|------|----------|------|
| 车辆管理 | `Vehicle` | 车辆信息 CRUD、状态管理 |
| 驾驶员管理 | `Driver` | 驾驶员信息 CRUD、关联用户 |
| 运单管理 | `Order` | 运单全生命周期管理 |
| 路线管理 | `Route` | 路线信息 CRUD |
| 客户管理 | `Customer` | 客户信息 CRUD |
| 结算管理 | - | 无模型，规划中 |
| 数据统计 | - | 无后端，规划中 |

### 模板演示页面

当前项目包含 EleAdminPlus 模板自带的演示页面（位于 `views/form`、`views/list`、`views/extension` 目录），这些页面在业务开发过程中将逐步替换或移除。

## API 对接

- 基路径：`/api/client`（开发环境通过 Vite Proxy 代理到 `http://localhost:8000`）
- 认证：`Authorization: Bearer {token}`
- 响应拦截：401 跳转登录，Token 自动刷新

## 环境变量

| 变量 | 说明 |
|------|------|
| `VITE_API_URL` | API 基路径（默认 `/api/client`） |
| `VITE_API_PROXY_URL` | 开发代理目标（默认 `http://localhost:8000`） |
