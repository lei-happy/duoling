<template>
  <svg
    class="overview-icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="canonical === 'waybill'">
      <path
        d="M13.5 3.5H7A1.5 1.5 0 0 0 5.5 5v14A1.5 1.5 0 0 0 7 20.5h10A1.5 1.5 0 0 0 18.5 19V8.5Z"
      />
      <path d="M13.5 3.5V8.5H18.5" />
      <path d="M8.5 12.5H15" />
      <path d="M8.5 15.5H15" />
    </template>
    <template v-else-if="canonical === 'task'">
      <path
        d="M6.5 6H17.5A1.5 1.5 0 0 1 19 7.5V19A1.5 1.5 0 0 1 17.5 20.5h-11A1.5 1.5 0 0 1 5 19V7.5A1.5 1.5 0 0 1 6.5 6Z"
      />
      <rect x="8.5" y="3.5" width="7" height="3.5" rx="1" />
      <path d="M8.5 11.5H15.5" />
      <path d="M8.5 15H13.5" />
    </template>
    <template v-else-if="canonical === 'stowage'">
      <path d="M12 4 4 8l8 4 8-4-8-4Z" />
      <path d="M4 8v8l8 4 8-4V8" />
      <path d="M12 12v8" />
    </template>
    <template v-else-if="canonical === 'dispatch'">
      <path d="M3.5 6.5h9.5v9H3.5z" />
      <path d="M13 9.5H16.5l3.5 3.5v2.5H13z" />
      <circle cx="7" cy="17.5" r="1.6" />
      <circle cx="16.5" cy="17.5" r="1.6" />
    </template>
    <template v-else-if="canonical === 'tracking'">
      <path d="M12 21s6-5.2 6-10a6 6 0 1 0-12 0c0 4.8 6 10 6 10Z" />
      <circle cx="12" cy="11" r="2.3" />
    </template>
    <template v-else-if="canonical === 'receipt'">
      <path
        d="M13.5 3.5H7A1.5 1.5 0 0 0 5.5 5v14A1.5 1.5 0 0 0 7 20.5h10A1.5 1.5 0 0 0 18.5 19V8.5Z"
      />
      <path d="M13.5 3.5V8.5H18.5" />
      <path d="M8.3 14l2.2 2.2L15.7 11.4" />
    </template>
    <template v-else-if="canonical === 'completed'">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8.2 12.3l2.6 2.6 5-5.2" />
    </template>
    <template v-else-if="canonical === 'smart'">
      <path d="M12 4l1.8 4.2L18 10l-4.2 1.8L12 16l-1.8-4.2L6 10l4.2-1.8z" />
      <path d="M17.6 15.4l.7 1.6 1.6.7-1.6.7-.7 1.6-.7-1.6-1.6-.7 1.6-.7z" />
    </template>
    <template v-else-if="canonical === 'people'">
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3.8 19.2c0-3.1 2.4-5.2 5.2-5.2s5.2 2.1 5.2 5.2" />
      <circle cx="17" cy="8.6" r="2.4" />
      <path d="M16 13.7c2.7-.1 4.6 1.8 4.6 4.5" />
    </template>
    <template v-else-if="canonical === 'money'">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8.6 8.4 12 12.4 15.4 8.4" />
      <path d="M12 12.4V17" />
      <path d="M9.2 13.2h5.6" />
      <path d="M9.2 15.3h5.6" />
    </template>
    <template v-else-if="canonical === 'chart'">
      <path d="M4 20h16" />
      <rect x="6" y="11" width="3" height="6" rx="0.6" />
      <rect x="10.5" y="7" width="3" height="10" rx="0.6" />
      <rect x="15" y="13.5" width="3" height="3.5" rx="0.6" />
    </template>
    <template v-else-if="canonical === 'shield'">
      <path d="M12 3.5 19 6v5c0 5-3.2 8-7 9.5C8.2 19 5 16 5 11V6Z" />
      <path d="M9 12l2.2 2.2L15.2 10" />
    </template>
    <template v-else-if="canonical === 'settings'">
      <circle cx="12" cy="12" r="3" />
      <path
        d="M12 3.6v2.2M12 18.2v2.2M20.4 12h-2.2M5.8 12H3.6M17.9 6.1l-1.6 1.6M7.7 16.3 6.1 17.9M17.9 17.9l-1.6-1.6M7.7 7.7 6.1 6.1"
      />
    </template>
    <template v-else-if="canonical === 'box'">
      <path d="M4 9.5 12 5l8 4.5V20H4Z" />
      <path d="M9 20v-6h6v6" />
    </template>
    <template v-else-if="canonical === 'contract'">
      <path
        d="M13.5 3.5H7A1.5 1.5 0 0 0 5.5 5v14A1.5 1.5 0 0 0 7 20.5h10A1.5 1.5 0 0 0 18.5 19V8.5Z"
      />
      <path d="M13.5 3.5V8.5H18.5" />
      <path d="M8.5 11.5h4" />
      <circle cx="14" cy="16" r="2.2" />
    </template>
    <template v-else-if="canonical === 'bell'">
      <path d="M7 10a5 5 0 0 1 10 0c0 4 1.5 5.5 2 6H5c.5-.5 2-2 2-6Z" />
      <path d="M10 19a2 2 0 0 0 4 0" />
    </template>
    <template v-else-if="canonical === 'list'">
      <path d="M8 7h11" />
      <path d="M8 12h11" />
      <path d="M8 17h11" />
      <circle cx="4.5" cy="7" r="1.1" />
      <circle cx="4.5" cy="12" r="1.1" />
      <circle cx="4.5" cy="17" r="1.1" />
    </template>
    <template v-else>
      <rect x="4.5" y="4.5" width="6" height="6" rx="1.4" />
      <rect x="13.5" y="4.5" width="6" height="6" rx="1.4" />
      <rect x="4.5" y="13.5" width="6" height="6" rx="1.4" />
      <rect x="13.5" y="13.5" width="6" height="6" rx="1.4" />
    </template>
  </svg>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';

  defineOptions({ name: 'OverviewIcon' });

  const props = defineProps<{
    /** 图标名称（支持别名，最终归一到基础图标） */
    name?: string;
  }>();

  /** 语义别名到基础图标的映射，便于各模块复用有限的基础图标集 */
  const ALIAS: Record<string, string> = {
    customer: 'people',
    carrier: 'people',
    supplier: 'people',
    org: 'people',
    user: 'people',
    role: 'people',
    driver: 'people',
    receivable: 'money',
    payable: 'money',
    profit: 'money',
    fund: 'money',
    report: 'chart',
    board: 'chart',
    cockpit: 'chart',
    forecast: 'chart',
    analysis: 'chart',
    license: 'shield',
    compliance: 'shield',
    security: 'shield',
    config: 'settings',
    dict: 'settings',
    gear: 'settings',
    data: 'settings',
    cargo: 'box',
    hall: 'box',
    service: 'box',
    warehouse: 'box',
    capacityhall: 'box',
    social: 'box',
    store: 'box',
    ecosystem: 'box',
    template: 'contract',
    invoice: 'contract',
    entity: 'contract',
    profile: 'contract',
    log: 'list',
    login: 'list',
    history: 'list',
    approval: 'completed',
    pending: 'completed',
    initiated: 'completed',
    reconcile: 'completed',
    deal: 'completed',
    route: 'tracking',
    link: 'tracking',
    vehicle: 'dispatch',
    overview: 'default'
  };

  /** 已实现的基础图标名称 */
  const CANONICAL = new Set([
    'waybill',
    'task',
    'stowage',
    'dispatch',
    'tracking',
    'receipt',
    'completed',
    'smart',
    'people',
    'money',
    'chart',
    'shield',
    'settings',
    'box',
    'contract',
    'bell',
    'list',
    'default'
  ]);

  const canonical = computed(() => {
    const raw = (props.name || 'default').toLowerCase();
    if (CANONICAL.has(raw)) {
      return raw;
    }
    return ALIAS[raw] || 'default';
  });
</script>

<style lang="scss" scoped>
  .overview-icon {
    width: 1em;
    height: 1em;
    display: inline-block;
    vertical-align: middle;
  }
</style>
