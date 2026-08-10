const fs = require('fs');
const path = require('path');

// 把误放进 .scroll 的底部操作条提升为 .screen 的直接子元素
const dir = process.argv[2];
const re = /\n *<div class="actionbar">\n([\s\S]*?)\n( *)<\/div>\n( *)<\/div>\n( *)<\/section>/g;

for (const f of fs.readdirSync(dir).filter(n => n.endsWith('.html'))) {
  const p = path.join(dir, f);
  const raw = fs.readFileSync(p, 'utf8');
  const crlf = raw.includes('\r\n');
  const src = crlf ? raw.replace(/\r\n/g, '\n') : raw;
  let n = 0;
  let out = src.replace(re, (m, body, ind, scrollInd, secInd) => {
    n++;
    const lines = body.split('\n').map(l => (l.startsWith('  ') ? l.slice(2) : l));
    return '\n' + scrollInd + '</div>\n' + scrollInd + '<div class="actionbar">\n'
      + lines.join('\n') + '\n' + scrollInd + '</div>\n' + secInd + '</section>';
  });
  if (n) {
    if (crlf) out = out.replace(/\n/g, '\r\n');
    fs.writeFileSync(p, out);
    console.log(f + ' 修正 ' + n + ' 处');
  }
}
