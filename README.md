# 智途(ZhiTu) - 物流车队综合操作系统

一套 SaaS + PaaS 架构的物流车队综合管理平台，支持多租户独立数据库，为物流企业提供车辆管理、驾驶员管理、运单管理等全方位数字化解决方案。

## 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                        客户端产品                              │
│ 产品官网 │ Console管理后台 │ Client客户端 │ 管理小程序 │ 驾驶员小程序 │
└──────────────────────────┬───────────────────────────────────┘
                           │
                      ┌────┴────┐
                      │  Nginx  │  （接入层 / 轻量网关）
                      └────┬────┘
                           │
┌──────────────────────────┴───────────────────────────────────┐
│                后端服务 (Python + FastAPI)                      │
│   /api/open（开放接口）│ /api/console（管理后台）│ /api/client（客户端）│
└────────┬──────────────────────┬──────────────────┬───────────┘
         │                      │                  │
    ┌────┴──────┐        ┌──────┴──────┐    ┌─────┴─────┐
    │zt_platform│        │zt_biz_1001  │    │zt_biz_xxxx│
    │  平台主库  │        │ 企业A业务库  │    │ 企业N业务库 │
    └───────────┘        └─────────────┘    └───────────┘
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Pydantic V2 |
| 数据库 | MySQL 8.0（多租户独立库） |
| 缓存 | Redis 7 |
| 前端 | Vue 3 / TypeScript / Vite / Element Plus / Pinia |
| 小程序 | UniApp（预留） |
| 部署 | Docker / Docker Compose / Nginx |

## 项目结构

```
zhitu/
├── doc/                    # 文档管理中心
│   ├── 开发计划/           # 开发路线图与里程碑
│   ├── 架构设计/           # 系统架构、开发规范、本地开发指南
│   ├── 需求文档/           # 按端划分的模块需求文档
│   │   ├── 运营后台/       # Console 端需求
│   │   ├── 企业端/         # Client 端需求
│   │   └── 移动端/         # 小程序端需求
│   ├── 数据库设计/         # 数据库设计文档 + 建表 SQL
│   └── 开发手册/           # 组件集成、开发指南等
├── backend/                # 后端服务（Python + FastAPI）
│   ├── app/                # FastAPI 应用
│   │   ├── core/           # 核心（配置/数据库/认证/中间件）
│   │   ├── modules/
│   │   │   ├── console/    # 管理后台模块（操作平台库）
│   │   │   ├── client/     # 客户端模块（操作租户库）
│   │   │   └── open/       # 开放接口模块（官网注册等）
│   │   └── common/         # 公共组件
│   └── scripts/            # 运维脚本
├── frontend/               # 前端工程
│   ├── template/           # 前端模板（EleAdminPlus）
│   ├── console/            # 管理后台前端
│   ├── client/             # 客户端前端
│   └── website/            # 产品官网
└── deploy/                 # 部署配置（线上环境）
    ├── docker/             # Docker 配置
    └── nginx/              # Nginx 配置
```

## 快速开始（本地开发）

### 前置条件

- MySQL 8.0（本地安装）
- Redis 7（本地安装，可选）
- Python 3.11+
- Node.js 20+

### 1. 后端启动

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量（修改数据库密码等）
# 编辑 .env 文件，开发环境默认 DB_SUFFIX=_ci

# 初始化平台数据库（zt_platform_ci）
python scripts/init_platform_db.py

# 写入种子数据
python scripts/seed_data.py

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端启动（另开终端）

```bash
# 管理后台（端口 5173）
cd frontend/console
npm install
npm run dev

# 客户端（端口 5174，另开终端）
cd frontend/client
npm install
npm run dev
```

### 3. 访问地址

| 服务 | 地址 |
|------|------|
| 后端 API 文档 | http://localhost:8000/docs |
| 管理后台 (Console) | http://localhost:5173 |
| 客户端 (Client) | http://localhost:5174 |

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |

## 线上部署

线上部署使用 Docker Compose，详见 `deploy/` 目录。

```bash
cd deploy/docker
docker-compose up -d
```

## 数据库命名规则

| 环境 | 平台库 | 租户库示例 |
|------|--------|-----------|
| 开发环境 | zt_platform_ci | zt_biz_1001_ci |
| 生产环境 | zt_platform | zt_biz_1001 |

通过 `.env` 中的 `DB_SUFFIX` 配置项控制。

## 多租户说明

- **平台主库**（zt_platform）：存储租户信息、平台用户、产品版本、数据字典等
- **租户业务库**（zt_biz_{编码}）：每个企业独立的业务数据库
- 新企业注册时自动创建独立数据库并初始化表结构
- 通过 JWT Token 中的 tenant_code 实现请求级数据库动态切换

## 产品端说明

| 产品 | 说明 | 本地端口 |
|------|------|---------|
| 产品官网 (Website) | 产品展示、企业自助注册 | 5175 |
| Console（管理后台） | 平台运营：租户管理、产品版本、系统配置 | 5173 |
| Client（客户端） | 企业业务：车辆、驾驶员、运单管理 | 5174 |
| 管理小程序 | 移动端审批、查看报表（预留） | - |
| 驾驶员小程序 | 接单、签到、轨迹上报（预留） | - |

## 开发规范

详见 [doc/架构设计/](doc/架构设计/) 目录下的开发规范文档。

## 开发计划

详见 [doc/开发计划/开发路线图.md](doc/开发计划/开发路线图.md)。
