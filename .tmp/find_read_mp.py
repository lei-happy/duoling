# -*- coding: utf-8 -*-
"""Find Read tool results or assistant dumps of original mp.css."""
import json
import re
from pathlib import Path

roots = [
    Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts"),
    Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-tools"),
]

# signatures unique to polished original (from patches)
sigs = [
    "单据状态横幅：底色与导航栏同色保持无缝",
    "画板进场",
    "个人中心头图",
    "--r-l:",
    "wx-capsule",
    "function reveal",
]

for root in roots:
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        if f.stat().st_size < 5000 or f.stat().st_size > 8_000_000:
            continue
        if f.suffix.lower() not in {".jsonl", ".txt", ".json", ".css", ".js", ".md", ""}:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        hit = [s for s in sigs if s in text]
        if not hit:
            continue
        print(f"\nFILE {f} size={f.stat().st_size} hits={hit}")
        # if it looks like a full css file
        if text.lstrip().startswith("/*") and ".pt-head" in text and len(text) > 40000:
            out = Path(r"D:\zhitu\.tmp\recovered_assets") / f"CANDIDATE_{f.stem}.css"
            out.write_text(text, encoding="utf-8")
            print("  SAVED CANDIDATE", out, "lines", text.count("\n") + 1)
        # if jsonl, find large contents fields
        if f.suffix == ".jsonl":
            for i, line in enumerate(text.splitlines(), 1):
                if "mp.css" not in line and "单据状态横幅" not in line:
                    continue
                if len(line) < 10000:
                    continue
                print(f"  L{i} len={len(line)}")
                # try extract contents
                for m in re.finditer(r'"contents"\s*:\s*"', line):
                    # unescape roughly by json
                    pass
                try:
                    obj = json.loads(line)
                except Exception:
                    # search for length of escaped css
                    idx = line.find("单据状态横幅")
                    if idx > 0:
                        print("  raw around banner comment present")
                    continue
                content = (obj.get("message") or {}).get("content")
                if isinstance(content, list):
                    for c in content:
                        if not isinstance(c, dict):
                            continue
                        # tool_result?
                        if c.get("type") in ("tool_result", "tool_use"):
                            inp = c.get("input") or c.get("content") or ""
                            if isinstance(inp, dict):
                                blob = inp.get("contents") or inp.get("new_string") or ""
                            else:
                                blob = str(inp)
                            if isinstance(blob, str) and len(blob) > 30000 and ".pt-head" in blob:
                                out = Path(r"D:\zhitu\.tmp\recovered_assets") / f"FROM_{f.parent.name}_L{i}.css"
                                out.write_text(blob, encoding="utf-8")
                                print("  SAVED", out, len(blob))
