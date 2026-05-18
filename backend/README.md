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
- Alembic（数据库迁移）

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
python scripts/init/init_platform_db.py

# 写入种子数据（管理员账号、默认角色、产品版本等）
python scripts/seed/seed_data.py

# 初始化示例租户库（可选，zt_biz_1001_ci）
python scripts/init/init_tenant_db.py 1001
```

### 4. 数据库迁移

本项目对**平台库**（zt_platform）和**租户业务库**（zt_biz_*）使用两套互补的迁移机制，
统一入口在 `scripts/migration/`，详见 [scripts/migration/README.md](scripts/migration/README.md)。

```bash
# 检查 ORM 与 snapshot 是否对齐（CI 也跑这个）
python -m scripts.migration.check

# 改了 ORM 模型后 → 自动生成迁移文件 + 刷新 snapshot
python -m scripts.migration.autogen tenant   --name "add waybill region"
python -m scripts.migration.autogen platform --name "add ai prompt template"

# 本地应用
python -m scripts.migration.platform_migrate    # 平台库（智能 stamp/upgrade）
python -m scripts.migration.runner              # 所有租户库

# 查看 alembic 当前版本
python -m scripts.migration.platform_migrate --status
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 健康检查: [http://localhost:8000/health](http://localhost:8000/health)

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
│   │   ├── permissions.py   # RBAC 权限校验（require_roles, require_any_role 等）
│   │   ├── middleware.py    # 中间件（RequestLog, Tenant）
│   │   └── events.py       # 生命周期事件（startup/shutdown）
│   ├── modules/             # 业务模块
│   │   ├── console/         # 管理后台模块（操作 zt_platform）
│   │   │   ├── api/         # API 路由（auth, tenant, system, product, basicdata, region...）
│   │   │   ├── models/      # 平台库 ORM 模型
│   │   │   ├── schemas/     # Pydantic 请求/响应 Schema
│   │   │   ├── services/    # 业务逻辑 Service
│   │   │   └── constants/   # 常量定义
│   │   ├── client/          # 客户端模块（操作 zt_biz_{code}）
│   │   │   ├── api/         # API 路由（auth, user, role, vehicle, driver, order...）
│   │   │   ├── models/      # 租户库 ORM 模型
│   │   │   ├── schemas/     # Pydantic 请求/响应 Schema
│   │   │   └── services/    # 业务逻辑 Service
│   │   └── open/            # 开放接口模块（无需认证）
│   │       ├── api/         # API 路由（register, product, changelog, sms）
│   │       ├── schemas/     # 请求 Schema
│   │       └── services/    # 业务逻辑
│   └── common/              # 公共组件
│       ├── response.py      # 统一响应格式（success/fail, PageData）
│       ├── exceptions.py    # 自定义异常 + 全局异常处理器
│       ├── pagination.py    # 分页参数 + 通用分页查询助手
│       ├── schemas/         # 共享 Schema 基类（跨 console/client 复用）
│       ├── file_upload.py   # 共享文件上传路由工厂
│       ├── enums.py         # 枚举常量
│       └── utils.py         # 工具函数（to_decimal, hash_password 等）
├── migrations/              # Alembic 平台库迁移目录（注意：故意不叫 alembic/，避免与 alembic 包重名）
│   ├── env.py               # 迁移环境配置（PlatformBase.metadata）
│   ├── script.py.mako       # 迁移脚本模板
│   └── versions/            # 迁移版本文件
├── scripts/                 # 运维脚本（按功能分类）
│   ├── init/                # 初始化脚本
│   ├── seed/                # 种子数据脚本
│   ├── fix/                 # 一次性修复脚本
│   └── migration/           # 数据库迁移工具（项目级规范）
│       ├── runner.py        # 租户业务库 schema runner（两阶段：补表 + versioned）
│       ├── platform_migrate.py # 平台库 alembic 智能入口（auto stamp/upgrade）
│       ├── check.py         # ORM ↔ snapshot drift 检查（CI 用）
│       ├── autogen.py       # 自动生成迁移 stub（tenant + platform）
│       ├── dump_snapshots.py # 重新刷新 snapshots/*.json
│       ├── snapshots/       # schema 快照（git tracked，作为对齐事实源）
│       └── versions/        # 租户业务库 versioned migrations（runner 风格）
├── alembic.ini              # Alembic 配置文件（script_location = migrations）
├── requirements.txt         # Python 依赖
└── .env.example             # 环境变量模板
```

## API 路由总览

### 路径前缀


| 前缀               | 说明     | 认证         | 数据库           |
| ---------------- | ------ | ---------- | ------------- |
| `/api/console/*` | 管理后台接口 | JWT（平台管理员） | zt_platform   |
| `/api/client/*`  | 客户端接口  | JWT（租户用户）  | zt_biz_{code} |
| `/api/open/*`    | 开放接口   | 无需认证       | zt_platform   |


### Console 模块（管理后台）


| 分组       | 路径前缀                             | 说明           |
| -------- | -------------------------------- | ------------ |
| 认证       | `/api/console/auth`              | 登录、用户信息、主题配置 |
| 租户管理     | `/api/console/tenant`            | CRUD、状态、产品授权 |
| 用户管理     | `/api/console/system/user`       | CRUD、状态、密码重置 |
| 角色管理     | `/api/console/system/role`       | CRUD、批量删除    |
| 菜单管理     | `/api/console/system/menu`       | 树形 CRUD      |
| 角色菜单     | `/api/console/system/role-menu`  | 查询/更新角色菜单分配  |
| 产品版本     | `/api/console/product-version`   | CRUD         |
| 数据字典     | `/api/console/system/dictionary` | CRUD         |
| 基础数据-品牌  | `/api/console/basicdata/brand`   | CRUD         |
| 基础数据-车系  | `/api/console/basicdata/series`  | CRUD         |
| 基础数据-经销商 | `/api/console/basicdata/dealer`  | CRUD         |
| 地区管理     | `/api/console/region`            | 树形 CRUD      |
| 文件上传     | `/api/console/file`              | 上传文件         |


### Client 模块（租户端）


| 分组       | 路径前缀                           | 说明           |
| -------- | ------------------------------ | ------------ |
| 认证       | `/api/client/auth`             | 登录、用户信息、密码修改 |
| 用户管理     | `/api/client/user`             | CRUD         |
| 角色管理     | `/api/client/role`             | CRUD         |
| 组织架构     | `/api/client/organization`     | 部门 CRUD      |
| 基础数据-品牌  | `/api/client/basicdata/brand`  | CRUD         |
| 基础数据-车系  | `/api/client/basicdata/series` | CRUD         |
| 基础数据-经销商 | `/api/client/basicdata/dealer` | CRUD         |
| 车辆管理     | `/api/client/vehicle`          | CRUD         |
| 驾驶员      | `/api/client/driver`           | CRUD         |
| 运单管理     | `/api/client/order`            | CRUD         |
| 客户管理     | `/api/client/customer`         | CRUD         |
| 工作台      | `/api/client/workbench/todo`   | 待办任务 CRUD    |
| 工作台      | `/api/client/workbench/activities` | 最新动态（当日列表） |
| 文件上传     | `/api/client/file`             | 上传文件         |


### Open 模块（开放接口）


| 分组   | 路径前缀                  | 说明       |
| ---- | --------------------- | -------- |
| 注册   | `/api/open/register`  | 企业自助注册   |
| 产品   | `/api/open/product`   | 公开产品版本列表 |
| 更新日志 | `/api/open/changelog` | 版本更新记录   |
| 短信   | `/api/open/sms`       | 短信验证码    |


## 中间件


| 顺序  | 中间件                  | 说明                                    |
| --- | -------------------- | ------------------------------------- |
| 1   | CORSMiddleware       | 跨域控制                                  |
| 2   | RequestLogMiddleware | 请求日志（方法、路径、状态码、耗时）                    |
| 3   | TenantMiddleware     | 从 JWT 提取 tenant_code 注入 request.state |


## 数据库命名


| 环境  | 平台库            | 租户库              |
| --- | -------------- | ---------------- |
| 开发  | zt_platform_ci | zt_biz_{code}_ci |
| 生产  | zt_platform    | zt_biz_{code}    |


## 默认账号


| 角色    | 用户名   | 密码       | 说明             |
| ----- | ----- | -------- | -------------- |
| 超级管理员 | admin | admin123 | Console 管理后台登录 |


