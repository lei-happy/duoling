# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\9477b0be-faef-45a9-9a8f-26b53ab24438"
    r"\9477b0be-faef-45a9-9a8f-26b53ab24438.jsonl"
)
out = Path(r"D:\zhitu\.tmp\recovered_assets")
out.mkdir(parents=True, exist_ok=True)
print("size", p.stat().st_size)

for i, line in enumerate(p.open(encoding="utf-8", errors="replace"), 1):
    if not any(
        k in line
        for k in (
            "mp.css",
            "mp.js",
            "两端共用",
            "原型运行时",
            "样式表",
            "样板代码",
        )
    ):
        continue
    try:
        obj = json.loads(line)
    except Exception:
        print(f"L{i} parse fail len={len(line)} has_phrase={'两端共用' in line}")
        continue
    for c in (obj.get("message") or {}).get("content") or []:
        if not isinstance(c, dict):
            continue
        if c.get("type") != "tool_use":
            continue
        name = c.get("name")
        if name not in ("Write", "StrReplace"):
            continue
        inp = c.get("input") or {}
        path = inp.get("path", "")
        contents = inp.get("contents") or inp.get("new_string") or ""
        old = inp.get("old_string") or ""
        blob = contents or old
        interesting = (
            "mp.css" in path
            or "mp.js" in path
            or "两端共用" in blob[:500]
            or "原型运行时" in blob[:500]
            or "样板代码" in blob[:500]
        )
        if not interesting:
            continue
        print(
            f"L{i} {name} path={path[-70:]} content_len={len(contents)} "
            f"old_len={len(old)}"
        )
        if contents:
            print("  head:", contents[:140].replace("\n", " | "))
            if len(contents) > 5000 and ("mp.css" in path or "两端共用" in contents[:300]):
                fname = f"9477_L{i}_{Path(path).name or 'blob'}"
                (out / fname).write_text(contents, encoding="utf-8")
                print("  SAVED", fname, "lines", contents.count("\n") + 1)
