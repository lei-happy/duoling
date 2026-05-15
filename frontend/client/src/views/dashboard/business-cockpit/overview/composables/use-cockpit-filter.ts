/**
 * 经营驾驶舱 - 图表时间范围 composable
 *
 * 在 overview/index.vue 顶层调用 provideCockpitFilter() 注入；
 * 趋势及以下模块读取「当月」起止（无顶部筛选条，与 KPI 卡无关）。
 */
import { inject, provide, reactive, readonly, type InjectionKey } from 'vue';
import dayjs from 'dayjs';

export interface CockpitFilterState {
  /** 起始时间（YYYY-MM-DD HH:mm:ss），当月 1 日 0 点 */
  start: string;
  /** 截止时间（YYYY-MM-DD HH:mm:ss），当月最后一天结束 */
  end: string;
}

export interface CockpitFilterContext {
  state: Readonly<CockpitFilterState>;
}

const FMT = 'YYYY-MM-DD HH:mm:ss';

function currentMonthRange(): { start: string; end: string } {
  const now = dayjs();
  return {
    start: now.startOf('month').format(FMT),
    end: now.endOf('month').format(FMT)
  };
}

const COCKPIT_FILTER_KEY: InjectionKey<CockpitFilterContext> = Symbol(
  'CockpitFilter'
);

/** 在 overview 页面顶层调用，向后代组件提供当月时间窗 */
export function provideCockpitFilter(): CockpitFilterContext {
  const init = currentMonthRange();
  const state = reactive<CockpitFilterState>({
    start: init.start,
    end: init.end
  });

  const ctx: CockpitFilterContext = {
    state: readonly(state) as Readonly<CockpitFilterState>
  };
  provide(COCKPIT_FILTER_KEY, ctx);
  return ctx;
}

/** 在子组件中调用，获取共享时间窗 */
export function useCockpitFilter(): CockpitFilterContext {
  const ctx = inject(COCKPIT_FILTER_KEY);
  if (!ctx) {
    throw new Error(
      'useCockpitFilter() 必须在 provideCockpitFilter() 范围内使用'
    );
  }
  return ctx;
}
