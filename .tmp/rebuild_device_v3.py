# -*- coding: utf-8 -*-
"""Rebuild mp.css/mp.js with iPhone 15 shell + WeChat official chrome + spacing polish."""
from pathlib import Path
import re

ROOTS = [
    Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序\assets"),
    Path(r"D:\zhitu\prototype\移动端\后台人员微信小程序\assets"),
]

# Replace device shell block in existing CSS
DEVICE_CSS = r'''
/* ========== iPhone 15 Pro 外壳 + 微信小程序顶栏（v3 高保真） ========== */
:root {
  --bezel: 14px;
  --frame-w: calc(var(--dev-w) + var(--bezel) * 2);
  --frame-h: calc(var(--dev-h) + var(--bezel) * 2);
  --safe-top: 47px;
  --nav-bar-h: 44px;
  --wx-header-h: 88px;
  --capsule-w: 87px;
  --capsule-h: 32px;
  --capsule-r: 16px;
  --capsule-right: 7px;
  --home-ind-area: 34px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --leading-tight: 1.25;
  --leading-body: 1.55;
  --leading-relaxed: 1.65;
}

.board { flex: 0 0 auto; width: var(--frame-w); scroll-snap-align: start; }
.board-cap {
  display: flex; align-items: center; gap: var(--space-2);
  margin-bottom: var(--space-3); min-height: 28px; padding: 0 2px;
}
.board-cap .n {
  width: 24px; height: 24px; border-radius: 7px; background: var(--brand); color: #fff;
  font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center;
}
.board-cap h3 { margin: 0; font-size: 13.5px; font-weight: 600; flex: 1; line-height: var(--leading-tight); }
.board-cap .tip {
  font-size: 11px; color: var(--t3); padding: 2px 8px; border-radius: var(--pill);
  background: #fff; border: 1px solid var(--line);
}

/* 外框：iPhone 15 Pro 钛金属边框 */
.dev {
  width: var(--frame-w); height: var(--frame-h);
  padding: var(--bezel);
  background: linear-gradient(165deg, #48484a 0%, #2c2c2e 22%, #1c1c1e 55%, #0d0d0f 100%);
  border-radius: 54px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.06),
    0 0 0 2.5px #141416,
    0 2px 4px rgba(0,0,0,0.12),
    0 32px 64px -12px rgba(0,0,0,0.45),
    inset 0 1px 0 rgba(255,255,255,0.14),
    inset 0 -1px 0 rgba(0,0,0,0.35);
  display: flex; flex-direction: column; position: relative; overflow: visible;
}
.dev::before {
  content: ""; position: absolute; left: -3px; top: 118px;
  width: 3px; height: 26px; border-radius: 2px 0 0 2px;
  background: linear-gradient(180deg, #3a3a3c, #252527);
  box-shadow: 0 42px 0 #3a3a3c, 0 78px 0 #3a3a3c;
}
.dev::after {
  content: ""; position: absolute; right: -3px; top: 168px;
  width: 3px; height: 64px; border-radius: 0 2px 2px 0;
  background: linear-gradient(180deg, #3a3a3c, #252527);
}
.dev.auto { height: auto; min-height: var(--frame-h); }

/* 内屏 */
.iphone-screen {
  width: 100%; flex: 1; min-height: var(--dev-h);
  border-radius: 46px; overflow: hidden; background: #000;
  display: flex; flex-direction: column; position: relative;
  box-shadow: inset 0 0 0 1.5px rgba(0,0,0,0.65);
}

/* Dynamic Island */
.iphone-island {
  position: absolute; top: 11px; left: 50%; transform: translateX(-50%);
  width: 122px; height: 34px; background: #000; border-radius: 18px;
  z-index: 300; pointer-events: none;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
}
.iphone-island::after {
  content: ""; position: absolute; right: 24px; top: 50%; transform: translateY(-50%);
  width: 11px; height: 11px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #1a1a2e, #0a0a0f);
}

/* Home Indicator */
.iphone-home-bar {
  flex-shrink: 0; height: var(--home-ind-area);
  display: flex; align-items: center; justify-content: center;
  background: inherit; position: relative; z-index: 20;
}
.iphone-home-bar i {
  display: block; width: 134px; height: 5px; border-radius: 100px;
  background: rgba(0,0,0,0.28);
}
.wx-foot .iphone-home-bar i,
.dev .tabbar ~ .iphone-home-bar i { background: rgba(0,0,0,0.22); }

/* ========== 微信自定义导航栏（对齐 getMenuButtonBoundingClientRect 375 基准） ========== */
.dev .wx-head {
  flex-shrink: 0; background: var(--brand); color: #fff;
  overflow: hidden; position: relative; z-index: 10;
}
.dev .wx-head.onpage { background: #fff; color: var(--t1); border-bottom: 0.5px solid rgba(0,0,0,0.08); }

.wx-chrome { position: relative; }

.wx-statusbar {
  height: var(--safe-top); display: flex; align-items: flex-end; justify-content: space-between;
  padding: 0 28px 6px 32px; position: relative; z-index: 50;
}
.wx-time {
  font-size: 15px; font-weight: 600; letter-spacing: -0.02em;
  font-family: -apple-system, "SF Pro Text", "PingFang SC", sans-serif;
  line-height: 1;
}
.wx-status-icons {
  display: flex; align-items: center; gap: 5px; height: 14px;
}
.wx-status-icons svg { display: block; }

.wx-navbar {
  height: var(--nav-bar-h); display: flex; align-items: center;
  padding: 0 var(--capsule-right); position: relative;
}
.wx-nav-left {
  width: 88px; display: flex; align-items: center; padding-left: 4px; flex-shrink: 0;
}
.wx-nav-left .back {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  font-size: 28px; line-height: 1; font-weight: 300; margin-left: -4px;
  border-radius: 8px;
}
.wx-nav-title {
  flex: 1; text-align: center; font-size: 17px; font-weight: 600;
  letter-spacing: -0.015em; line-height: var(--leading-tight);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  padding: 0 8px;
}
.wx-nav-spacer { width: 88px; flex-shrink: 0; }

/* 微信官方胶囊 87×32 */
.wx-capsule {
  position: absolute; right: var(--capsule-right); top: 50%; transform: translateY(-50%);
  width: var(--capsule-w); height: var(--capsule-h); border-radius: var(--capsule-r);
  border: 0.5px solid rgba(255,255,255,0.25);
  background: rgba(0,0,0,0.15);
  display: flex; align-items: center; overflow: hidden; z-index: 60;
  box-shadow: inset 0 0 0 0.5px rgba(255,255,255,0.08);
}
.wx-head.onpage .wx-capsule {
  border-color: rgba(0,0,0,0.12); background: rgba(255,255,255,0.55);
  box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.04);
}
.wx-capsule-more {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 3px; height: 100%;
}
.wx-capsule-more span {
  width: 4px; height: 4px; border-radius: 50%; background: currentColor; opacity: 0.92;
}
.wx-head.onpage .wx-capsule-more span { background: #1a1a1a; }
.wx-capsule-divider {
  width: 0.5px; height: 18px; background: rgba(255,255,255,0.25); flex-shrink: 0;
}
.wx-head.onpage .wx-capsule-divider { background: rgba(0,0,0,0.12); }
.wx-capsule-close {
  flex: 1; display: flex; align-items: center; justify-content: center; height: 100%;
}
.wx-capsule-close .ring {
  width: 17px; height: 17px; border-radius: 50%;
  border: 1.5px solid currentColor; opacity: 0.92;
  position: relative;
}
.wx-capsule-close .ring::after {
  content: ""; position: absolute; inset: 3px; border-radius: 50%;
  background: currentColor; opacity: 0.85;
}
.wx-head.onpage .wx-capsule-close .ring { border-color: #1a1a1a; }
.wx-head.onpage .wx-capsule-close .ring::after { background: #1a1a1a; }

/* legacy selectors kept for HTML not yet migrated */
.wx-status { display: none; }
.wx-nav { display: none; }

.wx-body {
  flex: 1; background: var(--page); overflow: hidden; min-height: 0;
  display: flex; flex-direction: column; position: relative;
  font-size: 14px; line-height: var(--leading-body);
}
.wx-body.scroll { overflow-y: auto; -webkit-overflow-scrolling: touch; display: block; }
.wx-body.white { background: #fff; }
.dev.auto .wx-body { overflow: visible; }

.wx-foot {
  flex-shrink: 0; background: #fff; overflow: hidden;
  box-shadow: 0 -0.5px 0 rgba(0,0,0,0.06);
}

/* ========== 间距与排版增强（v3） ========== */
.pad { padding: var(--space-4); }
.pad-b { padding: 0 var(--space-4) var(--space-4); }
.pad-t { padding-top: var(--space-4); }
.pad-x { padding-left: var(--space-4); padding-right: var(--space-4); }
.stack > * + * { margin-top: var(--space-3); }
.stack-sm > * + * { margin-top: var(--space-2); }
.stack-lg > * + * { margin-top: var(--space-4); }
.lead { font-size: 15px; line-height: var(--leading-relaxed); color: var(--t1); }
.sub { font-size: 13px; line-height: var(--leading-relaxed); color: var(--t2); }
.caption { font-size: 12px; line-height: 1.45; color: var(--t3); letter-spacing: 0.01em; }
.section-gap { margin-top: var(--space-5); }
.field { margin-bottom: var(--space-4); }
.field .lab {
  display: block; margin-bottom: var(--space-2);
  font-size: 13px; color: var(--t2); line-height: 1.4;
}
.field .inp, .field .ta {
  min-height: 44px; padding: 11px var(--space-3);
  background: #f8fafc; border-radius: var(--r-s);
  border: 1px solid var(--line); font-size: 14px; line-height: 1.45; color: var(--t1);
}
.field .ta { min-height: 88px; line-height: var(--leading-relaxed); }
.field .inp.ph { color: var(--t3); }

ol.notes {
  margin: var(--space-3) 0 0; padding-left: 18px;
  font-size: 12.5px; line-height: var(--leading-relaxed); color: var(--t2);
}
ol.notes li + li { margin-top: 6px; }
'''

