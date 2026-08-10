const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 切换角色视图后截图: node role.js <html> <out> <boss|fin|disp>
(async () => {
  const file = process.argv[2];
  const out = process.argv[3];
  const role = process.argv[4];
  const outDir = path.join(__dirname, 'out');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  await page.goto('file:///' + file.replace(/\\/g, '/'));
  await page.waitForTimeout(700);
  await page.click('.roles button[data-role="' + role + '"]');
  await page.waitForTimeout(900);
  const el = await page.$('.device');
  await el.screenshot({ path: path.join(outDir, out + '.png') });
  await browser.close();
})();
