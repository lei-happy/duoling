<template>
  <ele-page>
    <ele-card class="import-page-card">
      <div class="import-page-header">
        <div class="import-page-title">
          <span class="title-text">运单批量导入</span>
          <span class="title-tip">
            请先下载模板按列填写；支持 .xlsx / .xls。客户名称须与客户档案一致；出发地/目的地按行政区逐级用
            / 填写，无需编码。同一行多车须用 + 对齐「商品车品牌 / 车型 / VIN码」三列；旧模板仍支持「数量」列（将按台数拆行并生成占位
            VIN）。
          </span>
        </div>
      </div>
    </ele-card>

    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="WaybillImportBatchesTable"
      >
        <template #toolbar>
          <div class="import-toolbar-btns">            
            <el-upload
              :show-file-list="false"
              accept=".xlsx,.xls"
              :before-upload="beforeUpload"
              :http-request="onUpload"
              :disabled="uploading"
            >
              <el-button type="primary" :loading="uploading">
                上传 Excel
              </el-button>
            </el-upload>
            <el-button type="primary" plain @click="onDownloadTemplate">
              下载模板
            </el-button>
          </div>
        </template>
        <template #successCount="{ row }">
          <el-tag type="success" size="small">{{ row.successCount }}</el-tag>
        </template>
        <template #failCount="{ row }">
          <el-tag v-if="row.failCount > 0" type="danger" size="small">
            {{ row.failCount }}
          </el-tag>
          <span v-else>0</span>
        </template>
        <template #status="{ row }">
          <el-tag :type="statusType(row.status)" size="small">
            {{ statusText(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            type="link"
            :wrap="false"
            :items="[
              {
                title: '查看明细',
                onClick: () => openBatch(row)
              }
            ]"
          />
        </template>
      </ele-pro-table>
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
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    importWaybillExcel,
    pageImportBatches,
    downloadWaybillImportTemplate,
    type ImportBatchSummary
  } from '@/api/waybill';
  import { formatDateTime } from '@/utils/date-util';
  import WaybillImportBatch from '../components/waybill-import-batch.vue';

  defineOptions({ name: 'WaybillImportPage' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const uploading = ref(false);
  const batchDetailVisible = ref(false);
  const activeBatchId = ref<number | null>(null);

  const columns = ref([
    { prop: 'id', label: 'ID', width: 80, align: 'center' },
    { prop: 'fileName', label: '文件名', minWidth: 200 },
    { prop: 'totalCount', label: '总数', width: 80, align: 'center' },
    {
      columnKey: 'successCount',
      prop: 'successCount',
      label: '导入成功',
      width: 96,
      align: 'center',
      slot: 'successCount'
    },
    {
      columnKey: 'failCount',
      prop: 'failCount',
      label: '导入失败',
      width: 96,
      align: 'center',
      slot: 'failCount'
    },
    {
      columnKey: 'status',
      prop: 'status',
      label: '状态',
      width: 110,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '时间',
      width: 176,
      align: 'center',
      formatter: (row: { createdAt?: string }) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 112,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageImportBatches(pages.page, pages.limit ?? 20).then((res) => ({
      list: res?.list ?? [],
      count: res?.total ?? 0
    }));
  };

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

  const reloadTable = () => {
    tableRef.value?.reload?.();
  };

  const beforeUpload = (file: File) => {
    const ok = /\.(xlsx|xls)$/i.test(file.name);
    if (!ok) {
      EleMessage.warning({ message: '仅支持 .xlsx / .xls', plain: true });
      return false;
    }
    return true;
  };

  const onDownloadTemplate = async () => {
    try {
      await downloadWaybillImportTemplate();
      EleMessage.success({ message: '模板已开始下载', plain: true });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '下载失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const onUpload = async (opts: UploadRequestOptions) => {
    uploading.value = true;
    try {
      const data = await importWaybillExcel(opts.file as File);
      EleMessage.success({
        message: `导入完成：成功 ${data?.successCount ?? 0}，失败 ${data?.failCount ?? 0}`,
        plain: true
      });
      reloadTable();
      if (data?.batchId) {
        activeBatchId.value = data.batchId;
        batchDetailVisible.value = true;
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '上传失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      uploading.value = false;
    }
  };

  const openBatch = (row: ImportBatchSummary) => {
    activeBatchId.value = row.id;
    batchDetailVisible.value = true;
  };

  onMounted(() => {
    reloadTable();
  });
</script>

<style scoped lang="scss">
  .import-page-card {
    margin-bottom: 16px;
  }
  .import-page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
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
    line-height: 1.5;
  }
  .import-toolbar-btns {
    display: inline-flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }
</style>
