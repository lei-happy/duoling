# 数据库迁移规范（zt_platform + zt_biz_*）

> 本文件是项目级强制规范。任何 ORM 模型变更必须按这里描述的流程走。
> 违反规范的 PR 会被 CI 强制阻塞合并。

## 1. 为什么要这套机制

历史事故：开发者改 `biz_waybill` 加了 `origin_region_id` 列 →
`metadata.create_all` 在本地 fresh DB 自动建对，看不出问题 →
线上旧库没人写 ALTER → 部署后报：

```
sqlalchemy.exc.OperationalError: (1054, "Unknown column 'biz_waybill.origin_region_id' in 'field list'")
```

类似事故反复发生。这套规范的目标是让「忘记写迁移文件」**在合并前就被
强制发现**，三道防线：

```
本地 pre-commit hook（软提示） → CI（硬阻塞） → deploy.sh（兜底拒绝部署）
```

## 2. 总体架构

```
backend/
├── app/modules/**/models/**          # ORM 模型（唯一事实源）
├── migrations/                       # 平台库 alembic 版本目录（注意：不叫 alembic/，避免包名冲突）
│   └── versions/
│       └── 0001_baseline.py
├── alembic.ini                       # script_location = migrations
├── scripts/migration/                # 本套机制的工具集
│   ├── snapshots/                    # 「上一次集体对齐」的事实源（git tracked）
│   │   ├── tenant_schema.json
│   │   └── platform_schema.json
│   ├── versions/                     # 租户业务库 versioned migrations（runner 风格）
│   ├── runner.py                     # 租户业务库迁移执行器（两阶段）
│   ├── platform_migrate.py           # 平台库 alembic 智能入口（auto stamp/upgrade）
│   ├── check.py                      # ORM ↔ snapshot 静态 drift 检查（无需 DB）
│   ├── autogen.py                    # 自动生成迁移 stub（tenant + platform）
│   ├── dump_snapshots.py             # 重新刷新 snapshots/*.json
│   └── _metadata.py / _imports.py / _paths.py  # 内部工具
└── Makefile                          # 开发者命令封装（make help）
```

两个数据库走两套不同的迁移机制是有意为之：

| 库               | 工具                         | 原因                                                     |
| ---------------- | ---------------------------- | -------------------------------------------------------- |
| zt_platform      | Alembic（migrations/）       | 全局唯一，Alembic 单 DB 模型完美吻合                     |
| zt_biz_{tenant} | 自定义 runner（versions/）   | N 个租户 + 按 feature 动态裁剪表清单，Alembic 单 env 表达不便 |

## 3. 强制开发流程

> 改 `app/modules/**/models/**` 任意 ORM 文件 = 必须做下面所有步骤后才能 commit。

```
┌────────────────────────────────────────────────────────────┐
│  1. 改 ORM 模型                                            │
├────────────────────────────────────────────────────────────┤
│  2. cd backend && make migrate-check                       │
│     ├── 0  无 drift → 直接 commit（说明改的是非结构性内容）│
│     └── 1  有 drift → 进入步骤 3                           │
├────────────────────────────────────────────────────────────┤
│  3. 生成迁移文件（同时自动刷新 snapshot）                  │
│     # 改了租户业务库模型（biz_*）                          │
│     make migrate-new-tenant name="add waybill region"      │
│     # 改了平台库模型（sys_* / ai_* / open_*）              │
│     make migrate-new-platform name="add ai prompt"         │
├────────────────────────────────────────────────────────────┤
│  4. 人工 review 生成的迁移文件，重点检查：                 │
│     - NOT NULL 列是否需要回填                              │
│     - 改类型是否会截断旧数据                               │
│     - 索引/唯一约束是否影响线上查询                        │
│     - autogen 默认对删除/重命名生成 NotImplementedError，  │
│       人工启用前请确认数据保留策略                         │
├────────────────────────────────────────────────────────────┤
│  5. 本地应用验证：                                         │
│     make migrate-apply-local                               │
│     （= alembic upgrade head + runner，一次跑完）          │
├────────────────────────────────────────────────────────────┤
│  6. git add 同时提交：                                     │
│     - 改动的 ORM 文件                                      │
│     - scripts/migration/versions/<new>.py（租户）          │
│       或 migrations/versions/<rev>_*.py（平台）            │
│     - scripts/migration/snapshots/*.json（自动改的）       │
│  7. git commit / push                                      │
└────────────────────────────────────────────────────────────┘
```

## 4. 三道防线如何运转

### 4.1 本地 pre-commit（软提示）

`backend/tools/pre-commit` 是一个轻量级 shell hook，安装：

```bash
cd backend && make dev-setup
```

行为：commit 时若 staged 文件涉及 ORM/迁移目录，跑一次 `migrate-check`：
- 无 drift → 静默通过
- 有 drift → 打印 `[WARN]` 修复指引，但 **不阻断** commit
  （故意软提示：本地 Python 环境可能没装齐；硬阻塞交给 CI）

应急绕过：`SKIP_DB_CHECK=1 git commit ...`

### 4.2 CI（硬阻塞）

提供两套配置文件：

- `.github/workflows/migration-check.yml` （GitHub Actions）
- `.workflow/migration-check.yml`        （Gitee Go）

