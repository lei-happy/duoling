# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序")
classes = set()
for f in p.glob("*.html"):
    t = f.read_text(encoding="utf-8")
    print("FILE", f.name, "bytes", f.stat().st_size)
    # style blocks?
    if "<style" in t:
        print("  has inline style")
    if "svg" in t[:2000].lower() or 'id="i-' in t or "symbol" in t:
        print("  has svg sprites likely")
    for m in re.findall(r'class="([^"]+)"', t):
        for c in m.split():
            classes.add(c)

print("\nALL CLASSES", len(classes))
for c in sorted(classes):
    print(c)
