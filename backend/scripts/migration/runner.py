"""租户业务库 schema 自动迁移 runner（部署脚本 update 时自动调用）

工作流：
  1. 列出所有 active 租户（sys_tenant.is_deleted=0 AND db_initialized=1）
  2. 对每个租户：
       a) Phase 1 - ensure tables：根据其已开通版本对应的
          sys_product_feature.required_tables，自动补建缺失业务表
       b) Phase 2 - versioned migrations：扫描 scripts/migration/versions/
          下的迁移模块，按 MIGRATION_ID 字典序执行，
          跳过 biz_migration_log 已记录的、跳过 REQUIRES_TABLES 不齐的
  3. 输出每个租户的"建表清单 / 执行迁移清单 / 错误清单"

执行模式：
  python -m scripts.migration.runner               # apply 全部
  python -m scripts.migration.runner --dry-run     # 只打印计划，不写库
  python -m scripts.migration.runner --tenant 1001 # 只处理指定租户
  python -m scripts.migration.runner --skip-ensure # 跳过 Phase 1，仅跑 versioned migrations
  python -m scripts.migration.runner --skip-versioned  # 跳过 Phase 2，仅自动补表
  python -m scripts.migration.runner --check-drift # 仅报警：ORM vs 真实租户库列差异

退出码：
  0  全部成功
  1  至少有一个租户失败（其它租户照常处理，仅尾部退出码 != 0）
  2  配置/环境错误（连不上平台库等）
"""

from __future__ import annotations

import argparse
import importlib
import os
import pkgutil
import socket
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

_SCRIPT = Path(__file__).resolve()
_BACKEND = _SCRIPT.parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from sqlalchemy import create_engine, text, inspect as sa_inspect
from sqlalchemy.engine import Engine

from app.core.config import get_settings
from app.core.database import DatabaseManager, TenantBase

# 注入模型 metadata（迁移所需建表全部走 metadata.create_all）
import app.modules.client.models  # noqa: F401


# ---------------------------------------------------------------------------
# biz_migration_log：在租户库自举创建
# ---------------------------------------------------------------------------
_MIGRATION_LOG_DDL = """
CREATE TABLE IF NOT EXISTS biz_migration_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    migration_id VARCHAR(50) NOT NULL,
    migration_name VARCHAR(200) NOT NULL,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_migration_id (migration_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='租户业务库 schema 迁移记录'
"""


def _ensure_migration_log(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_MIGRATION_LOG_DDL))


def _applied_migration_ids(engine: Engine) -> Set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT migration_id FROM biz_migration_log"
        )).fetchall()
    return {r[0] for r in rows}


def _record_migration(
    engine: Engine, migration_id: str, migration_name: str, applied_by: str,
) -> None:
    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO biz_migration_log "
            "(migration_id, migration_name, applied_by) "
            "VALUES (:mid, :name, :by)"
        ), {"mid": migration_id, "name": migration_name, "by": applied_by})


# ---------------------------------------------------------------------------
# Phase 1：按 feature.required_tables 补表
# ---------------------------------------------------------------------------
def _tenant_required_tables(
    platform_engine: Engine, tenant_code: str,
) -> List[str]:
    """取该租户已开通所有版本对应 feature 的 required_tables 并集。"""
    with platform_engine.connect() as conn:
        rows = conn.execute(text(
            """
            SELECT DISTINCT pf.required_tables
            FROM sys_tenant t
            JOIN sys_tenant_product tp ON tp.tenant_id = t.id
              AND tp.is_deleted = 0 AND tp.status = 1
            JOIN sys_product_version v ON v.id = tp.version_id
              AND v.is_deleted = 0 AND v.status = 1
            JOIN sys_version_feature vf ON vf.version_id = v.id
              AND vf.is_deleted = 0 AND vf.status = 1
            JOIN sys_product_feature pf ON pf.id = vf.feature_id
              AND pf.is_deleted = 0 AND pf.status = 1
            WHERE t.tenant_code = :tc
              AND pf.required_tables IS NOT NULL
            """
        ), {"tc": tenant_code}).fetchall()

    import json
    table_set: Set[str] = set()
    for (rt,) in rows:
        if rt is None:
            continue
        if isinstance(rt, list):
            table_set.update(rt)
        elif isinstance(rt, str):
            try:
                arr = json.loads(rt)
                if isinstance(arr, list):
                    table_set.update(arr)
            except json.JSONDecodeError:
                pass
    return sorted(table_set)


