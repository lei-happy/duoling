import json
from pathlib import Path

d = json.loads(Path(r"D:/zhitu/.cursor_menu_tree.json").read_text(encoding="utf-8"))
lines = []
for x in d:
    children = x.get("children", [])
    lines.append(f"## {x['title']} ({x['path']}) — {len(children)} children")
    for c in children:
        gc = len(c.get("children", []))
        lines.append(f"  - {c['title']} ({c['path']}) [{gc} sub]")
Path(r"D:/zhitu/.tmp/menu_summary.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok", len(lines))
