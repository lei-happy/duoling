# -*- coding: utf-8 -*-
"""Global search for original mp.css/mp.js Write blobs by signature phrases."""
import json
from pathlib import Path

root = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts")
out = Path(r"D:\zhitu\.tmp\recovered_assets")
out.mkdir(parents=True, exist_ok=True)

phrases = (
    "两端共用",
    "原型运行时",
    "样板代码",
    "移动端微信小程序原型样式表",
    "全量保持",
    "26 个原型",
    "26个原型",
    "data-app=\"driver\"",
    "buildTabbars",
    "buildChrome",
)

hits = []
for f in sorted(root.rglob("*.jsonl")):
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print("read fail", f, e)
        continue
    found = [p for p in phrases if p in text]
    if not found:
        continue
    print(f"FILE {f.relative_to(root)} phrases={found} size={f.stat().st_size}")
    # line-level extract of Writes
    for i, line in enumerate(text.splitlines(), 1):
        if not any(p in line for p in phrases):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            # raw dump around phrase
            for p in found:
                idx = line.find(p)
                if idx >= 0:
                    print(f"  L{i} raw around {p}: ...{line[max(0,idx-40):idx+80]}...")
            continue
        content = (obj.get("message") or {}).get("content") or []
        if isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use" and c.get("name") in ("Write", "StrReplace"):
                    inp = c.get("input") or {}
                    blob = inp.get("contents") or inp.get("new_string") or ""
                    path = inp.get("path") or ""
                    if any(p in blob for p in phrases) or any(p in path for p in ("mp.css", "mp.js")):
                        print(
                            f"  L{i} {c['name']} path=...{path[-60:]} "
                            f"blob={len(blob)}"
                        )
                        if len(blob) > 8000 and any(
                            p in blob[:400] for p in ("两端共用", "原型运行时", "样式表", "运行时")
                        ):
                            name = f"ORIG_{f.parent.name}_L{i}_{Path(path).name or 'blob'}"
                            (out / name).write_text(blob, encoding="utf-8")
                            print("  SAVED", name, "lines", blob.count("\n") + 1)
                            hits.append(out / name)
                elif c.get("type") == "text":
                    t = c.get("text") or ""
                    if any(p in t for p in phrases):
                        print(f"  L{i} text len={len(t)} head={t[:120].replace(chr(10),' | ')}")

print("saved hits", len(hits))
for h in hits:
    print(h, h.stat().st_size)
