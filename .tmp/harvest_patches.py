# -*- coding: utf-8 -*-
"""Harvest all pre-wipe CSS/JS fragments from bf61 StrReplace ops."""
import json
from pathlib import Path

p = Path(
    r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68"
    r"\bf61f037-7da4-4399-b84e-3afeedd50d68.jsonl"
)
out = Path(r"D:\zhitu\.tmp\recovered_assets\fragments")
out.mkdir(parents=True, exist_ok=True)

css_parts = []
js_parts = []
for i, line in enumerate(p.open(encoding="utf-8"), 1):
    if i >= 72:
        break
    if "mp.css" not in line and "mp.js" not in line:
        continue
    obj = json.loads(line)
    for c in obj.get("message", {}).get("content") or []:
        if not isinstance(c, dict) or c.get("type") != "tool_use":
            continue
        if c.get("name") != "StrReplace":
            continue
        inp = c.get("input") or {}
        path = inp.get("path") or ""
        old = inp.get("old_string") or ""
        new = inp.get("new_string") or ""
        # prefer NEW (post-patch polished state); also keep OLD for context
        blob = new if len(new) >= len(old) else old
        if "mp.css" in path:
            css_parts.append((i, old, new))
            (out / f"css_L{i}_new.css").write_text(new, encoding="utf-8")
            (out / f"css_L{i}_old.css").write_text(old, encoding="utf-8")
        elif "mp.js" in path:
            js_parts.append((i, old, new))
            (out / f"js_L{i}_new.js").write_text(new, encoding="utf-8")
            (out / f"js_L{i}_old.js").write_text(old, encoding="utf-8")

# Concatenate all NEW css fragments (dedupe by exact text)
seen = set()
merged = []
for i, old, new in css_parts:
    for part in (new, old):
        if not part or part in seen:
            continue
        seen.add(part)
        merged.append(f"\n/* ---- from L{i} ---- */\n{part}\n")

all_css = "".join(merged)
(out / "_all_css_fragments.css").write_text(all_css, encoding="utf-8")
print("css ops", len(css_parts), "js ops", len(js_parts))
print("merged css chars", len(all_css), "lines", all_css.count("\n") + 1)

# Also dump assistant text that might quote large CSS
for i, line in enumerate(p.open(encoding="utf-8"), 1):
    if i >= 72:
        break
    if "智途" not in line and ".dev" not in line:
        continue
    try:
        obj = json.loads(line)
    except Exception:
        continue
    for c in obj.get("message", {}).get("content") or []:
        if isinstance(c, dict) and c.get("type") == "text":
            t = c.get("text") or ""
            if len(t) > 5000 and (".dev" in t or "mp.css" in t):
                (out / f"text_L{i}.md").write_text(t, encoding="utf-8")
                print("large text L", i, len(t))
