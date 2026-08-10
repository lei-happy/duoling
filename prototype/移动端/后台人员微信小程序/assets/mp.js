/* 智图 · 后台人员移动端原型运行时（与驾驶员端同源，增加五阶段卡带切换）
   声明式交互：data-push / data-back / data-tab / data-sheet / data-dialog / data-toast /
              data-refresh / data-swipe / data-icon / data-count-to
   动效遵循 ../DESIGN.md：弹簧从当前呈现值起算、1:1 跟手、动量投射、可中断 */
(function () {
  'use strict';

  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 弹簧 ---------- */
  function spring(opt) {
    var to = opt.to, x = opt.from, v = opt.velocity || 0;
    var damping = opt.damping == null ? 1 : opt.damping;
    var response = opt.response || 0.35;
    var k = Math.pow((2 * Math.PI) / response, 2);
    var c = (4 * Math.PI * damping) / response;
    var raf = null, last = null, dead = false;

    if (REDUCED) {
      opt.onUpdate(to, 0);
      opt.onDone && opt.onDone();
      return { stop: function () {}, value: function () { return to; } };
    }
    function frame(t) {
      if (dead) return;
      if (last === null) last = t;
      var dt = Math.min((t - last) / 1000, 1 / 30);
      last = t;
      var n = Math.max(1, Math.ceil(dt / (1 / 240))), h = dt / n;
      for (var i = 0; i < n; i++) {
        v += (-k * (x - to) - c * v) * h;
        x += v * h;
      }
      opt.onUpdate(x, v);
      if (Math.abs(x - to) < 0.12 && Math.abs(v) < 0.8) {
        opt.onUpdate(to, 0);
        opt.onDone && opt.onDone();
        return;
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return {
      stop: function () { dead = true; if (raf) cancelAnimationFrame(raf); },
      value: function () { return x; },
      velocity: function () { return v; }
    };
  }

  /* 动量投射：松手后会滑到哪 */
  function project(v, d) { d = d || 0.998; return (v / 1000) * d / (1 - d); }
  /* 橡皮筋阻尼 */
  function rubber(over, dim) { return (over * dim * 0.55) / (dim + 0.55 * Math.abs(over)); }

  /* 速度采样 */
  function Tracker() {
    var pts = [];
    return {
      add: function (val) {
        pts.push({ v: val, t: performance.now() });
        if (pts.length > 6) pts.shift();
      },
      reset: function () { pts = []; },
      velocity: function () {
        if (pts.length < 2) return 0;
        var a = pts[0], b = pts[pts.length - 1];
        var dt = (b.t - a.t) / 1000;
        return dt > 0.004 ? (b.v - a.v) / dt : 0;
      }
    };
  }

  /* ---------- 图标 ---------- */
  var ICONS = {
    home: 'M3 10.6 12 3.2l9 7.4M5.4 9.4V20.8h13.2V9.4',
    list: 'M8 6h13M8 12h13M8 18h13M3.2 6h.01M3.2 12h.01M3.2 18h.01',
    truck: 'M3 6.5h11.5v10H3zM14.5 9.5H18l3 3v4h-6.5M7.5 19.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM17.5 19.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z',
    wallet: 'M2.8 6.6h18.4v10.8H2.8zM12 14.6a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2ZM6 9.8h.01M18 14.2h.01',
    bell: 'M18 8.5a6 6 0 1 0-12 0c0 7-2.5 8.5-2.5 8.5h17S18 15.5 18 8.5M13.7 21a2 2 0 0 1-3.4 0',
    user: 'M20 21v-1.8a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4V21M12 11.2a4.1 4.1 0 1 0 0-8.2 4.1 4.1 0 0 0 0 8.2Z',
    users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
    right: 'm9 18 6-6-6-6',
    left: 'm15 18-6-6 6-6',
    down: 'm6 9 6 6 6-6',
    up: 'm6 15 6-6 6 6',
    check: 'M20 6 9 17l-5-5',
    checkc: 'M21.8 11.1V12a9.8 9.8 0 1 1-5.8-8.95M22 4.4 12 14.4l-3-3',
    warn: 'm10.3 3.9-8.2 14a2 2 0 0 0 1.7 3h16.4a2 2 0 0 0 1.7-3l-8.2-14a2 2 0 0 0-3.4 0ZM12 9.2v4M12 17.1h.01',
    clock: 'M12 21.8a9.8 9.8 0 1 0 0-19.6 9.8 9.8 0 0 0 0 19.6ZM12 6.4V12l3.8 2.2',
    camera: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.6a2 2 0 0 1 2-2h3l1.8-2.8h6.4L17 6.6h3a2 2 0 0 1 2 2zM12 17.2a3.9 3.9 0 1 0 0-7.8 3.9 3.9 0 0 0 0 7.8Z',
    pin: 'M20.5 10.2c0 6.6-8.5 12.3-8.5 12.3s-8.5-5.7-8.5-12.3a8.5 8.5 0 0 1 17 0ZM12 13.1a2.9 2.9 0 1 0 0-5.8 2.9 2.9 0 0 0 0 5.8Z',
    nav: 'm3 11 18.5-8.6L13 21l-2-8-8-2Z',
    map: 'M2.6 6.6 9 3.4v14l-6.4 3.2zM9 3.4l6 3.2v14l-6-3.2zM15 6.6l6.4-3.2v14L15 20.6z',
    phone: 'M21.9 16.9v2.9a2 2 0 0 1-2.2 2 19.6 19.6 0 0 1-8.5-3 19.3 19.3 0 0 1-6-6 19.6 19.6 0 0 1-3-8.6 2 2 0 0 1 2-2.2h2.9a2 2 0 0 1 2 1.7c.13.95.36 1.88.7 2.77a2 2 0 0 1-.45 2.1L8.1 9.9a15.9 15.9 0 0 0 6 6l1.25-1.25a2 2 0 0 1 2.1-.45c.9.34 1.82.57 2.77.7a2 2 0 0 1 1.7 2Z',
    file: 'M14 2.5H6.5a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8zM14 2.5v6h5.5M8.5 13.5h7M8.5 17.2h4.5',
    search: 'M11 18.6a7.8 7.8 0 1 0 0-15.6 7.8 7.8 0 0 0 0 15.6ZM21 21l-4.4-4.4',
    filter: 'M21.5 3.5h-19L10 12.8V19l4 2v-8.2z',
    plus: 'M12 5.2v13.6M5.2 12h13.6',
    x: 'M18 6 6 18M6 6l12 12',
    refresh: 'M20.9 12a8.9 8.9 0 1 1-3-6.6M20.9 3.4v6h-6',
    upload: 'M20.8 15.2v4a2 2 0 0 1-2 2H5.2a2 2 0 0 1-2-2v-4M16.6 7.8 12 3.2 7.4 7.8M12 3.2v13',
    image: 'M3.2 5.4a2 2 0 0 1 2-2h13.6a2 2 0 0 1 2 2V19a2 2 0 0 1-2 2H5.2a2 2 0 0 1-2-2zM8.6 10.4a1.6 1.6 0 1 0 0-3.2 1.6 1.6 0 0 0 0 3.2ZM20.8 15.4 16 10.6 5.2 21',
    chart: 'M3.4 20.8V10.4M9.1 20.8V3.2M14.9 20.8v-7.2M20.6 20.8V6.6',
    trend: 'm21.5 7-8.4 8.4-4.6-4.6-6.5 6.5M16.2 7h5.3v5.3',
    gauge: 'M12 14.1a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM13.4 10.7 18.6 5.5M20.4 17.3a9.4 9.4 0 1 0-16.8 0',
    settings: 'M4 20.8v-6.4M4 10.6V3.2M12 20.8v-8.2M12 8.8V3.2M20 20.8v-4.6M20 12.4V3.2M1.4 14.4h5.2M9.4 8.8h5.2M17.4 16.2h5.2',
    dots: 'M5.2 12h.01M12 12h.01M18.8 12h.01',
    shield: 'M12 21.8s7.8-3.9 7.8-9.8V5.1L12 2.2 4.2 5.1V12c0 5.9 7.8 9.8 7.8 9.8Z',
    shieldok: 'M12 21.8s7.8-3.9 7.8-9.8V5.1L12 2.2 4.2 5.1V12c0 5.9 7.8 9.8 7.8 9.8ZM9 11.8l2.1 2.1 4.1-4.1',
    calendar: 'M3.4 6.4a2 2 0 0 1 2-2h13.2a2 2 0 0 1 2 2v13.2a2 2 0 0 1-2 2H5.4a2 2 0 0 1-2-2zM16.2 2.4v4M7.8 2.4v4M3.4 10.4h17.2',
    fuel: 'M3 21.6h12M4 9.4h10M14 21.6V4.4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v17.2M14 13h2a2 2 0 0 1 2 2v1.8a2 2 0 0 0 4 0V9.9a2 2 0 0 0-.6-1.4L18 5',
    card: 'M2.4 8.2a2 2 0 0 1 2-2h15.2a2 2 0 0 1 2 2v8.6a2 2 0 0 1-2 2H4.4a2 2 0 0 1-2-2zM2.4 11h19.2M6 15.2h3.2',
    msg: 'M20.8 15a2 2 0 0 1-2 2H8l-4.8 3.8V5.2a2 2 0 0 1 2-2h13.6a2 2 0 0 1 2 2z',
    box: 'm21 8.2-9-5-9 5 9 5 9-5ZM3 8.2v7.6l9 5 9-5V8.2M12 13.2v8',
    route: 'M6 21a2.9 2.9 0 1 0 0-5.8A2.9 2.9 0 0 0 6 21ZM18 8.8a2.9 2.9 0 1 0 0-5.8 2.9 2.9 0 0 0 0 5.8ZM9 18h5.9a3 3 0 1 0 0-6H9.1a3 3 0 1 1 0-6H12',
    arrowr: 'M4.4 12h15.2M13 5.4l6.6 6.6-6.6 6.6',
    arrowl: 'M19.6 12H4.4M11 18.6 4.4 12 11 5.4',
    eye: 'M2.2 12S6 5.4 12 5.4 21.8 12 21.8 12 18 18.6 12 18.6 2.2 12 2.2 12ZM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    lock: 'M5.2 11.4a2 2 0 0 1 2-2h9.6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H7.2a2 2 0 0 1-2-2zM8.4 9.4V6.2a3.6 3.6 0 1 1 7.2 0v3.2',
    edit: 'M11 4.4H5.4a2 2 0 0 0-2 2v12.2a2 2 0 0 0 2 2h12.2a2 2 0 0 0 2-2V13M18.4 2.6a2.1 2.1 0 0 1 3 3L12 15l-4 1 1-4Z',
    trash: 'M3.4 6.2h17.2M8.4 6.2V4.4a1 1 0 0 1 1-1h5.2a1 1 0 0 1 1 1v1.8M18.6 6.2v13.4a2 2 0 0 1-2 2H7.4a2 2 0 0 1-2-2V6.2M10.2 11v6M13.8 11v6',
    download: 'M20.8 15.2v4a2 2 0 0 1-2 2H5.2a2 2 0 0 1-2-2v-4M7.4 11.4 12 16l4.6-4.6M12 16V3.2',
    mic: 'M12 14.8a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5.8a3 3 0 0 0 3 3ZM18.6 10.4v1.4a6.6 6.6 0 0 1-13.2 0v-1.4M12 18.4v3.2M8.6 21.6h6.8',
    send: 'm21.6 2.4-7 19.2-3.9-8.6-8.6-3.9Z',
    swap: 'M8 3.2 3.8 7.4 8 11.6M3.8 7.4h16.4M16 12.4l4.2 4.2-4.2 4.2M20.2 16.6H3.8',
    info: 'M12 21.8a9.8 9.8 0 1 0 0-19.6 9.8 9.8 0 0 0 0 19.6ZM12 16.4v-4.8M12 7.8h.01',
    building: 'M4.4 21V4.4a2 2 0 0 1 2-2h7.2a2 2 0 0 1 2 2V21M3.4 21h17.2M15.6 9.4h2a2 2 0 0 1 2 2V21M8.4 7h3M8.4 11h3M8.4 15h3',
    warehouse: 'M2.4 20.6h19.2M4.4 20.6V8.8L12 3.4l7.6 5.4v11.8M9.2 20.6v-6.2h5.6v6.2',
    star: 'm12 2.8 2.9 5.9 6.5.95-4.7 4.6 1.1 6.5L12 17.7l-5.8 3.05 1.1-6.5-4.7-4.6 6.5-.95z',
    qr: 'M3.4 3.4h6.2v6.2H3.4zM14.4 3.4h6.2v6.2h-6.2zM3.4 14.4h6.2v6.2H3.4zM14.4 14.4h2.8M20.6 14.4v2.8M17.2 17.8v2.8h3.4',
    sign: 'M3 17.5c4.2-9.5 6.3-12.5 8-12.5 2.5 0 1 8.5 3 8.5 1.3 0 2.4-1.8 3.4-1.8 1.1 0 1.8 1.3 3.6 1.3M3 21h18',
    wrench: 'M14.2 6.6a4.8 4.8 0 0 0 6.3 6.3l-8.6 8.6a2.4 2.4 0 0 1-3.4-3.4zM17.6 3.2l3.2 3.2M14.2 6.6 5.6 15.2',
    play: 'M6.5 4.6 19 12 6.5 19.4z',
    pause: 'M8.5 4.5h3v15h-3zM12.5 4.5h3v15h-3z',
    minus: 'M5.2 12h13.6',
    grid: 'M3.4 3.4h7v7h-7zM13.6 3.4h7v7h-7zM3.4 13.6h7v7h-7zM13.6 13.6h7v7h-7z',
    logout: 'M9.4 21H5.4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 16.6l4.6-4.6L16 7.4M20.6 12H9.4'
  };
  var FILLED = { play: 1, star: 1 };

  function svg(name, cls) {
    var d = ICONS[name];
    if (!d) return '';
    var fill = FILLED[name] ? 'currentColor' : 'none';
    return '<svg viewBox="0 0 24 24" fill="' + fill + '" stroke="currentColor" stroke-width="1.75" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' + (cls ? ' class="' + cls + '"' : '') +
      '><path d="' + d + '"/></svg>';
  }

  function paintIcons(root) {
    (root || document).querySelectorAll('[data-icon]').forEach(function (el) {
      if (el.dataset.iconDone) return;
      el.innerHTML = svg(el.dataset.icon);
      el.dataset.iconDone = '1';
    });
  }

  /* ---------- 微信 chrome ---------- */
  function buildChrome(mp) {
    var status = mp.querySelector('.mp__status');
    if (status && !status.children.length) {
      status.innerHTML =
        '<span>9:41</span><i class="mp__island"></i>' +
        '<span class="mp__sigs">' +
        '<svg width="18" height="12" viewBox="0 0 18 12" fill="currentColor"><rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5.5" width="3" height="6.5" rx="1"/><rect x="10" y="3" width="3" height="9" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1" opacity=".3"/></svg>' +
        '<svg width="16" height="12" viewBox="0 0 16 12" fill="currentColor"><path d="M8 11.2 6.1 9.3a2.7 2.7 0 0 1 3.8 0zM3.6 6.8 2.1 5.3a8.4 8.4 0 0 1 11.8 0l-1.5 1.5a6.3 6.3 0 0 0-8.8 0z"/></svg>' +
        '<svg width="26" height="12" viewBox="0 0 26 12" fill="none"><rect x=".6" y=".6" width="21" height="10.8" rx="3" stroke="currentColor" stroke-opacity=".4"/><rect x="2.2" y="2.2" width="15" height="7.6" rx="1.8" fill="currentColor"/><path d="M23.4 4.2v3.6a2 2 0 0 0 0-3.6" fill="currentColor" fill-opacity=".4"/></svg>' +
        '</span>';
    }
    var nav = mp.querySelector('.mp__nav');
    if (nav && !nav.querySelector('.mp__capsule')) {
      var back = document.createElement('button');
      back.className = 'mp__back';
      back.type = 'button';
      back.setAttribute('aria-label', '返回');
      back.innerHTML = svg('left');
      back.dataset.back = '';
      var title = nav.querySelector('.mp__nav-title');
      if (!title) {
        title = document.createElement('div');
        title.className = 'mp__nav-title';
        nav.appendChild(title);
      }
      nav.insertBefore(back, nav.firstChild);
      nav.appendChild(capsule());
    }
    /* 沉浸式页面（隐藏导航栏）时胶囊按钮依然常驻，禁触区不可被内容侵入 */
    if (!mp.querySelector('.mp__capsule--float')) {
      var f = capsule();
      f.classList.add('mp__capsule--float');
      mp.appendChild(f);
    }
  }

  function capsule() {
    var cap = document.createElement('div');
    cap.className = 'mp__capsule';
    cap.setAttribute('aria-hidden', 'true');
    cap.innerHTML =
      '<svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>' +
      '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="3.1" fill="currentColor" stroke="none"/></svg>';
    return cap;
  }

  /* ---------- App ---------- */
  function App(mp) {
    this.mp = mp;
    this.body = mp.querySelector('.mp__body');
    this.nav = mp.querySelector('.mp__nav');
    this.navTitle = mp.querySelector('.mp__nav-title');
    this.tabbar = mp.querySelector('.mp__tab');
    this.screens = {};
    this.stack = [];
    var self = this;
    mp.querySelectorAll('.screen[data-screen]').forEach(function (s) {
      self.screens[s.dataset.screen] = s;
      if (!s.querySelector('.screen__dim')) {
        var d = document.createElement('div');
        d.className = 'screen__dim';
        s.appendChild(d);
      }
    });
    this.scrim = mp.querySelector('.scrim');
    if (!this.scrim) {
      this.scrim = document.createElement('div');
      this.scrim.className = 'scrim';
      mp.appendChild(this.scrim);
    }
    this.toastEl = document.createElement('div');
    this.toastEl.className = 'toast';
    mp.appendChild(this.toastEl);
    this.openLayer = null;
  }

  App.prototype.root = function (id) {
    var s = this.screens[id];
    if (!s) return;
    this.stack.forEach(function (x) { x.classList.remove('is-active', 'is-stacked'); x.style.transform = ''; });
    this.stack = [s];
    s.classList.add('is-active');
    s.classList.remove('is-stacked');
    s.style.transform = '';
    this.sync();
  };

  App.prototype.push = function (id) {
    var next = this.screens[id];
    var cur = this.stack[this.stack.length - 1];
    if (!next || next === cur) return;
    if (this.anim) this.anim.stop();
    var w = this.body.clientWidth;
    next.classList.add('is-active', 'is-stacked');
    this.stack.push(next);
    this.sync();
    var dim = cur.querySelector('.screen__dim');
    var self = this;
    this.anim = spring({
      from: 1, to: 0, damping: 1, response: 0.38,
      onUpdate: function (p) {
        next.style.transform = 'translate3d(' + (p * w) + 'px,0,0)';
        cur.style.transform = 'translate3d(' + (-p * w * 0.3) + 'px,0,0)';
        if (dim) dim.style.opacity = (1 - p) * 0.14;
      },
      onDone: function () { self.anim = null; }
    });
  };

  App.prototype.pop = function () {
    if (this.stack.length < 2) return;
    if (this.anim) this.anim.stop();
    var w = this.body.clientWidth;
    var cur = this.stack.pop();
    var prev = this.stack[this.stack.length - 1];
    var dim = prev.querySelector('.screen__dim');
    var self = this;
    this.sync();
    this.anim = spring({
      from: 0, to: 1, damping: 1, response: 0.36,
      onUpdate: function (p) {
        cur.style.transform = 'translate3d(' + (p * w) + 'px,0,0)';
        prev.style.transform = 'translate3d(' + (-(1 - p) * w * 0.3) + 'px,0,0)';
        if (dim) dim.style.opacity = (1 - p) * 0.14;
      },
      onDone: function () {
        cur.classList.remove('is-active', 'is-stacked');
        cur.style.transform = '';
        prev.style.transform = '';
        if (dim) dim.style.opacity = 0;
        self.anim = null;
      }
    });
  };

  App.prototype.tab = function (id) {
    var next = this.screens[id];
    var cur = this.stack[this.stack.length - 1];
    if (!next) return;
    if (next === cur && this.stack.length === 1) return;
    this.stack.forEach(function (x) { x.classList.remove('is-active', 'is-stacked'); x.style.transform = ''; });
    this.stack = [next];
    next.classList.add('is-active');
    next.style.transform = '';
    if (!REDUCED) {
      next.animate([{ opacity: 0, transform: 'scale(.994)' }, { opacity: 1, transform: 'none' }],
        { duration: 200, easing: 'cubic-bezier(.32,.72,0,1)' });
    }
    this.sync();
    countUp(next);
  };

  App.prototype.sync = function () {
    var cur = this.stack[this.stack.length - 1];
    if (!cur) return;
    var depth = this.stack.length - 1;
    this.mp.dataset.depth = depth;
    /* 沉浸式：状态栏文字反白 + 顶部底色与页面头图同色，消除色差断层 */
    this.mp.classList.toggle('is-status-light', cur.dataset.statusLight === '1');
    this.mp.style.background = cur.dataset.mpbg || '';
    if (this.navTitle) this.navTitle.textContent = cur.dataset.nav || cur.dataset.title || '';
    var navHidden = cur.dataset.navHide === '1';
    if (this.nav) this.nav.style.display = navHidden ? 'none' : '';
    var fcap = this.mp.querySelector('.mp__capsule--float');
    if (fcap) fcap.style.display = navHidden ? 'flex' : 'none';
    var isTabRoot = cur.dataset.tabroot != null && depth === 0;
    if (this.tabbar) {
      this.tabbar.style.display = isTabRoot ? '' : 'none';
      this.tabbar.querySelectorAll('[data-tab]').forEach(function (b) {
        b.setAttribute('aria-selected', b.dataset.tab === cur.dataset.screen ? 'true' : 'false');
      });
    }
    var chips = document.querySelectorAll('.schip');
    chips.forEach(function (c) {
      c.setAttribute('aria-current', c.dataset.go === cur.dataset.screen ? 'true' : 'false');
    });
    layoutSegs(cur);
  };

  /* 弹层 */
  App.prototype.openSheet = function (id) {
    var el = this.mp.querySelector('.sheet[data-sheet-id="' + id + '"]');
    if (!el) return;
    this.closeLayer(true);
    this.openLayer = el;
    el.classList.add('is-open');
    this.scrim.classList.add('is-on');
    var h = el.offsetHeight;
    if (this.lay) this.lay.stop();
    this.lay = spring({
      from: h, to: 0, damping: 0.85, response: 0.34,
      onUpdate: function (y) { el.style.transform = 'translate3d(0,' + Math.max(0, y) + 'px,0)'; }
    });
  };
  App.prototype.openDialog = function (id) {
    var el = this.mp.querySelector('[data-dialog-id="' + id + '"]');
    if (!el) return;
    this.closeLayer(true);
    this.openLayer = el;
    el.classList.add('is-open');
    this.scrim.classList.add('is-on');
    if (el.classList.contains('asheet')) {
      var h = el.offsetHeight;
      if (this.lay) this.lay.stop();
      this.lay = spring({
        from: h + 20, to: 0, damping: 0.85, response: 0.34,
        onUpdate: function (y) { el.style.transform = 'translate3d(0,' + Math.max(0, y) + 'px,0)'; }
      });
    } else {
      el.style.opacity = 1;
      if (!REDUCED) {
        el.animate([
          { opacity: 0, transform: 'translate(-50%,-50%) scale(.9)' },
          { opacity: 1, transform: 'translate(-50%,-50%) scale(1)' }
        ], { duration: 240, easing: 'cubic-bezier(.32,.72,0,1)' });
      }
      el.style.transform = 'translate(-50%,-50%) scale(1)';
    }
  };
  App.prototype.closeLayer = function (instant) {
    var el = this.openLayer;
    if (!el) return;
    this.openLayer = null;
    this.scrim.classList.remove('is-on');
    var done = function () {
      el.classList.remove('is-open');
      el.style.transform = '';
      el.style.opacity = '';
    };
    if (instant || REDUCED) { done(); return; }
    if (el.classList.contains('sheet') || el.classList.contains('asheet')) {
      var h = el.offsetHeight + 24;
      var cur = currentY(el);
      if (this.lay) this.lay.stop();
      this.lay = spring({ from: cur, to: h, damping: 1, response: 0.3, onUpdate: function (y) { el.style.transform = 'translate3d(0,' + y + 'px,0)'; }, onDone: done });
    } else {
      el.animate([{ opacity: 1, transform: 'translate(-50%,-50%) scale(1)' }, { opacity: 0, transform: 'translate(-50%,-50%) scale(.94)' }],
        { duration: 170, easing: 'ease-in' }).onfinish = done;
    }
  };
  App.prototype.toast = function (msg, icon) {
    var el = this.toastEl;
    el.className = 'toast' + (icon ? '' : ' is-plain');
    el.innerHTML = (icon ? svg(icon === 'warn' ? 'warn' : 'checkc') : '') + '<div>' + msg + '</div>';
    el.style.visibility = 'visible';
    clearTimeout(this._tt);
    if (REDUCED) { el.style.opacity = 1; el.style.transform = 'translate(-50%,-50%) scale(1)'; }
    else {
      el.style.opacity = 1;
      el.style.transform = 'translate(-50%,-50%) scale(1)';
      el.animate([{ opacity: 0, transform: 'translate(-50%,-50%) scale(.92)' }, { opacity: 1, transform: 'translate(-50%,-50%) scale(1)' }],
        { duration: 200, easing: 'cubic-bezier(.32,.72,0,1)' });
    }
    this._tt = setTimeout(function () {
      var a = el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 200 });
      a.onfinish = function () { el.style.opacity = 0; el.style.visibility = 'hidden'; };
    }, 1600);
  };

  function currentY(el) {
    var m = new DOMMatrixReadOnly(getComputedStyle(el).transform === 'none' ? '' : getComputedStyle(el).transform);
    return m.m42 || 0;
  }

  /* ---------- 分段器指示块 ---------- */
  function layoutSegs(root) {
    (root || document).querySelectorAll('.seg').forEach(function (seg) {
      var thumb = seg.querySelector('.seg__thumb');
      if (!thumb) {
        thumb = document.createElement('i');
        thumb.className = 'seg__thumb';
        seg.insertBefore(thumb, seg.firstChild);
      }
      var on = seg.querySelector('[aria-selected="true"]') || seg.querySelector('button:not(.seg__thumb)');
      if (!on) return;
      thumb.style.left = on.offsetLeft + 'px';
      thumb.style.width = on.offsetWidth + 'px';
    });
  }
  function moveSeg(seg, btn) {
    var thumb = seg.querySelector('.seg__thumb');
    seg.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-selected', b === btn ? 'true' : 'false'); });
    if (!thumb) return;
    var from = parseFloat(thumb.style.left) || 0;
    spring({
      from: from, to: btn.offsetLeft, damping: 1, response: 0.3,
      onUpdate: function (x) { thumb.style.left = x + 'px'; }
    });
    thumb.style.width = btn.offsetWidth + 'px';
  }

  /* ---------- 批量选择计数 ---------- */
  function syncPick(scope) {
    if (!scope) return;
    var n = scope.querySelectorAll('[role="checkbox"][aria-checked="true"]').length;
    scope.querySelectorAll('[data-pick-count]').forEach(function (el) { el.textContent = n; });
    scope.querySelectorAll('[data-pick-disable]').forEach(function (el) { el.disabled = n === 0; });
  }

  /* ---------- 数字滚动 ---------- */
  function countUp(root) {
    (root || document).querySelectorAll('[data-count-to]').forEach(function (el) {
      var to = parseFloat(el.dataset.countTo);
      var dec = (el.dataset.countDec | 0);
      if (isNaN(to)) return;
      if (REDUCED) { el.textContent = to.toFixed(dec); return; }
      var t0 = performance.now(), dur = 780;
      function f(t) {
        var p = Math.min(1, (t - t0) / dur);
        var e = 1 - Math.pow(1 - p, 3);
        el.textContent = (to * e).toFixed(dec).replace(/\B(?=(\d{3})+(?!\d))/g, el.dataset.countSep === '1' ? ',' : '');
        if (p < 1) requestAnimationFrame(f);
      }
      requestAnimationFrame(f);
    });
  }

  /* ---------- 手势：sheet 下拉关闭 ---------- */
  function bindSheetDrag(app, sheet) {
    var grab = sheet.querySelector('.sheet__grab');
    if (!grab) return;
    var startY = 0, y0 = 0, tr = Tracker(), active = false;
    grab.addEventListener('pointerdown', function (e) {
      active = true;
      grab.setPointerCapture(e.pointerId);
      if (app.lay) app.lay.stop();
      startY = e.clientY;
      y0 = currentY(sheet);
      tr.reset(); tr.add(e.clientY);
    });
    grab.addEventListener('pointermove', function (e) {
      if (!active) return;
      var dy = e.clientY - startY + y0;
      if (dy < 0) dy = -rubber(-dy, sheet.offsetHeight);
      sheet.style.transform = 'translate3d(0,' + dy + 'px,0)';
      tr.add(e.clientY);
    });
    function end(e) {
      if (!active) return;
      active = false;
      var v = tr.velocity();
      var y = currentY(sheet);
      var landing = y + project(v);
      if (landing > sheet.offsetHeight * 0.32 || v > 700) {
        app.closeLayer();
      } else {
        if (app.lay) app.lay.stop();
        app.lay = spring({
          from: y, to: 0, velocity: v, damping: 0.85, response: 0.32,
          onUpdate: function (yy) { sheet.style.transform = 'translate3d(0,' + yy + 'px,0)'; }
        });
      }
    }
    grab.addEventListener('pointerup', end);
    grab.addEventListener('pointercancel', end);
  }

  /* ---------- 手势：左边缘返回 ---------- */
  function bindEdgeBack(app) {
    var body = app.body;
    var active = false, startX = 0, tr = Tracker(), w = 0, cur, prev, dim;
    body.addEventListener('pointerdown', function (e) {
      if (app.stack.length < 2) return;
      var r = body.getBoundingClientRect();
      if (e.clientX - r.left > 26) return;
      active = true; w = body.clientWidth; startX = e.clientX;
      cur = app.stack[app.stack.length - 1];
      prev = app.stack[app.stack.length - 2];
      dim = prev.querySelector('.screen__dim');
      if (app.anim) app.anim.stop();
      tr.reset(); tr.add(e.clientX);
      body.setPointerCapture(e.pointerId);
    });
    body.addEventListener('pointermove', function (e) {
      if (!active) return;
      var dx = Math.max(0, e.clientX - startX);
      if (dx > w) dx = w;
      var p = dx / w;
      cur.style.transform = 'translate3d(' + dx + 'px,0,0)';
      prev.style.transform = 'translate3d(' + (-(1 - p) * w * 0.3) + 'px,0,0)';
      if (dim) dim.style.opacity = (1 - p) * 0.14;
      tr.add(e.clientX);
    });
    function end() {
      if (!active) return;
      active = false;
      var v = tr.velocity();
      var x = parseFloat((cur.style.transform.match(/translate3d\((-?[\d.]+)px/) || [0, 0])[1]) || 0;
      var landing = x + project(v);
      var back = landing > w * 0.4 || v > 500;
      var _cur = cur, _prev = prev, _dim = dim;
      if (back) { app.stack.pop(); app.sync(); }
      app.anim = spring({
        from: x, to: back ? w : 0, velocity: v, damping: 1, response: 0.32,
        onUpdate: function (xx) {
          var p = xx / w;
          _cur.style.transform = 'translate3d(' + xx + 'px,0,0)';
          _prev.style.transform = 'translate3d(' + (-(1 - p) * w * 0.3) + 'px,0,0)';
          if (_dim) _dim.style.opacity = (1 - p) * 0.14;
        },
        onDone: function () {
          if (!back) return;
          _cur.classList.remove('is-active', 'is-stacked');
          _cur.style.transform = '';
          _prev.style.transform = '';
          if (_dim) _dim.style.opacity = 0;
        }
      });
    }
    body.addEventListener('pointerup', end);
    body.addEventListener('pointercancel', end);
  }

  /* ---------- 手势：下拉刷新 ---------- */
  function bindRefresh(app, sc) {
    var ref = document.createElement('div');
    ref.className = 'refresher';
    ref.innerHTML = svg('refresh') + '<span>下拉可刷新</span>';
    sc.parentNode.insertBefore(ref, sc);
    var label = ref.querySelector('span');
    var active = false, startY = 0, dy = 0, tr = Tracker(), busy = false;

    sc.addEventListener('pointerdown', function (e) {
      if (busy || sc.scrollTop > 0 || e.pointerType === 'mouse' && e.button !== 0) return;
      active = true; startY = e.clientY; dy = 0; tr.reset(); tr.add(e.clientY);
    });
    sc.addEventListener('pointermove', function (e) {
      if (!active) return;
      var raw = e.clientY - startY;
      if (raw <= 0 || sc.scrollTop > 0) { if (dy === 0) active = false; return; }
      dy = rubber(raw, 320);
      sc.style.transform = 'translate3d(0,' + dy + 'px,0)';
      ref.style.opacity = Math.min(1, dy / 40);
      ref.style.transform = 'translate3d(0,' + Math.min(dy - 10, 30) + 'px,0)';
      label.textContent = dy > 58 ? '松开立即刷新' : '下拉可刷新';
      tr.add(e.clientY);
    });
    function end() {
      if (!active) return;
      active = false;
      var v = tr.velocity();
      if (dy > 58 && !busy) {
        busy = true;
        ref.classList.add('is-spin');
        label.textContent = '正在刷新，请稍候…';
        spring({ from: dy, to: 56, velocity: v, damping: 1, response: 0.3, onUpdate: set });
        setTimeout(function () {
          busy = false;
          ref.classList.remove('is-spin');
          spring({ from: 56, to: 0, damping: 1, response: 0.34, onUpdate: set, onDone: function () { ref.style.opacity = 0; } });
          app.toast('已更新到最新');
        }, 1100);
      } else {
        spring({ from: dy, to: 0, velocity: v, damping: 1, response: 0.32, onUpdate: set, onDone: function () { ref.style.opacity = 0; } });
      }
      dy = 0;
      function set(y) {
        sc.style.transform = 'translate3d(0,' + y + 'px,0)';
        ref.style.transform = 'translate3d(0,' + Math.min(y - 10, 30) + 'px,0)';
        if (!busy) ref.style.opacity = Math.min(1, y / 40);
      }
    }
    sc.addEventListener('pointerup', end);
    sc.addEventListener('pointercancel', end);
  }

  /* ---------- 手势：列表左滑 ---------- */
  function bindSwipe(row) {
    var body = row.querySelector('.swipe__body');
    var acts = row.querySelector('.swipe__acts');
    if (!body || !acts) return;
    var max = 0, x = 0, startX = 0, startY = 0, dragging = false, decided = false, tr = Tracker(), anim = null;

    body.addEventListener('pointerdown', function (e) {
      max = acts.offsetWidth;
      dragging = true; decided = false;
      startX = e.clientX; startY = e.clientY;
      if (anim) anim.stop();
      tr.reset(); tr.add(e.clientX);
    });
    body.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX, dy = e.clientY - startY;
      if (!decided) {
        if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return;
        if (Math.abs(dy) > Math.abs(dx)) { dragging = false; return; }
        decided = true;
        body.setPointerCapture(e.pointerId);
      }
      var nx = x + dx;
      if (nx > 0) nx = rubber(nx, 200);
      if (nx < -max) nx = -max - rubber(-max - nx, 200);
      body.style.transform = 'translate3d(' + nx + 'px,0,0)';
      tr.add(e.clientX);
      e.preventDefault();
    });
    function end() {
      if (!dragging) return;
      dragging = false;
      if (!decided) return;
      var nx = parseFloat((body.style.transform.match(/translate3d\((-?[\d.]+)px/) || [0, 0])[1]) || 0;
      var v = tr.velocity();
      var landing = nx + project(v, 0.99);
      var to = landing < -max * 0.45 ? -max : 0;
      x = to;
      anim = spring({
        from: nx, to: to, velocity: v, damping: 0.85, response: 0.3,
        onUpdate: function (v2) { body.style.transform = 'translate3d(' + v2 + 'px,0,0)'; }
      });
    }
    body.addEventListener('pointerup', end);
    body.addEventListener('pointercancel', end);
    row.addEventListener('mp:reset', function () {
      if (anim) anim.stop();
      var nx = parseFloat((body.style.transform.match(/translate3d\((-?[\d.]+)px/) || [0, 0])[1]) || 0;
      x = 0;
      anim = spring({ from: nx, to: 0, damping: 1, response: 0.3, onUpdate: function (v2) { body.style.transform = 'translate3d(' + v2 + 'px,0,0)'; } });
    });
  }

  /* ---------- 设备自适应缩放 ---------- */
  function fitDevice() {
    var dev = document.querySelector('.device');
    if (!dev) return;
    var stage = document.querySelector('.stage');
    var wide = window.innerWidth > 1080;
    var availH = window.innerHeight - (wide ? 90 : 60);
    var availW = wide ? Math.min(520, window.innerWidth - 460) : window.innerWidth - 36;
    var k = Math.min(1, availH / 878, availW / 419);
    k = Math.max(0.52, k);
    dev.style.transform = 'scale(' + k.toFixed(4) + ')';
    dev.style.marginBottom = (878 * (k - 1)) + 'px';
    if (stage) stage.style.setProperty('--dev-scale', k.toFixed(4));
  }

  /* ---------- 初始化 ---------- */
  function init() {
    var mp = document.querySelector('.mp');
    if (!mp) return;
    buildChrome(mp);
    paintIcons(document);

    var app = new App(mp);
    window.MP = app;

    /* 屏幕索引 chips */
    var host = document.querySelector('[data-screen-index]');
    if (host) {
      Object.keys(app.screens).forEach(function (id) {
        var s = app.screens[id];
        if (!s.dataset.title) return;
        var b = document.createElement('button');
        b.className = 'schip';
        b.type = 'button';
        b.dataset.go = id;
        b.textContent = s.dataset.title;
        host.appendChild(b);
      });
      host.addEventListener('click', function (e) {
        var b = e.target.closest('.schip');
        if (!b) return;
        var s = app.screens[b.dataset.go];
        app.closeLayer(true);
        if (s.dataset.tabroot != null) app.tab(b.dataset.go);
        else {
          var parent = s.dataset.parent;
          if (parent && app.screens[parent]) { app.root(parent); app.push(b.dataset.go); }
          else app.root(b.dataset.go);
        }
      });
    }

    /* 首屏 */
    var first = mp.querySelector('.screen[data-start]') || mp.querySelector('.screen');
    if (first) app.root(first.dataset.screen);
    countUp(document);

    /* 事件委托 */
    mp.addEventListener('click', function (e) {
      var t = e.target;
      var el;
      if ((el = t.closest('[data-tab]')) && el.closest('.mp__tab')) { app.tab(el.dataset.tab); return; }
      if ((el = t.closest('[data-push]'))) { app.push(el.dataset.push); return; }
      if ((el = t.closest('[data-root]'))) { app.root(el.dataset.root); return; }
      if ((el = t.closest('[data-back]'))) { app.pop(); return; }
      if ((el = t.closest('[data-sheet]'))) { app.openSheet(el.dataset.sheet); return; }
      if ((el = t.closest('[data-dialog]'))) { app.openDialog(el.dataset.dialog); return; }
      if ((el = t.closest('[data-sheet-close]'))) {
        app.closeLayer();
        if (el.dataset.toast) app.toast(el.dataset.toast, el.dataset.toastIcon);
        if (el.dataset.then) setTimeout(function () { app.push(el.dataset.then); }, 260);
        if (el.dataset.thenRoot) setTimeout(function () { app.root(el.dataset.thenRoot); }, 260);
        return;
      }
      if ((el = t.closest('[data-toast]'))) { app.toast(el.dataset.toast, el.dataset.toastIcon); return; }
      if ((el = t.closest('.seg button:not(.seg__thumb)'))) { moveSeg(el.closest('.seg'), el); return; }
      if ((el = t.closest('.chip')) && el.parentNode.classList.contains('chipbar') && !el.dataset.static) {
        if (el.dataset.solo !== '0') {
          el.parentNode.querySelectorAll('.chip').forEach(function (c) { c.setAttribute('aria-selected', 'false'); });
        }
        el.setAttribute('aria-selected', 'true');
        return;
      }
      if ((el = t.closest('.radio'))) {
        el.parentNode.querySelectorAll('.radio').forEach(function (r) { r.setAttribute('aria-checked', 'false'); });
        el.setAttribute('aria-checked', 'true');
        return;
      }
      if ((el = t.closest('[role="checkbox"]'))) {
        el.setAttribute('aria-checked', el.getAttribute('aria-checked') === 'true' ? 'false' : 'true');
        syncPick(el.closest('.screen'));
        return;
      }
      /* 批量选择模式：data-mode="pick" 进入，"!pick" 退出 */
      if ((el = t.closest('[data-mode]'))) {
        var sc = el.closest('.screen');
        if (!sc) return;
        var name = el.dataset.mode;
        if (name.charAt(0) === '!') {
          sc.classList.remove('is-' + name.slice(1));
          sc.querySelectorAll('[role="checkbox"]').forEach(function (c) { c.setAttribute('aria-checked', 'false'); });
        } else {
          sc.classList.add('is-' + name);
        }
        syncPick(sc);
        return;
      }
      if ((el = t.closest('.switch'))) {
        var on = el.getAttribute('aria-checked') === 'true';
        el.setAttribute('aria-checked', on ? 'false' : 'true');
        return;
      }
      if ((el = t.closest('.stat[data-tabgo]'))) { app.tab(el.dataset.tabgo); return; }
      /* 运力候选：单选 + 毛利即时联动 */
      if ((el = t.closest('.cap'))) {
        if (el.classList.contains('is-off')) { app.toast(el.dataset.why || '这台车这单用不了'); return; }
        var grp = el.parentNode;
        grp.querySelectorAll('.cap').forEach(function (c) { c.setAttribute('aria-selected', c === el ? 'true' : 'false'); });
        var sc = el.closest('.screen');
        var bar = sc && sc.querySelector('.margin');
        if (bar && el.dataset.mv) {
          var v = bar.querySelector('.margin__v'), f = bar.querySelector('.margin__f'),
              sum = bar.querySelector('[data-margin-sum]'), note = bar.querySelector('.margin__c');
          var rate = parseFloat(el.dataset.mv);
          var tone = rate < 12 ? 'var(--danger)' : (rate < 18 ? 'var(--accent-deep)' : 'var(--success)');
          if (v) { v.textContent = el.dataset.mv + '%'; v.style.color = tone; }
          if (f) { f.style.width = Math.min(100, rate / 30 * 100) + '%'; f.style.background = rate < 12 ? 'var(--danger)' : (rate < 18 ? 'var(--accent)' : 'var(--success)'); }
          if (sum && el.dataset.mm) sum.textContent = '毛利 ' + el.dataset.mm;
          if (note && el.dataset.mc) note.textContent = el.dataset.mc;
          var act = sc.querySelector('[data-cap-label]');
          if (act && el.dataset.label) act.lastChild.textContent = el.dataset.label;
        }
        return;
      }
      /* 五阶段泳道卡带：切档 + 列表交叉淡入 */
      if ((el = t.closest('.bcard'))) {
        var band = el.closest('.band');
        band.querySelectorAll('.bcard').forEach(function (b) { b.setAttribute('aria-selected', b === el ? 'true' : 'false'); });
        el.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'nearest', inline: 'center' });
        var key = el.dataset.stage;
        if (key) {
          var scope = el.closest('.screen') || document;
          scope.querySelectorAll('[data-stage-panel]').forEach(function (p) {
            var on = p.dataset.stagePanel === key;
            p.hidden = !on;
            if (on && !REDUCED) {
              p.animate([{ opacity: 0, transform: 'translate3d(0,6px,0)' }, { opacity: 1, transform: 'none' }],
                { duration: 240, easing: 'cubic-bezier(.32,.72,0,1)' });
            }
          });
        }
        return;
      }
      /* 角色切换：老板 / 调度 / 财务三视图 */
      if ((el = t.closest('.roles button'))) {
        var grp = el.closest('.roles');
        grp.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-selected', b === el ? 'true' : 'false'); });
        var role = el.dataset.role;
        var host = el.closest('.screen') || document;
        host.querySelectorAll('[data-role-panel]').forEach(function (p) {
          var on = p.dataset.rolePanel === role;
          p.hidden = !on;
          if (on && !REDUCED) {
            p.animate([{ opacity: 0, transform: 'translate3d(0,8px,0)' }, { opacity: 1, transform: 'none' }],
              { duration: 280, easing: 'cubic-bezier(.32,.72,0,1)' });
          }
        });
        if (role) countUp(host);
        return;
      }
    });

    app.scrim.addEventListener('click', function () { app.closeLayer(); });

    mp.querySelectorAll('.sheet').forEach(function (s) { bindSheetDrag(app, s); });
    mp.querySelectorAll('.scroll[data-refresh]').forEach(function (s) { bindRefresh(app, s); });
    mp.querySelectorAll('[data-swipe]').forEach(bindSwipe);
    bindEdgeBack(app);

    /* 按下即反馈 */
    mp.addEventListener('pointerdown', function (e) {
      var el = e.target.closest('.ticket, .cell, .card[data-push], .chip, .btn');
      if (!el) return;
      el.classList.add('is-press');
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (evt) {
      mp.addEventListener(evt, function () {
        mp.querySelectorAll('.is-press').forEach(function (el) { el.classList.remove('is-press'); });
      });
    });

    layoutSegs(document);
    fitDevice();
    window.addEventListener('resize', fitDevice);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
