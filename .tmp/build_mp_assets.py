# -*- coding: utf-8 -*-
"""Rebuild mp.css + mp.js for the rich prototype design system."""
from pathlib import Path

CSS = r"""/* 智途 · 微信小程序原型设计系统
 * data-app="driver" → 品牌蓝 #1d4ed8
 * data-app="admin"  → 品牌蓝 #0052d9
 */
:root {
  --brand: #1d4ed8;
  --brand-deep: #1e3a8a;
  --brand-soft: #dbeafe;
  --brand-tint: #eff6ff;
  --success: #16a34a;
  --success-soft: #dcfce7;
  --warning: #f59e0b;
  --warning-soft: #fef3c7;
  --danger: #dc2626;
  --danger-soft: #fee2e2;
  --info: #0ea5e9;
  --info-soft: #e0f2fe;
  --muted: #64748b;
  --t1: #0f172a;
  --t2: #475569;
  --t3: #94a3b8;
  --bg: #eef2f7;
  --page: #f4f6fb;
  --card: #ffffff;
  --line: #e2e8f0;
  --r: 12px;
  --r-s: 8px;
  --r-l: 16px;
  --pill: 999px;
  --shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 12px rgba(15, 23, 42, 0.04);
  --font: "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei", sans-serif;
  --mono: "DIN Alternate", "SF Mono", "Menlo", "Consolas", monospace;
  --dev-w: 375px;
  --dev-h: 812px;
  --nav-h: 44px;
  --status-h: 44px;
}

body[data-app="admin"] {
  --brand: #0052d9;
  --brand-deep: #003cab;
  --brand-soft: #d9e1ff;
  --brand-tint: #f2f3ff;
  --success: #2ba471;
  --success-soft: #e3f9e9;
  --warning: #e37318;
  --warning-soft: #fff1e9;
  --danger: #d54941;
  --danger-soft: #fff0ed;
  --info: #0594fa;
  --info-soft: #ecf6ff;
  --page: #f3f3f3;
  --bg: #e8eef8;
}

*, *::before, *::after { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  font-family: var(--font);
  color: var(--t1);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
button { font-family: inherit; }
code {
  font-family: var(--mono);
  font-size: 12px;
  background: #f1f5f9;
  padding: 1px 5px;
  border-radius: 4px;
  color: var(--t1);
}
em { font-style: normal; color: var(--brand); font-weight: 600; }

/* ========== 模块说明头 ========== */
.pt-head {
  background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
  color: #e2e8f0;
  border-bottom: 1px solid #1f2937;
}
.pt-head-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 32px 22px;
}
.pt-kicker {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #94a3b8; margin-bottom: 10px;
}
.pt-kicker i {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--brand);
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.25);
}
.pt-kicker b { color: #e2e8f0; font-weight: 600; }
.pt-kicker span {
  margin-left: 4px; padding: 1px 8px; border-radius: var(--pill);
  background: #1e293b; color: #94a3b8; font-size: 11px;
}
.pt-title { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
.pt-title h1 { margin: 0; font-size: 28px; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.badge {
  display: inline-flex; align-items: center; height: 24px;
  padding: 0 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
}
.badge.p0 { background: #14532d; color: #bbf7d0; }
.badge.p1 { background: #7c2d12; color: #fed7aa; }
.badge.p2 { background: #334155; color: #cbd5e1; }
.pt-intent {
  max-width: 820px; margin: 0 0 18px; font-size: 14px; line-height: 1.7; color: #94a3b8;
}
.pt-meta {
  display: flex; flex-wrap: wrap; gap: 10px 22px; margin: 0 0 18px; padding: 0;
}
.pt-meta > div { display: flex; gap: 8px; align-items: baseline; font-size: 12.5px; }
.pt-meta dt { margin: 0; color: #64748b; }
.pt-meta dd { margin: 0; color: #cbd5e1; }
.pt-meta .sep { margin: 0 6px; color: #475569; }

.pt-rail {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.pt-rail a {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 12px; border-radius: 8px;
  background: #1e293b; border: 1px solid #334155;
  font-size: 12.5px; color: #cbd5e1; transition: .15s;
}
.pt-rail a:hover, .pt-rail a.active {
  background: var(--brand); border-color: var(--brand); color: #fff;
}
.pt-rail .n { font-size: 10px; font-weight: 700; letter-spacing: .04em; opacity: .7; }
.pt-rail.parallel a { flex-direction: column; align-items: flex-start; gap: 2px; min-width: 120px; }

/* ========== 主体 ========== */
.pt-body { max-width: 1280px; margin: 0 auto; padding: 28px 32px 60px; }
.pt-group { margin: 8px 0 18px; }
.pt-group-head h2 { margin: 0 0 4px; font-size: 18px; }
.pt-group-head .sub { font-size: 13px; color: var(--t2); }
.pt-gallery {
  display: flex; gap: 28px; overflow-x: auto;
  padding: 4px 4px 20px; scroll-snap-type: x proximity;
  align-items: flex-start;
}
.pt-rules {
  margin-top: 24px; padding: 18px 20px; background: #fff;
  border-radius: var(--r); border: 1px solid var(--line);
}
.pt-rules h4 { margin: 0 0 10px; font-size: 14px; }
.pt-rules ul { margin: 0; padding-left: 18px; font-size: 13px; color: var(--t2); line-height: 1.7; }
.pt-foot {
  text-align: center; padding: 20px; font-size: 12px; color: var(--t3);
  border-top: 1px solid var(--line);
}

/* ========== 画板 ========== */
.board {
  flex: 0 0 auto; width: var(--dev-w);
  scroll-snap-align: start;
  opacity: 1; transform: none;
}
.board-cap {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px; min-height: 28px;
}
.board-cap .n {
  width: 24px; height: 24px; border-radius: 7px;
  background: var(--brand); color: #fff;
  font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.board-cap h3 { margin: 0; font-size: 13.5px; font-weight: 600; flex: 1; }
.board-cap .tip {
  font-size: 11px; color: var(--t3);
  padding: 2px 8px; border-radius: var(--pill); background: #fff; border: 1px solid var(--line);
}

/* ========== 手机壳 ========== */
.dev {
  width: var(--dev-w); height: var(--dev-h);
  background: #0f172a; border-radius: 40px; padding: 11px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22), 0 0 0 1px rgba(15, 23, 42, 0.1);
  display: flex; flex-direction: column; position: relative; overflow: hidden;
}
.dev.auto { height: auto; min-height: var(--dev-h); }
.dev .wx-head {
  flex-shrink: 0; background: var(--brand); color: #fff;
  border-radius: 30px 30px 0 0; overflow: hidden; position: relative;
}
.dev .wx-head.onpage { background: #fff; color: var(--t1); }
.dev .wx-head.dark-cap { /* light page with dark capsule handled in js */ }

.wx-status {
  height: var(--status-h); display: flex; align-items: flex-end;
  justify-content: space-between; padding: 0 22px 7px;
  font-size: 12px; font-weight: 600;
}
.wx-status .sig { display: flex; gap: 3px; align-items: center; font-size: 11px; }

.wx-nav {
  height: var(--nav-h); display: flex; align-items: center;
  padding: 0 12px; position: relative;
}
.wx-nav .back {
  width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
  font-size: 22px; line-height: 1; margin-right: 2px; opacity: .95;
}
.wx-nav .ttl {
  position: absolute; left: 50%; transform: translateX(-50%);
  font-size: 16px; font-weight: 600; max-width: 180px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.wx-capsule {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  width: 87px; height: 32px; border-radius: 16px;
  border: 1px solid rgba(255,255,255,.35); background: rgba(255,255,255,.12);
  display: flex; align-items: center; z-index: 5;
}
.wx-head.onpage .wx-capsule,
.dev .wx-head[style*="background:#fff"] .wx-capsule,
.dev .wx-head[style*="background: #fff"] .wx-capsule {
  border-color: rgba(0,0,0,.12); background: rgba(0,0,0,.04);
}
.wx-capsule .dot { flex: 1; text-align: center; font-size: 11px; opacity: .9; }
.wx-capsule .sep { width: 1px; height: 14px; background: rgba(255,255,255,.35); }
.wx-head.onpage .wx-capsule .sep { background: rgba(0,0,0,.12); }

.wx-body {
  flex: 1; background: var(--page); overflow: hidden;
  display: flex; flex-direction: column; position: relative; min-height: 0;
}
.wx-body.scroll { overflow-y: auto; -webkit-overflow-scrolling: touch; display: block; }
.wx-body.white { background: #fff; }
.dev.auto .wx-body { overflow: visible; }

/* ========== 通用组件 ========== */
.pad { padding: 12px; }
.pad-b { padding: 0 16px 16px; }
.mt4 { margin-top: 4px; } .mt6 { margin-top: 6px; } .mt8 { margin-top: 8px; }
.mt10 { margin-top: 10px; } .mt12 { margin-top: 12px; } .mt16 { margin-top: 16px; }
.mb8 { margin-bottom: 8px; } .mb12 { margin-bottom: 12px; }
.fx { display: flex; align-items: center; }
.fx.g4 { gap: 4px; } .fx.g6 { gap: 6px; } .fx.g8 { gap: 8px; }
.fx.g10 { gap: 10px; } .fx.g14 { gap: 14px; }
.between { justify-content: space-between; }
.grow { flex: 1; min-width: 0; }
.rel { position: relative; }
.t1 { color: var(--t1); } .t2 { color: var(--t2); } .t3 { color: var(--t3); }
.strong { font-weight: 600; }
.blue { color: var(--brand); }
.mut { color: var(--t3); }
.ico { width: 16px; height: 16px; fill: currentColor; flex-shrink: 0; }

.card {
  background: var(--card); border-radius: var(--r);
  margin: 10px 12px; padding: 14px; box-shadow: var(--shadow);
}
.card.flat { box-shadow: none; border: 1px solid var(--line); }
.card.pull-up { margin-top: -14px; position: relative; z-index: 2; }
.card .hd {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px; font-size: 14px; font-weight: 600;
}
.card .hd::before {
  content: ""; width: 3px; height: 14px; border-radius: 2px;
  background: var(--brand); margin-right: 8px;
}
.card .hd { justify-content: flex-start; gap: 0; }
.card .hd .more { margin-left: auto; font-size: 12px; font-weight: 400; color: var(--t3); }

.stat, .chip {
  display: inline-flex; align-items: center; height: 22px;
  padding: 0 8px; border-radius: 6px; font-size: 11px; font-weight: 600;
}
.stat.warning, .chip.warning { background: var(--warning-soft); color: #b45309; }
.stat.info, .chip.info { background: var(--info-soft); color: #0369a1; }
.stat.success, .chip.success { background: var(--success-soft); color: var(--success); }
.stat.danger, .chip.danger { background: var(--danger-soft); color: var(--danger); }
.stat.primary, .chip.primary { background: var(--brand-soft); color: var(--brand); }
.stat.muted, .chip.muted { background: #f1f5f9; color: var(--t2); }

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  height: 40px; padding: 0 16px; border-radius: 10px;
  font-size: 14px; font-weight: 600; border: none; cursor: default;
  background: var(--brand); color: #fff;
}
.btn.block { width: 100%; display: flex; }
.btn.wide { flex: 1; }
.btn.line { background: #fff; color: var(--t1); border: 1px solid var(--line); }
.btn.ghost { background: transparent; color: var(--brand); border: 1px solid var(--brand-soft); }
.btn.danger { background: var(--danger); }
.btn.success { background: var(--success); }
.btn.warn { background: var(--warning); color: #fff; }
.btn.soft { background: var(--brand-tint); color: var(--brand); }
.btn.sm { height: 32px; padding: 0 12px; font-size: 13px; border-radius: 8px; }
.btn.xs { height: 26px; padding: 0 8px; font-size: 12px; border-radius: 6px; }
.btn.dis, .btn[disabled] { opacity: .45; }

.action-bar {
  flex-shrink: 0; display: flex; gap: 10px;
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom, 16px));
  background: #fff; border-top: 1px solid var(--line);
}
.tabbar {
  flex-shrink: 0; display: flex;
  padding: 6px 0 calc(6px + env(safe-area-inset-bottom, 16px));
  background: #fff; border-top: 1px solid var(--line);
}
.tabbar .item {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  gap: 2px; font-size: 10px; color: var(--t3); position: relative;
}
.tabbar .item.on { color: var(--brand); font-weight: 600; }
.tabbar .item .ico { width: 22px; height: 22px; }
.tabbar .item .dot {
  position: absolute; top: -1px; right: calc(50% - 16px);
  width: 7px; height: 7px; border-radius: 50%; background: var(--danger);
  border: 1.5px solid #fff;
}
.tabbar .item .num {
  position: absolute; top: -4px; right: calc(50% - 22px);
  min-width: 16px; height: 16px; padding: 0 4px; border-radius: 8px;
  background: var(--danger); color: #fff; font-size: 10px;
  display: flex; align-items: center; justify-content: center;
}

/* Banner */
.dev .banner {
  position: relative; padding: 12px 16px 24px; color: #fff;
  background-color: var(--brand);
  background-image: radial-gradient(130% 110% at 100% 100%, var(--brand-deep) 0%, transparent 62%);
}
.dev .banner .top { display: flex; align-items: center; gap: 8px; }
.dev .banner .stat {
  display: inline-flex; align-items: center; gap: 5px;
  height: 25px; padding: 0 11px; border-radius: var(--pill);
  font-size: 13px; font-weight: 600; color: #fff; background: var(--muted);
}
.dev .banner .stat::before {
  content: ""; width: 6px; height: 6px; border-radius: 50%; background: #fff; opacity: .92;
}
.dev .banner .stat.warning { background: var(--warning); }
.dev .banner .stat.info { background: var(--info); }
.dev .banner .stat.success { background: var(--success); }
.dev .banner .stat.danger { background: var(--danger); }
.dev .banner .stat.primary { color: var(--brand-deep); background: #fff; }
.dev .banner .stat.primary::before { background: var(--brand); opacity: 1; }
.dev .banner .no { margin-left: auto; font-family: var(--mono); font-size: 12px; opacity: .8; }
.dev .banner .nm { margin-top: 11px; font-size: 18.5px; font-weight: 600; letter-spacing: -.01em; }
.dev .banner .sub {
  display: flex; align-items: center; gap: 6px; margin-top: 5px;
  font-size: 12.5px; opacity: .84;
}
.dev .banner .sub .ico { width: 13px; height: 13px; }
.dev .banner .mini { display: flex; margin-top: 15px; }
.dev .banner .mini > div { flex: 1; min-width: 0; line-height: 1.28; }
.dev .banner .mini .k { font-size: 11px; opacity: .76; }
.dev .banner .mini .v { margin-top: 3px; font-family: var(--mono); font-size: 15px; font-weight: 600; }
.dev .banner .mut { color: inherit; opacity: .5; }

/* Notice */
.dev .notice {
  display: flex; align-items: flex-start; gap: 8px;
  margin: 0; padding: 10px 14px; font-size: 12.5px; line-height: 1.55;
  background: var(--warning-soft); color: #92400e;
}
.dev .notice .ico { width: 14px; height: 14px; margin-top: 2px; flex-shrink: 0; }
.dev .notice.info { background: var(--brand-tint); color: var(--brand-deep); }
.dev .notice.danger { background: var(--danger-soft); color: #991b1b; }

/* Route */
.dev .route { display: flex; flex-direction: column; gap: 0; position: relative; }
.dev .route .leg {
  display: flex; gap: 10px; padding: 4px 0 14px; position: relative;
}
.dev .route .leg::before {
  content: ""; width: 10px; height: 10px; border-radius: 50%;
  background: var(--brand); margin-top: 4px; flex-shrink: 0;
  box-shadow: 0 0 0 3px var(--brand-soft);
}
.dev .route .leg.to::before { background: var(--danger); box-shadow: 0 0 0 3px var(--danger-soft); border-radius: 2px; }
.dev .route .leg:not(:last-child)::after {
  content: ""; position: absolute; left: 4px; top: 18px; bottom: 0;
  width: 2px; background: repeating-linear-gradient(180deg, var(--line) 0 3px, transparent 3px 6px);
}
.dev .route .loc { font-size: 14px; font-weight: 600; }
.dev .route .when { font-size: 12px; color: var(--t3); margin-top: 3px; }
.dev .route .meta-side {
  position: absolute; right: 0; top: 8px; text-align: right; font-size: 12px; color: var(--t2);
}
.dev .route .meta-side .km { font-family: var(--mono); font-weight: 700; color: var(--t1); font-size: 14px; }

/* KPI */
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.kpis .kpi {
  background: rgba(255,255,255,.14); border-radius: 10px; padding: 10px 8px; text-align: center;
}
.kpis .kpi .v { font-size: 20px; font-weight: 700; font-family: var(--mono); line-height: 1.15; }
.kpis .kpi .v.sm { font-size: 15px; }
.kpis .kpi .k { font-size: 11px; opacity: .8; margin-top: 3px; }
.kpi-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 0 12px; margin: 10px 0;
}
.kpi-grid .kpi {
  background: #fff; border-radius: var(--r); padding: 12px; box-shadow: var(--shadow);
}
.kpi-grid .kpi .k { font-size: 11px; color: var(--t2); }
.kpi-grid .kpi .v { font-size: 22px; font-weight: 700; font-family: var(--mono); margin-top: 4px; }
.kpi-grid .kpi.warn .v { color: var(--warning); }
.kpi-grid .kpi.brand .v { color: var(--brand); }

/* Hero */
.dev .hero {
  background: linear-gradient(160deg, var(--brand) 0%, #2563eb 60%, #3b82f6 100%);
  color: #fff; padding: 8px 0 18px;
}
body[data-app="admin"] .dev .hero {
  background: linear-gradient(160deg, var(--brand) 0%, #266fe8 60%, #4787f0 100%);
}
.ava {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,.2); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; flex-shrink: 0;
}
.ava.sm { width: 36px; height: 36px; font-size: 14px; }

/* Cells / list */
.cells { background: #fff; border-radius: var(--r); margin: 10px 12px; overflow: hidden; box-shadow: var(--shadow); }
.cell {
  display: flex; align-items: center; gap: 10px;
  padding: 14px; border-bottom: 1px solid #f1f5f9; min-height: 48px;
}
.cell:last-child { border-bottom: none; }
.cell .k { flex: 1; font-size: 14px; color: var(--t1); }
.cell .v { font-size: 13px; color: var(--t2); text-align: right; }
.cell .caret { color: var(--t3); font-size: 14px; }
.cell .ib {
  width: 34px; height: 34px; border-radius: 9px;
  background: var(--brand-tint); color: var(--brand);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.lnk { font-size: 13px; color: var(--brand); }
.lnk.dim { color: var(--t3); }

/* Search / tabs */
.search {
  display: flex; align-items: center; gap: 8px;
  margin: 10px 12px; padding: 9px 12px; background: #fff;
  border-radius: 10px; box-shadow: var(--shadow); font-size: 13px; color: var(--t3);
}
.tabs {
  display: flex; gap: 0; overflow-x: auto; background: #fff;
  border-bottom: 1px solid var(--line); padding: 0 8px;
}
.tabs .tab {
  flex: 0 0 auto; padding: 12px 12px; font-size: 13px; color: var(--t2);
  position: relative; white-space: nowrap;
}
.tabs .tab.on { color: var(--brand); font-weight: 600; }
.tabs .tab.on::after {
  content: ""; position: absolute; left: 12px; right: 12px; bottom: 0;
  height: 2px; background: var(--brand); border-radius: 1px;
}
.chips { display: flex; gap: 8px; overflow-x: auto; padding: 10px 12px; }
.chips .chip {
  flex: 0 0 auto; height: 28px; padding: 0 12px; border-radius: var(--pill);
  background: #fff; border: 1px solid var(--line); font-weight: 500; color: var(--t2);
}
.chips .chip.on { background: var(--brand-tint); border-color: var(--brand-soft); color: var(--brand); }

/* Task card */
.task {
  background: #fff; border-radius: var(--r); margin: 0 12px 10px;
  padding: 14px; box-shadow: var(--shadow);
}
.task .top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.task .no { font-size: 12px; font-family: var(--mono); color: var(--t3); }
.task .nm { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
.task .meta { display: flex; flex-wrap: wrap; gap: 6px 12px; font-size: 12px; color: var(--t2); }

/* Form */
.field { margin-bottom: 14px; }
.field .lab { font-size: 12px; color: var(--t2); margin-bottom: 6px; }
.field .lab .req { color: var(--danger); }
.field .inp {
  height: 40px; border: 1px solid var(--line); border-radius: 8px;
  padding: 0 12px; display: flex; align-items: center; background: #fff;
  font-size: 14px; color: var(--t1);
}
.field .inp.ph { color: var(--t3); }
.field .ta {
  min-height: 80px; border: 1px solid var(--line); border-radius: 8px;
  padding: 10px 12px; background: #fff; font-size: 14px; color: var(--t3); line-height: 1.5;
}

/* Timeline / steps */
.steps { position: relative; padding-left: 18px; }
.steps::before {
  content: ""; position: absolute; left: 5px; top: 6px; bottom: 6px;
  width: 2px; background: var(--line);
}
.steps .s {
  position: relative; padding-bottom: 14px;
}
.steps .s:last-child { padding-bottom: 0; }
.steps .s::before {
  content: ""; position: absolute; left: -16px; top: 4px;
  width: 10px; height: 10px; border-radius: 50%;
  background: #fff; border: 2px solid var(--line); z-index: 1;
}
.steps .s.done::before { border-color: var(--brand); background: var(--brand); }
.steps .s.now::before {
  border-color: var(--brand); background: #fff;
  box-shadow: 0 0 0 3px var(--brand-soft);
}
.steps .s .t { font-size: 13px; font-weight: 600; }
.steps .s .d { font-size: 11px; color: var(--t3); margin-top: 2px; }
.steps .s:not(.done):not(.now) .t { color: var(--t3); font-weight: 400; }
.steps-h {
  display: flex; gap: 4px; overflow-x: auto; font-size: 11px;
}
.steps-h .s {
  flex: 1; text-align: center; padding: 6px 2px; border-radius: 6px;
  background: #f1f5f9; color: var(--t3); white-space: nowrap;
}
.steps-h .s.done { background: var(--brand-soft); color: var(--brand); }
.steps-h .s.now { background: var(--brand); color: #fff; font-weight: 600; }

/* Map */
.dev .map {
  position: relative; height: 160px; margin: 0 12px 10px; border-radius: var(--r); overflow: hidden;
  background:
    linear-gradient(135deg, rgba(29,78,216,.08), transparent 50%),
    repeating-linear-gradient(0deg, transparent, transparent 18px, #e2e8f0 18px, #e2e8f0 19px),
    repeating-linear-gradient(90deg, transparent, transparent 18px, #e2e8f0 18px, #e2e8f0 19px),
    #f8fafc;
}
.dev .map .path { position: absolute; inset: 0; width: 100%; height: 100%; }
.dev .map .path path {
  fill: none; stroke: var(--brand); stroke-width: 3; stroke-linecap: round;
}
.dev .map .path path.plan { stroke: #94a3b8; stroke-dasharray: 4 4; }
.dev .map .dotp {
  position: absolute; width: 12px; height: 12px; border-radius: 50%;
  background: var(--brand); border: 2px solid #fff;
  transform: translate(-50%, -50%); box-shadow: 0 1px 4px rgba(0,0,0,.2);
}
.dev .map .mrk {
  position: absolute; z-index: 2; transform: translate(-50%, -100%);
}
.dev .map .mrk .bub {
  position: relative; display: flex; align-items: center; gap: 4px;
  padding: 4px 8px; border-radius: var(--r-s); font-size: 11px; font-weight: 500;
  white-space: nowrap; color: #fff; background: var(--brand);
  box-shadow: 0 2px 6px rgba(16, 36, 43, 0.24);
}
.dev .map .mrk .bub::after {
  content: ""; position: absolute; bottom: -3px; left: 50%;
  width: 7px; height: 7px; margin-left: -3.5px;
  border-radius: 0 0 2px 0; transform: rotate(45deg); background: inherit;
}
.dev .map .hint {
  position: absolute; left: 10px; bottom: 10px;
  background: rgba(255,255,255,.92); padding: 4px 8px; border-radius: 4px;
  font-size: 11px; color: var(--t2);
}

/* Photos */
.photos { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.photos .slot {
  aspect-ratio: 1; border-radius: 8px; background: #f1f5f9;
  border: 1px dashed #cbd5e1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; color: var(--t3); font-size: 11px; gap: 4px;
}
.photos .slot.filled {
  border: none; background: linear-gradient(135deg, #94a3b8, #64748b); color: #fff; font-size: 18px;
}
.photos .slot .add { font-size: 22px; line-height: 1; }

/* Empty */
.empty { text-align: center; padding: 56px 28px; color: var(--t3); }
.empty .ico { width: 48px; height: 48px; margin: 0 auto 12px; opacity: .45; }
.empty .t { font-size: 14px; color: var(--t2); margin-bottom: 6px; }
.empty .d { font-size: 12px; line-height: 1.55; }

/* Overlay / sheet / dialog */
.mask {
  position: absolute; inset: 0; background: rgba(15, 23, 42, .45);
  z-index: 20; display: flex;
}
.mask.bottom { align-items: flex-end; }
.mask.center { align-items: center; justify-content: center; padding: 24px; }
.sheet {
  width: 100%; background: #fff; border-radius: 16px 16px 0 0;
  padding: 12px 16px 28px;
}
.sheet .handle {
  width: 36px; height: 4px; background: #e2e8f0; border-radius: 2px; margin: 0 auto 14px;
}
.dialog {
  width: 100%; max-width: 300px; background: #fff; border-radius: 14px;
  padding: 22px 20px 16px; text-align: center;
}
.dialog .t { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.dialog .d { font-size: 13px; color: var(--t2); line-height: 1.55; margin-bottom: 18px; }
.dialog .af { display: flex; gap: 10px; }
.toast {
  position: absolute; left: 50%; top: 42%; transform: translate(-50%, -50%);
  background: rgba(15, 23, 42, .84); color: #fff; padding: 12px 18px;
  border-radius: 8px; font-size: 13px; z-index: 30; text-align: center; max-width: 80%;
}
.wx-auth { background: #fff; padding: 18px 16px; }
.wx-auth .ah { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; }
.wx-auth .lg {
  width: 40px; height: 40px; border-radius: 10px; background: var(--brand);
  color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700;
}
.wx-auth .nm { font-size: 15px; font-weight: 600; }
.wx-auth .sub { font-size: 12px; color: var(--t3); }
.wx-auth .aq { font-size: 16px; font-weight: 600; margin-bottom: 10px; }
.wx-auth .ai { padding: 12px; background: #f8fafc; border-radius: 8px; margin-bottom: 16px; font-size: 18px; font-weight: 600; }
.wx-auth .af { display: flex; gap: 10px; }

/* Pin annotations */
.pin {
  position: absolute; top: -6px; right: -6px; z-index: 8;
  width: 18px; height: 18px; border-radius: 50%;
  background: #ef4444; color: #fff; font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 1px 3px rgba(16, 36, 43, 0.35);
  font-style: normal;
}
.pin.tl { top: -4px; left: -4px; right: auto; }
.pin.in { top: 5px; right: 5px; }
.pin.bar { top: -8px; left: 14px; right: auto; }

/* Checkbox */
.ck {
  width: 18px; height: 18px; border-radius: 4px; border: 1.5px solid #cbd5e1;
  display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: #fff; position: relative;
}
.ck.on { background: var(--brand); border-color: var(--brand); color: #fff; }
.ck.sq { border-radius: 4px; }

/* Quick grid */
.quick { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px 6px; padding: 4px 0; }
.quick .q {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  font-size: 11px; color: var(--t2);
}
.quick .q .ib {
  width: 42px; height: 42px; border-radius: 12px;
  background: var(--brand-tint); color: var(--brand);
  display: flex; align-items: center; justify-content: center;
}
.quick .q .ib.warn { background: var(--warning-soft); color: #b45309; }
.quick .q .ib.success { background: var(--success-soft); color: var(--success); }

/* Chart */
.chart-bars {
  display: flex; align-items: flex-end; gap: 8px; height: 100px; padding: 8px 0 18px;
}
.chart-bars .bar {
  flex: 1; background: linear-gradient(180deg, var(--brand), #60a5fa);
  border-radius: 4px 4px 0 0; min-height: 8px; position: relative;
}
.chart-bars .bar .lbl {
  position: absolute; bottom: -16px; left: 50%; transform: translateX(-50%);
  font-size: 10px; color: var(--t3); white-space: nowrap;
}

/* Money */
.money { font-weight: 700; font-family: var(--mono); color: #b45309; }
.hr { height: 1px; background: #f1f5f9; margin: 10px 0; }
.end {
  text-align: center; padding: 16px; font-size: 11px; color: var(--t3);
}

/* Notes under board */
.board > .notes, ol.notes {
  margin: 14px 0 0; padding: 12px 14px 12px 30px;
  background: #fff; border-radius: 10px; border: 1px solid var(--line);
  font-size: 12.5px; color: #475569; line-height: 1.7;
}
.notes .flag {
  display: inline-block; padding: 0 5px; border-radius: 3px;
  background: #7c2d12; color: #fed7aa; font-size: 10px; font-weight: 700; margin-right: 4px;
}
.notes li { margin-bottom: 6px; }
.notes li:last-child { margin-bottom: 0; }

/* Progress */
.progress { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; }
.progress .bar { height: 100%; background: var(--brand); border-radius: 3px; }

/* Misc helpers used in pages */
.grid { display: grid; gap: 8px; }
.item-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.item-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 12px; color: var(--t2); }
.counter { font-family: var(--mono); font-weight: 600; }
.full { width: 100%; }
.bare { box-shadow: none !important; }
.flush { margin-left: 0; margin-right: 0; border-radius: 0; }
.dim { opacity: .55; }
.green { color: var(--success); }
.err { color: var(--danger); }

/* Skeleton */
.sk {
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 37%, #e2e8f0 63%);
  background-size: 400% 100%; border-radius: 6px; height: 14px;
  animation: sk 1.4s ease infinite;
}
@keyframes sk { 0% { background-position: 100% 0; } 100% { background-position: 0 0; } }
"""