def _ensure_tables(
    engine: Engine, required_tables: List[str], dry_run: bool,
) -> List[str]:
    """对照 metadata 补建缺失表，返回本次新建的表名。"""
    if not required_tables:
        return []
    insp = sa_inspect(engine)
    existing = set(insp.get_table_names())
    missing_names = [t for t in required_tables if t not in existing]
    if not missing_names:
        return []
    table_objs = DatabaseManager.get_tables_by_names(missing_names)
    creatable = [t.name for t in table_objs]
    if dry_run:
        return creatable
    TenantBase.metadata.create_all(engine, tables=table_objs)
    return creatable


# ---------------------------------------------------------------------------
# Phase 2：versioned migrations
# ---------------------------------------------------------------------------
@dataclass
class LoadedMigration:
    id: str
    name: str
    requires_tables: List[str]
    upgrade_fn: callable
    module_name: str


def _load_migrations() -> List[LoadedMigration]:
    """加载 scripts.migration.versions 包内所有迁移模块，按 ID 排序。"""
    from scripts.migration import versions as versions_pkg

    out: List[LoadedMigration] = []
    for mod in pkgutil.iter_modules(versions_pkg.__path__):
        if mod.name.startswith("_"):
            continue
        fqname = f"scripts.migration.versions.{mod.name}"
        m = importlib.import_module(fqname)
        for attr in ("MIGRATION_ID", "MIGRATION_NAME", "upgrade"):
            if not hasattr(m, attr):
                raise RuntimeError(
                    f"迁移模块 {fqname} 缺少必要符号 {attr}"
                )
        out.append(LoadedMigration(
            id=str(m.MIGRATION_ID),
            name=str(m.MIGRATION_NAME),
            requires_tables=list(getattr(m, "REQUIRES_TABLES", []) or []),
            upgrade_fn=m.upgrade,
            module_name=fqname,
        ))
    out.sort(key=lambda x: x.id)
    # 校验 ID 唯一
    ids = [m.id for m in out]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise RuntimeError(f"重复的 MIGRATION_ID: {dup}")
    return out


def _run_versioned_migrations(
    engine: Engine,
    tenant_code: str,
    migrations: List[LoadedMigration],
    applied_by: str,
    dry_run: bool,
) -> Dict[str, List[str]]:
    """返回 {executed: [...], skipped_no_table: [...], already_applied: [...]}。"""
    result = {"executed": [], "skipped_no_table": [], "already_applied": []}
    if not migrations:
        return result

    _ensure_migration_log(engine)
    applied = _applied_migration_ids(engine)
    insp = sa_inspect(engine)
    existing_tables = set(insp.get_table_names())

    for mig in migrations:
        if mig.id in applied:
            result["already_applied"].append(mig.id)
            continue
        if mig.requires_tables:
            missing = [t for t in mig.requires_tables if t not in existing_tables]
            if missing:
                result["skipped_no_table"].append(
                    f"{mig.id}（缺表 {missing}）"
                )
                continue
        if dry_run:
            result["executed"].append(f"[dry-run] {mig.id} {mig.name}")
            continue
        with engine.begin() as conn:
            mig.upgrade_fn(conn, tenant_code)
        _record_migration(engine, mig.id, mig.name, applied_by)
        result["executed"].append(f"{mig.id} {mig.name}")
        # 表清单可能因迁移变化（少见），但下一个迁移仍能感知
        insp = sa_inspect(engine)
        existing_tables = set(insp.get_table_names())
    return result


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
@dataclass
class TenantReport:
    tenant_code: str
    created_tables: List[str] = field(default_factory=list)
    migration_result: Dict[str, List[str]] = field(default_factory=dict)
    error: Optional[str] = None


