import json
from collections import defaultdict

with open(r'D:\zhitu\backend\scripts\platform_sync\snapshots\client_menu.json', encoding='utf-8') as f:
    menus = json.load(f)

menus = [m for m in menus if m.get('app_type') == 'client' and m.get('is_deleted', 0) == 0]
children = defaultdict(list)
for m in menus:
    children[m['parent_id']].append(m)
for pid in children:
    children[pid].sort(key=lambda x: (x.get('sort_order', 0), x['id']))

def walk(pid, depth=0):
    for m in children.get(pid, []):
        indent = '  ' * depth
        comp = m.get('component') or ''
        feat = m.get('feature_code') or ''
        print(f"{indent}- {m['menu_name']} | path={m.get('path','')} | component={comp} | feature={feat}")
        walk(m['id'], depth + 1)

walk(0)
print('---TOTAL---', len(menus))
