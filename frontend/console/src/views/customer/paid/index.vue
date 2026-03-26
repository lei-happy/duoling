<!-- 付费客户 -->
<template>
  <ele-page>
    <customer-search
      :show-status="false"
      @search="(where) => handleSearch(where)"
    />
    <customer-table
      ref="tableRef"
      lifecycle="paid"
      :version-code="currentVersionCode"
      :expire-warning="activeTab === 'warning'"
      @reload="loadTabCounts"
    >
      <template #toolbar>
        <div class="paid-toolbar">
          <div class="paid-tabs">
            <div
              v-for="tab in tabs"
              :key="tab.name"
              class="paid-tab-item"
              :class="{ active: activeTab === tab.name }"
              @click="switchTab(tab.name)"
            >
              <span>{{ tab.label }}</span>
              <el-badge
                v-if="tab.count > 0"
                :value="tab.count"
                :max="999"
                class="tab-badge"
              />
            </div>
          </div>
        </div>
      </template>
    </customer-table>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, nextTick, onMounted } from 'vue';
  import CustomerSearch from '../components/customer-search.vue';
  import CustomerTable from '../components/customer-table.vue';
  import { pageCustomers, listProductVersions } from '@/api/customer';
  import type { CustomerParam } from '@/api/customer/model';

  defineOptions({ name: 'CustomerPaid' });

  const tableRef = ref<InstanceType<typeof CustomerTable> | null>(null);
  const activeTab = ref('all');

  interface TabItem {
    name: string;
    label: string;
    versionCode?: string;
    count: number;
  }

  const versionTabs = ref<TabItem[]>([]);

  const tabs = computed<TabItem[]>(() => [
    { name: 'all', label: '全部', count: tabCountMap.value.all ?? 0 },
    ...versionTabs.value,
    { name: 'warning', label: '到期预警', count: tabCountMap.value.warning ?? 0 }
  ]);

  const tabCountMap = ref<Record<string, number>>({});

  const currentVersionCode = computed(() => {
    const tab = tabs.value.find((t) => t.name === activeTab.value);
    return tab?.versionCode;
  });

  const switchTab = async (name: string) => {
    if (activeTab.value === name) return;
    activeTab.value = name;
    await nextTick();
    tableRef.value?.reload?.({ page: 1 });
  };

  const handleSearch = (where?: CustomerParam) => {
    tableRef.value?.reload?.({ where, page: 1 });
  };

  const loadVersionTabs = async () => {
    try {
      const list = await listProductVersions();
      versionTabs.value = (list || [])
        .filter((v: any) => v.status === 1)
        .map((v: any) => ({
          name: v.versionCode,
          label: v.versionName,
          versionCode: v.versionCode,
          count: 0
        }));
    } catch {
      // ignore
    }
  };

  const loadTabCounts = async () => {
    try {
      const queries: { key: string; params: CustomerParam }[] = [
        { key: 'all', params: { lifecycle: 'paid', page: 1, limit: 1 } },
        ...versionTabs.value.map((t) => ({
          key: t.name,
          params: { lifecycle: 'paid', versionCode: t.versionCode, page: 1, limit: 1 } as CustomerParam
        })),
        { key: 'warning', params: { lifecycle: 'paid', expireWarning: true, page: 1, limit: 1 } }
      ];
      const results = await Promise.all(
        queries.map((q) => pageCustomers(q.params).catch(() => ({ count: 0 })))
      );
      const map: Record<string, number> = {};
      queries.forEach((q, i) => {
        map[q.key] = (results[i] as any)?.count ?? 0;
      });
      tabCountMap.value = map;

      versionTabs.value.forEach((t) => {
        t.count = map[t.name] ?? 0;
      });
    } catch {
      // ignore
    }
  };

  onMounted(async () => {
    await loadVersionTabs();
    loadTabCounts();
  });
</script>

<style scoped>
  .paid-toolbar {
    display: flex;
    align-items: center;
    width: 100%;
  }

  .paid-tabs {
    display: flex;
    gap: 4px;
  }

  .paid-tab-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    color: var(--el-text-color-regular);
    transition: all 0.2s;
    user-select: none;
  }

  .paid-tab-item:hover {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .paid-tab-item.active {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-8);
    font-weight: 600;
  }

  .paid-tab-item :deep(.tab-badge .el-badge__content) {
    border: none;
  }
</style>
