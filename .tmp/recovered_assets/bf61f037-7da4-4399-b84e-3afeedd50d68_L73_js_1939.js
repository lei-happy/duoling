/* 智途 · 小程序原型 · 画廊交互 */
(function () {
  function initAnchorNav() {
    var nav = document.querySelector(".anchor-nav");
    if (!nav) return;
    var links = nav.querySelectorAll("a[href^='#']");
    var blocks = [];
    links.forEach(function (a) {
      var id = a.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      if (el) blocks.push({ link: a, el: el });
    });

    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var id = a.getAttribute("href").slice(1);
        var target = document.getElementById(id);
        if (!target) return;
        target.scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" });
        links.forEach(function (x) {
          x.classList.remove("active");
        });
        a.classList.add("active");
      });
    });
  }

  function initGallerySnap() {
    var gallery = document.querySelector(".gallery");
    if (!gallery) return;
    // 键盘左右切换屏幕
    document.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      var blocks = gallery.querySelectorAll(".screen-block");
      if (!blocks.length) return;
      var scrollLeft = gallery.scrollLeft;
      var idx = 0;
      var best = Infinity;
      for (var i = 0; i < blocks.length; i++) {
        var d = Math.abs(blocks[i].offsetLeft - scrollLeft);
        if (d < best) {
          best = d;
          idx = i;
        }
      }
      var next = e.key === "ArrowRight" ? Math.min(idx + 1, blocks.length - 1) : Math.max(idx - 1, 0);
      blocks[next].scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAnchorNav();
      initGallerySnap();
    });
  } else {
    initAnchorNav();
    initGallerySnap();
  }
})();
