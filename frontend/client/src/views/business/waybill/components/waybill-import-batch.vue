<template>
  <el-drawer
    title="导入批次明细"
    :model-value="visible"
    direction="rtl"
    size="900px"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <div v-if="batch" class="batch-summary">
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="批次ID">{{ batch.id }}</el-descriptions-item>
        <el-descriptions-item label="文件名">{{ batch.fileName || '--' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(batch.status)" size="small">
            {{ statusText(batch.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总数">{{ batch.totalCount }}</el-descriptions-item>
        <el-descriptions-item label="导入成功">
          <el-tag type="success" size="small">{{ batch.successCount }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="导入失败">
          <el-tag v-if="batch.failCount" type="danger" size="small">
            {{ batch.failCount }}
          </el-tag>
          <span v-else>0</span>
        </el-descriptions-item>
        <el-descriptions-item label="计算成功">{{ batch.calcSuccessCount }}</el-descriptions-item>
        <el-descriptions-item label="计算异常">
          <el-tag v-if="batch.calcExceptionCount" type="warning" size="small">
            {{ batch.calcExceptionCount }}
          </el-tag>
          <span v-else>0</span>
        </el-descriptions-item>
        <el-descriptions-item label="时间">{{ batch.createdAt }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <div class="batch-rows">
      <div class="rows-head">
        <span class="rows-cap">行明细</span>
        <el-radio-group v-model="filterStatus" size="small" @change="onFilterChange">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="success">成功</el-radio-button>
          <el-radio-button value="failed">失败</el-radio-button>
        </el-radio-group>
      </div>
      <el-table
        v-loading="loading"
        :data="rows"
        border
        stripe
        size="small"
        max-height="460"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <pre class="raw-json">{{ formatJson(row.rawData) }}</pre>
          </template>
        </el-table-column>
        <el-table-column prop="rowNo" label="行号" width="64" align="center" />
        <el-table-column prop="validateStatus" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.validateStatus === 'success' ? 'success' : row.validateStatus === 'failed' ? 'danger' : 'info'"
              size="small"
            >
              {{ row.validateStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="waybillId" label="运单ID" width="100" align="center">
          <template #default="{ row }">
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
        </el-table-column>
        <el-table-column prop="calcStatus" label="计算状态" width="100" align="center" />
        <el-table-column prop="validateMessage" label="错误/提示" min-width="220" />
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.validateStatus === 'failed'"
              text
              type="primary"
              @click="goException(row)"
            >
              异常中心
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager-row">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadRows"
        />
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    getImportBatch,
    listImportRows,
    type ImportBatchSummary,
    type ImportRowItem
  } from '@/api/waybill';

  const props = defineProps<{
    visible: boolean;
    batchId: number | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const router = useRouter();

  const batch = ref<ImportBatchSummary | null>(null);
  const rows = ref<ImportRowItem[]>([]);
  const loading = ref(false);
  const filterStatus = ref<string>('');
  const page = ref(1);
  const pageSize = ref(50);
  const total = ref(0);

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const statusType = (s?: string) => {
    if (s === 'done') return 'success';
    if (s === 'failed') return 'danger';
    if (s === 'imported') return 'warning';
    return 'info';
  };

  const statusText = (s?: string) => {
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

  const formatJson = (val: unknown): string => {
    if (val == null) return '--';
    try {
      return JSON.stringify(val, null, 2);
    } catch (_) {
      return String(val);
    }
  };

  const loadBatch = async () => {
    if (!props.batchId) return;
    try {
      batch.value = await getImportBatch(props.batchId);
    } catch (_) {
      batch.value = null;
    }
  };

  const loadRows = async () => {
    if (!props.batchId) return;
    loading.value = true;
    try {
      const data = await listImportRows(props.batchId, {
        validateStatus: filterStatus.value || undefined,
        page: page.value,
        limit: pageSize.value
      });
      rows.value = data?.list ?? [];
      total.value = data?.total ?? 0;
    } catch (_) {
      rows.value = [];
      total.value = 0;
    } finally {
      loading.value = false;
    }
  };

  const onOpen = () => {
    page.value = 1;
    filterStatus.value = '';
    loadBatch();
    loadRows();
  };

  const onFilterChange = () => {
    page.value = 1;
    loadRows();
  };

  const goWaybill = (id: number) => {
    router.push({ path: '/business/waybill', query: { focus: id } });
  };

  const goException = (row: ImportRowItem) => {
    router.push({
      path: '/billing/exception',
      query: row.waybillId ? { waybillId: row.waybillId } : { batchId: row.batchId }
    });
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) onOpen();
    }
  );
</script>

<style scoped lang="scss">
  .batch-summary {
    margin-bottom: 16px;
  }
  .batch-rows {
    margin-top: 8px;
  }
  .rows-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .rows-cap {
    font-size: 14px;
    font-weight: 600;
  }
  .raw-json {
    background: var(--el-fill-color-light);
    border-radius: 6px;
    padding: 8px 12px;
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 200px;
    overflow: auto;
  }
  .pager-row {
    margin-top: 8px;
    text-align: right;
  }
</style>
