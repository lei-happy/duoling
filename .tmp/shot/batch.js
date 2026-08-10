const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 批量：对目录下所有 HTML 逐个打开、遍历全部屏幕，收集 JS 错误与布局溢出
(async () => {
  const dir = process.argv[2];
  const shotAll = process.argv[3] === 'shot';
  const outDir = path.join(__dirname, 'out', path.basename(dir));
  fs.mkdirSync(outDir, { recursive: true });
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1.6 });
  let bad = 0;

  for (const f of files) {
    const errors = [];
    page.removeAllListeners('console');
    page.removeAllListeners('pageerror');
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
    await page.goto('file:///' + path.join(dir, f).replace(/\\/g, '/'));
    await page.waitForTimeout(500);

    const ids = await page.evaluate(() => Object.keys(window.MP.screens));
    const issues = [];
    for (const id of ids) {
      await page.evaluate((id) => {
        const s = window.MP.screens[id];
        window.MP.closeLayer(true);
        if (s.dataset.tabroot != null) window.MP.tab(id);
        else if (s.dataset.parent) { window.MP.root(s.dataset.parent); window.MP.push(id); }
        else window.MP.root(id);
      }, id);
      await page.waitForTimeout(420);
      // 横向溢出检测
      const over = await page.evaluate(() => {
        const sc = document.querySelector('.screen.is-active .scroll');
        if (!sc) return null;
        return sc.scrollWidth - sc.clientWidth;
      });
      if (over && over > 2) issues.push(id + ' 横向溢出 ' + over + 'px');
      if (shotAll) {
        const el = await page.$('.device');
        if (el) await el.screenshot({ path: path.join(outDir, f.replace('.html', '') + '__' + id + '.png') });
      }
    }
    // 未渲染的图标
    const blank = await page.evaluate(() => {
      let n = 0;
      document.querySelectorAll('[data-icon]').forEach(e => { if (!e.querySelector('svg')) n++; });
      return n;
    });
    const line = [f, errors.length ? 'JS错误:' + errors.join(' | ') : '', blank ? '空图标 ' + blank : '', issues.join('; ')]
      .filter(Boolean).join('  ');
    if (errors.length || blank || issues.length) { bad++; console.log('!! ' + line); }
    else console.log('ok ' + f + '  (' + ids.length + ' 屏)');
  }
  console.log(bad ? '\n有问题文件数: ' + bad : '\n全部通过');
  await browser.close();
})();
