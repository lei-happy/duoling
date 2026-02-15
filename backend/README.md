# 智途(ZhiTu) 后端服务

物流车队综合操作系统 - Python + FastAPI 后端服务

## 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (异步)
- MySQL 8.0（多租户独立数据库）
- Redis 7
- Pydantic V2
- JWT (python-jose)

## 快速开始（本地 Windows 开发）

### 1. 安装依赖

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 编辑 .env 文件，配置数据库连接信息
# 开发环境默认 DB_SUFFIX=_ci，数据库名为 zt_platform_ci
```

### 3. 初始化数据库

```bash
# 初始化平台主库（zt_platform_ci）
python scripts/init_platform_db.py

# 写入种子数据（管理员账号、默认角色、产品版本等）
python scripts/seed_data.py

# 初始化示例租户库（可选，zt_biz_1001_ci）
python scripts/init_tenant_db.py 1001
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 项目结构

```
backend/
├── app/
│   ├── main.py              # 应用入口（路由注册、中间件配置、生命周期）
│   ├── core/                # 核心基础设施
│   │   ├── config.py        # 配置管理（Settings，含 DB_SUFFIX 环境命名）
│   │   ├── security.py      # JWT 认证（签发/验证 Token，TokenData）
│   │   ├── database.py      # 多租户数据库管理器（连接池缓存）
│   │   ├── dependencies.py  # 依赖注入（get_platform_db, get_tenant_db, get_current_user）
│   │   ├── middleware.py    # 中间件（RequestLog, Tenant）
│   │   └── events.py       # 生命周期事件（startup/shutdown）
│   ├── modules/             # 业务模块
│   │   ├── console/         # 管理后台模块（操作 zt_platform）
│   │   │   ├── api/         # API 路由（auth, tenant, user, role, menu, dict, product_version...）
│   │   │   ├── models/      # 平台库 ORM 模型（13 个）
│   │   │   ├── schemas/     # Pydantic 请求/响应 Schema
│   │   │   └── services/    # 业务逻辑 Service
│   │   ├── client/          # 客户端模块（操作 zt_biz_{code}）
│   │   │   ├── api/         # API 路由（目前仅 auth）
│   │   │   ├── models/      # 租户库 ORM 模型（8 个）
│   │   │   ├── schemas/     # 待实现
│   │   │   └── services/    # 待实现
│   │   └── open/            # 开放接口模块（无需认证）
│   │       ├── api/         # API 路由（register, product, forgot_password）
│   │       ├── schemas/     # 注册请求 Schema
│   │       └── services/    # 注册业务逻辑
│   └── common/              # 公共组件
│       ├── response.py      # 统一响应格式（success/fail, PageData）
│       ├── exceptions.py    # 自定义异常 + 全局异常处理器
│       ├── pagination.py    # 分页参数（PageParams）
│       ├── enums.py         # 枚举常量
│       └── utils.py         # 工具函数
├── scripts/                 # 运维脚本
│   ├── init_platform_db.py  # 初始化平台库
│   ├── init_tenant_db.py    # 初始化租户库
│   └── seed_data.py         # 写入种子数据
├── requirements.txt         # Python 依赖
└── .env.example             # 环境变量模板
```

## API 路由总览

### 路径前缀

| 前缀 | 说明 | 认证 | 数据库 |
|------|------|------|--------|
| `/api/console/*` | 管理后台接口 | JWT（平台管理员） | zt_platform |
| `/api/client/*` | 客户端接口 | JWT（租户用户） | zt_biz_{code} |
| `/api/open/*` | 开放接口 | 无需认证 | zt_platform |

### Console 模块已实现端点（30+）

| 分组 | 路径前缀 | 端点数 | 说明 |
|------|----------|--------|------|
| 认证 | `/api/console/auth` | 3 | 登录、用户信息、主题配置 |
| 租户管理 | `/api/console/tenant` | 9 | CRUD、状态、产品授权 |
| 用户管理 | `/api/console/system/user` | 9 | CRUD、状态、密码重置、唯一性检查 |
| 角色管理 | `/api/console/system/role` | 6 | CRUD、批量删除 |
| 菜单管理 | `/api/console/system/menu` | 5 | 树形 CRUD |
| 角色菜单 | `/api/console/system/role-menu` | 2 | 查询/更新角色菜单分配 |
| 组织架构 | `/api/console/system/organization` | 2 | 列表、树形（stub） |
| 产品版本 | `/api/console/product-version` | 5 | CRUD |
| 数据字典 | `/api/console/system/dictionary` | 5 | CRUD |
| 字典数据 | `/api/console/system/dictionary-data` | 6 | CRUD、批量删除 |

### Client 模块已实现端点（3）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/client/auth/login` | 客户端登录（支持多租户选择） |
| GET | `/api/client/auth/user-info` | 获取当前用户信息 |
| PUT | `/api/client/auth/password` | 修改密码 |

> 业务 CRUD API（车辆、驾驶员、运单、路线、客户）路由已预留，待实现 schemas → services → api。

### Open 模块已实现端点（3）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/open/register` | 企业自助注册 |
| POST | `/api/open/forgot-password` | 忘记密码（stub） |
| GET | `/api/open/product/versions` | 公开产品版本列表 |

## 中间件

| 顺序 | 中间件 | 说明 |
|------|--------|------|
| 1 | CORSMiddleware | 跨域控制，Origins 由 `CORS_ORIGINS` 环境变量配置 |
| 2 | RequestLogMiddleware | 请求日志（方法、路径、状态码、耗时） |
| 3 | TenantMiddleware | 从 JWT 提取 tenant_code 注入 request.state |

## 模块实现进度

| 模块 | 模型 | Schema | Service | API | 说明 |
|------|------|--------|---------|-----|------|
| Console-认证 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-租户 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-用户 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-角色 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-菜单 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-产品版本 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-数据字典 | ✅ | ✅ | ✅ | ✅ | 完成 |
| Console-组织架构 | ✅ | - | - | 🔧 | API 为 stub |
| Console-反馈 | ✅ | - | - | - | 仅模型 |
| Console-操作日志 | ✅ | - | - | - | 仅模型 |
| Client-认证 | ✅ | ✅* | ✅* | ✅ | 复用 Console 的 Schema/Service |
| Client-用户 | ✅ | - | - | - | 仅模型 |
| Client-角色 | ✅ | - | - | - | 仅模型 |
| Client-菜单 | ✅ | - | - | - | 仅模型 |
| Client-车辆 | ✅ | - | - | - | 仅模型 |
| Client-驾驶员 | ✅ | - | - | - | 仅模型 |
| Client-运单 | ✅ | - | - | - | 仅模型 |
| Client-路线 | ✅ | - | - | - | 仅模型 |
| Client-客户 | ✅ | - | - | - | 仅模型 |
| Open-注册 | - | ✅ | ✅ | ✅ | 完成 |
| Open-产品查询 | - | - | - | ✅ | 完成 |
| Open-忘记密码 | - | - | - | 🔧 | stub |

## 数据库命名

| 环境 | 平台库 | 租户库 |
|------|--------|--------|
| 开发 | zt_platform_ci | zt_biz_{code}_ci |
| 生产 | zt_platform | zt_biz_{code} |

## 默认账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 超级管理员 | admin | admin123 | Console 管理后台登录 |