def _list_active_tenants(
    platform_engine: Engine, only: Optional[str] = None,
) -> List[str]:
    with platform_engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT tenant_code FROM sys_tenant "
            "WHERE is_deleted = 0 AND db_initialized = 1 "
            "ORDER BY tenant_code"
        )).fetchall()
    codes = [r[0] for r in rows]
    if only:
        codes = [c for c in codes if c == only]
    return codes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="租户业务库 schema 自动迁移（按 feature 补表 + versioned migrations）"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印计划，不写库")
    parser.add_argument("--tenant", default=None,
                        help="只处理指定 tenant_code")
    parser.add_argument("--skip-ensure", action="store_true",
                        help="跳过 Phase 1：按 feature 补表")
    parser.add_argument("--skip-versioned", action="store_true",
                        help="跳过 Phase 2：versioned migrations")
    parser.add_argument("--check-drift", action="store_true",
                        help="仅检查：连真实租户库对比 ORM 列差异，仅报警不写库")
    args = parser.parse_args()

    if args.check_drift:
        return _run_check_drift(args.tenant)

    settings = get_settings()
    applied_by = (
        os.environ.get("MIGRATION_APPLIED_BY")
        or f"runner@{socket.gethostname()}"
    )

    # 平台库连接
    plat_url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    try:
        platform_engine = create_engine(plat_url, pool_pre_ping=True)
        # 探活
        with platform_engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as e:
        print(f"[ERROR] 无法连接平台库: {e}", file=sys.stderr)
        return 2

    tenants = _list_active_tenants(platform_engine, args.tenant)
    if not tenants:
        print("[INFO] 没有需要处理的租户")
        platform_engine.dispose()
        return 0

    migrations = [] if args.skip_versioned else _load_migrations()

    mode_label = "DRY-RUN（不写库）" if args.dry_run else "APPLY（写库）"
    print(f"\n========== 租户业务库迁移 [{mode_label}] ==========")
    print(f"待处理租户: {tenants}")
    if not args.skip_versioned:
        print(f"versioned migrations 共 {len(migrations)} 条："
              f"{[m.id for m in migrations] if migrations else '(无)'}")
    if not args.skip_ensure:
        print("Phase 1 启用：按 feature 自动补表")
    if not args.skip_versioned:
        print("Phase 2 启用：versioned migrations")
    print("=" * 60)

    reports: List[TenantReport] = []
    for tc in tenants:
        rep = TenantReport(tenant_code=tc)
        print(f"\n>>> 租户 {tc}")
        try:
            tenant_url = settings.tenant_db_url_sync(tc)
            engine = create_engine(tenant_url, pool_pre_ping=True)

            # Phase 1: ensure tables
            if not args.skip_ensure:
                required = _tenant_required_tables(platform_engine, tc)
                if required:
                    created = _ensure_tables(engine, required, args.dry_run)
                    if created:
                        rep.created_tables = created
                        prefix = "[dry-run] 将补建" if args.dry_run else "已补建"
                        print(f"  {prefix} 表 ({len(created)}): {created}")
                    else:
                        print(f"  Phase 1：表已齐全（需 {len(required)} 张）")
                else:
                    print("  Phase 1：未开通任何带 required_tables 的 feature")

            # Phase 2: versioned migrations
            if not args.skip_versioned and migrations:
                mres = _run_versioned_migrations(
                    engine, tc, migrations, applied_by, args.dry_run,
                )
                rep.migration_result = mres
                if mres["executed"]:
                    prefix = "[dry-run] 将执行" if args.dry_run else "已执行"
                    print(f"  {prefix} migrations ({len(mres['executed'])}):")
                    for x in mres["executed"]:
                        print(f"    - {x}")
                if mres["skipped_no_table"]:
                    print(f"  跳过（缺前置表，未启用相关 feature）："
                          f"{mres['skipped_no_table']}")
                if mres["already_applied"]:
                    print(f"  已应用过 ({len(mres['already_applied'])}): "
                          f"{mres['already_applied']}")
                if (not mres["executed"]
                        and not mres["skipped_no_table"]
                        and not mres["already_applied"]):
                    print("  Phase 2：无可执行 migration")

            engine.dispose()
        except Exception as e:
            rep.error = f"{type(e).__name__}: {e}"
            print(f"  [ERROR] {rep.error}")
            traceback.print_exc()
        reports.append(rep)

    platform_engine.dispose()

    print("\n========== 汇总 ==========")
    ok = sum(1 for r in reports if r.error is None)
    fail = sum(1 for r in reports if r.error is not None)
    total_created = sum(len(r.created_tables) for r in reports)
    total_migrated = sum(
        len(r.migration_result.get("executed", []))
        for r in reports if not r.error
    )
    print(f"租户总数: {len(reports)}  成功: {ok}  失败: {fail}")
    print(f"本次共补建表 {total_created} 张；执行 versioned migrations {total_migrated} 次")
    for r in reports:
        if r.error:
            print(f"  [FAIL] {r.tenant_code}: {r.error}")
    print("=" * 30)

    return 0 if fail == 0 else 1


