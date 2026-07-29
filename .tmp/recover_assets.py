# -*- coding: utf-8 -*-
from pathlib import Path
import json

root = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts")
out_dir = Path(r"D:\zhitu\.tmp\recovered_assets")
out_dir.mkdir(parents=True, exist_ok=True)

best = []
for jf in root.rglob("*.jsonl"):
    for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
        if "mp.css" not in line and "mp.js" not in line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        content = obj.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for part in content:
            if part.get("type") != "tool_use":
                continue
            inp = part.get("input") or {}
            path = str(inp.get("path", ""))
            name = part.get("name")
            # Write with full contents
            c = inp.get("contents")
            if isinstance(c, str) and ("mp.css" in path or "mp.js" in path):
                kind = "css" if path.endswith("mp.css") else "js"
                fname = f"{jf.parent.name}_L{i}_{kind}_{len(c)}.{kind}"
                (out_dir / fname).write_text(c, encoding="utf-8")
                best.append((len(c), kind, fname, c[:100].replace("\n", "|")))
            # Also catch large CSS-like blobs
            if isinstance(c, str) and len(c) > 25000 and ".pt-head" in c and (".tag" in c or ".dev" in c):
                fname = f"BLOB_{jf.parent.name}_L{i}_{len(c)}.css"
                (out_dir / fname).write_text(c, encoding="utf-8")
                print("BLOB", fname)
            # StrReplace new_string that is huge
            ns = inp.get("new_string")
            if isinstance(ns, str) and len(ns) > 15000 and ("mp.css" in path or ".pt-head" in ns):
                fname = f"PATCHNEW_{jf.parent.name}_L{i}_{len(ns)}.txt"
                (out_dir / fname).write_text(ns, encoding="utf-8")
                print("BIG PATCH", fname)

print("=== writes ===")
for b in sorted(best, reverse=True):
    print(f"{b[0]:6d} {b[1]:3s} {b[2]}")
    print("      ", b[3][:80])

# Also scan for the distinctive original header comment fragments in any form
print("\n=== header scan ===")
for jf in root.rglob("*.jsonl"):
    for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
        if "样板代码" in line or "两端共用" in line or "原型样式表" in line or "原型运行时" in line:
            print("HIT", jf.parent.name, i, len(line))
            # try extract
            try:
                obj = json.loads(line)
            except Exception:
                # raw extract between markers
                continue
            for part in obj.get("message", {}).get("content", []) or []:
                if part.get("type") != "tool_use":
                    continue
                inp = part.get("input") or {}
                for key in ("contents", "old_string", "new_string"):
                    val = inp.get(key)
                    if isinstance(val, str) and ("样板代码" in val or "两端共用" in val or "原型样式表" in val or "原型运行时" in val):
                        ext = "css" if ("样式" in val[:200] or ":root" in val) else "js"
                        fname = f"HEADER_{jf.parent.name}_L{i}_{key}_{len(val)}.{ext}"
                        (out_dir / fname).write_text(val, encoding="utf-8")
                        print("  saved", fname)
