import { ref, nextTick, type Ref } from 'vue';
import { gsap, Flip } from '@/utils/gsap';

export interface UseFlipModalOptions {
  /** 运动的浮层面板元素 */
  panelRef: Ref<HTMLElement | null>;
  /** 遮罩元素（淡入淡出） */
  overlayRef: Ref<HTMLElement | null>;
  /** 面板内详情内容元素（延迟淡入，可选） */
  contentRef?: Ref<HTMLElement | null>;
  /** 动画时长（秒） */
  duration?: number;
  /** 缓动 */
  ease?: string;
  /** 透视距离（px），用于 rotateY 的 3D 翻转观感 */
  perspective?: number;
  onOpened?: () => void;
  onClosed?: () => void;
}

const prefersReducedMotion = (): boolean => {
  return (
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
};

/** 等待一帧，确保 DOM 已完成布局 */
const nextFrame = (): Promise<void> =>
  new Promise((resolve) => {
    requestAnimationFrame(() => resolve());
  });

/**
 * 基于 GSAP Flip 的"卡片翻转放大居中 / 原路返回"浮层动画。
 *
 * 机制：浮层 panel 始终渲染在最终的居中放大态（由 flex 布局居中，不依赖 transform）。
 * - 打开：用 Flip.fit 把 panel 瞬移贴合到来源卡片位置并记录该状态，随后清掉 transform 回到
 *   居中态，再 Flip.from(该状态) 形变到中心，同时叠加一条 rotationY(-90 -> 0) 翻转 tween。
 * - 关闭：用 Flip.fit 把 panel 动画形变回当前来源卡片位置（实时读取，规避滚动/resize 错位），
 *   同时叠加 rotationY(0 -> -90)。
 */
export function useFlipModal(options: UseFlipModalOptions) {
  const {
    panelRef,
    overlayRef,
    contentRef,
    duration = 0.55,
    ease = 'power3.inOut',
    perspective = 1600,
    onOpened,
    onClosed
  } = options;

  const visible = ref(false);
  const isAnimating = ref(false);

  let sourceEl: HTMLElement | null = null;
  let currentTl: gsap.core.Timeline | null = null;

  const lockScroll = (lock: boolean) => {
    if (typeof document === 'undefined') return;
    document.body.style.overflow = lock ? 'hidden' : '';
  };

  const killCurrent = () => {
    if (currentTl) {
      currentTl.kill();
      currentTl = null;
    }
    const panel = panelRef.value;
    if (panel) Flip.killFlipsOf(panel);
  };

  const open = async (source: HTMLElement) => {
    if (!source) return;
    killCurrent();
    sourceEl = source;
    visible.value = true;
    lockScroll(true);

    // 等待浮层渲染并完成布局
    await nextTick();
    await nextFrame();

    const panel = panelRef.value;
    const overlay = overlayRef.value;
    const content = contentRef?.value ?? null;
    if (!panel) {
      isAnimating.value = false;
      onOpened?.();
      return;
    }

    if (prefersReducedMotion()) {
      gsap.set(panel, { clearProps: 'transform' });
      gsap.set(panel, { autoAlpha: 1 });
      if (overlay) gsap.set(overlay, { autoAlpha: 1 });
      if (content) gsap.set(content, { autoAlpha: 1 });
      isAnimating.value = false;
      onOpened?.();
      return;
    }

    isAnimating.value = true;

    // 1. 瞬移贴合来源卡片，记录"起始（卡片）"状态
    Flip.fit(panel, sourceEl, { scale: true });
    const startState = Flip.getState(panel);
    // 2. 回到居中放大态（清掉 fit 留下的 transform）
    gsap.set(panel, { clearProps: 'transform' });
    gsap.set(panel, {
      autoAlpha: 1,
      // 透视作用于面板自身，灭点始终跟随面板中心，
      // 避免卡片靠屏幕边缘时 rotateY 畸变
      transformPerspective: perspective,
      transformOrigin: 'center center',
      backfaceVisibility: 'hidden'
    });

    const tl = gsap.timeline({
      onComplete: () => {
        isAnimating.value = false;
        currentTl = null;
        onOpened?.();
      }
    });

    // 3. 形变：从卡片位置/尺寸 -> 居中放大
    tl.add(Flip.from(startState, { targets: panel, scale: true, duration, ease }), 0);
    // 叠加翻转
    tl.fromTo(panel, { rotationY: -90 }, { rotationY: 0, duration, ease }, 0);
    // 遮罩淡入
    if (overlay) {
      tl.fromTo(
        overlay,
        { autoAlpha: 0 },
        { autoAlpha: 1, duration: duration * 0.6, ease: 'power1.out' },
        0
      );
    }
    // 详情内容延迟淡入
    if (content) {
      tl.fromTo(
        content,
        { autoAlpha: 0 },
        { autoAlpha: 1, duration: duration * 0.45, ease: 'power1.out' },
        duration * 0.5
      );
    }

    currentTl = tl;
  };

  const close = () => {
    if (!visible.value) return;
    killCurrent();

    const panel = panelRef.value;
    const overlay = overlayRef.value;
    const content = contentRef?.value ?? null;

    const finish = () => {
      isAnimating.value = false;
      currentTl = null;
      visible.value = false;
      lockScroll(false);
      if (panel) gsap.set(panel, { clearProps: 'all' });
      sourceEl = null;
      onClosed?.();
    };

    if (!panel || !sourceEl || prefersReducedMotion()) {
      finish();
      return;
    }

    isAnimating.value = true;

    gsap.set(panel, {
      transformPerspective: perspective,
      transformOrigin: 'center center',
      backfaceVisibility: 'hidden'
    });

    const tl = gsap.timeline({ onComplete: finish });

    // 详情内容先淡出
    if (content) {
      tl.to(content, { autoAlpha: 0, duration: duration * 0.35, ease: 'power1.in' }, 0);
    }
    // 形变回卡片位置（实时读取来源元素，避免滚动/resize 错位）
    tl.add(
      Flip.fit(panel, sourceEl, { scale: true, duration, ease }) as gsap.core.Tween,
      content ? duration * 0.2 : 0
    );
    // 逆向翻转
    tl.to(panel, { rotationY: -90, duration, ease }, '<');
    // 遮罩淡出
    if (overlay) {
      tl.to(overlay, { autoAlpha: 0, duration: duration * 0.7, ease: 'power1.in' }, '<');
    }

    currentTl = tl;
  };

  return {
    visible,
    isAnimating,
    open,
    close
  };
}
