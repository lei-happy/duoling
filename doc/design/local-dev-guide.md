# 本地开发环境搭建指南（Windows PowerShell）

## 1. 前置条件

请确保本地已安装以下软件：

| 软件 | 版本要求 | 验证命令 |
|------|---------|---------|
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| MySQL | 8.0 | `mysql --version` |
| Redis | 7+（可选） | `redis-cli --version` |

> **说明**：Redis 在开发阶段为可选组件，暂时不安装不影响核心功能调试。

---

## 2. 数据库准备

### 2.1 启动 MySQL 服务

如果 MySQL 已安装为 Windows 服务，通常开机自动启动。否则手动启动：

```powershell
# 检查 MySQL 服务状态
Get-Service -Name "MySQL*"

# 启动 MySQL 服务（需管理员权限）
Start-Service -Name "MySQL80"
```

### 2.2 初始化平台数据库

开发环境数据库名带 `_ci` 后缀（通过 `.env` 中 `DB_SUFFIX=_ci` 控制）。

可以使用后端初始化脚本（见第 3 步），也可以手动创建：

```sql
-- 使用 MySQL 客户端连接后执行
CREATE DATABASE IF NOT EXISTS `zt_platform_ci`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

---

## 3. 后端服务启动

### 3.1 安装 Python 依赖

```powershell
# 进入后端目录
cd d:\zhitu\backend

# 建议先创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

> **提示**：如果遇到 `Activate.ps1` 执行策略问题，先运行：
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3.2 配置环境变量

编辑 `backend/.env` 文件，确认以下关键配置：

```ini
# 数据库环境后缀（开发环境必须为 _ci）
DB_SUFFIX=_ci

# MySQL 连接信息（根据本地实际情况修改）
PLATFORM_DB_HOST=127.0.0.1
PLATFORM_DB_PORT=3306
PLATFORM_DB_USER=root
PLATFORM_DB_PASSWORD=root

# 租户库连接信息（同一 MySQL 实例）
TENANT_DB_HOST=127.0.0.1
TENANT_DB_PORT=3306
TENANT_DB_USER=root
TENANT_DB_PASSWORD=root
```

### 3.3 初始化数据库和种子数据

```powershell
# 确保在 backend 目录且虚拟环境已激活
cd d:\zhitu\backend

# 初始化平台主库（创建 zt_platform_ci 库 + 表结构）
python scripts/init_platform_db.py

# 写入种子数据（管理员账号、默认角色、产品版本、数据字典）
python scripts/seed_data.py

# （可选）初始化一个示例租户库
python scripts/init_tenant_db.py 1001
```

成功输出示例：

```
[OK] 数据库 zt_platform_ci 已创建
[OK] 平台库表结构已初始化

平台主库初始化完成！
```

### 3.4 启动后端服务

```powershell
cd d:\zhitu\backend

# 确保虚拟环境已激活
.\venv\Scripts\Activate.ps1

# 启动 FastAPI（开发模式，自动热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：

- API 文档 (Swagger)：http://localhost:8000/docs
- API 文档 (ReDoc)：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

---

## 4. 前端服务启动

每个前端项目需要在**独立的 PowerShell 窗口**中启动。

### 4.1 管理后台（Console）

```powershell
cd d:\zhitu\frontend\console

# 首次启动需安装依赖
npm install

# 启动开发服务器（端口 5173）
npm run dev
```

访问地址：http://localhost:5173

### 4.2 客户端（Client）

```powershell
cd d:\zhitu\frontend\client

# 首次启动需安装依赖
npm install

# 启动开发服务器（端口 5174）
npm run dev
```

访问地址：http://localhost:5174

### 4.3 产品官网（Website）

```powershell
cd d:\zhitu\frontend\website

# 首次启动需安装依赖
npm install

# 启动开发服务器（端口 5175）
npm run dev
```

访问地址：http://localhost:5175

---

## 5. 完整启动清单

本地开发需要开启**4 个 PowerShell 窗口**（终端），分别运行：

| 终端 | 目录 | 命令 | 端口 | 说明 |
|------|------|------|------|------|
| 终端 1 | `backend` | `uvicorn app.main:app --reload --port 8000` | 8000 | 后端 API |
| 终端 2 | `frontend/console` | `npm run dev` | 5173 | 管理后台 |
| 终端 3 | `frontend/client` | `npm run dev` | 5174 | 客户端 |
| 终端 4 | `frontend/website` | `npm run dev` | 5175 | 产品官网 |

> **快捷操作**：可以使用 Windows Terminal 的多标签页功能，在同一个窗口中管理所有终端。

---

## 6. 默认登录账号

| 系统 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| Console 管理后台 | admin | admin123 | 超级管理员 |

> 客户端登录需要先通过管理后台创建企业和企业超管账号。

---

## 7. 数据库命名说明

| 环境 | 平台库 | 租户库示例 | 控制项 |
|------|--------|-----------|--------|
| 本地开发 | `zt_platform_ci` | `zt_biz_1001_ci` | `DB_SUFFIX=_ci` |
| 线上生产 | `zt_platform` | `zt_biz_1001` | `DB_SUFFIX=`（空） |

---

## 8. 常见问题

### Q1：pip install 报错找不到 `aiomysql` 或 `mysqlclient`

确保已安装 MySQL 客户端开发库。Windows 上推荐使用 `aiomysql`（纯 Python），不需要额外的 C 库。如果 `requirements.txt` 中有 `mysqlclient`，可以改用 `pymysql`。

### Q2：uvicorn 启动后提示数据库连接失败

1. 检查 MySQL 服务是否已启动：`Get-Service -Name "MySQL*"`
2. 检查 `.env` 中的数据库连接信息是否正确
3. 确认数据库 `zt_platform_ci` 已创建（运行 `python scripts/init_platform_db.py`）

### Q3：前端 npm install 很慢

设置国内镜像源：

```powershell
npm config set registry https://registry.npmmirror.com
```

### Q4：PowerShell 执行脚本被拒绝

```powershell
# 设置执行策略（仅当前用户，一次性操作）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q5：端口被占用

查找占用端口的进程并关闭：

```powershell
# 查看 8000 端口占用情况
netstat -ano | findstr :8000

# 根据 PID 关闭进程
Stop-Process -Id <PID> -Force
```

### Q6：如何重置数据库

```powershell
# 连接 MySQL 删除数据库
mysql -u root -p -e "DROP DATABASE IF EXISTS zt_platform_ci;"

# 重新初始化
cd d:\zhitu\backend
python scripts/init_platform_db.py
python scripts/seed_data.py
```
