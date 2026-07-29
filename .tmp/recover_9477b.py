# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\9477b0be-faef-45a9-9a8f-26b53ab24438"
    r"\9477b0be-faef-45a9-9a8f-26b53ab24438.jsonl"
)

keys = ("mp.css", "mp.js", "两端共用", "原型运行时", "样式表", "样板代码", "Write", "StrReplace")
for i, line in enumerate(p.open(encoding="utf-8", errors="replace"), 1):
    hits = [k for k in keys if k in line]
    if not hits:
        continue
    print(f"L{i} len={len(line)} hits={hits}")
    try:
        obj = json.loads(line)
    except Exception as e:
        print("  parse err", e)
        # dump snippet around 两端共用
        for k in ("两端共用", "原型运行时", "mp.css"):
            idx = line.find(k)
            if idx >= 0:
                print("  around", k, ":", line[max(0, idx - 80) : idx + 120])
        continue
    role = (obj.get("message") or {}).get("role")
    print("  role", role, "keys", list(obj.keys())[:10])
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        print("  content str len", len(content), content[:200].replace("\n", " | "))
    elif isinstance(content, list):
        for j, c in enumerate(content):
            if isinstance(c, dict):
                print(
                    f"  content[{j}] type={c.get('type')} name={c.get('name')} "
                    f"keys={list(c.keys())}"
                )
                if c.get("type") == "tool_use":
                    inp = c.get("input") or {}
                    print(
                        "    path",
                        str(inp.get("path", ""))[-80:],
                        "contents_len",
                        len(inp.get("contents") or ""),
                        "new_len",
                        len(inp.get("new_string") or ""),
                    )
            else:
                print(f"  content[{j}] {type(c)}")
