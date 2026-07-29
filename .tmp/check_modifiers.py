# -*- coding: utf-8 -*-
import re
from pathlib import Path

root = Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序")
css = (root / "assets/mp.css").read_text(encoding="utf-8")
short = ["c", "cur", "act", "st", "sh", "sq", "tt", "x", "bad", "g", "o", "i", "r", "sm", "lg"]

for html in sorted(root.glob("0[1-6]*.html")):
    text = html.read_text(encoding="utf-8")
    for m in re.finditer(r'class="([^"]+)"', text):
        parts = m.group(1).split()
        for p in parts:
            if p in short:
                # context: nearby 80 chars
                start = max(0, m.start() - 40)
                ctx = text[start : m.end() + 40].replace("\n", " ")
                # check if css has parent.child or .p
                ok = f".{p}" in css or f".{p} " in css or f".{p}," in css or f".{p}:" in css
                print(f"{html.name}: .{p} css={ok} :: {ctx[:120]}")
