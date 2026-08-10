const fs = require('fs');
const path = require('path');

// 校验 tabBar：目标屏存在、起始屏被某个 tab 指向、无孤儿 tabroot
const dir = process.argv[2];
let bad = 0;
for (const f of fs.readdirSync(dir).filter(n => n.endsWith('.html'))) {
  const html = fs.readFileSync(path.join(dir, f), 'utf8');
  const screens = [...html.matchAll(/data-screen="([^"]+)"/g)].map(m => m[1]);
  const tabroots = [...html.matchAll(/<section class="screen"[^>]*>/g)]
    .filter(m => m[0].includes('data-tabroot'))
    .map(m => /data-screen="([^"]+)"/.exec(m[0])[1]);
  const tabs = [...html.matchAll(/class="tabi" data-tab="([^"]+)"/g)].map(m => m[1]);
  if (!tabs.length) continue;
  const start = (/<section class="screen"[^>]*data-start[^>]*>/.exec(html) || [''])[0];
  const startId = start ? /data-screen="([^"]+)"/.exec(start)[1] : tabroots[0];
  const msgs = [];
  tabs.forEach(t => { if (!screens.includes(t)) msgs.push('tab 指向不存在的屏: ' + t); });
  if (!tabs.includes(startId)) msgs.push('起始屏 ' + startId + ' 没有对应 tab（tabBar 无高亮）');
  tabroots.forEach(r => { if (!tabs.includes(r)) msgs.push('孤儿 tabroot: ' + r); });
  if (msgs.length) { bad++; console.log(f + '\n  ' + msgs.join('\n  ')); }
}
console.log(bad ? '' : 'tabBar 全部一致');
