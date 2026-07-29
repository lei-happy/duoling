# -*- coding: utf-8 -*-
from pathlib import Path
import json

roots = [
    Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts\bf61f037-7da4-4399-b84e-3afeedd50d68"),
    Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts\8b162f96-dae6-4e41-93b4-7f8c85e4b07b"),
]
out = Path(r"D:\zhitu\.tmp\recovered_assets")
out.mkdir(exist_ok=True)

for root in roots:
    print("===", root.name, "===")
    for jf in root.rglob("*.jsonl"):
        for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
            if "mp.css" not in line and "mp.js" not in line and "原型样式" not in line and "样板代码" not in line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            for part in obj.get("message", {}).get("content", []) or []:
                if part.get("type") != "tool_use":
                    continue
                inp = part.get("input") or {}
                path = str(inp.get("path", ""))
                c = inp.get("contents")
                if not isinstance(c, str):
                    continue
                if "mp.css" in path or "mp.js" in path or (len(c) > 40000 and (".pt-head" in c or "样式表" in c[:500])):
                    nlines = c.count("\n")
                    rel = jf.relative_to(root)
                    print(f"{rel} L{i} {part.get('name')} path=...{path[-40:]} len={len(c)} lines={nlines}")
                    print("  head:", c[:160].replace("\n", " | "))
                    if nlines > 1800 or "样式表" in c[:400] or "运行时" in c[:400] or ("两端共用" in c[:400]):
                        dest = out / f"SUB_{root.name[:8]}_{jf.stem[:12]}_L{i}_{len(c)}.txt"
                        dest.write_text(c, encoding="utf-8")
                        print("  >>> SAVED", dest.name)

# Also search ALL transcripts for 样式表 / 样板代码 in contents
print("\n=== global contents search ===")
base = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts")
for jf in base.rglob("*.jsonl"):
    # quick filter
    try:
        raw = jf.read_bytes()
    except Exception:
        continue
    if "样式表".encode("utf-8") not in raw and "样板代码".encode("utf-8") not in raw and "原型运行时".encode("utf-8") not in raw:
        continue
    print("FILE HIT", jf)
    for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
        if "样式表" not in line and "样板代码" not in line and "原型运行时" not in line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            print("  L", i, "raw len", len(line))
            continue
        for part in obj.get("message", {}).get("content", []) or []:
            if part.get("type") != "tool_use":
                continue
            inp = part.get("input") or {}
            for key in ("contents", "old_string", "new_string"):
                val = inp.get(key)
                if isinstance(val, str) and ("样式表" in val or "样板代码" in val or "原型运行时" in val):
                    dest = out / f"GLOBAL_{jf.parent.name[:8]}_L{i}_{key}_{len(val)}.txt"
                    dest.write_text(val, encoding="utf-8")
                    print("  saved", dest.name, "lines", val.count("\n"), "path", str(inp.get("path", ""))[-50:])
