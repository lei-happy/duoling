const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 用法: node shot.js <html绝对路径> <输出名> [屏幕id,屏幕id,...]
(async () => {
  const file = process.argv[2];
  const out = process.argv[3] || 'shot';
  const screens = (process.argv[4] || '').split(',').filter(Boolean);
  const outDir = path.join(__dirname, 'out');
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  await page.goto('file:///' + file.replace(/\\/g, '/'));
  await page.waitForTimeout(900);

  await page.screenshot({ path: path.join(outDir, out + '-stage.png') });

  const shotDevice = async (name) => {
    const el = await page.$('.device');
    if (el) await el.screenshot({ path: path.join(outDir, name + '.png') });
  };
  await shotDevice(out + '-00');

  for (let i = 0; i < screens.length; i++) {
    await page.evaluate((id) => {
      if (id.startsWith('sheet:')) { window.MP.openSheet(id.slice(6)); return; }
      if (id.startsWith('dialog:')) { window.MP.openDialog(id.slice(7)); return; }
      const s = window.MP.screens[id];
      window.MP.closeLayer(true);
      if (s.dataset.tabroot != null) window.MP.tab(id);
      else if (s.dataset.parent) { window.MP.root(s.dataset.parent); window.MP.push(id); }
      else window.MP.root(id);
    }, screens[i]);
    await page.waitForTimeout(750);
    await shotDevice(out + '-' + String(i + 1).padStart(2, '0') + '-' + screens[i]);
  }

  if (errors.length) console.log('JS 错误:\n' + errors.join('\n'));
  else console.log('无 JS 错误');
  await browser.close();
})();
