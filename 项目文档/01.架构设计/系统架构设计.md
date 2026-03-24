# 智途(ZhiTu) 系统架构设计文档

> **最后更新**：2026-02-15
>
> 本文档反映代码仓库的实际实现状态。功能状态标记说明：
> - ✅ 已完成（前后端均已实现）
> - 🔧 部分完成（后端或前端部分实现）
> - 📐 仅模型/设计（ORM 模型或 SQL 已定义，业务逻辑未实现）
> - 📋 规划中（列入计划但无代码实现）

## 1. 概述

智途是一个面向物流车队行业的 SaaS + PaaS 综合操作系统。平台提供统一的基础架构和管理后台，各企业客户在统一的产品体系下使用独立的数据库进行业务操作。

## 2. 系统组成

### 2.1 产品官网（Website） ✅

面向潜在客户的公开网站，所有页面均已实现：

| 页面 | 路由 | 状态 | 说明 |
|------|------|------|------|
| 首页 | `/` | ✅ | Hero 动画、核心功能卡片、数据指标、优势展示、CTA |
| 产品功能 | `/features` | ✅ | 5 大功能亮点（AI 助理、全链路管理、成本在线、智能 BI、移动办公） |
| 价格方案 | `/pricing` | ✅ | 3 档定价（免费版/基础版/旗舰版）、功能对比表、FAQ |
| 企业注册 | `/register` | ✅ | 独立全屏布局、注册表单、支持推荐码、成功弹窗 |
| 关于我们 | `/about` | ✅ | 使命愿景、核心价值观、团队介绍、联系方式 |

技术特点：独立轻量级 Vue 3 项目，不依赖 EleAdminPlus 后台模板，使用 Element Plus 基础组件 + 自定义 SCSS 设计系统。支持滚动动画（Intersection Observer）、响应式布局、粒子特效。

API 集成：通过 `/api/open` 调用后端开放接口（企业注册、产品版本查询）。

### 2.2 管理后台（Console） 🔧

平台运营团队使用的管理系统：

| 功能模块 | 状态 | 后端 API | 前端页面 | 说明 |
|----------|------|----------|----------|------|
| 认证登录 | ✅ | `/api/console/auth` | 登录页 | 登录、用户信息、主题配置 |
| 租户管理 | ✅ | `/api/console/tenant` | 租户列表 | CRUD、状态管理、产品授权、数据库初始化 |
| 产品版本管理 | ✅ | `/api/console/product-version` | - | CRUD（前端页面通过租户管理页集成） |
| 用户管理 | ✅ | `/api/console/system/user` | 用户管理页 | CRUD、状态管理、密码重置、批量删除 |
| 角色管理 | ✅ | `/api/console/system/role` | 角色管理页 | CRUD、批量删除 |
| 菜单管理 | ✅ | `/api/console/system/menu` | 菜单管理页 | 树形 CRUD |
| 角色菜单分配 | ✅ | `/api/console/system/role-menu` | 角色权限弹窗 | 查询/更新角色菜单 |
| 数据字典 | ✅ | `/api/console/system/dictionary` | 字典管理页 | 字典 + 字典项 CRUD |
| 字典数据 | ✅ | `/api/console/system/dictionary-data` | 字典数据页 | 字典项 CRUD、批量删除 |
| 组织架构 | 🔧 | `/api/console/system/organization` | 组织架构页 | API 为 stub 实现（返回空数据），前端页面已就绪 |
| 意见反馈 | 📐 | - | - | 仅有 `Feedback` 数据模型，API 和前端未实现 |
| 操作日志 | 📐 | - | 操作记录页 | 有 `OperationLog` 模型，API 路由未注册，前端页面已就绪（待对接） |
| 登录日志 | 📋 | - | 登录记录页 | 无后端实现，前端页面已就绪（待对接） |

