# -*- coding: utf-8 -*-
"""Rebuild polished mp.css + mp.js matching original HTML class system."""
from pathlib import Path

CSS = r'''/* 智途 · 微信小程序原型设计系统（精致版）
 * 对齐 01–06 模块 HTML 类名 + 截图视觉
 * data-app="driver" | data-app="admin"
 */
:root {
  --brand: #1d4ed8;
  --brand-deep: #1e3a8a;
  --brand-mid: #2563eb;
  --brand-soft: #dbeafe;
  --brand-tint: #eff6ff;
  --success: #16a34a;
  --success-soft: #dcfce7;
  --warning: #f59e0b;
  --warning-soft: #fef3c7;
  --warning-ink: #92400e;
  --danger: #ef4444;
  --danger-soft: #fee2e2;
  --info: #0ea5e9;
  --info-soft: #e0f2fe;
  --muted: #64748b;
  --t1: #0f172a;
  --t2: #475569;
  --t3: #94a3b8;
  --bg: #e8eef6;
  --page: #f1f4f9;
  --card: #ffffff;
  --line: #e8edf3;
  --r: 14px;
  --r-s: 10px;
  --r-xs: 6px;
  --pill: 999px;
  --shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 6px 16px rgba(15, 23, 42, 0.05);
  --shadow-lg: 0 8px 28px rgba(15, 23, 42, 0.12);
  --font: "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei", sans-serif;
  --mono: "DIN Alternate", "SF Mono", Menlo, Consolas, monospace;
  --dev-w: 375px;
  --dev-h: 812px;
  --status-h: 44px;
  --nav-h: 44px;
}

body[data-app="admin"] {
  --brand: #0052d9;
  --brand-deep: #003cab;
  --brand-mid: #266fe8;
  --brand-soft: #d9e1ff;
  --brand-tint: #f2f3ff;
  --success: #2ba471;
  --success-soft: #e3f9e9;
  --warning: #e37318;
  --warning-soft: #fff1e9;
  --warning-ink: #9a3412;
  --danger: #d54941;
  --danger-soft: #fff0ed;
  --info: #0594fa;
  --info-soft: #ecf6ff;
  --page: #f3f3f3;
  --bg: #e6ebf5;
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
button { font-family: inherit; border: none; background: none; }
code {
  font-family: var(--mono); font-size: 11.5px;
  background: #f1f5f9; padding: 1px 5px; border-radius: 4px; color: var(--t1);
}
em { font-style: normal; color: var(--brand); font-weight: 600; }
b { font-weight: 600; }

/* ========== 文档壳 ========== */
.pt-head {
  background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
  color: #e2e8f0; border-bottom: 1px solid #1f2937;
}
.pt-head-inner { max-width: 1320px; margin: 0 auto; padding: 28px 32px 20px; }
.pt-kicker {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #94a3b8; margin-bottom: 10px;
}
.pt-kicker i {
  width: 8px; height: 8px; border-radius: 50%; background: var(--brand);
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.28);
}
.pt-kicker b { color: #e2e8f0; font-weight: 600; }
.pt-kicker span {
  margin-left: 4px; padding: 1px 8px; border-radius: var(--pill);
  background: #1e293b; color: #94a3b8; font-size: 11px;
}
.pt-title { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
.pt-title h1 {
  margin: 0; font-size: 28px; font-weight: 700; color: #fff; letter-spacing: -0.02em;
}
.badge {
  display: inline-flex; align-items: center; height: 24px;
  padding: 0 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
}
.badge.p0 { background: #14532d; color: #bbf7d0; }
.badge.p1 { background: #7c2d12; color: #fed7aa; }
.badge.p2 { background: #334155; color: #cbd5e1; }
.pt-intent {
  max-width: 860px; margin: 0 0 16px; font-size: 14px; line-height: 1.7; color: #94a3b8;
}
.pt-meta { display: flex; flex-wrap: wrap; gap: 10px 22px; margin: 0 0 16px; padding: 0; }
.pt-meta > div { display: flex; gap: 8px; align-items: baseline; font-size: 12.5px; }
.pt-meta dt { margin: 0; color: #64748b; }
.pt-meta dd { margin: 0; color: #cbd5e1; }
.pt-meta .sep { margin: 0 6px; color: #475569; }
.pt-rail { display: flex; flex-wrap: wrap; gap: 8px; }
.pt-rail a {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 12px; border-radius: 8px;
  background: #1e293b; border: 1px solid #334155;
  font-size: 12.5px; color: #cbd5e1; transition: .15s ease;
}
.pt-rail a:hover, .pt-rail a.active {
  background: var(--brand); border-color: var(--brand); color: #fff;
}
.pt-rail .n { font-size: 10px; font-weight: 700; letter-spacing: .04em; opacity: .7; }
.pt-rail.parallel a { flex-direction: column; align-items: flex-start; gap: 2px; min-width: 118px; }
.pt-body { max-width: 1320px; margin: 0 auto; padding: 28px 32px 64px; }
.pt-group { margin: 8px 0 18px; }
.pt-group-head h2 { margin: 0 0 4px; font-size: 18px; }
.pt-group-head .sub { font-size: 13px; color: var(--t2); }
.pt-gallery {
  display: flex; gap: 28px; overflow-x: auto; align-items: flex-start;
  padding: 4px 4px 24px; scroll-snap-type: x proximity;
}
.pt-rules {
  margin-top: 24px; padding: 18px 20px; background: #fff;
  border-radius: var(--r); border: 1px solid var(--line); box-shadow: var(--shadow);
}
.pt-rules h4 { margin: 0 0 10px; font-size: 14px; }
.pt-rules ul { margin: 0; padding-left: 18px; font-size: 13px; color: var(--t2); line-height: 1.7; }
.pt-rules table { width: 100%; border-collapse: collapse; font-size: 12.5px; color: var(--t2); }
.pt-rules th, .pt-rules td {
  text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top;
}
.pt-rules th { color: var(--t1); font-weight: 600; background: #f8fafc; }
.pt-foot {
  text-align: center; padding: 22px; font-size: 12px; color: var(--t3);
  border-top: 1px solid var(--line);
}

/* ========== 画板 + 手机壳 ========== */
.board { flex: 0 0 auto; width: var(--dev-w); scroll-snap-align: start; }
.board-cap {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px; min-height: 28px;
}
.board-cap .n {
  width: 24px; height: 24px; border-radius: 7px; background: var(--brand); color: #fff;
  font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center;
}
.board-cap h3 { margin: 0; font-size: 13.5px; font-weight: 600; flex: 1; }
.board-cap .tip {
  font-size: 11px; color: var(--t3); padding: 2px 8px; border-radius: var(--pill);
  background: #fff; border: 1px solid var(--line);
}
.dev {
  width: var(--dev-w); height: var(--dev-h);
  background: #0b1220; border-radius: 42px; padding: 12px;
  box-shadow: 0 28px 64px rgba(15, 23, 42, 0.24), 0 0 0 1px rgba(15, 23, 42, 0.12);
  display: flex; flex-direction: column; position: relative; overflow: hidden;
}
.dev.auto { height: auto; min-height: var(--dev-h); }
.dev .wx-head {
  flex-shrink: 0; background: var(--brand); color: #fff;
  border-radius: 30px 30px 0 0; overflow: hidden; position: relative;
}
.dev .wx-head.onpage { background: #fff; color: var(--t1); }

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
  font-size: 24px; line-height: 1; margin-right: 2px; font-weight: 300;
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
.wx-head.onpage .wx-capsule {
  border-color: rgba(0,0,0,.1); background: rgba(0,0,0,.04);
}
.wx-capsule .dot { flex: 1; text-align: center; font-size: 11px; opacity: .9; }
.wx-capsule .sep { width: 1px; height: 14px; background: rgba(255,255,255,.35); }
.wx-head.onpage .wx-capsule .sep { background: rgba(0,0,0,.12); }

.wx-body {
  flex: 1; background: var(--page); overflow: hidden; min-height: 0;
  display: flex; flex-direction: column; position: relative;
}
.wx-body.scroll { overflow-y: auto; -webkit-overflow-scrolling: touch; display: block; }
.wx-body.white { background: #fff; }
.dev.auto .wx-body { overflow: visible; }

.wx-foot {
  flex-shrink: 0; background: #fff;
  border-radius: 0 0 30px 30px; overflow: hidden;
  box-shadow: 0 -4px 16px rgba(15, 23, 42, 0.04);
}

/* ========== 工具类 ========== */
.pad { padding: 12px; }
.pad-b { padding: 0 16px 16px; }
.mt4 { margin-top: 4px; } .mt6 { margin-top: 6px; } .mt8 { margin-top: 8px; }
.mt10 { margin-top: 10px; } .mt12 { margin-top: 12px; } .mt16 { margin-top: 16px; }
.mb0 { margin-bottom: 0; } .mb8 { margin-bottom: 8px; } .mb10 { margin-bottom: 10px; }
.mb12 { margin-bottom: 12px; }
.fx { display: flex; align-items: center; }
.fx.g4 { gap: 4px; } .fx.g6 { gap: 6px; } .fx.g8 { gap: 8px; }
.fx.g10 { gap: 10px; } .fx.g14 { gap: 14px; }
.between { justify-content: space-between; }
.grow { flex: 1; min-width: 0; }
.rel { position: relative; }
.t1 { color: var(--t1); } .t2 { color: var(--t2); } .t3 { color: var(--t3); }
.strong { font-weight: 600; }
.blue { color: var(--brand); }
.green { color: var(--success); }
.red, .err { color: var(--danger); }
.mut { color: var(--t3); }
.dim { opacity: .55; }
.full { width: 100%; }
.ico { width: 16px; height: 16px; fill: currentColor; flex-shrink: 0; }
.ico.arrow { width: 14px; height: 14px; color: var(--t3); }

/* ========== Tag ========== */
.tag {
  display: inline-flex; align-items: center; gap: 3px;
  height: 22px; padding: 0 8px; border-radius: 6px;
  font-size: 11px; font-weight: 600; white-space: nowrap;
  background: #f1f5f9; color: var(--t2);
}
.tag.sm { height: 18px; padding: 0 6px; font-size: 10px; border-radius: 5px; }
.tag.primary { background: var(--brand-soft); color: var(--brand); }
.tag.success { background: var(--success-soft); color: var(--success); }
.tag.warning { background: var(--warning-soft); color: #b45309; }
.tag.danger { background: var(--danger-soft); color: var(--danger); }
.tag.info { background: var(--info-soft); color: #0369a1; }
.tag .ico { width: 11px; height: 11px; }

/* 兼容旧别名 */
.stat { /* banner 内状态胶囊见下 */ }
.chip {
  display: inline-flex; align-items: center; height: 22px;
  padding: 0 8px; border-radius: 6px; font-size: 11px; font-weight: 600;
  background: #f1f5f9; color: var(--t2);
}
.chip.primary { background: var(--brand-soft); color: var(--brand); }
.chip.success { background: var(--success-soft); color: var(--success); }
.chip.warning { background: var(--warning-soft); color: #b45309; }
.chip.danger { background: var(--danger-soft); color: var(--danger); }
.chip.info { background: var(--info-soft); color: #0369a1; }
.chip.muted { background: #f1f5f9; color: var(--t2); }
.chip.on { background: var(--brand-tint); color: var(--brand); border: 1px solid var(--brand-soft); }

/* ========== Button ========== */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  height: 42px; padding: 0 16px; border-radius: 12px;
  font-size: 14px; font-weight: 600; border: none; cursor: default;
  background: var(--brand); color: #fff;
  box-shadow: 0 1px 0 rgba(255,255,255,.12) inset;
}
.btn.block { width: 100%; display: flex; }
.btn.wide { flex: 1; }
.btn.grow { flex: 1; }
.btn.line {
  background: #fff; color: var(--t1); border: 1px solid var(--line);
  box-shadow: none;
}
.btn.ghost {
  background: var(--brand-tint); color: var(--brand); box-shadow: none;
}
.btn.soft { background: var(--brand-tint); color: var(--brand); box-shadow: none; }
.btn.danger { background: #f87171; }
.btn.success { background: var(--success); }
.btn.warn { background: var(--warning); color: #fff; }
.btn.sm {
  height: 30px; padding: 0 12px; font-size: 12.5px; border-radius: 8px;
}
.btn.xs {
  height: 26px; padding: 0 8px; font-size: 12px; border-radius: 7px;
}
.btn.dis, .btn[disabled] { opacity: .42; }

/* ========== Card / cells ========== */
.card {
  background: var(--card); border-radius: var(--r);
  margin: 10px 12px; padding: 14px 14px; box-shadow: var(--shadow);
}
.card.flat { box-shadow: none; border: 1px solid var(--line); }
.card.pull-up { margin-top: -16px; position: relative; z-index: 2; }
.card.tight { padding: 14px 10px 12px; }
.card .hd {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px; font-size: 14px; font-weight: 600;
}
.card .hd::before {
  content: ""; width: 3px; height: 13px; border-radius: 2px; background: var(--brand);
}
.card .hd .more {
  margin-left: auto; font-size: 12px; font-weight: 400; color: var(--t3);
}

.cells {
  background: #fff; border-radius: var(--r); margin: 10px 12px;
  overflow: hidden; box-shadow: var(--shadow);
}
.cells.flush { margin: 0; border-radius: 0; box-shadow: none; }
.cell {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 14px; border-bottom: 1px solid #f1f5f9; min-height: 52px;
}
.cell:last-child { border-bottom: none; }
.cell .k {
  flex: 1; min-width: 0; font-size: 14px; color: var(--t1);
  display: flex; flex-direction: column; gap: 2px;
}
.cell .k .sub, .cell .sub {
  display: block; font-size: 11.5px; color: var(--t3); font-weight: 400; line-height: 1.4;
}
.cell .v { font-size: 13px; color: var(--t2); text-align: right; flex-shrink: 0; }
.cell .caret { color: var(--t3); }
.cell .lead, .lead {
  width: 34px; height: 34px; border-radius: 10px;
  background: var(--brand-tint); color: var(--brand);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.lead.n { background: #f1f5f9; color: var(--t2); }
.lead.o { background: var(--warning-soft); color: #b45309; }
.lead.g { background: var(--success-soft); color: var(--success); }
.lead.i { background: var(--info-soft); color: #0369a1; }

.lnk { font-size: 13px; color: var(--brand); }
.lnk.dim { color: var(--t3); }

/* ========== Hero / Banner ========== */
.dev .hero {
  background: linear-gradient(165deg, var(--brand) 0%, var(--brand-mid) 55%, #3b82f6 100%);
  color: #fff; padding: 6px 0 20px;
}
body[data-app="admin"] .dev .hero {
  background: linear-gradient(165deg, var(--brand) 0%, var(--brand-mid) 55%, #4787f0 100%);
}
.ava {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,.22); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; flex-shrink: 0;
  position: relative;
}
.ava.sm { width: 36px; height: 36px; font-size: 14px; }
.ava.lg { width: 56px; height: 56px; font-size: 20px; }
.ava .pin, .ava i.pin { /* keep pin positioning */ }

.kpis {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
}
.kpis .kpi {
  background: rgba(255,255,255,.16); border-radius: 12px;
  padding: 10px 6px; text-align: center; backdrop-filter: blur(4px);
}
.kpis .kpi .v {
  font-size: 20px; font-weight: 700; font-family: var(--mono); line-height: 1.15;
}
.kpis .kpi .v.sm { font-size: 15px; }
.kpis .kpi .k { font-size: 11px; opacity: .82; margin-top: 3px; }

.kpi-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
  padding: 0 12px; margin: 10px 0;
}
.kpi-grid .kpi {
  background: #fff; border-radius: var(--r); padding: 12px; box-shadow: var(--shadow);
}
.kpi-grid .kpi .k { font-size: 11px; color: var(--t2); }
.kpi-grid .kpi .v {
  font-size: 22px; font-weight: 700; font-family: var(--mono); margin-top: 4px;
}
.kpi-grid .kpi.warn .v { color: var(--warning); }
.kpi-grid .kpi.brand .v { color: var(--brand); }

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
.dev .banner .no {
  margin-left: auto; font-family: var(--mono); font-size: 12px; opacity: .8;
}
.dev .banner .nm {
  margin-top: 11px; font-size: 18.5px; font-weight: 600; letter-spacing: -.01em;
}
.dev .banner .sub {
  display: flex; align-items: center; gap: 6px; margin-top: 5px;
  font-size: 12.5px; opacity: .84;
}
.dev .banner .sub .ico { width: 13px; height: 13px; }
.dev .banner .mini { display: flex; margin-top: 15px; }
.dev .banner .mini > div { flex: 1; min-width: 0; line-height: 1.28; }
.dev .banner .mini .k { font-size: 11px; opacity: .76; }
.dev .banner .mini .v {
  margin-top: 3px; font-family: var(--mono); font-size: 15px; font-weight: 600;
}
.dev .banner .mut { color: inherit; opacity: .5; }

/* ========== Notice ========== */
.dev .notice {
  display: flex; align-items: flex-start; gap: 8px;
  margin: 0; padding: 10px 12px; font-size: 12.5px; line-height: 1.55;
  background: var(--warning-soft); color: var(--warning-ink);
}
.dev .notice .ico { width: 14px; height: 14px; margin-top: 2px; flex-shrink: 0; }
.dev .notice.info { background: var(--brand-tint); color: var(--brand-deep); }
.dev .notice.danger { background: var(--danger-soft); color: #991b1b; }
.dev .notice.warn { background: var(--warning-soft); color: var(--warning-ink); }

/* ========== Quick grid ========== */
.card .grid, .grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px 4px;
}
.card .grid a, .grid a {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  font-size: 11px; color: var(--t2);
}
.ib {
  width: 42px; height: 42px; border-radius: 13px;
  background: var(--brand-tint); color: var(--brand);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.ib .ico { width: 20px; height: 20px; }
.ib.g { background: #e8f8ef; color: #16a34a; }
.ib.o { background: #fff3e8; color: #e37318; }
.ib.i { background: #e8f4ff; color: #0ea5e9; }
.ib.r { background: var(--danger-soft); color: var(--danger); }
.lb { font-size: 11px; color: var(--t2); line-height: 1.25; text-align: center; }

/* ========== Section / Item / Route ========== */
.sec-h {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px 8px; font-size: 14px; font-weight: 600; color: var(--t1);
}
.sec-h .more { font-size: 12px; font-weight: 400; color: var(--brand); }
.sec-t { font-size: 12px; color: var(--t3); font-weight: 400; }

.item {
  background: #fff; border-radius: var(--r); margin: 0 12px 10px;
  padding: 14px; box-shadow: var(--shadow);
}
.item-top {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  margin-bottom: 8px;
}
.item-top .no {
  font-size: 12px; font-family: var(--mono); color: var(--t3);
}
.item-foot {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 10px; font-size: 12px; color: var(--t2);
}
.item-foot .meta { color: var(--t3); }

.route-h {
  display: flex; align-items: center; gap: 8px;
  font-size: 16px; font-weight: 700; letter-spacing: -.01em;
}
.route-h .mid {
  flex: 1; display: flex; align-items: center; justify-content: center;
  position: relative; height: 18px;
}
.route-h .mid::before {
  content: ""; position: absolute; left: 4px; right: 4px; top: 50%;
  height: 1px; background: linear-gradient(90deg, var(--brand-soft), var(--brand), var(--brand-soft));
}
.route-h .km {
  position: relative; z-index: 1;
  font-size: 10px; font-weight: 600; font-family: var(--mono);
  color: var(--brand); background: #fff; padding: 0 6px;
}

.route { display: flex; flex-direction: column; position: relative; }
.route .leg {
  display: flex; gap: 10px; padding: 4px 0 14px; position: relative;
}
.route .leg::before {
  content: ""; width: 10px; height: 10px; border-radius: 50%;
  background: var(--brand); margin-top: 4px; flex-shrink: 0;
  box-shadow: 0 0 0 3px var(--brand-soft);
}
.route .leg.to::before {
  background: var(--danger); border-radius: 2px; box-shadow: 0 0 0 3px var(--danger-soft);
}
.route .leg:not(:last-child)::after {
  content: ""; position: absolute; left: 4px; top: 18px; bottom: 0; width: 2px;
  background: repeating-linear-gradient(180deg, var(--line) 0 3px, transparent 3px 6px);
}
.route .loc { font-size: 14px; font-weight: 600; }
.route .when { font-size: 12px; color: var(--t3); margin-top: 3px; }

/* task alias for generated pages */
.task {
  background: #fff; border-radius: var(--r); margin: 0 12px 10px;
  padding: 14px; box-shadow: var(--shadow);
}
.task .top {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;
}
.task .no { font-size: 12px; font-family: var(--mono); color: var(--t3); }
.task .nm { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
.task .meta {
  display: flex; flex-wrap: wrap; gap: 6px 12px; font-size: 12px; color: var(--t2);
}

/* ========== Search / Tabs / Chips ========== */
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
  height: 2.5px; background: var(--brand); border-radius: 2px;
}
.chips { display: flex; gap: 8px; overflow-x: auto; padding: 10px 12px; flex-wrap: wrap; }
.chips .chip {
  flex: 0 0 auto; height: 28px; padding: 0 12px; border-radius: var(--pill);
  background: #fff; border: 1px solid var(--line); font-weight: 500; color: var(--t2);
}
.chips .chip.on {
  background: var(--brand-tint); border-color: var(--brand-soft); color: var(--brand);
}

/* ========== Upload photos ========== */
.ups {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.ups .add, .ups .ph {
  width: 72px; height: 72px; border-radius: 10px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 2px; position: relative; overflow: hidden;
}
.ups .add {
  background: #f4f6fa; border: 1px dashed #cfd6e0; color: var(--t3); font-size: 11px;
}
.ups .add .ico { width: 20px; height: 20px; color: var(--brand); }
.ups .add .n { font-size: 10px; color: var(--t3); }
.ups .ph {
  background: linear-gradient(145deg, #94a3b8, #64748b); color: #fff;
}
.ups .ph.b { background: linear-gradient(145deg, #789, #4b5563); }
.ups .mk {
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 3px 4px; font-size: 10px; text-align: center;
  background: rgba(15, 23, 42, .45);
}
.photos {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
}
.photos .slot {
  aspect-ratio: 1; border-radius: 10px; background: #f4f6fa;
  border: 1px dashed #cfd6e0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; color: var(--t3); font-size: 11px; gap: 4px;
}
.photos .slot.filled {
  border: none; background: linear-gradient(145deg, #94a3b8, #64748b); color: #fff; font-size: 18px;
}
.photos .slot .add, .photos .slot .plus { font-size: 22px; line-height: 1; color: var(--brand); }

/* ========== Action bar / Tabbar ========== */
.action-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px calc(10px + 16px);
  background: #fff; border-top: 1px solid var(--line);
}
.action-bar .sum {
  flex-shrink: 0; padding-right: 4px; line-height: 1.2;
}
.action-bar .sum .k { font-size: 11px; color: var(--t3); }
.action-bar .sum .v {
  font-size: 16px; font-weight: 700; color: var(--danger); font-family: var(--mono);
}

.tabbar {
  display: flex; padding: 6px 0 18px; background: #fff;
  border-top: 1px solid var(--line);
}
.tabbar .item {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  gap: 2px; font-size: 10px; color: var(--t3); position: relative; padding-top: 2px;
}
.tabbar .item.on { color: var(--brand); font-weight: 600; }
.tabbar .item .ico { width: 22px; height: 22px; }
.tabbar .item .dot {
  position: absolute; top: 0; right: calc(50% - 14px);
  width: 7px; height: 7px; border-radius: 50%; background: var(--danger);
  border: 1.5px solid #fff;
}
.tabbar .item .num {
  position: absolute; top: -3px; right: calc(50% - 20px);
  min-width: 16px; height: 16px; padding: 0 4px; border-radius: 8px;
  background: var(--danger); color: #fff; font-size: 10px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
}

/* ========== Form ========== */
.field { margin-bottom: 14px; }
.field .lab { font-size: 12px; color: var(--t2); margin-bottom: 6px; }
.field .lab .req { color: var(--danger); }
.field .inp {
  height: 40px; border: 1px solid var(--line); border-radius: 10px;
  padding: 0 12px; display: flex; align-items: center; background: #fff; font-size: 14px;
}
.field .inp.ph { color: var(--t3); }
.field .ta, .ta {
  min-height: 84px; border: 1px solid var(--line); border-radius: 10px;
  padding: 10px 12px; background: #f8fafc; font-size: 14px; color: var(--t3); line-height: 1.5;
}

/* ========== Timeline ========== */
.steps { position: relative; padding-left: 18px; }
.steps::before {
  content: ""; position: absolute; left: 5px; top: 6px; bottom: 6px;
  width: 2px; background: var(--line);
}
.steps .s { position: relative; padding-bottom: 14px; }
.steps .s:last-child { padding-bottom: 0; }
.steps .s::before {
  content: ""; position: absolute; left: -16px; top: 4px;
  width: 10px; height: 10px; border-radius: 50%;
  background: #fff; border: 2px solid var(--line); z-index: 1;
}
.steps .s.done::before { border-color: var(--brand); background: var(--brand); }
.steps .s.now::before {
  border-color: var(--brand); background: #fff; box-shadow: 0 0 0 3px var(--brand-soft);
}
.steps .s .t { font-size: 13px; font-weight: 600; }
.steps .s .d { font-size: 11px; color: var(--t3); margin-top: 2px; }
.steps .s:not(.done):not(.now) .t { color: var(--t3); font-weight: 400; }
.steps-h { display: flex; gap: 4px; overflow-x: auto; font-size: 11px; }
.steps-h .s {
  flex: 1; text-align: center; padding: 6px 2px; border-radius: 6px;
  background: #f1f5f9; color: var(--t3); white-space: nowrap;
}
.steps-h .s.done { background: var(--brand-soft); color: var(--brand); }
.steps-h .s.now { background: var(--brand); color: #fff; font-weight: 600; }

/* ========== Map ========== */
.dev .map {
  position: relative; height: 160px; margin: 0 12px 10px; border-radius: var(--r); overflow: hidden;
  background:
    linear-gradient(135deg, rgba(29,78,216,.07), transparent 50%),
    repeating-linear-gradient(0deg, transparent, transparent 18px, #e8edf3 18px, #e8edf3 19px),
    repeating-linear-gradient(90deg, transparent, transparent 18px, #e8edf3 18px, #e8edf3 19px),
    #f8fafc;
}
.dev .map .path { position: absolute; inset: 0; width: 100%; height: 100%; }
.dev .map .path path { fill: none; stroke: var(--brand); stroke-width: 3; stroke-linecap: round; }
.dev .map .path path.plan { stroke: #94a3b8; stroke-dasharray: 4 4; }
.dev .map .dotp {
  position: absolute; width: 12px; height: 12px; border-radius: 50%;
  background: var(--brand); border: 2px solid #fff;
  transform: translate(-50%, -50%); box-shadow: 0 1px 4px rgba(0,0,0,.2);
}
.dev .map .mrk { position: absolute; z-index: 2; transform: translate(-50%, -100%); }
.dev .map .mrk .bub {
  position: relative; display: flex; align-items: center; gap: 4px;
  padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 500;
  white-space: nowrap; color: #fff; background: var(--brand);
  box-shadow: 0 2px 6px rgba(16, 36, 43, 0.24);
}
.dev .map .mrk .bub::after {
  content: ""; position: absolute; bottom: -3px; left: 50%;
  width: 7px; height: 7px; margin-left: -3.5px;
  border-radius: 0 0 2px 0; transform: rotate(45deg); background: inherit;
}
.dev .map .mrk.r .bub { background: var(--danger); }
.dev .map .mrk.g .bub { background: var(--success); }
.dev .map .hint {
  position: absolute; left: 10px; bottom: 10px;
  background: rgba(255,255,255,.94); padding: 4px 8px; border-radius: 6px;
  font-size: 11px; color: var(--t2); box-shadow: var(--shadow);
}

/* ========== Overlay ========== */
.mask {
  position: absolute; inset: 0; background: rgba(15, 23, 42, .48);
  z-index: 20; display: flex; align-items: center; justify-content: center;
}
.mask.bottom { align-items: flex-end; }
.mask.center { align-items: center; justify-content: center; padding: 24px; }
.sheet {
  width: 100%; background: #f4f6fa; border-radius: 18px 18px 0 0;
  padding: 10px 0 24px; box-shadow: var(--shadow-lg);
}
.sheet .handle, .sb .handle {
  width: 36px; height: 4px; background: #d1d5db; border-radius: 2px; margin: 6px auto 10px;
}
.sb { background: #fff; }
.dialog {
  width: 100%; max-width: 300px; background: #fff; border-radius: 16px;
  padding: 22px 18px 16px; text-align: center; box-shadow: var(--shadow-lg);
}
.dialog .t { font-size: 17px; font-weight: 600; margin-bottom: 8px; }
.dialog .d { font-size: 13px; color: var(--t2); line-height: 1.6; margin-bottom: 18px; text-align: left; }
.dialog .af, .dialog .actions { display: flex; gap: 10px; }
.toast {
  position: absolute; left: 50%; top: 42%; transform: translate(-50%, -50%);
  background: rgba(15, 23, 42, .86); color: #fff; padding: 12px 18px;
  border-radius: 10px; font-size: 13px; z-index: 30; text-align: center; max-width: 80%;
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
.wx-auth .ai {
  padding: 12px; background: #f8fafc; border-radius: 10px; margin-bottom: 16px;
  font-size: 18px; font-weight: 600;
}
.wx-auth .af { display: flex; gap: 10px; }

/* ========== Pin ========== */
.pin {
  position: absolute; top: -6px; right: -6px; z-index: 8;
  width: 18px; height: 18px; border-radius: 50%;
  background: #ef4444; color: #fff; font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 1px 3px rgba(16, 36, 43, 0.35); font-style: normal;
}
.pin.tl { top: -4px; left: -4px; right: auto; }
.pin.in { top: 5px; right: 5px; }
.pin.bar { top: -8px; left: 14px; right: auto; }

.ck {
  width: 18px; height: 18px; border-radius: 5px; border: 1.5px solid #cbd5e1;
  display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: #fff; font-size: 11px; color: #fff;
}
.ck.on { background: var(--brand); border-color: var(--brand); }

/* ========== Misc ========== */
.empty { text-align: center; padding: 56px 28px; color: var(--t3); }
.empty .ico { width: 48px; height: 48px; margin: 0 auto 12px; opacity: .4; display: block; }
.empty .t { font-size: 14px; color: var(--t2); margin-bottom: 6px; }
.empty .d { font-size: 12px; line-height: 1.55; }
.end { text-align: center; padding: 16px; font-size: 11px; color: var(--t3); }
.hr { height: 1px; background: #f1f5f9; margin: 10px 0; }
.money { font-weight: 700; font-family: var(--mono); color: #b45309; }
.progress { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; }
.progress .bar { height: 100%; background: var(--brand); border-radius: 3px; }
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
.sk {
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 37%, #e2e8f0 63%);
  background-size: 400% 100%; border-radius: 6px; height: 14px;
  animation: sk 1.4s ease infinite;
}
@keyframes sk { 0% { background-position: 100% 0; } 100% { background-position: 0 0; } }

.l1 {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  font-size: 13px; font-weight: 600; margin-bottom: 4px;
}
.l2 { font-size: 12px; color: var(--t3); }
.kv { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; }
.pg { font-size: 12px; color: var(--t3); }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.wait { color: var(--warning); }
.side { text-align: right; }
.wrap { flex-wrap: wrap; }
.row { display: flex; align-items: center; gap: 8px; }
.box { background: #f8fafc; border-radius: 10px; padding: 12px; }
.go { color: var(--brand); font-weight: 600; }
.main { font-weight: 600; }
.mid { /* used in route-h */ }
.left { text-align: left; }
.db, .df, .dh, .sf, .sw, .tm, .by, .c1, .seg, .del, .refresh { /* rare helpers */ }
.counter { font-family: var(--mono); font-weight: 600; }
.bare { box-shadow: none !important; }
.flush { margin-left: 0 !important; margin-right: 0 !important; border-radius: 0 !important; }

.board > .notes, ol.notes {
  margin: 14px 0 0; padding: 12px 14px 12px 30px;
  background: #fff; border-radius: 12px; border: 1px solid var(--line);
  font-size: 12.5px; color: #475569; line-height: 1.7; box-shadow: var(--shadow);
}
.notes .flag {
  display: inline-block; padding: 0 5px; border-radius: 3px;
  background: #7c2d12; color: #fed7aa; font-size: 10px; font-weight: 700; margin-right: 4px;
}
.notes li { margin-bottom: 6px; }
.notes li:last-child { margin-bottom: 0; }

.quick { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px 6px; padding: 4px 0; }
.quick .q {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  font-size: 11px; color: var(--t2);
}
'''

