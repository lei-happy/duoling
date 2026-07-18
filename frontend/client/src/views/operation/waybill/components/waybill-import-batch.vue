<template>
  <el-drawer
    :model-value="visible"
    direction="rtl"
    size="min(960px, 92vw)"
    class="waybill-import-drawer"
    :destroy-on-close="true"
    @update:model-value="updateVisible"
  >
    <template #header>
      <div class="drawer-header-block">
        <div class="drawer-title">导入批次明细</div>
        <div class="drawer-sub" :title="batch?.fileName || ''">
          {{ batch?.fileName || '—' }}
        </div>
      </div>
    </template>

    <div v-loading="batchLoading" class="drawer-body">
      <ele-card
        v-if="batch"
        shadow="never"
        class="summary-card"
        :body-style="{ padding: '12px 16px' }"
      >
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="批次 ID">
            {{ batch.id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="batchStatusType(batch.status)" size="small">
              {{ batchStatusText(batch.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总数">
            {{ batch.totalCount }}
          </el-descriptions-item>
          <el-descriptions-item label="导入成功">
            <el-tag type="success" size="small">{{
              batch.successCount
            }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="导入失败">
            <el-tag v-if="batch.failCount" type="danger" size="small">
              {{ batch.failCount }}
            </el-tag>
            <span v-else>0</span>
          </el-descriptions-item>
          <el-descriptions-item label="计算成功">
            {{ batch.calcSuccessCount }}
          </el-descriptions-item>
          <el-descriptions-item label="计算异常">
            <el-tag v-if="batch.calcExceptionCount" type="warning" size="small">
              {{ batch.calcExceptionCount }}
            </el-tag>
            <span v-else>0</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDateTime(batch.createdAt) }}
          </el-descriptions-item>
        </el-descriptions>
      </ele-card>

      <ele-card
        shadow="never"
        class="rows-card"
        :body-style="{ padding: '12px 16px 16px' }"
      >
        <div class="rows-toolbar">
          <span class="rows-cap">行明细</span>
          <el-radio-group
            v-model="filterStatus"
            size="small"
            @change="onFilterChange"
          >
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="success">成功</el-radio-button>
            <el-radio-button value="failed">失败</el-radio-button>
          </el-radio-group>
        </div>
        <ele-pro-table
          ref="rowsTableRef"
          row-key="id"
          :columns="rowColumns"
          :datasource="rowDatasource"
          :show-overflow-tooltip="true"
          cache-key="WaybillImportRowsTable"
        >
          <template #expand="{ row }">
            <div class="expand-wrap">
              <div class="expand-label">原始行数据</div>
              <pre class="raw-json">{{ formatJson(row.rawData) }}</pre>
            </div>
          </template>
          <template #validateStatus="{ row }">
            <el-tag :type="validateStatusType(row.validateStatus)" size="small">
              {{ validateStatusText(row.validateStatus) }}
            </el-tag>
          </template>
          <template #waybillId="{ row }">
            <el-button
              v-if="row.waybillId"
              text
              type="primary"
              @click="goWaybill(row.waybillId)"
            >
              #{{ row.waybillId }}
            </el-button>
            <span v-else>--</span>
          </template>
          <template #calcStatus="{ row }">
            <el-tag :type="calcStatusType(row.calcStatus)" size="small">
              {{ calcStatusText(row.calcStatus) }}
            </el-tag>
          </template>
        </ele-pro-table>
      </ele-card>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, watch, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import type { EleProTable } from 'ele-admin-plus';
  import type { DatasourceFunction } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    getImportBatch,
    listImportRows,
    type ImportBatchSummary
  } from '@/api/waybill';
  import { formatDateTime } from '@/utils/date-util';

  const props = defineProps<{
    visible: boolean;
    batchId: number | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const router = useRouter();
  const rowsTableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const batch = ref<ImportBatchSummary | null>(null);
  const batchLoading = ref(false);
  const filterStatus = ref<string>('');

  const rowColumns = ref([
    {
      type: 'expand',
      columnKey: 'expand',
      width: 44,
      align: 'center',
      slot: 'expand',
      formatter: (row: Record<string, unknown>) => formatJson(row.rawData)
    },
    { prop: 'rowNo', label: '行号', width: 72, align: 'center' },
    {
      columnKey: 'validateStatus',
      prop: 'validateStatus',
      label: '状态',
      width: 88,
      align: 'center',
      slot: 'validateStatus'
    },
    {
      columnKey: 'waybillId',
      prop: 'waybillId',
      label: '计划 ID',
      width: 108,
      align: 'center',
      slot: 'waybillId'
    },
    {
      columnKey: 'calcStatus',
      prop: 'calcStatus',
      label: '计算状态',
      width: 100,
      align: 'center',
      slot: 'calcStatus'
    },
    {
      prop: 'validateMessage',
      label: '错误/提示',
      minWidth: 200
    }
  ]);

  const rowDatasource: DatasourceFunction = ({ pages }) => {
    const bid = props.batchId;
    if (!bid) {
      return Promise.resolve({ list: [], count: 0 });
    }
    return listImportRows(bid, {
      validateStatus: filterStatus.value || undefined,
      page: pages.page,
      limit: pages.limit ?? 50
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.total ?? 0
    }));
  };

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const batchStatusType = (s?: string) => {
    if (s === 'done') return 'success';
    if (s === 'failed') return 'danger';
    if (s === 'imported') return 'warning';
    if (s === 'importing' || s === 'calculating') return 'primary';
    return 'info';
  };

  const batchStatusText = (s?: string) => {
    const m: Record<string, string> = {
      pending: '待开始',
      importing: '导入中',
      imported: '已导入',
      calculating: '计算中',
      done: '已完成',
      failed: '失败'
    };
    return s ? m[s] || s : '--';
  };

  const validateStatusType = (s?: string) => {
    if (s === 'success') return 'success';
    if (s === 'failed') return 'danger';
    return 'info';
  };

  const validateStatusText = (s?: string) => {
    const m: Record<string, string> = {
      pending: '待处理',
      success: '成功',
      failed: '失败'
    };
    return s ? m[s] || s : '--';
  };

  const calcStatusType = (s?: string) => {
    if (s === 'calculated') return 'success';
    if (s === 'pending') return 'info';
    if (s === 'calculating') return 'primary';
    if (s === 'exception') return 'danger';
    if (s === 'locked') return 'warning';
    return 'info';
  };

  const calcStatusText = (s?: string) => {
    const m: Record<string, string> = {
      pending: '待计算',
      calculating: '计算中',
      calculated: '已计算',
      exception: '异常',
      locked: '已锁定'
    };
    return s ? m[s] || s : '--';
  };

  const formatJson = (val: unknown): string => {
    if (val == null) return '--';
    try {
      return JSON.stringify(val, null, 2);
    } catch (_) {
      return String(val);
    }
  };

  const loadBatch = async () => {
    if (!props.batchId) {
      batch.value = null;
      return;
    }
    batchLoading.value = true;
    try {
      batch.value = await getImportBatch(props.batchId);
    } catch (_) {
      batch.value = null;
    } finally {
      batchLoading.value = false;
    }
  };

  const onFilterChange = () => {
    nextTick(() => {
      rowsTableRef.value?.reload?.({ page: 1 });
    });
  };

  const goWaybill = (id: number) => {
    router.push({ path: '/operation/waybill', query: { focus: String(id) } });
  };

  watch(
    () => [props.visible, props.batchId] as const,
    ([v, id]) => {
      if (v && id) {
        filterStatus.value = '';
        loadBatch();
        nextTick(() => {
          rowsTableRef.value?.reload?.({ page: 1 });
        });
      }
    }
  );
</script>

<style scoped lang="scss">
  .waybill-import-drawer {
    :deep(.el-drawer__header) {
      margin-bottom: 0;
      padding: 16px 20px 12px;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }
    :deep(.el-drawer__body) {
      padding: 16px 20px 20px;
    }
  }
  .drawer-header-block {
    padding-right: 28px;
  }
  .drawer-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .drawer-sub {
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .drawer-body {
    min-height: 200px;
  }
  .summary-card {
    margin-bottom: 16px;
    border-radius: 8px;
  }
  .rows-card {
    border-radius: 8px;
  }
  .rows-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 12px;
  }
  .rows-cap {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .expand-wrap {
    padding: 8px 12px 12px 36px;
  }
  .expand-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
  }
  .raw-json {
    background: var(--el-fill-color-light);
    border-radius: 6px;
    padding: 10px 12px;
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 220px;
    overflow: auto;
  }
</style>
