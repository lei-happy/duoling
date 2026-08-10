const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 列出真正被截断的文本，人工判断是否丢了关键信息
(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  for (const f of fs.readdirSync(dir).filter(n => n.endsWith('.html'))) {
    await page.goto('file:///' + path.join(dir, f).replace(/\\/g, '/'));
    await page.waitForTimeout(250);
    const hits = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('.mp *').forEach(el => {
        if (getComputedStyle(el).textOverflow !== 'ellipsis') return;
        if (el.scrollWidth - el.clientWidth < 2) return;
        out.push(el.textContent.trim());
      });
      return [...new Set(out)];
    });
    if (hits.length) console.log(f + '\n  ' + hits.join('\n  '));
  }
  await browser.close();
})();
