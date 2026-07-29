# -*- coding: utf-8 -*-
from pathlib import Path
import json

jf = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts\bf61f037-7da4-4399-b84e-3afeedd50d68\bf61f037-7da4-4399-b84e-3afeedd50d68.jsonl")
out = Path(r"D:\zhitu\.tmp\recovered_assets")

print("total lines", sum(1 for _ in jf.open(encoding="utf-8", errors="ignore")))

# Scan ALL tool uses that touch assets or write large content
for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
    try:
        obj = json.loads(line)
    except Exception:
        continue
    role = obj.get("role")
    parts = obj.get("message", {}).get("content", [])
    if not isinstance(parts, list):
        continue
    for part in parts:
        if part.get("type") != "tool_use":
            continue
        name = part.get("name")
        inp = part.get("input") or {}
        path = str(inp.get("path", ""))
        cmd = str(inp.get("command", ""))[:200]
        contents = inp.get("contents")
        clen = len(contents) if isinstance(contents, str) else 0
        # interesting?
        interesting = (
            "mp.css" in path
            or "mp.js" in path
            or (isinstance(contents, str) and clen > 30000)
            or ("mp.css" in cmd or "mp.js" in cmd)
            or name in ("Shell",) and ("mp.css" in str(inp.get("command", "")) or "Set-Content" in str(inp.get("command", "")) or "Out-File" in str(inp.get("command", "")))
        )
        if not interesting:
            continue
        print(f"L{i:3d} {name:12s} path={path[-70:]!r} clen={clen} cmd={cmd[:80]!r}")
        if isinstance(contents, str) and clen > 5000:
            nlines = contents.count("\n")
            head = contents[:150].replace("\n", " | ")
            print(f"       lines={nlines} head={head}")
            if nlines > 1000 or "样式表" in contents[:300] or "运行时" in contents[:300]:
                dest = out / f"ORIG_L{i}_{clen}.txt"
                dest.write_text(contents, encoding="utf-8")
                print("       >>> SAVED", dest.name)

# Also dump first StrReplace old_string context - the file already existed
print("\n=== first mp.css StrReplace old_strings (prove prior content) ===")
for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
    try:
        obj = json.loads(line)
    except Exception:
        continue
    for part in obj.get("message", {}).get("content", []) or []:
        if part.get("type") != "tool_use":
            continue
        inp = part.get("input") or {}
        if "mp.css" not in str(inp.get("path", "")):
            continue
        if part.get("name") == "StrReplace":
            old = inp.get("old_string", "")
            new = inp.get("new_string", "")
            print(f"L{i} old_len={len(old)} new_len={len(new)}")
            print(" OLD head:", old[:120].replace("\n", "|"))
            print(" NEW head:", new[:120].replace("\n", "|"))