**使用流程**：平台管理员在 Console 中创建企业 → 系统自动初始化企业独立数据库 → 创建企业超管账号 → 企业超管登录 Client 客户端

### 2.3 客户端（Client） 🔧

企业客户使用的业务系统：

| 功能模块 | 状态 | 后端 API | 前端页面 | 说明 |
|----------|------|----------|----------|------|
| 认证登录 | ✅ | `/api/client/auth` | 登录页 | 登录（支持多租户选择）、用户信息、修改密码 |
| 用户管理 | 🔧 | - | 用户管理页 | 前端页面已就绪，后端 Client 端用户 CRUD API 待实现 |
| 角色管理 | 🔧 | - | 角色管理页 | 前端页面已就绪，后端 API 待实现 |
| 菜单管理 | 🔧 | - | 菜单管理页 | 前端页面已就绪，后端 API 待实现 |
| 组织架构 | 🔧 | - | 组织架构页 | 前端页面已就绪，后端 API 待实现 |
| 数据字典 | 🔧 | - | 字典管理页 | 前端页面已就绪，后端 API 待实现 |
| 车辆管理 | 📐 | - | - | ORM 模型已定义（`Vehicle`），API / 前端待开发 |
| 驾驶员管理 | 📐 | - | - | ORM 模型已定义（`Driver`），API / 前端待开发 |
| 运单管理 | 📐 | - | - | ORM 模型已定义（`Order`），API / 前端待开发 |
| 路线管理 | 📐 | - | - | ORM 模型已定义（`Route`），API / 前端待开发 |
| 客户管理 | 📐 | - | - | ORM 模型已定义（`Customer`），API / 前端待开发 |
| 结算管理 | 📋 | - | - | 无模型、无代码，列入后续规划 |
| 数据统计 | 📋 | - | - | 无后端实现，前端有 Dashboard 模板页（待对接实际数据） |

**Console 与 Client 的共同功能**：用户管理、角色管理、菜单管理、组织架构管理在两端功能一致，区别在于 Console 操作平台库（zt_platform），Client 操作对应的租户业务库（zt_biz_{code}）。

> **注意**：Client 前端目前基于 EleAdminPlus 模板，包含大量模板自带的演示页面（form、list、extension 等），这些演示页面将在业务页面开发过程中逐步替换或移除。

### 2.4 微信小程序 📋

- 管理人员端：移动审批、报表查看、消息通知
- 驾驶员端：接单、签到、位置上报、电子回单

> 小程序部分为远期规划，暂无代码实现。技术预选 UniApp。

## 3. 多租户架构

### 3.1 数据隔离策略

采用 **独立数据库** 方式实现租户数据隔离：

- 每个企业拥有独立的 MySQL 数据库
- 数据库命名规则：`zt_biz_{tenant_code}` + 环境后缀
- 优点：数据完全隔离、安全性高、便于数据备份和迁移
- 缺点：数据库数量随租户增长、运维复杂度增加

### 3.2 数据库环境命名规则

| 环境 | 平台库 | 租户库示例 | 配置项 |
|------|--------|-----------|--------|
| 开发环境 | zt_platform_ci | zt_biz_1001_ci | DB_SUFFIX=_ci |
| 生产环境 | zt_platform | zt_biz_1001 | DB_SUFFIX= |

通过 `.env` 中的 `DB_SUFFIX` 统一控制，避免开发和生产数据库混淆。

### 3.3 数据库切换机制

1. 用户登录时，JWT Token 中携带 `tenant_code`
2. 每个请求经过租户中间件（`TenantMiddleware`），解析 Token 获取租户编码
3. 数据库管理器根据租户编码获取/创建对应的数据库引擎
4. 通过 FastAPI 依赖注入（`get_platform_db` / `get_tenant_db`）将正确的数据库 Session 传递给业务层

### 3.4 连接池管理

