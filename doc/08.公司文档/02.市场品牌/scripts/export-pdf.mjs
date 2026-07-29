/**
 * 将「朵灵科技品牌定义方案.html」渲染为内容完整、版式稳定的 PDF。
 *
 * 用法（在 scripts 目录）：
 *   npm install
 *   npx playwright install chromium
 *   npm run export-pdf
 */
import { chromium } from 'playwright';
import { createRequire } from 'module';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BRAND_DIR = path.resolve(__dirname, '..');
const HTML_PATH = path.join(BRAND_DIR, '朵灵科技品牌定义方案.html');
const PDF_PATH = path.join(BRAND_DIR, '朵灵科技品牌定义方案.pdf');

const MUST_CONTAIN = [
  '朵灵科技品牌定义方案',
  '北京朵灵科技有限公司',
  '名称职责分层',
  '单一母品牌',
  '朵灵运输',
  '朵灵运力',
  '朵灵司机',
  '朵灵AI',
  '推广路径',
  '行动摘要',
  '让每一公里都不白跑',
];

function fail(msg) {
  console.error(`\n[export-pdf] FAIL: ${msg}`);
  process.exit(1);
}

async function main() {
  await fs.access(HTML_PATH).catch(() => fail(`找不到 HTML：${HTML_PATH}`));

  const fileUrl = `${pathToFileURL(HTML_PATH).href}?pdf=1`;
  console.log('[export-pdf] HTML:', HTML_PATH);
  console.log('[export-pdf] URL :', fileUrl);

  const browser = await chromium.launch({
    headless: true,
    args: ['--font-render-hinting=medium', '--disable-dev-shm-usage'],
  });

  try {
    const page = await browser.newPage({
      viewport: { width: 1280, height: 1800 },
      deviceScaleFactor: 2,
    });

    // 放宽本地 file:// + 字体加载；超时给足
    page.setDefaultTimeout(90_000);
    await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 90_000 });

    // 强制导出模式 + 全部内容可见（防止 opacity:0 漏渲染）
    await page.evaluate(() => {
      document.documentElement.classList.add('pdf-export');
      document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-in'));
    });

    const ready = await page.evaluate(async () => {
      if (window.__brandReportReady) return window.__brandReportReady;
      if (document.fonts?.ready) await document.fonts.ready;
      return {
        title: document.title,
        textLength: (document.body?.innerText || '').replace(/\s+/g, '').length,
        revealCount: document.querySelectorAll('.reveal').length,
      };
    });

    console.log('[export-pdf] DOM ready:', ready);
    if (!ready || ready.textLength < 2000) {
      fail(`DOM 文本过短（${ready?.textLength ?? 0}），疑似内容未渲染`);
    }

    // 再等一帧，确保字体与布局稳定
    await page.waitForTimeout(600);

    // 用 print 媒体查询生成分页，保留背景色
    await page.emulateMedia({ media: 'print' });
    await page.evaluate(() => {
      document.documentElement.classList.add('pdf-export');
      document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-in'));
    });

    await page.pdf({
      path: PDF_PATH,
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: '12mm', right: '10mm', bottom: '14mm', left: '10mm' },
      displayHeaderFooter: true,
      headerTemplate: '<div></div>',
      footerTemplate: `
        <div style="width:100%;font-size:9px;color:#5A6573;padding:0 12mm;display:flex;justify-content:space-between;font-family:sans-serif;">
          <span>朵灵科技品牌定义方案 V1.0</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
      `,
    });
  } finally {
    await browser.close();
  }

  const stat = await fs.stat(PDF_PATH);
  console.log(`[export-pdf] wrote ${PDF_PATH} (${stat.size} bytes)`);
  if (stat.size < 80_000) fail(`PDF 体积过小（${stat.size}），疑似空白页`);

  const buf = await fs.readFile(PDF_PATH);
  const parsed = await pdfParse(buf);
  const text = (parsed.text || '').replace(/\s+/g, ' ').trim();
  const compact = text.replace(/\s+/g, '');

  console.log(`[export-pdf] pages=${parsed.numpages}, chars=${compact.length}`);

  if (parsed.numpages < 3) fail(`页数过少（${parsed.numpages}），版式可能异常`);
  if (compact.length < 1500) fail(`提取文本过短（${compact.length}），内容可能丢失`);

  const missing = MUST_CONTAIN.filter((s) => !compact.includes(s.replace(/\s+/g, '')));
  if (missing.length) {
    fail(`PDF 文本缺少关键段落：${missing.join('、')}`);
  }

  console.log('[export-pdf] OK — 内容校验通过');
  console.log(`  pages : ${parsed.numpages}`);
  console.log(`  size  : ${stat.size} bytes`);
  console.log(`  sample: ${text.slice(0, 120)}…`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
