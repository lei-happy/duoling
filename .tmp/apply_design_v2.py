# -*- coding: utf-8 -*-
"""Apply apple-design + frontend-design enhancements to mp.css and mp.js."""
from pathlib import Path

CSS_PATCH = r"""
/* ========== v2 · apple-design + frontend-design ========== */
:root {
  --accent-warm: #e8871e;
  --accent-warm-soft: #fef3e2;
  --glass: rgba(255, 255, 255, 0.78);
  --glass-border: rgba(255, 255, 255, 0.55);
  --glass-blur: 20px;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --dur-fast: 120ms;
  --dur-normal: 280ms;
  --shadow-soft: 0 1px 2px rgba(15, 23, 42, 0.03), 0 2px 8px rgba(15, 23, 42, 0.04);
}

body[data-app="driver"] { --accent: var(--accent-warm); }
body[data-app="admin"] { --accent: var(--brand); }

/* Typography optical sizing */
.money, .kpis .kpi .v, .kpi-grid .kpi .v {
  letter-spacing: -0.02em;
}
.chip, .tag, .tabbar .item, .tabs .tab {
  letter-spacing: 0.02em;
}
.card .hd, .task .nm, .dev .banner .nm {
  letter-spacing: -0.015em;
}

/* Materials: floating chrome */
.tabbar {
  background: var(--glass) !important;
  backdrop-filter: blur(var(--glass-blur)) saturate(180%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(180%);
  border-top: 1px solid var(--glass-border) !important;
  box-shadow: 0 -1px 0 rgba(15, 23, 42, 0.04);
}
.action-bar {
  background: var(--glass) !important;
  backdrop-filter: blur(var(--glass-blur)) saturate(180%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(180%);
  border-top: 1px solid rgba(15, 23, 42, 0.06) !important;
}

/* Card refinement: hairline + soft shadow */
.card, .task, .cells, .kpi-grid .kpi {
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(15, 23, 42, 0.04);
}

/* Press feedback — response on down (apple-design §1) */
.btn, .tabbar .item, .cell, .quick .q, .pt-rail a, .chips .chip {
  transition: transform var(--dur-fast) var(--ease-out),
              background var(--dur-fast) ease,
              border-color var(--dur-fast) ease;
  -webkit-tap-highlight-color: transparent;
}
.btn:active, .tabbar .item:active, .cell:active, .quick .q:active {
  transform: scale(0.97);
}
.pt-rail a:active { transform: scale(0.98); }

/* Driver signature: alert-card */
.alert-card {
  margin: 10px 12px;
  padding: 14px 14px 14px 16px;
  background: var(--card);
  border-radius: var(--r);
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(15, 23, 42, 0.04);
  border-left: 4px solid var(--accent-warm);
}
.alert-card .ttl {
  font-size: 15px; font-weight: 600; color: var(--t1);
  letter-spacing: -0.01em;
}
.alert-card .sub {
  font-size: 12px; color: var(--t2); margin-top: 4px; line-height: 1.45;
}
.alert-card .act {
  margin-top: 10px; font-size: 13px; font-weight: 600; color: var(--brand);
}

/* Admin glass KPI in hero */
.kpis .kpi {
  border: 1px solid rgba(255, 255, 255, 0.22);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

/* Hero depth */
.dev .hero {
  background: linear-gradient(168deg, var(--brand-deep) 0%, var(--brand) 42%, var(--brand-mid) 100%);
}
.dev .hero::after {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(120% 80% at 100% 0%, rgba(255,255,255,0.08) 0%, transparent 55%);
  pointer-events: none;
}
.dev .hero { position: relative; overflow: hidden; }

/* Scroll edge fade hint under floating chrome */
.wx-body.scroll {
  mask-image: linear-gradient(to bottom, #000 calc(100% - 28px), transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, #000 calc(100% - 28px), transparent 100%);
}

/* Sheet spatial consistency */
.sheet {
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -8px 32px rgba(15, 23, 42, 0.12);
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  .btn:active, .tabbar .item:active, .cell:active, .quick .q:active {
    transform: none;
  }
  .wx-body.scroll {
    mask-image: none;
    -webkit-mask-image: none;
  }
}
@media (prefers-reduced-transparency: reduce) {
  .tabbar, .action-bar {
    background: #fff !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
  }
}
"""

JS_PATCH = r"""
  /* v2 press feedback */
  function bindPress() {
    var sel = '.btn, .tabbar .item, .cell, .quick .q';
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll(sel).forEach(function (el) {
      el.addEventListener('pointerdown', function () { el.classList.add('is-pressed'); });
      function up() { el.classList.remove('is-pressed'); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up); }
      el.addEventListener('pointerdown', function () { el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up); });
    });
  }

  function smoothScroll() {
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.querySelectorAll('.pt-rail a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function () {
        if (reduced) return;
      });
    });
  }
"""

JS_BOOT_PATCH = """    bindPress();
    smoothScroll();"""


def main():
    roots = [
        Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序\assets"),
        Path(r"D:\zhitu\prototype\移动端\后台人员微信小程序\assets"),
    ]
    for root in roots:
        css_path = root / "mp.css"
        js_path = root / "mp.js"
        css = css_path.read_text(encoding="utf-8")
        if "v2 · apple-design" not in css:
            css = css.rstrip() + "\n" + CSS_PATCH
            css_path.write_text(css, encoding="utf-8")
            print("CSS patched", root.parent.name)

        js = js_path.read_text(encoding="utf-8")
        if "bindPress" not in js:
            js = js.replace("  function boot() {", JS_PATCH + "\n  function boot() {")
            js = js.replace("    tools();", "    tools();\n" + JS_BOOT_PATCH)
            js_path.write_text(js, encoding="utf-8")
            print("JS patched", root.parent.name)

    print("Done")


if __name__ == "__main__":
    main()
