# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68.jsonl"
)
# first 10 lines summary
for i, line in enumerate(p.open(encoding="utf-8"), 1):
    if i > 10:
        break
    try:
        obj = json.loads(line)
    except Exception:
        print(i, "parse fail", len(line))
        continue
    content = (obj.get("message") or {}).get("content") or []
    role = obj.get("role") or (obj.get("message") or {}).get("role")
    print(f"L{i} role={role} len={len(line)}")
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict):
                print(
                    f"  type={c.get('type')} name={c.get('name')} "
                    f"text_len={len(c.get('text') or '')} "
                    f"path={str((c.get('input') or {}).get('path') or '')[-70:]}"
                )

# also list ALL parent transcripts that mention 驾驶员微信小程序/assets
root = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts")
for f in root.glob("*/*.jsonl"):
    if "subagents" in str(f):
        continue
    try:
        t = f.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if "驾驶员微信小程序" in t and "mp.css" in t:
        # count Write of mp.css
        n = t.count("mp.css")
        print(f"TRANSCRIPT {f.parent.name} mp.css mentions={n} size={f.stat().st_size}")
