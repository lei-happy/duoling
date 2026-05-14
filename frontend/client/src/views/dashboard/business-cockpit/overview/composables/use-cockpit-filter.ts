/**
 * 经营驾驶舱 - 全局时间筛选 composable
 *
 * 在 overview/index.vue 顶层调用 provideCockpitFilter() 注入；
 * 各子组件调用 useCockpitFilter() 拿到响应式的 [start, end] 区间，
 * 并通过 watch(range) 触发数据重拉。
 */
import { inject, provide, reactive, readonly, type InjectionKey } from 'vue';
import dayjs from 'dayjs';

export type DatePreset = '1' | '2' | '3' | '4' | 'custom';

export interface CockpitFilterState {
  /** 起始时间（YYYY-MM-DD HH:mm:ss） */
  start: string;
  /** 截止时间（YYYY-MM-DD HH:mm:ss） */
  end: string;
  /** 当前生效的预设：1今天 2本周 3本月 4本年 custom 自定义 */
  preset: DatePreset;
}

export interface CockpitFilterContext {
  state: Readonly<CockpitFilterState>;
  setRange(start: string, end: string, preset?: DatePreset): void;
  setPreset(preset: DatePreset): void;
}

const FMT = 'YYYY-MM-DD HH:mm:ss';

function presetRange(preset: DatePreset): { start: string; end: string } {
  const now = dayjs();
  if (preset === '1') {
    return { start: now.startOf('day').format(FMT), end: now.endOf('day').format(FMT) };
  }
  if (preset === '2') {
    return { start: now.startOf('week').format(FMT), end: now.endOf('week').format(FMT) };
  }
  if (preset === '4') {
    return { start: now.startOf('year').format(FMT), end: now.endOf('year').format(FMT) };
  }
  return { start: now.startOf('month').format(FMT), end: now.endOf('month').format(FMT) };
}

const COCKPIT_FILTER_KEY: InjectionKey<CockpitFilterContext> = Symbol(
  'CockpitFilter'
);

/** 在 overview 页面顶层调用，向后代组件提供筛选状态 */
export function provideCockpitFilter(
  initialPreset: DatePreset = '3'
): CockpitFilterContext {
  const init = presetRange(initialPreset);
  const state = reactive<CockpitFilterState>({
    start: init.start,
    end: init.end,
    preset: initialPreset
  });

  const setRange = (start: string, end: string, preset: DatePreset = 'custom') => {
    state.start = start;
    state.end = end;
    state.preset = preset;
  };

  const setPreset = (preset: DatePreset) => {
    if (preset === 'custom') {
      state.preset = 'custom';
      return;
    }
    const r = presetRange(preset);
    state.start = r.start;
    state.end = r.end;
    state.preset = preset;
  };

  const ctx: CockpitFilterContext = {
    state: readonly(state) as Readonly<CockpitFilterState>,
    setRange,
    setPreset
  };
  provide(COCKPIT_FILTER_KEY, ctx);
  return ctx;
}

/** 在子组件中调用，获取共享筛选状态 */
export function useCockpitFilter(): CockpitFilterContext {
  const ctx = inject(COCKPIT_FILTER_KEY);
  if (!ctx) {
    throw new Error(
      'useCockpitFilter() 必须在 provideCockpitFilter() 范围内使用'
    );
  }
  return ctx;
}
