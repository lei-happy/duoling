/**
 * 模拟微信开发者工具「构建 npm」：
 * 将带 miniprogram 字段的包拷到 miniprogram_npm/
 * （也可在开发者工具中：工具 → 构建 npm）
 */
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const nm = path.join(root, 'node_modules');
const out = path.join(root, 'miniprogram_npm');

function rimraf(dir) {
  if (!fs.existsSync(dir)) return;
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const name of fs.readdirSync(src)) {
    if (name === 'node_modules' || name === '.git') continue;
    const from = path.join(src, name);
    const to = path.join(dest, name);
    const stat = fs.statSync(from);
    if (stat.isDirectory()) copyDir(from, to);
    else fs.copyFileSync(from, to);
  }
}

function buildPackage(pkgName) {
  const pkgDir = path.join(nm, pkgName);
  const pkgJsonPath = path.join(pkgDir, 'package.json');
  if (!fs.existsSync(pkgJsonPath)) {
    console.warn(`[skip] 未找到依赖：${pkgName}`);
    return;
  }
  const pkg = JSON.parse(fs.readFileSync(pkgJsonPath, 'utf8'));
  const dest = path.join(out, pkgName);
  rimraf(dest);
  const mini = pkg.miniprogram;
  if (mini) {
    const src = path.join(pkgDir, mini);
    if (!fs.existsSync(src)) {
      throw new Error(`${pkgName} 缺少 miniprogram 目录：${mini}`);
    }
    copyDir(src, dest);
  } else {
    copyDir(pkgDir, dest);
  }
  console.log(`[ok] ${pkgName}`);
}

rimraf(out);
fs.mkdirSync(out, { recursive: true });

// tdesign 依赖 tslib（ESM import），需一并构建
['tdesign-miniprogram', 'tslib'].forEach(buildPackage);
console.log('npm 构建完成 → miniprogram_npm/');
