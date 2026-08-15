import { onUnmounted, ref, watch, type Ref } from 'vue';

interface SpringOptions {
  /**
   * 阻尼比。1 = 临界阻尼，无回弹；小于 1 会略微越过目标再回来。
   * 只有当运动本身带有"被抛出去"的物理感时才降到 1 以下。
   */
  damping?: number;
  /** 响应时间（秒）。越小越干脆。这不是"时长"，弹簧没有固定时长。 */
  response?: number;
}

/**
 * 弹簧数值动画。
 *
 * 与 CSS transition 的区别在于可打断：目标值中途改变时，
 * 它从当前的实际位置和当前速度继续算，不会跳回起点重来，
 * 也不会在反向时撞出一堵"速度墙"。
 *
 * 用户开启「减弱动态效果」时直接取目标值，不做动画。
 */
export function useSpringValue(
  target: Ref<number>,
  options: SpringOptions = {}
): Ref<number> {
  const { damping = 1, response = 0.35 } = options;

  const current = ref(target.value);
  let velocity = 0;
  let frame = 0;
  let lastTime = 0;

  const prefersReduced =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const omega = (2 * Math.PI) / response;

  const step = (now: number) => {
    // 首帧没有上一帧时间，按 16ms 估
    const dt = lastTime ? Math.min((now - lastTime) / 1000, 0.064) : 0.016;
    lastTime = now;

    const displacement = current.value - target.value;
    const accel = -omega * omega * displacement - 2 * damping * omega * velocity;

    velocity += accel * dt;
    current.value += velocity * dt;

    // 位置和速度都足够小时收敛，避免无限逼近导致 rAF 永不停
    if (Math.abs(current.value - target.value) < 0.01 && Math.abs(velocity) < 0.01) {
      current.value = target.value;
      velocity = 0;
      frame = 0;
      return;
    }

    frame = requestAnimationFrame(step);
  };

  watch(target, (next) => {
    if (prefersReduced) {
      current.value = next;
      return;
    }
    if (frame) {
      return; // 已在运行，让它带着当前速度重新收敛到新目标
    }
    lastTime = 0;
    frame = requestAnimationFrame(step);
  });

  onUnmounted(() => {
    if (frame) {
      cancelAnimationFrame(frame);
      frame = 0;
    }
  });

  return current;
}
