const { chromium } = require('playwright');
(async () => {
  const file = process.argv[2];
  const sel = process.argv[3];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto('file:///' + file.replace(/\\/g, '/'));
  await page.waitForTimeout(700);
  const info = await page.evaluate((sel) => {
    const el = document.querySelector('.screen.is-active ' + sel);
    if (!el) return 'not found';
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      rect: { top: Math.round(r.top), h: Math.round(r.height), w: Math.round(r.width) },
      display: cs.display, position: cs.position, overflow: cs.overflow, zIndex: cs.zIndex,
      parent: el.parentElement.className,
      parentRect: (p => ({ top: Math.round(p.top), h: Math.round(p.height) }))(el.parentElement.getBoundingClientRect()),
      children: [...el.children].map(c => c.className + ' h=' + Math.round(c.getBoundingClientRect().height))
    };
  }, sel);
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
})();