- 平台主库：固定连接池（pool_size=20, max_overflow=10）
- 租户业务库：按需创建连接池并缓存（pool_size=10, max_overflow=5）
- 连接池回收时间：3600秒
- 启用 pool_pre_ping 防止连接断开

## 4. 后端架构

### 4.1 分层结构

```
API 路由层 (api/) → 业务服务层 (services/) → 数据模型层 (models/)
     ↑                    ↑                        ↑
  Schemas 校验        异常处理/日志            SQLAlchemy ORM
```

### 4.2 模块划分

- **console**：管理后台模块。操作平台主库（zt_platform）。
  - 已实现：认证、租户管理、用户管理、角色管理、菜单管理、角色菜单分配、产品版本管理、数据字典管理
  - 部分实现：组织架构（stub）
  - 待实现：意见反馈 CRUD、操作日志查询、登录日志查询
- **client**：客户端模块。操作租户业务库（zt_biz_{code}）。
  - 已实现：认证（登录、用户信息、修改密码）
  - 已定义模型：BizUser、BizRole、BizMenu、Vehicle、Driver、Order、Route、Customer
  - 待实现：全部业务 CRUD API（schemas / services / api 均为空）
- **open**：开放接口模块。无需登录认证。
  - 已实现：企业自助注册、产品版本公开查询、忘记密码（stub）
- **common**：公共组件（响应格式 `success`/`fail`、异常处理、分页 `PageResult`、枚举、工具函数）
- **core**：核心基础设施（配置 `Settings`、安全 JWT、数据库管理器、中间件、依赖注入）

### 4.3 API 路径设计

