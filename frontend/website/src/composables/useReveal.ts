import { onMounted, onUnmounted, onUpdated } from 'vue';

/**
 * 滚动进场：元素进入视口后播放一次 opacity + 8px 位移。
 *
 * 用法：给元素加 `reveal` class。
 * - 同组元素加 `data-stagger="0|1|2..."`，按 40ms 递增延迟依次进场
 * - 也可用 `data-delay="120"` 直接指定毫秒延迟
 *
 * 用户开启「减弱动态效果」时不再排队播放，一次性全部显示，
 * 避免内容因为等待动画而迟迟不出现。
 */

/** 同组元素之间的进场间隔，短到刚好能被察觉为"依次"，不拖慢阅读 */
const STAGGER_STEP = 40;

export function useReveal() {
  let observer: IntersectionObserver | null = null;
  /** 已接管的元素，避免重复扫描时重新观察同一个节点 */
  const seen = new WeakSet<HTMLElement>();
  let showImmediately = false;

  /**
   * 扫描页面上尚未接管的 .reveal。
   * 挂载后还会再跑，因为 v-if 里的内容是后来才进 DOM 的 ——
   * 只在 onMounted 扫一次的话，那些元素会永远停在 opacity: 0。
   */
  function scan() {
    document.querySelectorAll<HTMLElement>('.reveal').forEach((el) => {
      if (seen.has(el)) {
        return;
      }
      seen.add(el);

      if (showImmediately) {
        el.classList.add('is-in');
        return;
      }
      observer?.observe(el);
    });
  }

  onMounted(() => {
    // 无 IntersectionObserver 或用户要求减弱动效时，内容直接出现，不排队等动画
    showImmediately =
      !('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!showImmediately) {
      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) {
              return;
            }
            const el = entry.target as HTMLElement;
            const delay =
              el.dataset.delay ??
              String(Number(el.dataset.stagger ?? 0) * STAGGER_STEP);
            el.style.transitionDelay = `${delay}ms`;
            el.classList.add('is-in');
            observer?.unobserve(el);
          });
        },
        { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
      );
    }

    scan();
  });

  onUpdated(scan);

  onUnmounted(() => {
    observer?.disconnect();
    observer = null;
  });
}
