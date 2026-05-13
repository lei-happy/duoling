<template>
  <ele-page>
    <ele-card class="import-page-card">
      <div class="import-page-header">
        <div class="import-page-title">
          <span class="title-text">运单批量导入</span>
          <span class="title-tip">
            支持 .xlsx；同一行多车型可用 + 拼接（品牌/车型/数量列同步对齐）
          </span>
        </div>
        <div class="import-page-actions">
          <el-upload
            :show-file-list="false"
            accept=".xlsx,.xls"
            :before-upload="beforeUpload"
            :http-request="onUpload"
            :disabled="uploading"
          >
            <el-button type="primary" :loading="uploading">上传 Excel</el-button>
          </el-upload>
          <el-button @click="loadBatches">刷新</el-button>
        </div>
      </div>
    </ele-card>

    <ele-card class="import-page-card">
      <div class="batches-cap">导入批次</div>
      <el-table
        v-loading="loading"
        :data="batches"
        border
        stripe
        size="small"
        @row-click="onRowClick"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="fileName" label="文件名" min-width="180" />
        <el-table-column prop="totalCount" label="总数" width="80" align="center" />
        <el-table-column prop="successCount" label="导入成功" width="92" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.successCount }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failCount" label="导入失败" width="92" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.failCount > 0" type="danger" size="small">
              {{ row.failCount }}
            </el-tag>
            <span v-else>0</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="170" align="center" />
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              @click.stop="openBatch(row)"
            >
              查看明细
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager-row">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="loadBatches"
        />
      </div>
    </ele-card>

    <waybill-import-batch
      v-model:visible="batchDetailVisible"
      :batch-id="activeBatchId"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import type { UploadRequestOptions } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    importWaybillExcel,
    pageImportBatches,
    type ImportBatchSummary
  } from '@/api/waybill';
  import WaybillImportBatch from '../components/waybill-import-batch.vue';

  defineOptions({ name: 'WaybillImportPage' });

  const uploading = ref(false);
  const loading = ref(false);
  const batches = ref<ImportBatchSummary[]>([]);
  const page = ref(1);
  const pageSize = ref(20);
  const total = ref(0);
  const batchDetailVisible = ref(false);
  const activeBatchId = ref<number | null>(null);

  const statusType = (s?: string) => {
    if (s === 'done') return 'success';
    if (s === 'failed') return 'danger';
    if (s === 'imported') return 'warning';
    if (s === 'importing' || s === 'calculating') return 'primary';
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

  const beforeUpload = (file: File) => {
    const ok = /\.(xlsx|xls)$/i.test(file.name);
    if (!ok) {
      EleMessage.warning({ message: '仅支持 .xlsx / .xls', plain: true });
      return false;
    }
    return true;
  };

  const onUpload = async (opts: UploadRequestOptions) => {
    uploading.value = true;
    try {
      const data = await importWaybillExcel(opts.file as File);
      EleMessage.success({
        message: `导入完成：成功 ${data?.successCount ?? 0}，失败 ${data?.failCount ?? 0}`,
        plain: true
      });
      await loadBatches();
      if (data?.batchId) {
        activeBatchId.value = data.batchId;
        batchDetailVisible.value = true;
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      uploading.value = false;
    }
  };

  const loadBatches = async () => {
    loading.value = true;
    try {
      const data = await pageImportBatches(page.value, pageSize.value);
      batches.value = data?.list ?? [];
      total.value = data?.total ?? 0;
    } catch (_) {
      batches.value = [];
      total.value = 0;
    } finally {
      loading.value = false;
    }
  };

  const openBatch = (row: ImportBatchSummary) => {
    activeBatchId.value = row.id;
    batchDetailVisible.value = true;
  };

  const onRowClick = (row: ImportBatchSummary) => openBatch(row);

  onMounted(() => {
    loadBatches();
  });
</script>

<style scoped lang="scss">
  .import-page-card {
    margin-bottom: 16px;
  }
  .import-page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }
  .import-page-title {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .title-text {
    font-size: 16px;
    font-weight: 600;
  }
  .title-tip {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
  .import-page-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .batches-cap {
    margin-bottom: 12px;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .pager-row {
    margin-top: 12px;
    text-align: right;
  }
</style>