JS_V3 = r'''/* 智途 · 小程序原型 · iPhone 壳 / 微信顶栏 / 图标 / TabBar */
(function () {
  var ICONS = {
    truck: '<path d="M3 7h11v8H3zm11 2h4l3 3v3h-7z"/><circle cx="7.2" cy="17.2" r="1.7"/><circle cx="16.5" cy="17.2" r="1.7"/>',
    building: '<path d="M4 20V6l6-3 6 3v14H4zm4-2h2v-3H8v3zm6 0h2v-3h-2v3zM8 11h2V8H8v3zm6 0h2V8h-2v3z"/>',
    clock: '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 7.5v5l3 1.8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    home: '<path d="M4 11.5 12 4l8 7.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-8.5z"/>',
    list: '<path d="M8 7h11M8 12h11M8 17h11M4.5 7h.01M4.5 12h.01M4.5 17h.01" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    wallet: '<path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H18v2.5H6.2A1.2 1.2 0 0 0 5 8.7V17.5h13.5V10H11v4.5h9.5V19A1.5 1.5 0 0 1 19 20.5H5A2 2 0 0 1 3 18.5v-11z"/><circle cx="16.5" cy="12.25" r="1"/>',
    user: '<circle cx="12" cy="8" r="3.2"/><path d="M5 19c1.5-3.2 4-4.8 7-4.8s5.5 1.6 7 4.8"/>',
    users: '<circle cx="9" cy="8" r="2.6"/><circle cx="16" cy="9" r="2.2"/><path d="M3.5 18c1.2-2.6 3.2-3.8 5.5-3.8s4.3 1.2 5.5 3.8M14 14.2c1.5-.3 3 .4 4 2.3"/>',
    wechat: '<path d="M9.2 7.2c-3.3 0-6 2.2-6 5 0 1.6.8 3 2.1 4l-.4 1.6 1.9-1c.7.2 1.5.3 2.3.3.3 0 .6 0 .9-.1A4.7 4.7 0 0 1 9 14.6c0-3.2 3.1-5.8 7-6.2-.6-1.8-2.9-3.2-6.8-3.2zm-2.1 3.1a.85.85 0 1 1 0-1.7.85.85 0 0 1 0 1.7zm4.2 0a.85.85 0 1 1 0-1.7.85.85 0 0 1 0 1.7zM16 9.8c-3.4 0-6.1 2.2-6.1 4.9s2.7 4.9 6.1 4.9c.7 0 1.3-.1 1.9-.3l1.6.8-.4-1.4c1.1-.9 1.8-2.1 1.8-3.9 0-2.8-2.7-5-4.9-5zm-2 .9a.7.7 0 1 1 0-1.4.7.7 0 0 1 0 1.4zm3.9 0a.7.7 0 1 1 0-1.4.7.7 0 0 1 0 1.4z"/>',
    swap: '<path d="M7 7h9l-2-2m2 2-2 2M17 17H8l2 2m-2-2 2-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
    search: '<circle cx="10.5" cy="10.5" r="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M15 15l4 4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    phone: '<path d="M7.5 3.5h3l1.2 3.2-1.8 1.2a11 11 0 0 0 5.2 5.2l1.2-1.8 3.2 1.2v3A1.5 1.5 0 0 1 18 17.5 13.5 13.5 0 0 1 4.5 4a1.5 1.5 0 0 1 1.5-1.5h1.5z"/>',
    nav: '<path d="M12 3l8 17-8-4-8 4 8-17z"/>',
    camera: '<path d="M4 8h3l1.5-2h7L17 8h3v11H4V8z"/><circle cx="12" cy="13.2" r="3.1" fill="none" stroke="#fff" stroke-width="1.5"/>',
    cam: '<path d="M4 8h3l1.5-2h7L17 8h3v11H4V8z"/><circle cx="12" cy="13.2" r="3.1" fill="none" stroke="#fff" stroke-width="1.5"/>',
    bell: '<path d="M12 3a5 5 0 0 1 5 5v3.5l1.5 2.5H5.5L7 11.5V8a5 5 0 0 1 5-5z"/><path d="M10 19a2 2 0 0 0 4 0"/>',
    chart: '<path d="M4 19h16M7 16V10m5 6V7m5 9v-4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    check: '<path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    warn: '<path d="M12 4l9 16H3L12 4z"/><path d="M12 10v4m0 3h.01" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>',
    warning: '<path d="M12 4l9 16H3L12 4z"/><path d="M12 10v4m0 3h.01" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>',
    info: '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 10.5V17m0-7.5h.01" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    plus: '<path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    filter: '<path d="M4 6h16l-6 7v5l-4 2v-7L4 6z"/>',
    msg: '<path d="M4 6h16v10H8l-4 3V6z"/>',
    chat: '<path d="M4 6h16v10H8l-4 3V6z"/>',
    car: '<path d="M4 14l2-5h12l2 5v4h-2.2a1.8 1.8 0 0 1-3.6 0H9.8a1.8 1.8 0 0 1-3.6 0H4v-4z"/>',
    gas: '<path d="M6 4h8v14H6zM14 8h2.5a2 2 0 0 1 2 2v7a1.5 1.5 0 0 0 1.5 1.5"/><path d="M8 8h4" fill="none" stroke="#fff" stroke-width="1.4"/>',
    fuel: '<path d="M6 4h8v14H6zM14 8h2.5a2 2 0 0 1 2 2v7a1.5 1.5 0 0 0 1.5 1.5"/><path d="M8 8h4" fill="none" stroke="#fff" stroke-width="1.4"/>',
    calendar: '<rect x="4" y="6" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 4v4M16 4v4M4 11h16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    shield: '<path d="M12 3l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-3z"/>',
    setting: '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v2.2m0 14.6v2.2M2.5 12h2.2m14.6 0h2.2M5.1 5.1l1.6 1.6m10.6 10.6 1.6 1.6m0-14.8-1.6 1.6M6.7 17.3l-1.6 1.6" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>',
    money: '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v10M9.2 9.2c.8-1 2-1.5 2.8-1.5 1.6 0 2.8.9 2.8 2.2S13.6 12 12 12s-2.8.8-2.8 2.1 1.3 2.2 2.9 2.2c.9 0 2-.5 2.7-1.4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    card: '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18" fill="none" stroke="#fff" stroke-width="1.5"/>',
    help: '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.8 2.1c-.8.5-1.3 1-1.3 2v.4M12 17h.01" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    file: '<path d="M7 3h7l4 4v14H7V3z"/><path d="M14 3v4h4" fill="none" stroke="#fff" stroke-width="1.3"/>',
    right: '<path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    close: '<path d="M7 7l10 10M17 7 7 17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    trash: '<path d="M5 7h14M9 7V5h6v2m-7 0v12h8V7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
    location: '<path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11z"/><circle cx="12" cy="10" r="2.2" fill="#fff"/>',
    image: '<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="1.5" fill="#fff"/><path d="M4 16l5-4 4 3 3-2 4 3" fill="none" stroke="#fff" stroke-width="1.4"/>',
    upload: '<path d="M12 16V7m0 0l-3.5 3.5M12 7l3.5 3.5M5 18h14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
    download: '<path d="M12 7v9m0 0l-3.5-3.5M12 16l3.5-3.5M5 19h14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
    eye: '<path d="M2.5 12S6 6.5 12 6.5 21.5 12 21.5 12 18 17.5 12 17.5 2.5 12 2.5 12z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="2.4"/>',
    refresh: '<path d="M20 12a8 8 0 1 1-2.3-5.5M20 5v4h-4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
    lock: '<rect x="6" y="10" width="12" height="10" rx="2"/><path d="M9 10V7.5a3 3 0 0 1 6 0V10" fill="none" stroke="currentColor" stroke-width="1.6"/>',
    package: '<path d="M3 8l9-4 9 4-9 4-9-4zM3 8v8l9 4 9-4V8"/><path d="M12 12v8M7.5 9.8 16 14" fill="none" stroke="#fff" stroke-width="1.2"/>',
    signature: '<path d="M4 17c2-4 4-6 6-6s2 3 4 3 3-2 6-5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><path d="M4 19h16" fill="none" stroke="currentColor" stroke-width="1.4"/>',
    approve: '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 12.2l2.6 2.6L16.5 9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
  };

  var STATUS_SVG = '<svg width="18" height="12" viewBox="0 0 18 12" fill="currentColor" aria-hidden="true">'
    + '<rect x="0" y="8" width="3" height="4" rx="0.5" opacity=".35"/>'
    + '<rect x="4.5" y="5.5" width="3" height="6.5" rx="0.5" opacity=".55"/>'
    + '<rect x="9" y="3" width="3" height="9" rx="0.5" opacity=".75"/>'
    + '<rect x="13.5" y="0" width="3" height="12" rx="0.5"/>'
    + '</svg>'
    + '<svg width="16" height="12" viewBox="0 0 16 12" fill="currentColor" aria-hidden="true" style="margin-left:2px">'
    + '<path d="M8 2.4C5.4 2.4 3.1 3.6 1.6 5.5L0 4c1.9-2.3 4.8-3.7 8-3.7s6.1 1.4 8 3.7l-1.6 1.5C12.9 3.6 10.6 2.4 8 2.4z" opacity=".35"/>'
    + '<path d="M8 5.6c-1.7 0-3.2.7-4.3 1.9L2.1 6c1.4-1.5 3.4-2.4 5.9-2.4s4.5.9 5.9 2.4l-1.6 1.5C11.2 6.3 9.7 5.6 8 5.6z" opacity=".65"/>'
    + '<path d="M8 8.8c-.9 0-1.7.4-2.3 1L8 12l2.3-2.2c-.6-.6-1.4-1-2.3-1z"/>'
    + '</svg>'
    + '<svg width="27" height="13" viewBox="0 0 27 13" aria-hidden="true" style="margin-left:3px">'
    + '<rect x=".5" y=".5" width="22" height="12" rx="3.2" stroke="currentColor" fill="none" opacity=".35"/>'
    + '<rect x="2" y="2" width="17" height="9" rx="2" fill="currentColor"/>'
    + '<path d="M24 4.5v4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity=".4"/>'
    + '</svg>';

  var CAPSULE_HTML = '<div class="wx-capsule" aria-hidden="true">'
    + '<div class="wx-capsule-more"><span></span><span></span><span></span></div>'
    + '<div class="wx-capsule-divider"></div>'
    + '<div class="wx-capsule-close"><span class="ring"></span></div></div>';

  var TAB_DRIVER = [
    { key: 'home', label: '工作台', icon: 'home' },
    { key: 'task', label: '任务', icon: 'list' },
    { key: 'finance', label: '收入', icon: 'wallet' },
    { key: 'me', label: '我的', icon: 'user' }
  ];
  var TAB_ADMIN = [
    { key: 'home', label: '工作台', icon: 'home' },
    { key: 'dispatch', label: '调度', icon: 'truck' },
    { key: 'approve', label: '审批', icon: 'approve' },
    { key: 'me', label: '我的', icon: 'user' }
  ];

  function injectSprite() {
    if (document.getElementById('mp-sprite')) return;
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.id = 'mp-sprite'; svg.setAttribute('aria-hidden', 'true'); svg.style.display = 'none';
    var html = '';
    Object.keys(ICONS).forEach(function (k) {
      html += '<symbol id="i-' + k + '" viewBox="0 0 24 24">' + ICONS[k] + '</symbol>';
    });
    svg.innerHTML = html;
    document.body.insertBefore(svg, document.body.firstChild);
  }

  function wrapDevices() {
    document.querySelectorAll('.dev').forEach(function (dev) {
      if (dev.querySelector(':scope > .iphone-screen')) return;
      var screen = document.createElement('div');
      screen.className = 'iphone-screen';
      var island = document.createElement('div');
      island.className = 'iphone-island';
      screen.appendChild(island);
      while (dev.firstChild) screen.appendChild(dev.firstChild);
      var home = document.createElement('div');
      home.className = 'iphone-home-bar';
      home.innerHTML = '<i></i>';
      screen.appendChild(home);
      dev.appendChild(screen);
    });
  }

  function buildChrome() {
    document.querySelectorAll('.wx-head').forEach(function (head) {
      if (head.querySelector('.wx-chrome')) return;
      var light = head.classList.contains('onpage');
      var oldNav = head.querySelector('.wx-nav');
      var title = oldNav ? (oldNav.querySelector('.ttl') || {}).textContent || '' : '';
      var hasBack = oldNav && oldNav.hasAttribute('data-back');
      var chrome = document.createElement('div');
      chrome.className = 'wx-chrome';
      chrome.innerHTML = '<div class="wx-statusbar"><span class="wx-time">9:41</span>'
        + '<div class="wx-status-icons">' + STATUS_SVG + '</div></div>'
        + '<div class="wx-navbar">'
        + '<div class="wx-nav-left">' + (hasBack ? '<span class="back" aria-hidden="true">‹</span>' : '') + '</div>'
        + '<div class="wx-nav-title">' + title + '</div>'
        + '<div class="wx-nav-spacer"></div>'
        + CAPSULE_HTML
        + '</div>';
      head.textContent = '';
      head.appendChild(chrome);
      if (light) head.classList.add('onpage');
    });
  }

  function parseBadges(raw) {
    var map = {};
    if (!raw) return map;
    raw.split(',').forEach(function (part) {
      var kv = part.split(':');
      if (kv.length === 2) map[kv[0].trim()] = kv[1].trim();
    });
    return map;
  }

  function buildTabbars() {
    var isAdmin = document.body.getAttribute('data-app') === 'admin';
    document.querySelectorAll('.tabbar[data-tab]').forEach(function (el) {
      if (el.getAttribute('data-built')) return;
      var active = el.getAttribute('data-tab') || 'home';
      var badges = parseBadges(el.getAttribute('data-badge'));
      var keys = isAdmin ? ['home', 'dispatch', 'approve', 'me'] : ['home', 'task', 'finance', 'me'];
      var defs = isAdmin ? TAB_ADMIN : TAB_DRIVER;
      var html = '';
      keys.forEach(function (key) {
        var def = defs.filter(function (d) { return d.key === key; })[0];
        if (!def) return;
        var on = active === key || (key === 'me' && (active === 'profile' || active === 'me')) ? ' on' : '';
        var b = badges[key] || badges.approve || badges.task || '';
        var badge = b === 'dot' ? '<i class="dot"></i>' : (b ? '<i class="num">' + b + '</i>' : '');
        html += '<div class="item' + on + '"><svg class="ico"><use href="#i-' + def.icon + '"></use></svg>' + def.label + badge + '</div>';
      });
      el.innerHTML = html;
      el.setAttribute('data-built', '1');
    });
  }

  function buildRail() {
    var rail = document.querySelector('.pt-rail');
    if (!rail) return;
    rail.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href').slice(1);
        var el = document.getElementById(id);
        if (!el) return;
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
        rail.querySelectorAll('a').forEach(function (x) { x.classList.remove('active'); });
        a.classList.add('active');
      });
    });
  }

  function tools() {
    var gallery = document.querySelector('.pt-gallery');
    if (!gallery) return;
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var boards = gallery.querySelectorAll('.board');
      var scrollLeft = gallery.scrollLeft, idx = 0, best = Infinity;
      for (var i = 0; i < boards.length; i++) {
        var d = Math.abs(boards[i].offsetLeft - scrollLeft);
        if (d < best) { best = d; idx = i; }
      }
      var next = e.key === 'ArrowRight' ? Math.min(idx + 1, boards.length - 1) : Math.max(idx - 1, 0);
      boards[next].scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
    });
  }

  function bindPress() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.btn, .tabbar .item, .cell, .quick .q').forEach(function (el) {
      el.addEventListener('pointerdown', function () { el.classList.add('is-pressed'); });
      function up() {
        el.classList.remove('is-pressed');
        el.removeEventListener('pointerup', up);
        el.removeEventListener('pointercancel', up);
      }
      el.addEventListener('pointerdown', function () {
        el.addEventListener('pointerup', up);
        el.addEventListener('pointercancel', up);
      });
    });
  }

  function boot() {
    injectSprite();
    wrapDevices();
    buildChrome();
    buildTabbars();
    buildRail();
    tools();
    bindPress();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
'''


def patch_css(css: str) -> str:
    # Remove old device block through wx-foot section
    start = css.find('/* ========== 画板 + 手机壳')
    if start == -1:
        start = css.find('/* ========== iPhone')
    end = css.find('/* ========== 工具类')
    if start != -1 and end != -1:
        css = css[:start] + DEVICE_CSS + '\n' + css[end:]
    # Remove duplicate v2 patch if re-run
    css = re.sub(r'\n/\* ========== v2 · apple-design.*?(?=\n/\* ==========|\Z)', '\n', css, flags=re.S)
    # Ensure card/task spacing uses tokens
    css = css.replace('margin: 10px 12px', 'margin: var(--space-3) var(--space-4)')
    css = css.replace('padding: 13px 14px', 'padding: 14px var(--space-4)')
    return css


def main():
    for root in ROOTS:
        css_path = root / 'mp.css'
        js_path = root / 'mp.js'
        css = patch_css(css_path.read_text(encoding='utf-8'))
        css_path.write_text(css, encoding='utf-8')
        js_path.write_text(JS_V3, encoding='utf-8')
        print('OK', root.parent.name, 'css', len(css), 'js', len(JS_V3))


if __name__ == '__main__':
    main()
