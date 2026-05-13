<template>
  <ele-page>
    <div class="exception-stats" v-if="stats">
      <ele-card class="stats-card" v-for="item in statsItems" :key="item.key">
        <div class="stats-label">{{ item.label }}</div>
        <div class="stats-value">{{ item.value }}</div>
      </ele-card>
    </div>

    <ele-card>
      <el-form
        ref="searchForm"
        :model="searchModel"
        size="default"
        @submit.prevent="onSearch"
        inline
      >
        <el-form-item label="异常类型">
          <el-select
            v-model="searchModel.exceptionType"
            placeholder="全部"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="o in EXCEPTION_TYPE_OPTIONS"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchModel.status"
            placeholder="全部"
            clearable
            style="width: 140px"
          >
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="processed" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item label="运单ID">
          <el-input
            v-model.number="searchModel.waybillId"
            placeholder="输入运单ID"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item label="批次ID">
          <el-input
            v-model.number="searchModel.batchId"
            placeholder="导入批次ID"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSearch">查询</el-button>
          <el-button @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <ele-card class="table-card">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :selection="true"
        cache-key="BillingExceptionTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                title: '批量重算',
                onClick: onBatchRecalc,
                disabled: selectedIds.length === 0
              }
            ]"
          />
        </template>
        <template #exceptionType="{ row }">
          <el-tag :type="exceptionTypeTagType(row.exceptionType)" size="small">
            {{ exceptionTypeLabel(row.exceptionType) }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="rowActions(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <el-dialog
      v-model="processDialog.visible"
      :title="processDialog.action === 'resolve' ? '处理异常' : '忽略异常'"
      width="420px"
    >
      <el-form>
        <el-form-item label="处理备注">
          <el-input
            v-model="processDialog.remark"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="onConfirmProcess">确定</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type { ButtonItem } from 'ele-admin-plus/es/ele-buttons/types';
  import {
    pageExceptions,
    statsExceptions,
    resolveException,
    ignoreException,
    batchRecalcExceptions,
    type FreightCalcException,
    type ExceptionStats,
    type ExceptionPageParam
  } from '@/api/billing/engine';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'BillingException' });

  const EXCEPTION_TYPE_OPTIONS = [
    { value: 'AREA_NOT_RECOGNIZED', label: '地区未识别' },
    { value: 'SERIES_NOT_RECOGNIZED', label: '车型未识别' },
    { value: 'CONTRACT_NOT_FOUND', label: '无生效合同' },
    { value: 'RULE_NOT_FOUND', label: '未匹配运价' },
    { value: 'RULE_CONFLICT', label: '规则冲突' },
    { value: 'INVALID_QTY', label: '台数无效' },
    { value: 'WAYBILL_LOCKED', label: '运单锁定' },
    { value: 'IMPORT_VALIDATE_FAILED', label: '导入校验失败' }
  ];

  const exceptionTypeLabel = (t: string) =>
    EXCEPTION_TYPE_OPTIONS.find((o) => o.value === t)?.label ?? t;

  const exceptionTypeTagType = (t: string) => {
    if (t === 'RULE_CONFLICT' || t === 'WAYBILL_LOCKED') return 'warning';
    if (t === 'IMPORT_VALIDATE_FAILED') return 'danger';
    return 'info';
  };

  const statusLabel = (s: string) =>
    s === 'pending' ? '待处理' : s === 'processed' ? '已处理' : '已忽略';
  const statusTagType = (s: string) =>
    s === 'pending' ? 'danger' : s === 'processed' ? 'success' : 'info';

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const stats = ref<ExceptionStats | null>(null);
  const selectedIds = ref<number[]>([]);

  const searchModel = reactive<ExceptionPageParam>({
    exceptionType: '',
    status: '',
    waybillId: undefined,
    batchId: undefined
  });

  const statsItems = computed(() => {
    if (!stats.value) return [];
    const out: { key: string; label: string; value: number }[] = [];
    out.push({
      key: 'pending',
      label: '待处理总数',
      value: stats.value.byStatus?.pending ?? 0
    });
    out.push({
      key: 'processed',
      label: '已处理',
      value: stats.value.byStatus?.processed ?? 0
    });
    out.push({
      key: 'ignored',
      label: '已忽略',
      value: stats.value.byStatus?.ignored ?? 0
    });
    Object.entries(stats.value.pendingByType ?? {}).forEach(([k, v]) =>
      out.push({ key: `t_${k}`, label: exceptionTypeLabel(k), value: v })
    );
    return out;
  });

  const columns = ref([
    { type: 'selection', width: 50, align: 'center', fixed: 'left' },
    { prop: 'id', label: 'ID', width: 80, fixed: 'left' },
    {
      prop: 'exceptionType',
      label: '异常类型',
      width: 130,
      slot: 'exceptionType'
    },
    { prop: 'exceptionMessage', label: '异常描述', minWidth: 280 },
    { prop: 'waybillId', label: '运单ID', width: 100 },
    { prop: 'batchId', label: '批次ID', width: 100 },
    { prop: 'status', label: '状态', width: 90, align: 'center', slot: 'status' },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      prop: 'processedAt',
      label: '处理时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.processedAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 220,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ] as unknown as Columns);

  const loadStats = async () => {
    try {
      stats.value = (await statsExceptions()) ?? null;
    } catch {
      stats.value = null;
    }
  };

  const datasource: DatasourceFunction = async ({ pages, where }) => {
    const params: ExceptionPageParam = {
      ...searchModel,
      ...pages
    } as ExceptionPageParam;
    Object.keys(where ?? {}).forEach((k) => {
      const v = (where as Record<string, unknown>)[k];
      if (v != null && v !== '') (params as Record<string, unknown>)[k] = v;
    });
    Object.keys(params).forEach((k) => {
      const v = (params as Record<string, unknown>)[k];
      if (v == null || v === '')
        delete (params as Record<string, unknown>)[k];
    });
    const res = await pageExceptions(params);
    const raw = res as {
      list?: FreightCalcException[];
      count?: number;
      total?: number;
    };
    const list = raw.list ?? [];
    selectedIds.value = []; // 翻页清空选择
    return { list, count: raw.count ?? raw.total ?? 0 };
  };

  // ele-pro-table 选择回调（注：这里用 emits 监听）
  const onSelectionChange = (rows: FreightCalcException[]) => {
    selectedIds.value = rows.map((r) => r.id);
  };
  // 直接监听 table 实例的 selection-change（ele-admin-plus 透传）
  // 简化处理：让 row click 也允许选中，由 ele-pro-table 自己处理多选

  const onSearch = () => {
    tableRef.value?.reload({ page: 1 });
    loadStats();
  };

  const onReset = () => {
    searchModel.exceptionType = '';
    searchModel.status = '';
    searchModel.waybillId = undefined;
    searchModel.batchId = undefined;
    onSearch();
  };

  const processDialog = reactive({
    visible: false,
    action: 'resolve' as 'resolve' | 'ignore',
    id: 0 as number,
    remark: ''
  });

  const openProcess = (
    row: FreightCalcException,
    action: 'resolve' | 'ignore'
  ) => {
    processDialog.visible = true;
    processDialog.action = action;
    processDialog.id = row.id;
    processDialog.remark = '';
  };

  const onConfirmProcess = async () => {
    try {
      if (processDialog.action === 'resolve') {
        await resolveException(processDialog.id, processDialog.remark);
      } else {
        await ignoreException(processDialog.id, processDialog.remark);
      }
      EleMessage.success({ message: '操作成功', plain: true });
      processDialog.visible = false;
      tableRef.value?.reload();
      loadStats();
    } catch (e: unknown) {
      EleMessage.error({ message: (e as Error).message, plain: true });
    }
  };

  const onBatchRecalc = async () => {
    if (!selectedIds.value.length) return;
    try {
      await ElMessageBox.confirm(
        `确认对选中的 ${selectedIds.value.length} 条异常关联的运单批量重算？`,
        '系统提示',
        { type: 'info' }
      );
      const r = await batchRecalcExceptions(selectedIds.value);
      EleMessage.success({
        message: `已入队 ${r?.recalcCount ?? 0} 个任务`,
        plain: true
      });
      tableRef.value?.reload();
      loadStats();
    } catch {
      // 取消
    }
  };

  const rowActions = (row: FreightCalcException): ButtonItem[] => {
    const acts: ButtonItem[] = [];
    if (row.status === 'pending') {
      acts.push({
        title: '重算',
        onClick: async () => {
          try {
            const r = await batchRecalcExceptions([row.id]);
            EleMessage.success({
              message: `已入队 ${r?.recalcCount ?? 0} 个任务`,
              plain: true
            });
            tableRef.value?.reload();
            loadStats();
          } catch (e: unknown) {
            EleMessage.error({ message: (e as Error).message, plain: true });
          }
        }
      });
      acts.push({ title: '处理', onClick: () => openProcess(row, 'resolve') });
      acts.push({ title: '忽略', onClick: () => openProcess(row, 'ignore') });
    } else {
      acts.push({ title: '已结案', disabled: true, onClick: () => {} });
    }
    return acts;
  };

  onMounted(() => {
    loadStats();
  });

  // 暴露 onSelectionChange，以便后续用 v-on 绑定（ele-pro-table 透传）
  defineExpose({ onSelectionChange });
</script>

<style scoped>
  .exception-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }
  .stats-card {
    text-align: center;
  }
  .stats-label {
    color: #909399;
    font-size: 13px;
  }
  .stats-value {
    color: #303133;
    font-size: 22px;
    font-weight: 600;
    margin-top: 4px;
  }
  .table-card {
    margin-top: 12px;
  }
</style>
