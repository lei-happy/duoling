/**
 * 利润总览 - 图表时间范围 composable
 *
 * 在 profit/index.vue 顶层调用 provideProfitFilter() 注入；
 * 各卡片读取「当月」起止（KPI 卡按服务端当日口径，与此窗口无关）。
 */
import { inject, provide, reactive, readonly, type InjectionKey } from 'vue';
import dayjs from 'dayjs';

export interface ProfitFilterState {
  /** 起始时间（YYYY-MM-DD HH:mm:ss），当月 1 日 0 点 */
  start: string;
  /** 截止时间（YYYY-MM-DD HH:mm:ss），当月最后一天结束 */
  end: string;
}

export interface ProfitFilterContext {
  state: Readonly<ProfitFilterState>;
}

const FMT = 'YYYY-MM-DD HH:mm:ss';

function currentMonthRange(): { start: string; end: string } {
  const now = dayjs();
  return {
    start: now.startOf('month').format(FMT),
    end: now.endOf('month').format(FMT)
  };
}

const PROFIT_FILTER_KEY: InjectionKey<ProfitFilterContext> =
  Symbol('ProfitFilter');

/** 在 profit 页面顶层调用，向后代组件提供当月时间窗 */
export function provideProfitFilter(): ProfitFilterContext {
  const init = currentMonthRange();
  const state = reactive<ProfitFilterState>({
    start: init.start,
    end: init.end
  });

  const ctx: ProfitFilterContext = {
    state: readonly(state) as Readonly<ProfitFilterState>
  };
  provide(PROFIT_FILTER_KEY, ctx);
  return ctx;
}

/** 在子组件中调用，获取共享时间窗 */
export function useProfitFilter(): ProfitFilterContext {
  const ctx = inject(PROFIT_FILTER_KEY);
  if (!ctx) {
    throw new Error(
      'useProfitFilter() 必须在 provideProfitFilter() 范围内使用'
    );
  }
  return ctx;
}
