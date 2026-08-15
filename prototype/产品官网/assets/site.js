/* 朵灵·企云产品官网原型 · 通用交互
   包含：导航吸顶与移动端菜单、滚动进场、通用 Tab、Banner 幻灯、价格周期切换、原型表单占位提交 */

(function () {
  'use strict';

  /* ---------------- 导航 ---------------- */
  const nav = document.querySelector('.nav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('is-stuck', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.addEventListener('click', () => {
      const open = links.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------------- 滚动进场 ---------------- */
  const revealItems = document.querySelectorAll('.reveal');
  if (revealItems.length) {
    if (!('IntersectionObserver' in window)) {
      revealItems.forEach((el) => el.classList.add('is-in'));
    } else {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const el = entry.target;
            const delay = Number(el.dataset.delay || 0);
            window.setTimeout(() => el.classList.add('is-in'), delay);
            io.unobserve(el);
          });
        },
        { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
      );
      revealItems.forEach((el) => io.observe(el));
    }
  }

  /* ---------------- 通用 Tab ---------------- */
  document.querySelectorAll('[data-tabs]').forEach((group) => {
    const buttons = group.querySelectorAll('[data-tab-btn]');
    const panels = group.querySelectorAll('[data-tab-panel]');

    const activate = (key) => {
      buttons.forEach((btn) =>
        btn.setAttribute('aria-selected', btn.dataset.tabBtn === key ? 'true' : 'false')
      );
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.tabPanel !== key;
      });
    };

    buttons.forEach((btn) => {
      btn.addEventListener('click', () => activate(btn.dataset.tabBtn));
    });

    const initial =
      group.querySelector('[data-tab-btn][aria-selected="true"]') || buttons[0];
    if (initial) activate(initial.dataset.tabBtn);
  });

  /* ---------------- 价格周期切换 ---------------- */
  const cycleSwitch = document.querySelector('[data-cycle-switch]');
  if (cycleSwitch) {
    const CYCLE = {
      month: { label: '/月', note: '按月付费，随时停用' },
      year: { label: '/年', note: '年付约 8 折，相当于省 2 个多月' }
    };

    const setCycle = (key) => {
      const conf = CYCLE[key] || CYCLE.year;

      cycleSwitch.querySelectorAll('[data-cycle]').forEach((btn) =>
        btn.setAttribute('aria-selected', btn.dataset.cycle === key ? 'true' : 'false')
      );

      document.querySelectorAll('[data-price]').forEach((el) => {
        const value = el.dataset['price' + key.charAt(0).toUpperCase() + key.slice(1)];
        if (value) el.textContent = Number(value).toLocaleString('zh-CN');
      });

      document.querySelectorAll('[data-period-label]').forEach((el) => {
        el.textContent = conf.label;
      });

      document.querySelectorAll('[data-cycle-note]').forEach((el) => {
        el.textContent = conf.note;
      });
    };

    cycleSwitch.querySelectorAll('[data-cycle]').forEach((btn) => {
      btn.addEventListener('click', () => setCycle(btn.dataset.cycle));
    });

    const preset = cycleSwitch.querySelector('[data-cycle][aria-selected="true"]');
    setCycle(preset ? preset.dataset.cycle : 'year');
  }

  /* ---------------- 横向 Banner 幻灯 ---------------- */
  document.querySelectorAll('[data-banner]').forEach((root) => {
    const track = root.querySelector('.banner-track');
    const slides = root.querySelectorAll('.banner-slide');
    const prev = root.querySelector('[data-banner-prev]');
    const next = root.querySelector('[data-banner-next]');
    const dotsWrap = root.querySelector('[data-banner-dots]');
    if (!track || !slides.length) return;

    let index = 0;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    slides.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.setAttribute('aria-label', '第 ' + (i + 1) + ' 层');
      dot.addEventListener('click', () => go(i));
      dotsWrap.appendChild(dot);
    });

    const go = (i) => {
      index = (i + slides.length) % slides.length;
      track.style.transition = reduce ? 'none' : '';
      track.style.transform = 'translateX(-' + index * 100 + '%)';
      dotsWrap.querySelectorAll('button').forEach((dot, di) => {
        dot.setAttribute('aria-current', di === index ? 'true' : 'false');
      });
    };

    if (prev) prev.addEventListener('click', () => go(index - 1));
    if (next) next.addEventListener('click', () => go(index + 1));

    root.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') go(index - 1);
      if (event.key === 'ArrowRight') go(index + 1);
    });
    root.setAttribute('tabindex', '0');

    go(0);
  });

  /* ---------------- 原型表单：不真实提交 ---------------- */
  document.querySelectorAll('form[data-proto-form]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const tip = form.querySelector('[data-proto-tip]');
      if (tip) {
        tip.textContent = '原型演示：这里会把信息发给顾问，并在 1 个工作日内回电。';
        tip.hidden = false;
      }
    });
  });
})();