| 路径前缀 | 说明 | 认证方式 | 数据库 |
|----------|------|----------|--------|
| /api/console/* | 管理后台接口 | JWT（平台管理员） | zt_platform |
| /api/client/* | 客户端接口 | JWT（租户用户） | zt_biz_{code} |
| /api/open/* | 开放接口 | 无需认证 | zt_platform |

### 4.4 已实现 API 端点清单

#### Console 模块（`/api/console`）

**认证** `/api/console/auth`：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 平台管理员登录 |
| GET | `/auth/user-info` | 获取当前用户信息（含角色、菜单、权限） |
| PUT | `/auth/user-theme` | 更新用户主题配置 |

**租户管理** `/api/console/tenant`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tenant/page` | 分页查询租户列表 |
| GET | `/tenant/{tenant_id}` | 获取租户详情 |
| POST | `/tenant` | 创建租户（自动初始化数据库） |
| PUT | `/tenant` | 更新租户信息 |
| DELETE | `/tenant/batch` | 批量删除租户 |
| PUT | `/tenant/status` | 更新租户状态（启用/停用） |
| GET | `/tenant/{tenant_id}/products` | 获取租户已授权产品列表 |
| POST | `/tenant/{tenant_id}/products` | 为租户授权产品版本 |
| DELETE | `/tenant/{tenant_id}/products/{product_id}` | 移除租户产品授权 |

**用户管理** `/api/console/system/user`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/user/page` | 分页查询用户列表 |
| GET | `/system/user/existence` | 检查字段唯一性（用户名/手机号等） |
| GET | `/system/user/{user_id}` | 根据 ID 获取用户 |
| GET | `/system/user` | 查询用户列表 |
| POST | `/system/user` | 创建用户 |
| PUT | `/system/user` | 更新用户 |
| DELETE | `/system/user/batch` | 批量删除用户 |
| PUT | `/system/user/status` | 更新用户状态 |
| PUT | `/system/user/password` | 重置用户密码 |

**菜单管理** `/api/console/system/menu`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/menu` | 查询菜单列表（树形） |
| GET | `/system/menu/page` | 分页查询菜单 |
| POST | `/system/menu` | 创建菜单 |
| PUT | `/system/menu` | 更新菜单 |
| DELETE | `/system/menu/{menu_id}` | 删除菜单 |

**角色管理** `/api/console/system/role`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/role/page` | 分页查询角色 |
| GET | `/system/role` | 查询角色列表 |
| POST | `/system/role` | 创建角色 |
| PUT | `/system/role` | 更新角色 |
| DELETE | `/system/role/batch` | 批量删除角色 |
| DELETE | `/system/role/{role_id}` | 删除单个角色 |

**角色菜单分配** `/api/console/system/role-menu`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/role-menu/{role_id}` | 获取角色已分配菜单 |
| PUT | `/system/role-menu/{role_id}` | 更新角色菜单分配 |

**组织架构** `/api/console/system/organization`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/organization` | 查询组织列表（stub，返回空） |
| GET | `/system/organization/tree` | 查询组织树（stub，返回空） |

**产品版本** `/api/console/product-version`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/product-version` | 查询产品版本列表 |
| GET | `/product-version/{version_id}` | 获取版本详情 |
| POST | `/product-version` | 创建产品版本 |
| PUT | `/product-version/{version_id}` | 更新产品版本 |
| DELETE | `/product-version/{version_id}` | 删除产品版本 |

**数据字典** `/api/console/system/dictionary`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/dictionary/page` | 分页查询字典 |
| GET | `/system/dictionary` | 查询字典列表 |
| POST | `/system/dictionary` | 创建字典 |
| PUT | `/system/dictionary` | 更新字典 |
| DELETE | `/system/dictionary/{dict_id}` | 删除字典 |

**字典数据** `/api/console/system/dictionary-data`：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system/dictionary-data/page` | 分页查询字典项 |
| GET | `/system/dictionary-data` | 查询字典项列表 |
| POST | `/system/dictionary-data` | 创建字典项 |
| PUT | `/system/dictionary-data` | 更新字典项 |
| DELETE | `/system/dictionary-data/batch` | 批量删除字典项 |
| DELETE | `/system/dictionary-data/{dict_data_id}` | 删除单个字典项 |

#### Client 模块（`/api/client`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 客户端登录（支持多租户选择） |
| GET | `/auth/user-info` | 获取当前用户信息（含角色、菜单、权限） |
| PUT | `/auth/password` | 修改密码（支持首次登录强制修改） |

> Client 模块的业务 CRUD API（车辆、驾驶员、运单等）尚未实现，路由预留在 `client/api/__init__.py` 注释中。

#### Open 模块（`/api/open`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 企业自助注册（创建租户 + 初始化数据库） |
| POST | `/forgot-password` | 忘记密码（stub，待实现） |
| GET | `/product/versions` | 查询公开产品版本列表 |

#### 其他端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/docs` | Swagger API 文档 |
| GET | `/redoc` | ReDoc API 文档 |

### 4.5 中间件

| 中间件 | 说明 |
|--------|------|
| CORSMiddleware | 跨域资源共享，允许的 Origins 通过 `CORS_ORIGINS` 环境变量配置 |
| RequestLogMiddleware | 请求日志，记录请求方法、路径、状态码、耗时 |
| TenantMiddleware | 租户中间件，从 JWT Token 解析 `tenant_code` 注入 `request.state`；跳过登录、开放接口、文档等路径 |

## 5. 接入层与网关设计

### 5.1 当前方案

当前阶段（0-1），不引入独立的 API 网关服务（如 Kong、APISIX），原因：

- FastAPI 自身已具备路由分组、中间件（认证、日志、跨域）能力
- 当前只有一个后端服务进程，不存在微服务间路由问题
- 引入独立网关增加运维复杂度，对初期开发效率无明显提升

**Nginx 充当轻量级网关角色**，负责：

- 反向代理（将请求转发到后端服务）
- 负载均衡（未来多实例部署时）
- SSL/TLS 终止
- 静态资源缓存和分发
- 基础的请求限流（limit_req）

### 5.2 架构演进路径

```
阶段1（当前）: 客户端 → Nginx → FastAPI（单进程）
阶段2（中期）: 客户端 → Nginx → FastAPI（多 Worker）
阶段3（远期）: 客户端 → API 网关(Kong) → FastAPI-Console | FastAPI-Client | FastAPI-Open
```

当出现以下需求时，考虑引入独立 API 网关：

- 后端拆分为多个独立微服务
- 需要开放第三方 API 并做 API Key / OAuth / 限流管理
- 需要跨服务的统一认证、灰度发布、流量染色等高级能力

## 6. 前端架构

### 6.1 技术选型

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5.x | 组合式 API（Composition API + `<script setup>`） |
| TypeScript | 5.9.x | 全面类型支持 |
| Element Plus | 2.11.x | UI 组件库 |
| EleAdminPlus | - | 后台管理模板框架（Console/Client 共用） |
| Pinia | 3.0.x | 状态管理 |
| Vue Router | 4.5.x | 路由管理 |
| Vite | 7.1.x | 构建工具 |
| Axios | 1.12.x | HTTP 客户端 |
| ECharts | 5.6.x | 图表库 |
| Vue I18n | 11.x | 国际化（zh_CN / zh_TW / en） |
| Sass | 1.93.x | CSS 预处理 |

### 6.2 项目划分

| 项目 | 目录 | 端口 | API 基路径 | 说明 |
|------|------|------|-----------|------|
| 产品官网 | frontend/website | 5175 | `/api/open` | 产品展示、企业自助注册 |
| 管理后台 | frontend/console | 5173 | `/api/console` | 平台运营管理（基于 EleAdminPlus 模板） |
| 客户端 | frontend/client | 5174 | `/api/client` | 企业业务操作（基于 EleAdminPlus 模板） |
| 模板 | frontend/template | - | - | EleAdminPlus 原始模板，不直接部署 |
| 共享组件 | frontend/components | - | - | 跨项目共享的前端组件库 |

### 6.3 产品官网（Website）

独立轻量级 Vue 3 项目，不依赖 EleAdminPlus 后台模板。

**页面结构**：

| 页面 | 路由 | 组件 | 布局 |
|------|------|------|------|
| 首页 | `/` | `Home.vue` | 标准（Header + Footer） |
| 产品功能 | `/features` | `Features.vue` | 标准 |
| 价格方案 | `/pricing` | `Pricing.vue` | 标准 |
| 关于我们 | `/about` | `About.vue` | 标准 |
| 企业注册 | `/register` | `Register.vue` | 全屏（无 Header/Footer） |

**技术特点**：
- 路由懒加载，HTML5 History 模式
- 滚动动画（`useScrollAnimation` composable，基于 Intersection Observer）
- 自定义 SCSS 设计系统（CSS 变量、渐变、阴影、圆角等设计 Token）
- 响应式设计（断点 768px / 1024px）
- 导航栏滚动透明度变化效果
- 注册支持推荐码（URL 参数 `?ref=xxx`）
- 环境变量 `VITE_CLIENT_URL` 配置客户端跳转地址

### 6.4 管理后台（Console）与客户端（Client）

Console 和 Client 均基于 EleAdminPlus 模板开发，共享相同的技术架构：

**公共架构**：
- 布局组件 `ele-pro-layout`：支持多种布局模式（侧边栏、顶部导航、混合等 30+ 预设）
- 动态路由：后端返回菜单数据 → 前端生成路由 → 自动匹配 `views/` 下的组件
- Tab 页管理：多标签页导航 + Keep-Alive 缓存
- 主题系统：深色模式、自定义主题色、圆角、皮肤背景
- 国际化：zh_CN / zh_TW / en 三语言

**Pinia 状态管理**：

| Store | 职责 |
|-------|------|
| User Store | 用户信息、菜单、权限标识、角色 |
| Theme Store | 布局配置、主题色、深色模式（持久化到 localStorage + 服务端同步） |
| Tab Store | 标签页列表、Keep-Alive 缓存管理 |
| Dict Store | 数据字典缓存（Map 结构） |
| Notice Store | 通知、私信、待办（本地数据） |

**权限系统**：
- RBAC 基于角色的访问控制
- 权限指令：`v-role`、`v-any-role`、`v-permission`、`v-any-permission`
- 权限 Hook：`usePermission()` 提供 `hasPermission()` / `hasRole()` 等方法
- 路由守卫：Token 验证 → 用户信息加载 → 动态路由生成
- 菜单可见性由后端菜单数据控制

**API 层**：
- 统一 Axios 实例（`utils/request.ts`），请求拦截器自动添加 Token
- 响应拦截器处理 401（跳转登录）、Token 自动刷新（从响应头更新）
- API 按模块组织在 `src/api/` 目录下
- 开发环境通过 Vite Proxy 代理到后端

**共享组件库**（Console 包含 24+ 共享组件）：
- 选择器：UserSelect、RoleSelect、DepartmentSelect、RegionsSelect
- 上传：FileUpload、ImageUpload、FilePicker
- 编辑器：MonacoEditor（代码）、TinymceEditor（富文本）、ByteMdEditor（Markdown）
- 构建器：ProForm（表单构建）、ProCrud（CRUD 构建）
- 工具：IconSelect、DictData、CronBuilder、CodeViewer

### 6.5 路径别名配置

三个前端项目均配置了以下路径别名：

| 别名 | 指向 | 说明 |
|------|------|------|
| `@/` | `src/` | 项目源码目录 |
| `@shared/` | `../components/` | 跨项目共享组件 |

Console 和 Client 额外配置：
| 别名 | 指向 | 说明 |
|------|------|------|
| `ele-admin-plus` | `components/` | EleAdminPlus 组件库本地引用 |

## 7. 认证与权限

### 7.1 认证流程

1. 用户提交用户名 + 密码（Client 端还需租户编码，支持多租户选择）
2. 后端验证后签发 JWT Token
3. Token 载荷包含：user_id、username、user_type、tenant_code、roles
4. 前端将 Token 存储在 localStorage，每次请求通过 `Authorization: Bearer {token}` 发送
5. 响应头中若包含新 Token，前端自动更新（Token 刷新机制）

### 7.2 权限模型

- RBAC（基于角色的访问控制）
- 支持菜单级和按钮级权限
- Console 和 Client 共用相同的权限模型，通过 `app_type` 区分菜单归属
- 产品版本控制：不同版本的企业看到不同的功能菜单

### 7.3 租户中间件跳过路径

以下路径不经过租户中间件（无需 Token）：
- `/api/console/auth/login`
- `/api/client/auth/login`
- `/api/open/*`
- `/docs`、`/redoc`、`/openapi.json`
- `/health`

## 8. 部署架构

### 8.1 开发环境

- 本地 Windows 终端直接启动服务（4 个 PowerShell 窗口）
- MySQL / Redis 本地安装
- 数据库名带 `_ci` 后缀
- 前端通过 Vite Dev Server 的 Proxy 代理到后端

### 8.2 生产环境

- Docker Compose 一键部署（MySQL + Redis + Backend + Nginx）
- 前端构建为静态文件，通过 Nginx 分发
- 数据库名不带后缀
- 建议 MySQL 主从复制，Redis 集群

**部署文件**：

| 文件 | 说明 |
|------|------|
| `deploy/docker/docker-compose.yml` | Docker Compose 编排 |
| `deploy/docker/Dockerfile.backend` | 后端 Docker 镜像 |
| `deploy/docker/Dockerfile.frontend` | 前端 Docker 镜像 |
| `deploy/docker/init-db.sql` | 数据库初始化 SQL |
| `deploy/nginx/console.conf` | Console Nginx 配置 |
| `deploy/nginx/client.conf` | Client Nginx 配置 |
| `deploy/nginx/website.conf` | Website Nginx 配置 |
