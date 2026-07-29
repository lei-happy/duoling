# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68.jsonl"
)
out = Path(r"D:\zhitu\.tmp\recovered_assets")

for target in (12, 53, 54, 55, 56, 67, 78, 107):
    for i, line in enumerate(p.open(encoding="utf-8"), 1):
        if i != target:
            continue
        print(f"=== L{i} len={len(line)} ===")
        try:
            obj = json.loads(line)
        except Exception as e:
            print("parse fail", e)
            (out / f"raw_L{i}.txt").write_text(line[:5000], encoding="utf-8")
            break
        content = (obj.get("message") or {}).get("content") or []
        if isinstance(content, list):
            for j, c in enumerate(content):
                if not isinstance(c, dict):
                    print(j, type(c))
                    continue
                typ = c.get("type")
                name = c.get("name")
                print(f"  [{j}] type={typ} name={name}")
                if typ == "tool_use":
                    inp = c.get("input") or {}
                    path = inp.get("path", "")
                    contents = inp.get("contents") or ""
                    new_s = inp.get("new_string") or ""
                    old_s = inp.get("old_string") or ""
                    print(f"    path={path}")
                    print(f"    contents={len(contents)} new={len(new_s)} old={len(old_s)}")
                    blob = contents or (new_s if len(new_s) > len(old_s) else old_s)
                    if blob and len(blob) > 5000:
                        fname = f"L{i}_{Path(path).name or 'blob'}_{len(blob)}.txt"
                        (out / fname).write_text(blob, encoding="utf-8")
                        print("    SAVED", fname, "head:", blob[:100].replace("\n", " | "))
                elif typ == "text":
                    t = c.get("text") or ""
                    print(f"    text len={len(t)} head={t[:120].replace(chr(10),' | ')}")
        break