# ---------------------------------------------------------------------------
# --check-drift：连真实租户库对比 ORM 列，仅报警不写库
# ---------------------------------------------------------------------------
def _run_check_drift(tenant_filter: Optional[str]) -> int:
    """对每个租户库做真实 schema vs ORM 列差异巡检。

    用途：scripts.migration.check 是「ORM vs snapshot」静态对比；本子命令
    则是「ORM vs 真实租户库」动态对比，能发现：
      - 某租户的迁移意外失败但 biz_migration_log 已写入（参考 1054 事故）
      - 老租户库被人手动改过 schema
      - 某迁移文件因 REQUIRES_TABLES 被跳过，但实际该租户已有那张表

    退出码：0 = 所有租户都对齐；1 = 至少 1 个租户存在 drift
    （仅打印告警，不修复——修复请走 scripts.migration.versions/）
    """
    settings = get_settings()
    plat_url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    try:
        platform_engine = create_engine(plat_url, pool_pre_ping=True)
        with platform_engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as e:
        print(f"[ERROR] 无法连接平台库: {e}", file=sys.stderr)
        return 2

    tenants = _list_active_tenants(platform_engine, tenant_filter)
    if not tenants:
        print("[INFO] 没有需要检查的租户")
        platform_engine.dispose()
        return 0

    # 把 ORM 中所有租户表的「列名集合」预先算好，按表索引
    orm_table_cols: Dict[str, Set[str]] = {}
    for t in TenantBase.metadata.sorted_tables:
        orm_table_cols[t.name] = {c.name for c in t.columns}

    print(f"\n========== 租户库 drift 巡检（{len(tenants)} 个租户） ==========")
    fail_tenants = []
    for tc in tenants:
        try:
            tenant_url = settings.tenant_db_url_sync(tc)
            engine = create_engine(tenant_url, pool_pre_ping=True)
            insp = sa_inspect(engine)
            tenant_tables = set(insp.get_table_names())
            tenant_drift: List[str] = []
            for tn in sorted(tenant_tables & set(orm_table_cols.keys())):
                db_cols = {c["name"] for c in insp.get_columns(tn)}
                orm_cols = orm_table_cols[tn]
                missing_in_db = orm_cols - db_cols
                extra_in_db = db_cols - orm_cols
                if missing_in_db:
                    tenant_drift.append(
                        f"  [缺列] {tn}: {sorted(missing_in_db)}"
                    )
                if extra_in_db:
                    tenant_drift.append(
                        f"  [多列] {tn}: {sorted(extra_in_db)}（ORM 已删除？）"
                    )
            engine.dispose()
            if tenant_drift:
                print(f"\n>>> {tc} —— {len(tenant_drift)} 处 drift")
                for line in tenant_drift:
                    print(line)
                fail_tenants.append(tc)
            else:
                print(f">>> {tc} —— OK")
        except Exception as e:
            print(f">>> {tc} —— [ERROR] {type(e).__name__}: {e}")
            fail_tenants.append(tc)

    platform_engine.dispose()

    print("\n========== 巡检汇总 ==========")
    if fail_tenants:
        print(f"[DRIFT] 共 {len(fail_tenants)} 个租户存在 drift：{fail_tenants}")
        print("修复路径：")
        print("  1) 确认 ORM 模型为期望事实源")
        print("  2) cd backend && python -m scripts.migration.autogen tenant --name '<desc>'")
        print("  3) review/补全生成的迁移文件，提交 + 部署")
        return 1
    print("[OK] 所有租户库列结构与 ORM 一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
