# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序")
css = (root / "assets/mp.css").read_text(encoding="utf-8")
js = (root / "assets/mp.js").read_text(encoding="utf-8")

classes = set()
icons = set()
for f in root.glob("0*.html"):
    t = f.read_text(encoding="utf-8")
    for m in re.findall(r'class="([^"]+)"', t):
        classes.update(m.split())
    for m in re.findall(r'href="#(i-[^"]+)"', t):
        icons.add(m)

# classes that look component-like and might be missing from CSS
suspect = []
for c in sorted(classes):
    if c in ("on", "in", "to", "b", "n", "t", "k", "v", "d", "s", "g", "r", "w", "sm", "lg", "xs", "rel", "fx", "grow", "between", "strong", "mut", "blue", "green", "err", "dim", "full", "bare", "flush", "auto", "scroll", "white", "block", "wide", "line", "ghost", "danger", "success", "warn", "soft", "dis", "primary", "warning", "info", "muted", "active", "done", "now", "cur", "sq", "tl", "bar", "parallel"):
        continue
    # present if .classname { or .classname, or .classname. or space
    if f".{c}" not in css and f".{c} " not in css:
        suspect.append(c)

print("MISSING_OR_WEAK_CLASSES", len(suspect))
for c in suspect:
    print(" ", c)

print("\nICONS_USED")
for i in sorted(icons):
    present = i.replace("i-", "") in js or f'"{i}"' in js or f"'{i}'" in js or f"id=\"{i}\"" in js or f"i-{i[2:]}" in js
    # check symbol generation: ICONS keys
    key = i[2:]
    ok = f"{key}:" in js or f'"{key}"' in js or f"'{key}'" in js
    print((" OK" if ok else "MISS"), i)
