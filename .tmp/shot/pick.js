const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  await page.goto('file:///D:/zhitu/prototype/移动端/后台人员微信小程序/05-调度工作台五阶段.html');
  await page.waitForTimeout(700);
  await page.click('[data-mode="pick"]');
  await page.waitForTimeout(500);
  const boxes = await page.$$('.screen.is-active .pick');
  await boxes[0].click();
  await boxes[2].click();
  await page.waitForTimeout(700);
  const el = await page.$('.device');
  await el.screenshot({ path: 'out/a05-pick.png' });
  await browser.close();
})();
