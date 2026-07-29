# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

hist = Path(os.environ["APPDATA"]) / "Cursor" / "User" / "History"
print("hist", hist, "exists", hist.exists())
if not hist.exists():
    raise SystemExit(0)

# Find entries mentioning mp.css or 微信小程序 assets
found = []
for entries in hist.rglob("entries.json"):
    try:
        data = json.loads(entries.read_text(encoding="utf-8"))
    except Exception:
        continue
    resource = data.get("resource", "")
    if "mp.css" in resource or "mp.js" in resource or (
        "微信小程序" in resource and "assets" in resource
    ):
        found.append((entries.parent, resource, data))
        print("HIT", entries.parent.name, resource)

print("total hits", len(found))
for folder, resource, data in found:
    for e in data.get("entries", []):
        eid = e.get("id")
        src = folder / eid
        if src.exists():
            text = src.read_text(encoding="utf-8", errors="replace")
            print(
                folder.name,
                eid,
                "len",
                len(text),
                "lines",
                text.count("\n") + 1,
                "head",
                text[:100].replace("\n", " | "),
            )
            if "两端共用" in text or "原型运行时" in text or len(text) > 40000:
                out = Path(r"D:\zhitu\.tmp\recovered_assets") / f"history_{folder.name}_{eid}"
                out.write_text(text, encoding="utf-8")
                print("SAVED", out)

# Also scan workspaceStorage for backups
ws = Path(os.environ["APPDATA"]) / "Cursor" / "User" / "workspaceStorage"
print("ws", ws.exists())
count = 0
for p in ws.rglob("*"):
    if not p.is_file():
        continue
    name = p.name.lower()
    if "mp.css" in name or "mp.js" in name:
        print("ws file", p, p.stat().st_size)
        count += 1
    if count > 30:
        break

# Search any file containing 两端共用 under Cursor user data (limited)
needle = "两端共用"
checked = 0
for p in hist.rglob("*"):
    if not p.is_file() or p.suffix in (".png", ".jpg", ".zip"):
        continue
    if p.stat().st_size > 5_000_000:
        continue
    try:
        raw = p.read_bytes()
    except Exception:
        continue
    checked += 1
    if needle.encode("utf-8") in raw:
        print("NEEDLE in", p, p.stat().st_size)
print("checked history files", checked)
