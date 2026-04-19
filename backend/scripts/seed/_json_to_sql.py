"""
将 backend/scripts/seed/sys_menu.json 转换为 项目文档/sys_menu.sql 的 INSERT 语句格式。

输出与现有 sys_menu.sql 完全一致的结构（每行一条 INSERT），便于作为参考文档。
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "backend" / "scripts" / "seed" / "sys_menu.json"
DST = ROOT / "项目文档" / "sys_menu.sql"


def _date(s):
    """统一时间格式 → 'YYYY-MM-DD HH:MM:SS'。
    兼容 'D/M/YYYY HH:MM:SS' 与 'YYYY-MM-DD HH:MM:SS'。
    """
    if not s:
        return "2026-04-19 12:00:00"
    s = str(s).strip()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return "2026-04-19 12:00:00"


def _q(v):
    """SQL 字面量序列化"""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


COLS = (
    "parent_id", "menu_name", "menu_code", "menu_type",
    "path", "component", "icon", "sort_order",
    "visible", "status", "app_type", "feature_code",
    "id", "created_at", "updated_at", "is_deleted",
)


def row_to_sql(r: dict) -> str:
    vals = []
    for c in COLS:
        v = r.get(c)
        if c == "menu_code" and v == "":
            v = ""  # 保留空串兼容旧数据
        if c in ("created_at", "updated_at"):
            v = _date(v)
        vals.append(_q(v))
    cols_q = ", ".join(f"`{c}`" for c in COLS)
    return (
        f"INSERT INTO `sys_menu` ({cols_q}) VALUES ({', '.join(vals)});"
    )


def main():
    with open(SRC, encoding="utf-8") as f:
        rows = json.load(f)
    rows.sort(key=lambda x: int(x["id"]))
    lines = [row_to_sql(r) for r in rows]
    DST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已写入 {DST}（共 {len(rows)} 条）")


if __name__ == "__main__":
    main()
