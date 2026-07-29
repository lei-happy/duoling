# -*- coding: utf-8 -*-
"""Find original mp.css/js by distinctive header / size / structure."""
from pathlib import Path
import json
import re

root = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts")
out = Path(r"D:\zhitu\.tmp\recovered_assets")
out.mkdir(exist_ok=True)

# Distinctive fragments from user screenshot of deleted code
needles = [
    "移动端微信小程序原型样式表",
    "两端共用，视觉差异",
    "微信小程序原型运行时",
    "避免重复写样板代码",
    "让 26 个原型文件保持一致",
    "data-app=\"driver\"",
    "data-app=\\\"driver\\\"",
]

# Also search raw files in workspace .tmp and cursor projects for large css
search_dirs = [
    root,
    Path(r"C:\Users\qinxi\AppData\Roaming\Cursor\User\History"),
    Path(r"C:\Users\qinxi\AppData\Roaming\Cursor\User\workspaceStorage"),
    Path(r"D:\zhitu\.tmp"),
]

print("=== needle scan in jsonl ===")
for jf in root.rglob("*.jsonl"):
    raw = jf.read_text(encoding="utf-8", errors="ignore")
    for n in needles:
        if n in raw:
            print("HIT", n, "in", jf.parent.name)

print("\n=== find large text files with pt-head + tag + ups ===")
candidates = []
for base in search_dirs:
    if not base.exists():
        continue
    for f in base.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() not in {".css", ".js", ".txt", ".md", ".json", ".jsonl", ""} and "entries" not in f.name:
            # still check history blobs without extension
            if "History" not in str(f):
                continue
        try:
            size = f.stat().st_size
        except OSError:
            continue
        if size < 20000 or size > 500000:
            continue
        try:
            # read start
            head = f.read_bytes()[:4000]
            if b"pt-head" not in head and b".ups" not in head and "样式表".encode() not in head:
                # deeper check for css-like
                if b":root" not in head and b"buildChrome" not in head:
                    continue
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        score = sum([
            ".pt-head" in text,
            ".tag" in text,
            ".ups" in text,
            ".route-h" in text,
            "buildChrome" in text or "buildTabbars" in text or "buildTab" in text,
            "样式表" in text or "运行时" in text,
            "两端共用" in text,
            text.count("\n") > 1500,
        ])
        if score >= 3:
            candidates.append((score, size, text.count("\n"), f))

candidates.sort(reverse=True)
print("candidates", len(candidates))
for score, size, lines, f in candidates[:20]:
    print(f"score={score} lines={lines} size={size} {f}")
    # save top ones
    if score >= 4:
        dest = out / f"CAND_{score}_{lines}_{f.name}"
        try:
            dest.write_bytes(f.read_bytes())
            print("  saved", dest.name)
        except Exception as e:
            print("  save fail", e)

# Parse bf61f037 more carefully: find ANY tool payload > 40k with CSS
print("\n=== large tool payloads in bf61f037 ===")
jf = next(root.rglob("bf61f037*/**/*.jsonl"), None)
if not jf:
    jfs = list(root.glob("bf61f037*/*.jsonl"))
    jf = jfs[0] if jfs else None
print("jf", jf)
if jf:
    for i, line in enumerate(jf.open(encoding="utf-8", errors="ignore")):
        if len(line) < 40000:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        for part in obj.get("message", {}).get("content", []) or []:
            if part.get("type") != "tool_use":
                continue
            inp = part.get("input") or {}
            for key in ("contents", "command", "new_string", "old_string"):
                val = inp.get(key)
                if not isinstance(val, str) or len(val) < 20000:
                    continue
                lines = val.count("\n")
                print(f"L{i} {part.get('name')} {key} len={len(val)} lines={lines} path={str(inp.get('path',''))[-60:]}")
                if lines > 1500 or ("样式表" in val[:500]) or (".ups" in val and ".pt-head" in val and len(val) > 40000):
                    fname = f"LARGE_L{i}_{key}_{len(val)}.txt"
                    (out / fname).write_text(val, encoding="utf-8")
                    print("  SAVED", fname, "head:", val[:100].replace("\n", "|"))
