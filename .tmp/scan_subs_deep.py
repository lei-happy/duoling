# -*- coding: utf-8 -*-
import json
from pathlib import Path

sub = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68\subagents"
)
out = Path(r"D:\zhitu\.tmp\recovered_assets")

for f in sorted(sub.glob("*.jsonl")):
    print(f"\n=== {f.name} size={f.stat().st_size} ===")
    for i, line in enumerate(f.open(encoding="utf-8", errors="replace"), 1):
        if "mp.css" not in line and "mp.js" not in line and "Write" not in line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            if "两端共用" in line or "原型样式表" in line:
                print(f"L{i} RAW hit phrase len={len(line)}")
            continue
        content = (obj.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") != "tool_use":
                continue
            name = c.get("name")
            inp = c.get("input") or {}
            path = str(inp.get("path") or "")
            contents = inp.get("contents") or ""
            if name == "Write" and ("mp.css" in path or "mp.js" in path):
                print(f"L{i} Write {path[-60:]} len={len(contents)} lines={contents.count(chr(10))+1}")
                print(" head:", contents[:150].replace("\n", " | "))
                if len(contents) > 10000:
                    dest = out / f"SUB_{f.stem[:8]}_L{i}_{Path(path).name}"
                    dest.write_text(contents, encoding="utf-8")
                    print(" SAVED", dest.name)
            if name == "Write" and contents and (
                "两端共用" in contents[:500]
                or "原型运行时" in contents[:500]
                or "移动端微信小程序原型样式表" in contents[:300]
            ):
                print(f"L{i} SIGNATURE WRITE path={path[-60:]} len={len(contents)}")
                dest = out / f"ORIG_SIG_{f.stem[:8]}_{Path(path).name or 'blob'}"
                dest.write_text(contents, encoding="utf-8")
                print(" SAVED", dest)
