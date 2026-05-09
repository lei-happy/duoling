"""
初始化产品版本（sys_product_version 表）

事实源：backend/scripts/platform_sync/snapshots/product_version.json
  —— 由 `python -m scripts.platform_sync export` 在 dev 端生成。

幂等：
  - 按 version_code 业务主键 upsert
  - 已存在的版本：UPDATE 全部业务字段
  - 不存在的版本：INSERT
  - 快照里没有但 prod 有的版本：**保留不动**（避免误删正在使用的版本，
    若需删除应通过 console 后台手工操作并审计）

由 `python -m scripts.platform_sync sync` 自动调用，发版人无需手工执行。
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


SNAPSHOT_DIR = (
    Path(__file__).resolve().parent.parent / "platform_sync" / "snapshots"
)
VERSION_SNAPSHOT = SNAPSHOT_DIR / "product_version.json"


def _load_versions() -> list:
    if not VERSION_SNAPSHOT.is_file():
        print(
            f"[ERROR] 找不到产品版本快照: {VERSION_SNAPSHOT}\n"
            f"        请先在 dev 跑：\n"
            f"            cd backend && python -m scripts.platform_sync export",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = json.loads(VERSION_SNAPSHOT.read_text(encoding="utf-8"))
    versions = []
    for item in raw:
        versions.append({
            "version_code": item["version_code"],
            "version_name": item["version_name"],
            "description": item.get("description"),
            "max_users": int(item.get("max_users") or 0),
            "max_vehicles": int(item.get("max_vehicles") or 0),
            "price": item.get("price"),
            "sort_order": int(item.get("sort_order") or 0),
            "status": int(item.get("status") or 1),
        })
    return versions


def main():
    settings = get_settings()
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)

    versions = _load_versions()
    print(f"[INFO] 已加载快照：{len(versions)} 个产品版本")

    inserted = updated = skipped = 0
    with engine.connect() as conn:
        # 确保表存在
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sys_product_version (
                id BIGINT NOT NULL AUTO_INCREMENT,
                version_code VARCHAR(50) NOT NULL,
                version_name VARCHAR(100) NOT NULL,
                description TEXT DEFAULT NULL,
                features JSON DEFAULT NULL,
                max_users INT DEFAULT 10,
                max_vehicles INT DEFAULT 50,
                price VARCHAR(50) DEFAULT NULL,
                sort_order SMALLINT DEFAULT 0,
                status SMALLINT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted SMALLINT DEFAULT 0,
                PRIMARY KEY (id),
                UNIQUE KEY uk_version_code (version_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品版本表'
        """))
        conn.commit()

        for v in versions:
            existing = conn.execute(
                text(
                    "SELECT id FROM sys_product_version "
                    "WHERE version_code = :code AND is_deleted = 0"
                ),
                {"code": v["version_code"]},
            ).scalar()

            if existing:
                conn.execute(
                    text(
                        "UPDATE sys_product_version SET "
                        "version_name = :version_name, "
                        "description = :description, "
                        "max_users = :max_users, "
                        "max_vehicles = :max_vehicles, "
                        "price = :price, "
                        "sort_order = :sort_order, "
                        "status = :status "
                        "WHERE id = :id"
                    ),
                    {**v, "id": existing},
                )
                print(f"  更新版本: {v['version_code']} - {v['version_name']} (id={existing})")
                updated += 1
            else:
                # 显式给 is_deleted / created_at / updated_at 赋值
                # 防御老库 DDL 中这些字段没有 DEFAULT 值（MySQL strict mode 下会 1364）
                conn.execute(
                    text(
                        "INSERT INTO sys_product_version "
                        "(version_code, version_name, description, max_users, max_vehicles, "
                        "price, sort_order, status, is_deleted, created_at, updated_at) "
                        "VALUES (:version_code, :version_name, :description, :max_users, :max_vehicles, "
                        ":price, :sort_order, :status, 0, NOW(), NOW())"
                    ),
                    v,
                )
                print(f"  插入版本: {v['version_code']} - {v['version_name']}")
                inserted += 1

        conn.commit()

        # 报告 prod 多余的版本（保留不删，仅打印 warning）
        snapshot_codes = {v["version_code"] for v in versions}
        extra_rows = conn.execute(text(
            "SELECT version_code, version_name FROM sys_product_version "
            "WHERE is_deleted = 0"
        )).fetchall()
        extra = [r for r in extra_rows if r[0] not in snapshot_codes]
        if extra:
            print(
                f"\n[WARN] prod 库存在 {len(extra)} 个快照中没有的版本（保留不删，"
                "如需停用请手工 console 后台操作）："
            )
            for r in extra:
                print(f"  - {r[0]} ({r[1]})")
            skipped = len(extra)

    engine.dispose()
    print(
        f"\n产品版本初始化完成！新增 {inserted} / 更新 {updated} / "
        f"保留 {skipped}（快照外）"
    )


if __name__ == "__main__":
    main()
