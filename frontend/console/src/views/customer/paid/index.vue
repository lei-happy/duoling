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
  import { ref, computed, reactive, onMounted } from 'vue';
  import CustomerSearch from '../components/customer-search.vue';
  import CustomerTable from '../components/customer-table.vue';
  import { pageCustomers } from '@/api/customer';
  import type { CustomerParam } from '@/api/customer/model';

  defineOptions({ name: 'CustomerPaid' });

  const tableRef = ref<InstanceType<typeof CustomerTable> | null>(null);
  const activeTab = ref('all');

  const tabCounts = reactive({ all: 0, pro: 0, enterprise: 0, warning: 0 });

  const tabs = computed(() => [
    { name: 'all', label: '全部', count: tabCounts.all },
    { name: 'pro', label: '专业版', count: tabCounts.pro },
    { name: 'enterprise', label: '旗舰版', count: tabCounts.enterprise },
    { name: 'warning', label: '到期预警', count: tabCounts.warning }
  ]);

  const currentVersionCode = computed(() => {
    if (activeTab.value === 'pro') return 'pro';
    if (activeTab.value === 'enterprise') return 'enterprise';
    return undefined;
  });

  const switchTab = (name: string) => {
    if (activeTab.value === name) return;
    activeTab.value = name;
    tableRef.value?.reload?.({ page: 1 });
  };

  const handleSearch = (where?: CustomerParam) => {
    tableRef.value?.reload?.({ where, page: 1 });
  };

  const loadTabCounts = async () => {
    try {
      const queries = [
        { key: 'all' as const, params: { lifecycle: 'paid', page: 1, limit: 1 } },
        { key: 'pro' as const, params: { lifecycle: 'paid', versionCode: 'pro', page: 1, limit: 1 } },
        { key: 'enterprise' as const, params: { lifecycle: 'paid', versionCode: 'enterprise', page: 1, limit: 1 } },
        { key: 'warning' as const, params: { lifecycle: 'paid', expireWarning: true, page: 1, limit: 1 } }
      ];
      const results = await Promise.all(
        queries.map((q) => pageCustomers(q.params).catch(() => ({ count: 0 })))
      );
      queries.forEach((q, i) => {
        tabCounts[q.key] = (results[i] as any)?.count ?? 0;
      });
    } catch {
      // ignore
    }
  };

  onMounted(() => {
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
