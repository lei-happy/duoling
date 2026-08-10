const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 找出设了 text-overflow:ellipsis 却仍是 inline 的元素（省略号不会生效）
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
      document.querySelectorAll('.mp *').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.textOverflow === 'ellipsis' && cs.display === 'inline') {
          out.push(el.className || el.tagName);
        }
      });
      return [...new Set(out)];
    });
    if (hits.length) { bad++; console.log(f + ' → ' + hits.join(', ')); }
  }
  console.log(bad ? '' : '省略号全部生效');
  await browser.close();
})();
