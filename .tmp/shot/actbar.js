const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 校验底部操作条：必须是 .screen 直接子元素（否则会被卷进滚动区看不见）
(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  let bad = 0;
  for (const f of fs.readdirSync(dir).filter(n => n.endsWith('.html'))) {
    await page.goto('file:///' + path.join(dir, f).replace(/\\/g, '/'));
    await page.waitForTimeout(250);
    const hits = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('.actionbar, .pickbar').forEach(el => {
        const p = el.parentElement;
        if (!p.classList.contains('screen')) {
          const s = el.closest('.screen');
          out.push((s ? s.dataset.screen : '?') + ' 的 .' + el.className.split(' ')[0] + ' 挂在 .' + p.className.split(' ')[0] + ' 里');
        }
      });
      return out;
    });
    if (hits.length) { bad++; console.log(f + '\n  ' + hits.join('\n  ')); }
  }
  console.log(bad ? '' : '底部操作条位置正确');
  await browser.close();
})();