JS = r"""/* 智途 · 小程序原型 · 机身铬合金 + 图标 + 锚点 */
(function () {
  var ICONS = {
    truck: '<path d="M3 7h11v8H3zm11 2h4l3 3v3h-7z"/><circle cx="7" cy="17" r="1.6"/><circle cx="16.5" cy="17" r="1.6"/>',
    building: '<path d="M4 20V6l6-3 6 3v14H4zm4-2h2v-3H8v3zm6 0h2v-3h-2v3zM8 11h2V8H8v3zm6 0h2V8h-2v3z"/>',
    clock: '<circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    home: '<path d="M4 11.5 12 4l8 7.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-8.5z"/>',
    list: '<path d="M8 7h11M8 12h11M8 17h11M4 7h.01M4 12h.01M4 17h.01" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    wallet: '<path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H18v2.5H6.2A1.2 1.2 0 0 0 5 8.7V17.5h13.5V10H11v4.5h9.5V19A1.5 1.5 0 0 1 19 20.5H5A2 2 0 0 1 3 18.5v-11z"/><circle cx="16.5" cy="12.25" r="1"/>',
    user: '<circle cx="12" cy="8" r="3.2"/><path d="M5 19c1.5-3.2 4-4.8 7-4.8s5.5 1.6 7 4.8"/>',
    wechat: '<path d="M9.2 7.2c-3.3 0-6 2.2-6 5 0 1.6.8 3 2.1 4l-.4 1.6 1.9-1c.7.2 1.5.3 2.3.3.3 0 .6 0 .9-.1A4.7 4.7 0 0 1 9 14.6c0-3.2 3.1-5.8 7-6.2-.6-1.8-2.9-3.2-6.8-3.2zm-2.1 3.1a.85.85 0 1 1 0-1.7.85.85 0 0 1 0 1.7zm4.2 0a.85.85 0 1 1 0-1.7.85.85 0 0 1 0 1.7zM16 9.8c-3.4 0-6.1 2.2-6.1 4.9s2.7 4.9 6.1 4.9c.7 0 1.3-.1 1.9-.3l1.6.8-.4-1.4c1.1-.9 1.8-2.1 1.8-3.9 0-2.8-2.7-5-4.9-5zm-2 .9a.7.7 0 1 1 0-1.4.7.7 0 0 1 0 1.4zm3.9 0a.7.7 0 1 1 0-1.4.7.7 0 0 1 0 1.4z"/>',
    swap: '<path d="M7 7h9l-2-2m2 2-2 2M17 17H8l2 2m-2-2 2-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
    search: '<circle cx="10.5" cy="10.5" r="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M15 15l4 4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    phone: '<path d="M7.5 3.5h3l1.2 3.2-1.8 1.2a11 11 0 0 0 5.2 5.2l1.2-1.8 3.2 1.2v3A1.5 1.5 0 0 1 18 17.5 13.5 13.5 0 0 1 4.5 4a1.5 1.5 0 0 1 1.5-1.5h1.5z"/>',
    nav: '<path d="M12 3l8 17-8-4-8 4 8-17z"/>',
    cam: '<path d="M4 8h3l1.5-2h7L17 8h3v11H4V8z"/><circle cx="12" cy="13" r="3.2" fill="none" stroke="#fff" stroke-width="1.5"/>',
    bell: '<path d="M12 3a5 5 0 0 1 5 5v3.5l1.5 2.5H5.5L7 11.5V8a5 5 0 0 1 5-5z"/><path d="M10 19a2 2 0 0 0 4 0"/>',
    chart: '<path d="M4 19h16M7 16V10m5 6V7m5 9v-4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    check: '<path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    warn: '<path d="M12 4l9 16H3L12 4z"/><path d="M12 10v4m0 3h.01" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>',
    plus: '<path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    filter: '<path d="M4 6h16l-6 7v5l-4 2v-7L4 6z"/>',
    msg: '<path d="M4 6h16v10H8l-4 3V6z"/>',
    car: '<path d="M4 14l2-5h12l2 5v4h-2.2a1.8 1.8 0 0 1-3.6 0H9.8a1.8 1.8 0 0 1-3.6 0H4v-4z"/>',
    fuel: '<path d="M6 4h8v14H6zM14 8h2.5a2 2 0 0 1 2 2v7a1.5 1.5 0 0 0 1.5 1.5"/><path d="M8 8h4" fill="none" stroke="#fff" stroke-width="1.4"/>',
    calendar: '<rect x="4" y="6" width="16" height="14" rx="2"/><path d="M8 4v4M16 4v4M4 11h16" fill="none" stroke="#fff" stroke-width="1.4"/>',
    shield: '<path d="M12 3l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-3z"/>',
    setting: '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v2.2m0 14.6v2.2M2.5 12h2.2m14.6 0h2.2M5.1 5.1l1.6 1.6m10.6 10.6 1.6 1.6m0-14.8-1.6 1.6M6.7 17.3l-1.6 1.6" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>'
  };

  function injectSprite() {
    if (document.getElementById('mp-sprite')) return;
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('id', 'mp-sprite');
    svg.setAttribute('style', 'display:none');
    svg.setAttribute('aria-hidden', 'true');
    var html = '';
    Object.keys(ICONS).forEach(function (k) {
      html += '<symbol id="i-' + k + '" viewBox="0 0 24 24">' + ICONS[k] + '</symbol>';
    });
    svg.innerHTML = html;
    document.body.insertBefore(svg, document.body.firstChild);
  }

  function buildChrome() {
    var heads = document.querySelectorAll('.wx-head');
    heads.forEach(function (head) {
      if (head.querySelector('.wx-status')) return;
      var light = head.classList.contains('onpage') ||
        /background\s*:\s*#fff/i.test(head.getAttribute('style') || '');
      var status = document.createElement('div');
      status.className = 'wx-status';
      status.innerHTML = '<span>09:41</span><span class="sig">▮▮▮ Wi‑Fi 🔋</span>';
      head.insertBefore(status, head.firstChild);

      var nav = head.querySelector('.wx-nav');
      if (nav && !nav.querySelector('.wx-capsule')) {
        if (nav.hasAttribute('data-back') && !nav.querySelector('.back')) {
          var back = document.createElement('span');
          back.className = 'back';
          back.textContent = '‹';
          nav.insertBefore(back, nav.firstChild);
        }
        var cap = document.createElement('div');
        cap.className = 'wx-capsule';
        cap.innerHTML = '<span class="dot">···</span><span class="sep"></span><span class="dot">◎</span>';
        nav.appendChild(cap);
      }
      if (light) head.classList.add('onpage');
    });
  }

  function buildRail() {
    var rail = document.querySelector('.pt-rail');
    if (!rail) return;
    var links = rail.querySelectorAll('a[href^="#"]');
    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href').slice(1);
        var el = document.getElementById(id);
        if (!el) return;
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
        links.forEach(function (x) { x.classList.remove('active'); });
        a.classList.add('active');
      });
    });
  }

  function tools() {
    // 键盘左右切屏
    var gallery = document.querySelector('.pt-gallery');
    if (!gallery) return;
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var boards = gallery.querySelectorAll('.board');
      if (!boards.length) return;
      var scrollLeft = gallery.scrollLeft;
      var idx = 0, best = Infinity;
      for (var i = 0; i < boards.length; i++) {
        var d = Math.abs(boards[i].offsetLeft - scrollLeft);
        if (d < best) { best = d; idx = i; }
      }
      var next = e.key === 'ArrowRight'
        ? Math.min(idx + 1, boards.length - 1)
        : Math.max(idx - 1, 0);
      boards[next].scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
    });
  }

  function boot() {
    injectSprite();
    buildChrome();
    buildRail();
    tools();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
"""

def main():
    roots = [
        Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序\assets"),
        Path(r"D:\zhitu\prototype\移动端\后台人员微信小程序\assets"),
    ]
    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
        (root / "mp.css").write_text(CSS, encoding="utf-8")
        (root / "mp.js").write_text(JS, encoding="utf-8")
        print("wrote", root, "css", len(CSS), "js", len(JS))

if __name__ == "__main__":
    main()