JS = r'''/* 智途 · 小程序原型 · 铬合金 / 图标 / TabBar / 锚点 */
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

  var TAB_DRIVER = [
    { key: 'home', label: '工作台', icon: 'home' },
    { key: 'task', label: '任务', icon: 'list' },
    { key: 'finance', label: '收入', icon: 'wallet' },
    { key: 'me', label: '我的', icon: 'user' },
    { key: 'profile', label: '我的', icon: 'user' }
  ];
  var TAB_ADMIN = [
    { key: 'home', label: '工作台', icon: 'home' },
    { key: 'dispatch', label: '调度', icon: 'truck' },
    { key: 'approve', label: '审批', icon: 'approve' },
    { key: 'me', label: '我的', icon: 'user' },
    { key: 'profile', label: '我的', icon: 'user' }
  ];

  function injectSprite() {
    if (document.getElementById('mp-sprite')) return;
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.id = 'mp-sprite';
    svg.setAttribute('aria-hidden', 'true');
    svg.style.display = 'none';
    var html = '';
    Object.keys(ICONS).forEach(function (k) {
      html += '<symbol id="i-' + k + '" viewBox="0 0 24 24">' + ICONS[k] + '</symbol>';
    });
    svg.innerHTML = html;
    document.body.insertBefore(svg, document.body.firstChild);
  }

  function buildChrome() {
    document.querySelectorAll('.wx-head').forEach(function (head) {
      if (head.querySelector('.wx-status')) return;
      var style = head.getAttribute('style') || '';
      var light = head.classList.contains('onpage') || /background\s*:\s*#fff/i.test(style);
      var status = document.createElement('div');
      status.className = 'wx-status';
      status.innerHTML = '<span>09:41</span><span class="sig">▮▮▮ Wi‑Fi 🔋</span>';
      head.insertBefore(status, head.firstChild);
      var nav = head.querySelector('.wx-nav');
      if (nav) {
        if (nav.hasAttribute('data-back') && !nav.querySelector('.back')) {
          var back = document.createElement('span');
          back.className = 'back';
          back.textContent = '‹';
          nav.insertBefore(back, nav.firstChild);
        }
        if (!nav.querySelector('.wx-capsule')) {
          var cap = document.createElement('div');
          cap.className = 'wx-capsule';
          cap.innerHTML = '<span class="dot">···</span><span class="sep"></span><span class="dot">◎</span>';
          nav.appendChild(cap);
        }
      }
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
      var defs = isAdmin ? TAB_ADMIN : TAB_DRIVER;
      // unique by key for render (profile/me collapse)
      var seen = {};
      var keys = isAdmin
        ? ['home', 'dispatch', 'approve', 'me']
        : ['home', 'task', 'finance', 'me'];
      var html = '';
      keys.forEach(function (key) {
        var def = defs.filter(function (d) { return d.key === key; })[0];
        if (!def || seen[key]) return;
        seen[key] = true;
        var on = active === key || (key === 'me' && (active === 'profile' || active === 'me')) ? ' on' : '';
        var badge = '';
        var b = badges[key] || (key === 'me' ? badges.me || badges.profile : '') || (key === 'task' ? badges.task : '') || (key === 'approve' ? badges.approve : '');
        if (b === 'dot') badge = '<i class="dot"></i>';
        else if (b) badge = '<i class="num">' + b + '</i>';
        html += '<div class="item' + on + '"><svg class="ico"><use href="#i-' + def.icon + '"></use></svg>' + def.label + badge + '</div>';
      });
      el.innerHTML = html;
      el.setAttribute('data-built', '1');
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
    var gallery = document.querySelector('.pt-gallery');
    if (!gallery) return;
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var boards = gallery.querySelectorAll('.board');
      if (!boards.length) return;
      var scrollLeft = gallery.scrollLeft, idx = 0, best = Infinity;
      for (var i = 0; i < boards.length; i++) {
        var d = Math.abs(boards[i].offsetLeft - scrollLeft);
        if (d < best) { best = d; idx = i; }
      }
      var next = e.key === 'ArrowRight' ? Math.min(idx + 1, boards.length - 1) : Math.max(idx - 1, 0);
      boards[next].scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
    });
  }

  function boot() {
    injectSprite();
    buildChrome();
    buildTabbars();
    buildRail();
    tools();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
'''

def main():
    for root in [
        Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序\assets"),
        Path(r"D:\zhitu\prototype\移动端\后台人员微信小程序\assets"),
    ]:
        root.mkdir(parents=True, exist_ok=True)
        (root / "mp.css").write_text(CSS, encoding="utf-8")
        (root / "mp.js").write_text(JS, encoding="utf-8")
        print("OK", root, "css", len(CSS), "js", len(JS))

if __name__ == "__main__":
    main()
