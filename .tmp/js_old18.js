  /* ---------- 4. 画板进场 + 工具条 ---------- */
  function reveal() {
    var boards = Array.prototype.slice.call(document.querySelectorAll('.board'));
    if (!('IntersectionObserver' in window)) {
      boards.forEach(function (b) {
        b.classList.add('in');
      });
      return;
    }
    var obs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en, i) {
          if (!en.isIntersecting) return;
          var el = en.target;
          setTimeout(function () {
            el.classList.add('in');
          }, i * 40);
          obs.unobserve(el);
        });
      },
      { rootMargin: '0px 0px -8% 0px' }
    );
    boards.forEach(function (b) {
      obs.observe(b);
    });
  }

  function tools() {