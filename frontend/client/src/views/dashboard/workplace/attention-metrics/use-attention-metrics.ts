import { computed, onMounted, ref } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/store/modules/user';
import { usePermission } from '@/utils/use-permission';
import { getWaybillWorkbenchStats } from '@/api/waybill';
import { getTaskWorkbenchStats } from '@/api/operation/task';
import { getFinanceWorkbenchStats } from '@/api/operation/task-finance';
import { approvalStats } from '@/api/capacity/social-capacity/approval';
import {
  ATTENTION_METRICS_REGISTRY,
  type AttentionMetricConfig
} from './attention-metrics-registry';

export interface AttentionMetricItem {
  key: string;
  label: string;
  icon: string;
  tagType: AttentionMetricConfig['tagType'];
  value: number | null;
  route: RouteLocationRaw;
  urgent: boolean;
}

const APPROVAL_FINANCE_PERMISSION = 'operation:task-finance:approve';
const APPROVAL_SOCIAL_PERMISSION = 'capacity:social_capacity:approval:list';

function isPathInUserMenus(path: string, menus: unknown): boolean {
  if (!menus || !Array.isArray(menus)) {
    return false;
  }
  for (const node of menus) {
    const item = node as { path?: string; children?: unknown[] };
    if (item.path === path) {
      return true;
    }
    if (item.children?.length && isPathInUserMenus(path, item.children)) {
      return true;
    }
  }
  return false;
}

async function loadWaybillPendingConfirm(): Promise<number> {
  const stats = await getWaybillWorkbenchStats();
  return stats?.totals?.pendingConfirm ?? 0;
}

async function loadTaskDispatchTransit(): Promise<number> {
  const stats = await getTaskWorkbenchStats();
  const t = stats?.totals;
  return (
    (t?.pendingDispatch ?? 0) +
    (t?.pendingLoad ?? 0) +
    (t?.loading ?? 0) +
    (t?.onWay ?? 0)
  );
}

async function loadApprovalPending(options: {
  canFinance: boolean;
  canSocial: boolean;
}): Promise<{ total: number; route: RouteLocationRaw }> {
  let financeCount = 0;
  let socialCount = 0;

  const tasks: Promise<void>[] = [];
  if (options.canFinance) {
    tasks.push(
      getFinanceWorkbenchStats()
        .then((stats) => {
          financeCount = stats?.totals?.pendingReview ?? 0;
        })
        .catch(() => {
          financeCount = 0;
        })
    );
  }
  if (options.canSocial) {
    tasks.push(
      approvalStats()
        .then((stats) => {
          socialCount = stats?.pendingCount ?? 0;
        })
        .catch(() => {
          socialCount = 0;
        })
    );
  }
  await Promise.all(tasks);

  const total = financeCount + socialCount;
  let route: RouteLocationRaw = {
    path: '/operation/task-finance-workbench',
    query: { tab: 'pending-review' }
  };
  if (socialCount > financeCount) {
    route = { path: '/capacity/social-capacity/capacity-approval' };
  } else if (financeCount === 0 && socialCount > 0) {
    route = { path: '/capacity/social-capacity/capacity-approval' };
  }

  return { total, route };
}

const LOADERS: Record<
  string,
  (ctx: { canFinance: boolean; canSocial: boolean }) => Promise<{
    value: number;
    route?: RouteLocationRaw;
  }>
> = {
  'waybill.pending_confirm': async () => ({
    value: await loadWaybillPendingConfirm()
  }),
  'task.dispatch_transit': async () => ({
    value: await loadTaskDispatchTransit()
  }),
  'approval.pending': async (ctx) => {
    const { total, route } = await loadApprovalPending(ctx);
    return { value: total, route };
  }
};

export function useAttentionMetrics() {
  const userStore = useUserStore();
  const { menus } = storeToRefs(userStore);
  const { hasPermission, hasAnyPermission } = usePermission();

  const loading = ref(false);
  const items = ref<AttentionMetricItem[]>([]);

  const canFinanceApproval = computed(
    () =>
      hasPermission(APPROVAL_FINANCE_PERMISSION) ||
      isPathInUserMenus('/operation/task-finance-workbench', menus.value)
  );
  const canSocialApproval = computed(() =>
    hasPermission(APPROVAL_SOCIAL_PERMISSION)
  );

  const isMetricAccessible = (config: AttentionMetricConfig): boolean => {
    if (config.key === 'approval.pending') {
      return canFinanceApproval.value || canSocialApproval.value;
    }
    if (config.feature && !userStore.hasFeature(config.feature)) {
      return false;
    }
    if (config.permission) {
      return Array.isArray(config.permission)
        ? hasAnyPermission(config.permission)
        : hasPermission(config.permission);
    }
    const path =
      typeof config.route === 'string' ? config.route : config.route.path;
    return path ? isPathInUserMenus(path, menus.value) : false;
  };

  const accessibleRegistry = computed(() =>
    ATTENTION_METRICS_REGISTRY.filter(isMetricAccessible)
  );

  const summaryText = computed(() => {
    if (loading.value) {
      return '正在加载今日需关注事项…';
    }
    const urgentParts = items.value
      .filter((item) => item.value != null && item.value > 0)
      .map((item) => `${item.value} ${item.label}`);
    if (!urgentParts.length) {
      return '今日暂无待处理的业务事项，继续保持。';
    }
    return `今日需关注：${urgentParts.join('、')}`;
  });

  const load = async () => {
    const registry = accessibleRegistry.value;
    if (!registry.length) {
      items.value = [];
      return;
    }

    loading.value = true;
    const ctx = {
      canFinance: canFinanceApproval.value,
      canSocial: canSocialApproval.value
    };

    try {
      const results = await Promise.all(
        registry.map(async (config) => {
          const loader = LOADERS[config.key];
          let value: number | null = null;
          let route = config.route;
          if (loader) {
            try {
              const result = await loader(ctx);
              value = result.value;
              if (result.route) {
                route = result.route;
              }
            } catch {
              value = null;
            }
          }
          return {
            key: config.key,
            label: config.label,
            icon: config.icon,
            tagType: config.tagType,
            value,
            route,
            urgent: (value ?? 0) > 0
          } satisfies AttentionMetricItem;
        })
      );
      items.value = results;
    } finally {
      loading.value = false;
    }
  };

  onMounted(load);

  return {
    loading,
    items,
    summaryText,
    reload: load
  };
}
