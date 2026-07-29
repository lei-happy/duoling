# -*- coding: utf-8 -*-
"""Scan bf61 transcript for all mp.css / mp.js tool ops and reconstruct timeline."""
import json
from pathlib import Path

root = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-transcripts")
tid = "bf61f037-7da4-4399-b84e-3afeedd50d68"
main = root / tid / f"{tid}.jsonl"
out = Path(r"D:\zhitu\.tmp\recovered_assets")
out.mkdir(parents=True, exist_ok=True)

ops = []


def walk(path: Path):
    if not path.exists():
        return
    for i, line in enumerate(path.open(encoding="utf-8", errors="replace"), 1):
        if "mp.css" not in line and "mp.js" not in line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        content = (obj.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            name = c.get("name")
            if name not in ("Write", "StrReplace"):
                continue
            inp = c.get("input") or {}
            p = inp.get("path") or ""
            if "mp.css" not in p and "mp.js" not in p:
                continue
            contents = inp.get("contents") or ""
            new_s = inp.get("new_string") or ""
            old_s = inp.get("old_string") or ""
            ops.append(
                {
                    "file": path.name,
                    "line": i,
                    "name": name,
                    "path": p,
                    "contents_len": len(contents),
                    "new_len": len(new_s),
                    "old_len": len(old_s),
                    "head": (contents or new_s or old_s)[:160].replace("\n", " | "),
                    "contents": contents,
                    "new_string": new_s,
                    "old_string": old_s,
                }
            )


walk(main)
sub = root / tid / "subagents"
if sub.exists():
    for f in sorted(sub.glob("*.jsonl")):
        walk(f)

print(f"ops={len(ops)}")
for o in ops:
    print(
        f"{o['file']} L{o['line']} {o['name']} "
        f"path=...{o['path'][-50:]} c={o['contents_len']} "
        f"new={o['new_len']} old={o['old_len']}"
    )
    print(" ", o["head"][:140])

# Save largest Write blobs and all StrReplace old/new for css
css_patches = []
js_patches = []
for o in ops:
    base = Path(o["path"]).name
    if o["name"] == "Write" and o["contents_len"] > 1000:
        fname = f"{o['file']}_L{o['line']}_{base}"
        (out / fname).write_text(o["contents"], encoding="utf-8")
        print("SAVED WRITE", fname, o["contents"].count("\n") + 1)
    if o["name"] == "StrReplace":
        target = css_patches if base == "mp.css" else js_patches
        target.append(o)
        # also save individual
        (out / f"patch_{base}_L{o['line']}_old.txt").write_text(
            o["old_string"], encoding="utf-8"
        )
        (out / f"patch_{base}_L{o['line']}_new.txt").write_text(
            o["new_string"], encoding="utf-8"
        )

print("css_patches", len(css_patches), "js_patches", len(js_patches))

# Heuristic: largest old_string that looks like a substantial original chunk
for label, patches in (("css", css_patches), ("js", js_patches)):
    if not patches:
        continue
    best = max(patches, key=lambda x: x["old_len"])
    print(f"largest {label} old_string L{best['line']} len={best['old_len']}")
    print(" head:", best["old_string"][:200].replace("\n", " | "))
