# -*- coding: utf-8 -*-
"""Compare classes used in driver HTML 01-06 vs defined in current mp.css."""
import re
from pathlib import Path
from collections import Counter

root = Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序")
css = (root / "assets" / "mp.css").read_text(encoding="utf-8")
js = (root / "assets" / "mp.js").read_text(encoding="utf-8")

# classes defined in css (rough)
defined = set(re.findall(r"\.([a-zA-Z_][a-zA-Z0-9_-]*)", css))
# also ids in js/css
defined_ids = set(re.findall(r"#([a-zA-Z_][a-zA-Z0-9_-]*)", css + js))

used = Counter()
used_ids = Counter()
for html in sorted(root.glob("0[1-6]*.html")):
    text = html.read_text(encoding="utf-8")
    for m in re.finditer(r'class="([^"]+)"', text):
        for c in m.group(1).split():
            used[c] += 1
    for m in re.finditer(r'id="([^"]+)"', text):
        used_ids[m.group(1)] += 1
    for m in re.finditer(r'href="#(i-[^"]+)"', text):
        used_ids[m.group(1)] += 1
    for m in re.finditer(r'<use[^>]+href="#([^"]+)"', text):
        used_ids[m.group(1)] += 1

missing = sorted([c for c in used if c not in defined], key=lambda x: -used[x])
print("HTML 01-06 unique classes", len(used), "css selectors", len(defined))
print("missing classes (top 40):")
for c in missing[:40]:
    print(f"  .{c} x{used[c]}")

# icon ids referenced
icon_refs = sorted({i for i in used_ids if i.startswith("i-")})
js_icons = set(re.findall(r"['\"](i-[a-z0-9-]+)['\"]", js)) | set(
    re.findall(r"id=['\"](i-[a-z0-9-]+)['\"]", js)
)
# ICONS keys in js
icon_keys = set(re.findall(r"^\s*([a-z0-9_]+):\s*'<", js, re.M))
print("\nicon hrefs", icon_refs)
print("js icon ids", sorted(js_icons)[:30])
print("js ICONS keys", sorted(icon_keys))

# Check tabbar / chrome expectations
for needle in (
    "tabbar",
    "wx-foot",
    "buildChrome",
    "buildTabbars",
    "pt-rail",
    "data-badge",
    "sprite",
    "i-camera",
    "i-money",
):
    print(f"{needle}: css={needle in css} js={needle in js}")

print("\ncss lines", css.count("\n") + 1, "js lines", js.count("\n") + 1)
print("css bytes", len(css.encode("utf-8")), "js bytes", len(js.encode("utf-8")))
