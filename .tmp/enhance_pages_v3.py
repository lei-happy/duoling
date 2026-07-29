# -*- coding: utf-8 -*-
"""Enhance prototype HTML: spacing, scenes, structure fixes."""
from pathlib import Path
import re

BASE = Path(r"D:\zhitu\prototype\移动端")

# Per-file screen injections / replacements for thin modules
ENHANCEMENTS = {}

def fix_structure(html: str) -> str:
    # wx-body should scroll
    html = re.sub(
        r'(<div class="wx-body)(?! scroll)',
        r'\1 scroll',
        html,
    )
    # wrap loose tabbar in wx-foot
    html = re.sub(
        r'(\s*)<div class="tabbar" data-tab',
        r'\1<div class="wx-foot">\n\1  <div class="tabbar" data-tab',
        html,
    )
    html = re.sub(
        r'(</div>\s*)<!-- end tabbar -->\s*\n(\s*)</div>\s*\n(\s*)</div>\s*\n(\s*)<ol class="notes">',
        r'\1  </div>\n\2</div>\n\3</div>\n\4<ol class="notes">',
        html,
    )
    # close wx-foot after tabbar if missing
    def close_foot(m):
        block = m.group(0)
        if '</div>\n        </div>\n\n      </div>' in block:
            return block
        return block.replace(
            '</div>\n\n      </div>',
            '</div>\n        </div>\n\n      </div>',
            1,
        )
    html = re.sub(
        r'<div class="wx-foot">\s*<div class="tabbar"[^>]*>[\s\S]*?</div>\s*\n\s*</div>',
        close_foot,
        html,
    )
    # loose tabbar not in wx-foot
    html = re.sub(
        r'(\s*)<div class="tabbar">\s*\n',
        r'\1<div class="wx-foot">\n\1  <div class="tabbar">\n',
        html,
    )
    # Improve common tight padding
    html = html.replace('padding-top:32px', 'padding-top:var(--space-8)')
    html = html.replace('padding-top:36px', 'padding-top:var(--space-8)')
    html = html.replace('padding-top:28px', 'padding-top:var(--space-6)')
    html = html.replace('padding-top:80px', 'padding-top:var(--space-8)')
    html = html.replace('margin-bottom:32px', 'margin-bottom:var(--space-8)')
    html = html.replace('margin-bottom:16px', 'margin-bottom:var(--space-4)')
    html = html.replace('margin-top:36px', 'margin-top:var(--space-8)')
    html = html.replace('margin-top:20px', 'margin-top:var(--space-5)')
    html = html.replace('gap: 10px', 'gap: var(--space-3)')
    return html


ADMIN_01_EXTRA = '''
    <section class="board" id="s4">
      <div class="board-cap"><span class="n">04</span><h3>手机号密码登录</h3><span class="tip">P0</span></div>
      <div class="dev">
        <div class="wx-head onpage">
          <div class="wx-nav" data-back><span class="ttl">密码登录</span></div>
        </div>
        <div class="wx-body scroll">
          <div class="pad stack-lg" style="padding-top:var(--space-6)">
            <div class="field">
              <div class="lab">手机号</div>
              <div class="inp">138 1234 5678</div>
            </div>
            <div class="field">
              <div class="lab">密码</div>
              <div class="inp">••••••••</div>
            </div>
            <a class="btn block section-gap">登录</a>
            <div class="caption" style="text-align:center">忘记密码？联系企业管理员重置</div>
          </div>
        </div>
      </div>
      <ol class="notes"><li>密码错误：账号或密码不对，请重试。</li><li>网络失败：登录失败，请稍后重试。</li></ol>
    </section>


    <section class="board" id="s5">
      <div class="board-cap"><span class="n">05</span><h3>登录中</h3><span class="tip">P0</span></div>
      <div class="dev">
        <div class="wx-head onpage">
          <div class="wx-nav"><span class="ttl">智途管理</span></div>
        </div>
        <div class="wx-body scroll white">
          <div class="empty" style="padding-top:120px">
            <div style="width:36px;height:36px;border:3px solid var(--brand-soft);border-top-color:var(--brand);border-radius:50%;margin:0 auto 16px"></div>
            <div class="t">正在登录，请稍候…</div>
            <div class="d">验证账号与企业权限</div>
          </div>
        </div>
      </div>
      <ol class="notes"><li>Loading 文案带业务动作，不用「请求中」。</li></ol>
    </section>
'''


