const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// reduced-motion 降级验证: node rm.js <html> <out> [screenId]
(async () => {
  const file = process.argv[2];
  const out = process.argv[3] || 'rm';
  const screen = process.argv[4];
  const outDir = path.join(__dirname, 'out');
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  await page.goto('file:///' + file.replace(/\\/g, '/'));
  await page.waitForTimeout(700);
  if (screen) {
    await page.evaluate((id) => {
      const s = window.MP.screens[id];
      if (s.dataset.tabroot != null) window.MP.tab(id);
      else if (s.dataset.parent) { window.MP.root(s.dataset.parent); window.MP.push(id); }
      else window.MP.root(id);
    }, screen);
    await page.waitForTimeout(600);
  }
  const el = await page.$('.device');
  await el.screenshot({ path: path.join(outDir, out + '.png') });
  console.log(errors.length ? errors.join('\n') : 'reduced-motion 无错误');
  await browser.close();
})();
