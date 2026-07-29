# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(r"D:/zhitu/prototype/移动端")
errors = []
html_files = sorted(root.rglob("*.html"))

for f in html_files:
    t = f.read_text(encoding="utf-8")
    checks = [
        ("assets/mp.css", "assets/mp.css" in t),
        ("assets/mp.js", "assets/mp.js" in t),
        ("pt-head", "pt-head" in t),
        ("pt-gallery", "pt-gallery" in t),
        ("pt-rules", "pt-rules" in t),
    ]
    for name, ok in checks:
        if not ok:
            errors.append(f"{f.relative_to(root)}: missing {name}")
    assets = f.parent / "assets"
    for fn in ("mp.css", "mp.js"):
        if not (assets / fn).exists():
            errors.append(f"{f.relative_to(root)}: disk missing assets/{fn}")


def build_tree(d):
    nodes = []
    for p in sorted(d.iterdir()):
        if p.name.startswith("."):
            continue
        if p.is_dir():
            ch = build_tree(p)
            if ch:
                nodes.append({"name": p.name, "count": len(ch), "children": ch})
        elif p.suffix.lower() in {".html", ".htm"}:
            nodes.append({"name": p.name, "type": "html"})
    return nodes


tree = build_tree(root)
driver_count = len(list((root / "驾驶员微信小程序").glob("*.html")))
admin_count = len(list((root / "后台人员微信小程序").glob("*.html")))

print(f"Total HTML: {len(html_files)} (driver={driver_count}, admin={admin_count})")
for branch in tree:
    n = branch.get("count", 0)
    print(f"  {branch['name']}: {n} items")
if errors:
    print("ERRORS:")
    for e in errors:
        print(" ", e)
    raise SystemExit(1)
print("All checks passed")
