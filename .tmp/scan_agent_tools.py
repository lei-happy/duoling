# -*- coding: utf-8 -*-
from pathlib import Path

dir_ = Path(r"C:\Users\qinxi\.cursor\projects\d-zhitu\agent-tools")
needles = [
    "移动端微信小程序原型样式表",
    "两端共用",
    "原型运行时",
    "全量保持",
    "样板代码",
    "buildTabbars",
    "function reveal",
    "智途 · 移动端",
]
for f in sorted(dir_.iterdir(), key=lambda p: -p.stat().st_size):
    if not f.is_file():
        continue
    raw = f.read_bytes()
    # try utf-8
    try:
        text = raw.decode("utf-8")
    except Exception:
        text = raw.decode("utf-8", errors="replace")
    hits = [n for n in needles if n in text]
    if hits:
        print(f"HIT {f.name} size={f.stat().st_size} hits={hits}")
        for n in hits:
            i = text.find(n)
            print(" ", n, "ctx:", repr(text[max(0, i - 60) : i + 80]))
    # look for very large CSS blocks mentioning both pt-gallery and wx-capsule
    if "pt-gallery" in text and "wx-capsule" in text and ".dev .banner" in text:
        print(f"RICHPROTO {f.name} size={f.stat().st_size}")
        # estimate css size if present
        if "contents" in text[:500] or '"contents"' in text:
            print("  may be tool payload")
