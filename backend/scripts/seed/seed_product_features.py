"""
初始化产品功能清单和版本-功能关联（v2.0）

本脚本以 platform_sync 工具产出的快照为唯一事实源，向 sys_product_feature
与 sys_version_feature 表做幂等 upsert：

  - sys_product_feature 数据来自:
      backend/scripts/platform_sync/snapshots/product_feature.json
  - sys_version_feature 数据来自:
      backend/scripts/platform_sync/snapshots/version_feature.json

如果快照不存在，本脚本会拒绝执行并提示先运行 platform_sync 工具：

    cd backend
    python -m scripts.platform_sync export

如何更新本脚本写入的内容？
  1. 在 dev 环境的 console 后台修改 / 新增 / 删除 feature 与版本-功能关联
  2. 在 backend/ 下跑 `python -m scripts.platform_sync export`
  3. 提交 git，部署后自动执行本脚本（位于 deploy/deploy.sh sync_platform_data）

如何在生产端单独触发？请使用：
    python -m scripts.platform_sync sync   （包装本脚本，带交互确认）
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


# ---------------------------------------------------------------------------
# 快照路径与加载
# ---------------------------------------------------------------------------
SNAPSHOT_DIR = (
    Path(__file__).resolve().parent.parent / "platform_sync" / "snapshots"
)
FEATURE_SNAPSHOT = SNAPSHOT_DIR / "product_feature.json"
VERSION_FEATURE_SNAPSHOT = SNAPSHOT_DIR / "version_feature.json"


def _load_features() -> list:
    """加载功能清单快照。required_tables 统一序列化为 JSON 字符串，
    便于通过 raw SQL 写入 MySQL JSON 列。"""
    if not FEATURE_SNAPSHOT.is_file():
        print(
            f"[ERROR] 找不到功能清单快照: {FEATURE_SNAPSHOT}\n"
            f"        请先在 dev 环境跑：\n"
            f"            cd backend && python -m scripts.platform_sync export\n"
            f"        以从 console API 生成 snapshots/*.json",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = json.loads(FEATURE_SNAPSHOT.read_text(encoding="utf-8"))
    features = []
    for item in raw:
        rt = item.get("required_tables")
        if isinstance(rt, list):
            rt_serialized = json.dumps(rt, ensure_ascii=False)
        elif isinstance(rt, str):
            rt_serialized = rt
        else:
            rt_serialized = None
        features.append({
            "feature_code": item["feature_code"],
            "feature_name": item["feature_name"],
            "module": item.get("module"),
            "sort_order": int(item.get("sort_order") or 0),
            "required_tables": rt_serialized,
        })
    return features


def _load_version_features() -> dict:
    """加载版本-功能映射快照：{version_code: [feature_code, ...]}"""
    if not VERSION_FEATURE_SNAPSHOT.is_file():
        print(
            f"[ERROR] 找不到版本-功能映射快照: {VERSION_FEATURE_SNAPSHOT}\n"
            f"        请先在 dev 环境跑：\n"
            f"            cd backend && python -m scripts.platform_sync export",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(VERSION_FEATURE_SNAPSHOT.read_text(encoding="utf-8"))


def main():
    settings = get_settings()
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)

    features = _load_features()
    version_features = _load_version_features()

    print(
        f"[INFO] 已加载快照：{len(features)} 个 feature，"
        f"{len(version_features)} 个版本（{', '.join(version_features.keys())}）"
    )

    with engine.connect() as conn:
        # 确保表存在
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sys_product_feature (
                id BIGINT NOT NULL AUTO_INCREMENT,
                feature_code VARCHAR(50) NOT NULL,
                feature_name VARCHAR(100) NOT NULL,
                module VARCHAR(50) DEFAULT NULL,
                description VARCHAR(255) DEFAULT NULL,
                required_tables JSON DEFAULT NULL,
                sort_order SMALLINT DEFAULT 0,
                status SMALLINT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted SMALLINT DEFAULT 0,
                PRIMARY KEY (id),
                UNIQUE KEY uk_feature_code (feature_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品功能清单表'
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sys_version_feature (
                id BIGINT NOT NULL AUTO_INCREMENT,
                version_id BIGINT NOT NULL,
                feature_id BIGINT NOT NULL,
                status SMALLINT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted SMALLINT DEFAULT 0,
                PRIMARY KEY (id),
                KEY idx_vf_version_id (version_id),
                KEY idx_vf_feature_id (feature_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='版本功能关联表'
        """))
        conn.commit()

        # 插入或更新功能清单
        for f in features:
            result = conn.execute(text(
                "SELECT id FROM sys_product_feature WHERE feature_code = :code AND is_deleted = 0"
            ), {"code": f["feature_code"]})
            existing_id = result.scalar()
            if existing_id:
                conn.execute(text(
                    "UPDATE sys_product_feature "
                    "SET feature_name = :name, module = :module, sort_order = :sort, required_tables = :tables "
                    "WHERE id = :id"
                ), {
                    "id": existing_id,
                    "name": f["feature_name"],
                    "module": f["module"],
                    "sort": f["sort_order"],
                    "tables": f["required_tables"],
                })
                print(f"  更新功能: {f['feature_code']} (id={existing_id})")
            else:
                conn.execute(text(
                    "INSERT INTO sys_product_feature (feature_code, feature_name, module, sort_order, required_tables) "
                    "VALUES (:code, :name, :module, :sort, :tables)"
                ), {
                    "code": f["feature_code"],
                    "name": f["feature_name"],
                    "module": f["module"],
                    "sort": f["sort_order"],
                    "tables": f["required_tables"],
                })
                print(f"  插入功能: {f['feature_code']} - {f['feature_name']}")
        conn.commit()

        # 建立版本-功能关联
        for version_code, feature_codes in version_features.items():
            result = conn.execute(text(
                "SELECT id FROM sys_product_version WHERE version_code = :code AND is_deleted = 0"
            ), {"code": version_code})
            version_id = result.scalar()
            if not version_id:
                print(
                    f"  [跳过] 版本 {version_code} 不存在于本环境，"
                    "如需启用请先在 console 创建该版本（或先跑 seed_data.py）"
                )
                continue

            # 清除旧关联
            conn.execute(text(
                "UPDATE sys_version_feature SET is_deleted = 1 WHERE version_id = :vid"
            ), {"vid": version_id})

            for fc in feature_codes:
                result = conn.execute(text(
                    "SELECT id FROM sys_product_feature WHERE feature_code = :code AND is_deleted = 0"
                ), {"code": fc})
                feature_id = result.scalar()
                if not feature_id:
                    print(f"  [警告] 版本 {version_code} 引用了不存在的 feature_code={fc}，已跳过")
                    continue
                conn.execute(text(
                    "INSERT INTO sys_version_feature (version_id, feature_id, status) "
                    "VALUES (:vid, :fid, 1)"
                ), {"vid": version_id, "fid": feature_id})

            print(f"  版本 {version_code}: 关联 {len(feature_codes)} 个功能")
        conn.commit()

        # ---- 末尾自检：打印「脏 feature_code」「未绑版本 feature_code」清单 ----
        feature_codes_in_snapshot = {f["feature_code"] for f in features}

        menu_codes_rows = conn.execute(text(
            "SELECT DISTINCT feature_code FROM sys_menu "
            "WHERE app_type = 'client' AND is_deleted = 0 "
            "AND feature_code IS NOT NULL AND feature_code <> ''"
        )).fetchall()
        menu_codes = {r[0] for r in menu_codes_rows if r[0]}

        bound_codes_rows = conn.execute(text(
            "SELECT DISTINCT pf.feature_code "
            "FROM sys_product_feature pf "
            "JOIN sys_version_feature vf ON vf.feature_id = pf.id "
            "WHERE pf.is_deleted = 0 AND vf.is_deleted = 0 AND vf.status = 1"
        )).fetchall()
        bound_codes = {r[0] for r in bound_codes_rows if r[0]}

        orphan = sorted(menu_codes - feature_codes_in_snapshot)
        unbound = sorted(feature_codes_in_snapshot - bound_codes)

        print("\n========== 全链路自检 ==========")
        if orphan:
            print(f"[警告] sys_menu 中引用但快照未定义的脏 feature_code 共 {len(orphan)} 个：")
            for c in orphan:
                print(f"  - {c}")
            print("  请使用 backend/scripts/fix/fix_stale_feature_codes.py 修复")
        else:
            print("[OK] sys_menu 全部 feature_code 均在快照中存在")

        if unbound:
            print(f"[提示] 快照中存在但任何启用版本都未勾选的 feature_code 共 {len(unbound)} 个：")
            for c in unbound:
                print(f"  - {c}")
        else:
            print("[OK] 所有功能都至少已关联到一个版本")
        print("==================================\n")

        # ---- 末尾：bump 所有 active 租户的 menu_version ----
        # 版本-功能关联变了之后，每个已登录的客户端需要重拉菜单。
        # 客户端 store 通过 GET /auth/menu-version 轮询比对此戳，
        # 不一致则触发整页刷新重建动态路由。
        bump_res = conn.execute(text(
            "UPDATE sys_tenant SET menu_version = menu_version + 1 "
            "WHERE is_deleted = 0"
        ))
        conn.commit()
        try:
            affected = bump_res.rowcount
        except Exception:
            affected = -1
        print(f"[OK] sys_tenant.menu_version 已统一 +1，影响 {affected} 条 → "
              f"所有在线客户端将在数秒内自动重拉菜单。\n")

    engine.dispose()
    print("\n产品功能清单和版本关联初始化完成！")


if __name__ == "__main__":
    main()
