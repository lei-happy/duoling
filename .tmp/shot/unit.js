const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 找出被 CSS 误伤成 block 的行内单位 span（会把「万 / % / 元」挤到下一行）
(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  let bad = 0;
  for (const f of fs.readdirSync(dir).filter(n => n.endsWith('.html'))) {
    await page.goto('file:///' + path.join(dir, f).replace(/\\/g, '/'));
    await page.waitForTimeout(300);
    const hits = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('.mp b > span, .mp strong > span').forEach(el => {
        if (getComputedStyle(el).display === 'block') {
          out.push((el.parentElement.className || 'b') + ' → “' + el.textContent.trim() + '”');
        }
      });
      return [...new Set(out)];
    });
    if (hits.length) { bad++; console.log(f + '\n  ' + hits.join('\n  ')); }
  }
  console.log(bad ? '' : '行内单位无误伤');
  await browser.close();
})();
