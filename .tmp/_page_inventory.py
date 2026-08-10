import json
import os
from collections import defaultdict

# Extract page routes from frontend views
views_root = r'D:\zhitu\frontend\client\src\views'
pages = []
for root, dirs, files in os.walk(views_root):
    if 'index.vue' in files:
        rel = os.path.relpath(root, views_root).replace('\\', '/')
        path = '/' + rel if rel != '.' else '/'
        pages.append(path)
    for f in files:
        if f.endswith('.vue') and f != 'index.vue':
            rel = os.path.relpath(os.path.join(root, f), views_root).replace('\\', '/')
            path = '/' + rel.replace('.vue', '')
            pages.append(path)

pages = sorted(set(pages))
# filter out extension/example/demo pages
skip_prefixes = ('/extension/', '/example/', '/form/', '/list/', '/result/')
biz_pages = [p for p in pages if not any(p.startswith(s) for s in skip_prefixes)]

with open(r'D:\zhitu\backend\scripts\platform_sync\snapshots\client_menu.json', encoding='utf-8') as f:
    menus = json.load(f)

menus = [m for m in menus if m.get('app_type') == 'client' and m.get('is_deleted', 0) == 0]
leaf_menus = [m for m in menus if m.get('component') and m.get('path')]

print('=== MENU PAGES (path + name) ===')
for m in sorted(leaf_menus, key=lambda x: x.get('path', '')):
    comp = m['component']
    exists = any(comp.endswith(p.replace('/index', '')) or p == comp.replace('/index', '') for p in biz_pages)
    # simpler check
    view_path = comp.replace('/index', '') + '/index.vue'
    full = os.path.join(views_root, view_path.lstrip('/'))
    exists = os.path.exists(full)
    flag = 'OK' if exists else 'MISSING'
    print(f"{flag}\t{m['path']}\t{m['menu_name']}\t{m['component']}")

print('\n=== EXTRA STATIC ROUTES ===')
static = [
    '/billing/contract/detail/:id',
    '/billing/carrier-contract/detail/:id',
    '/operation/waybill/import',
    '/operation/task-create',
    '/operation/smart-stowage',
    '/enterprise/approval-config/flow/:id',
    '/enterprise/manage',
    '/invite-landing/:code',
    '/upgrade-plans',
]
for s in static:
    print(s)

print('\n=== BIZ VIEW PAGES COUNT ===', len(biz_pages))
