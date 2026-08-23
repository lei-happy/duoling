/**
 * tabBar 只认 PNG。用同一套线性 SVG 渲成 81×81，灰/蓝各一套。
 * 运行：node scripts/render-tab-icons.js
 */
const fs = require('fs');
const path = require('path');

async function main() {
  let Resvg;
  try {
    ({ Resvg } = require('@resvg/resvg-js'));
  } catch (err) {
    console.error('缺少 @resvg/resvg-js，请先在本目录执行：npm i -D @resvg/resvg-js');
    throw err;
  }

  const root = path.resolve(__dirname, '..');
  const svgDir = path.join(root, 'assets/icons/svg');
  const outDir = path.join(root, 'assets/icons');
  const size = 81;
  const jobs = [
    ['home', 'home.png', '#94a3b8'],
    ['home', 'home-active.png', '#1d4ed8'],
    ['task', 'task.png', '#94a3b8'],
    ['task', 'task-active.png', '#1d4ed8'],
    ['wallet', 'finance.png', '#94a3b8'],
    ['wallet', 'finance-active.png', '#1d4ed8'],
    ['user', 'profile.png', '#94a3b8'],
    ['user', 'profile-active.png', '#1d4ed8']
  ];

  for (const [name, file, color] of jobs) {
    const raw = fs.readFileSync(path.join(svgDir, `${name}.svg`), 'utf8')
      .replace(/stroke="#000"/g, `stroke="${color}"`);
    // 四周留白，避免 tabBar 里描边贴边、显得比文字大
    const src = raw.replace(
      'viewBox="0 0 24 24"',
      'viewBox="-2 -2 28 28"'
    );
    const png = new Resvg(src, {
      fitTo: { mode: 'width', value: size },
      background: 'rgba(0,0,0,0)'
    }).render().asPng();
    fs.writeFileSync(path.join(outDir, file), png);
    console.log(`${file}  ${(png.length / 1024).toFixed(1)}KB`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
