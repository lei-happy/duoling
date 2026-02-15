# 智途(ZhiTu) 后端服务

物流车队综合操作系统 - Python + FastAPI 后端服务

## 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (异步)
- MySQL 8.0
- Redis
- Pydantic V2
- JWT (python-jose)

## 快速开始（本地 Windows 开发）

### 1. 安装依赖

```bash
cd backend
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

## 项目结构

```
backend/
├── app/
│   ├── main.py              # 应用入口
│   ├── core/                # 核心基础设施
│   │   ├── config.py        # 配置管理（含 DB_SUFFIX 环境命名）
│   │   ├── security.py      # JWT认证
│   │   ├── database.py      # 多租户数据库管理
│   │   ├── dependencies.py  # 依赖注入
│   │   ├── middleware.py    # 中间件
│   │   └── events.py       # 生命周期事件
│   ├── modules/             # 业务模块
│   │   ├── console/         # 管理后台（租户管理、用户、角色、产品版本等）
│   │   ├── client/          # 客户端业务（车辆、驾驶员、运单等）
│   │   └── open/            # 开放接口（企业自助注册等）
│   └── common/              # 公共组件
├── scripts/                 # 运维脚本
├── tests/                   # 测试
└── requirements.txt
```

## API 路径

| 前缀 | 说明 | 数据库 |
|------|------|--------|
| /api/console/* | 管理后台接口 | zt_platform |
| /api/client/* | 客户端接口 | zt_biz_{code} |
| /api/open/* | 开放接口（无需认证） | zt_platform |

## 数据库命名

| 环境 | 平台库 | 租户库 |
|------|--------|--------|
| 开发 | zt_platform_ci | zt_biz_{code}_ci |
| 生产 | zt_platform | zt_biz_{code} |

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