也可在任意 CI 系统直接调：

```bash
bash backend/scripts/ci/migration_check.sh
```

退出码 0 / 1 / 2 同 `python -m scripts.migration.check`。

### 4.3 部署兜底（drift check + alembic upgrade）

[deploy/deploy.sh](../../../deploy/deploy.sh) 的 `update` 命令在 build 完
backend 容器、wait HTTP ready 之后立即跑：

```bash
docker compose exec backend python -m scripts.migration.check
```

有 drift 即 `exit 1`，部署中止。修复后重跑 `bash deploy.sh update` 即可。

紧急绕过：`bash deploy.sh update --skip-drift-check`（强烈不建议）。

## 5. Snapshot 怎么保证可靠

`snapshots/*.json` 是结构化序列化（按字段名稳定排序），包含每张表的：

- 表名 / comment / `__table_tier__`
- 列：name / type（MySQL 方言）/ nullable / primary_key / autoincrement /
  server_default / comment
- 主键 / 唯一约束 / 索引 / 外键

不包含：
- `default=`（Python 端默认，不影响 schema）
- `onupdate=`（应用层语义）
- 列顺序（业务上无关，反而易抖）

**snapshot 由 autogen / dump_snapshots 工具自动生成，不要手编**。
误改 → `make migrate-snapshot` 重建。

## 6. 命名约定

### 6.1 租户业务库 versioned migration

文件：`scripts/migration/versions/YYYYMMDD_NNN_<slug>.py`

变量：
```python
MIGRATION_ID = "20260520_001"          # 同一天 NNN 自增
MIGRATION_NAME = "add waybill region"  # 人类可读
REQUIRES_TABLES = ["biz_waybill"]      # 缺前置表自动跳过（避免误伤未启用 feature 的租户）

def upgrade(conn, tenant_code: str) -> None:
    ...   # 内部用 information_schema 自检后再 ALTER（幂等）
```

`MIGRATION_ID` **永不回退/修改**：发布到 master 的就是历史事实。
功能下线也别删文件，避免新租户跳过历史步骤。

### 6.2 平台库 alembic migration

文件：`migrations/versions/<rev>_<slug>.py`，命名由 alembic 自动生成。

baseline = `0001_baseline.py`，行为：
- 老库（已有 sys_user）首次纳管 → `alembic stamp head`，跳过 baseline 内的 create_all
- 新库 → `alembic upgrade head`，从 metadata.create_all 一次建好

由 `platform_migrate.py` 智能判别。

## 7. 常见场景速查

| 场景                                  | 操作                                                   |
| ------------------------------------- | ------------------------------------------------------ |
| 新增列                                 | `make migrate-new-tenant name="add x"` → review 默认值  |
| 改列类型                               | 同上 → review 是否会截断                                |
| 加索引                                 | 同上 → 视表大小评估对线上查询影响                       |
| 删列 / 重命名                          | autogen 默认生成 NotImplementedError；需人工启用 + 灰度 |
| **新增表**                             | **不需要写迁移文件**：runner Phase 1 + `feature.required_tables` 自动建表；只需更新 snapshot |
| 平台库改字段                           | `make migrate-new-platform name="..."`                 |
| 老租户库列被人手改了                   | `make migrate-runner-drift` 巡检报警                   |
| 误删 snapshot                          | `make migrate-snapshot` 重建                           |
| 已 commit 的 migration 错了            | 加一条新 MIGRATION_ID 修正，**不要改老文件**             |

## 8. 调试 & 排查

```bash
# 当前是否对齐？
python -m scripts.migration.check

# 详细 drift 报告（JSON）
python -m scripts.migration.check --json

# 看平台库 alembic 版本
python -m scripts.migration.platform_migrate --status

# 看历史 versioned migration 在每个租户的应用情况
docker compose exec backend python -m scripts.migration.runner --dry-run

# 巡检线上某租户 schema 是否与 ORM 一致（连真库）
docker compose exec backend python -m scripts.migration.runner --check-drift --tenant 1001
```

## 9. FAQ

**Q：为什么不直接全用 Alembic？**
A：Alembic 的 env.py 是单 DB 模型，要同时管 N 个租户库的话需要写循环 +
   显式跳过逻辑，反而比 runner.py 复杂。runner.py 已经在管 biz_migration_log
   做幂等，迁移成本不划算。

**Q：autogen 出来的文件能直接合并吗？**
A：**不能**。autogen 是 stub 生成器，重点要人工补：
   - NOT NULL 列的回填策略（需在 ALTER 之前 UPDATE）
   - 危险操作（删表 / 删列 / 重命名）默认 NotImplementedError，需人工启用
   - 改类型时是否需要先复制到新列再切换

**Q：本地没装 MySQL，能跑 autogen 吗？**
A：`autogen tenant` 不连 DB，纯静态对比 snapshot；`autogen platform` 走
   alembic autogenerate，需要平台库可达。CI 上只跑 `check`（不连 DB）。

**Q：如何回滚一个错误的迁移？**
A：不要 downgrade（数据风险大）。加一条新 MIGRATION_ID 写"反向修正"的
   ALTER 即可。snapshot 也跟着自动更新。
