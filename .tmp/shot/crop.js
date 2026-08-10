const { chromium } = require('playwright');
const path = require('path');

// 截屏幕底部区域: node crop.js <html> <out> [screenId]
(async () => {
  const file = process.argv[2];
  const out = process.argv[3];
  const screen = process.argv[4];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 3 });
  await page.goto('file:///' + file.replace(/\\/g, '/'));
  await page.waitForTimeout(700);
  if (screen) {
    await page.evaluate((id) => {
      const s = window.MP.screens[id];
      if (s.dataset.tabroot != null) window.MP.tab(id);
      else if (s.dataset.parent) { window.MP.root(s.dataset.parent); window.MP.push(id); }
      else window.MP.root(id);
    }, screen);
    await page.waitForTimeout(700);
  }
  const box = await (await page.$('.device')).boundingBox();
  await page.screenshot({
    path: path.join(__dirname, 'out', out + '.png'),
    clip: { x: box.x, y: box.y + box.height - 260, width: box.width, height: 260 }
  });
  await browser.close();
})();