def enhance_admin_01(html: str) -> str:
    if 'id="s4"' in html and '手机号密码登录' in html:
        return html
    html = html.replace(
        '<nav class="pt-rail"><a href="#s1"><span class="n">1</span><span class="t">登录</span></a><a href="#s2"><span class="n">2</span><span class="t">选企业</span></a><a href="#s3"><span class="n">3</span><span class="t">无权限</span></a></nav>',
        '<nav class="pt-rail"><a href="#s1"><span class="n">1</span><span class="t">微信登录</span></a><a href="#s2"><span class="n">2</span><span class="t">密码登录</span></a><a href="#s3"><span class="n">3</span><span class="t">选企业</span></a><a href="#s4"><span class="n">4</span><span class="t">无权限</span></a><a href="#s5"><span class="n">5</span><span class="t">登录中</span></a></nav>',
    )
    html = html.replace('<div><dt>覆盖屏数</dt><dd>3 屏</dd></div>', '<div><dt>覆盖屏数</dt><dd>5 屏</dd></div>')
    # re-id s3->s4 for no permission, insert password at s2
    html = html.replace('id="s3"', 'id="s4"', 1)
    html = html.replace('id="s2"', 'id="s3"', 1)
    pwd = '''
    <section class="board" id="s2">
      <div class="board-cap"><span class="n">02</span><h3>手机号密码登录</h3><span class="tip">P0</span></div>
      <div class="dev">
        <div class="wx-head onpage">
          <div class="wx-nav" data-back><span class="ttl">密码登录</span></div>
        </div>
        <div class="wx-body scroll">
          <div class="pad stack-lg" style="padding-top:var(--space-6)">
            <div class="field"><div class="lab">手机号</div><div class="inp">138 1234 5678</div></div>
            <div class="field"><div class="lab">密码</div><div class="inp">••••••••</div></div>
            <a class="btn block section-gap">登录</a>
            <div class="caption" style="text-align:center">忘记密码？联系企业管理员重置</div>
          </div>
        </div>
      </div>
      <ol class="notes"><li>失败：账号或密码不对 / 登录失败，请稍后重试。</li></ol>
    </section>
'''
    html = html.replace('    <section class="board" id="s2">\n      <div class="board-cap"><span class="n">02</span><h3>选择企业与角色</h3>', pwd + '\n    <section class="board" id="s3">\n      <div class="board-cap"><span class="n">03</span><h3>选择企业与角色</h3>')
    html = html.replace('<span class="n">03</span><h3>无权限空态</h3>', '<span class="n">04</span><h3>无权限空态</h3>')
    html = html.replace('id="s5"', 'id="s5"', 1)
    if 'id="s5"' not in html:
        html = html.replace(
            '  </div>\n\n\n  <div class="pt-rules">',
            '''
    <section class="board" id="s5">
      <div class="board-cap"><span class="n">05</span><h3>登录中</h3><span class="tip">P0</span></div>
      <div class="dev">
        <div class="wx-head onpage"><div class="wx-nav"><span class="ttl">智途管理</span></div></div>
        <div class="wx-body scroll white">
          <div class="empty" style="padding-top:120px">
            <div style="width:36px;height:36px;border:3px solid var(--brand-soft);border-top-color:var(--brand);border-radius:50%;margin:0 auto var(--space-4)"></div>
            <div class="t">正在登录，请稍候…</div>
            <div class="d">验证账号与企业权限</div>
          </div>
        </div>
      </div>
      <ol class="notes"><li>Loading 带业务动作。</li></ol>
    </section>

  </div>


  <div class="pt-rules">''',
        )
    return html


def enhance_cards_spacing(html: str) -> str:
    # Add stack to pad blocks with multiple cards
    html = re.sub(
        r'(<div class="pad"[^>]*>)\s*(<div class="t3[^"]*"[^>]*>[^<]+</div>\s*<div class="card")',
        r'\1<div class="stack-lg">\2',
        html,
    )
    return html


HANDLERS = {
    '01-登录与企业切换.html': enhance_admin_01,
}


def process_file(path: Path):
    html = path.read_text(encoding='utf-8')
    rel = path.name
    parent = path.parent.name
    key = rel
    if key in HANDLERS:
        html = HANDLERS[key](html)
    html = fix_structure(html)
    html = enhance_cards_spacing(html)
    path.write_text(html, encoding='utf-8')
    print('enhanced', parent, rel)


def main():
    for html in sorted(BASE.rglob('*.html')):
        process_file(html)
    print('done', len(list(BASE.rglob('*.html'))), 'files')


if __name__ == '__main__':
    main()
