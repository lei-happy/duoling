# -*- coding: utf-8 -*-
import re
from pathlib import Path

root = Path(r"d:\zhitu\frontend\client\src\api")
pat = re.compile(r"""['"`](/[A-Za-z0-9_\-./{}]+)['"`]""")
found = set()
for f in root.rglob("*.ts"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    for m in pat.findall(text):
        if "${" in m or "{" in m:
            # keep templates with {id} lightly
            if m.count("{") > 2:
                continue
        found.add(m)

for p in sorted(found):
    print(p)
