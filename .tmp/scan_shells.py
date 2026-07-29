# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68.jsonl"
)
for i, line in enumerate(p.open(encoding="utf-8"), 1):
    if i > 72:
        break
    if '"Shell"' not in line and '"Write"' not in line:
        continue
    try:
        obj = json.loads(line)
    except Exception:
        continue
    for c in (obj.get("message") or {}).get("content") or []:
        if not isinstance(c, dict) or c.get("type") != "tool_use":
            continue
        name = c.get("name")
        if name not in ("Shell", "Write"):
            continue
        inp = c.get("input") or {}
        if name == "Shell":
            cmd = inp.get("command") or ""
            if any(k in cmd for k in ("mp.css", "mp.js", "assets", "prototype", "python")):
                print(f"L{i} Shell: {cmd[:240].replace(chr(10), ' | ')}")
        else:
            path = inp.get("path") or ""
            contents = inp.get("contents") or ""
            if "mp." in path or "assets" in path or "build" in path.lower():
                print(
                    f"L{i} Write {path[-70:]} len={len(contents)} "
                    f"head={(contents[:80]).replace(chr(10),' | ')}"
                )
