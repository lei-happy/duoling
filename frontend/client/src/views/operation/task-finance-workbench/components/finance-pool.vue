<!--
  费用单池表格 - 费用工作台核心列表

  Props:
    - status: 当前 Tab 对应的 status
    - primaryActionKey: 该 Tab 行内主动作
    - reloadToken: 外部触发刷新

  支持批量主动作（如批量审批 / 批量撤销），批量支付走单独弹窗。
-->
<template>
  <div class="finance-pool">
    <div class="finance-pool__toolbar">
      <el-input
        v-model="keyword"
        placeholder="单据号 / 收款人"
        clearable
        style="width: 220px"
        @change="doReload"
      />
      <el-select
        v-model="docType"
        placeholder="单据类型"
        clearable
        style="width: 140px"
        @change="doReload"
      >
        <el-option
          v-for="o in FIN_DOC_TYPE_OPTIONS"
          :key="o.value"
          :value="o.value"
          :label="o.label"
        />
      </el-select>
      <el-button
        v-if="primaryAction && selections.length > 0"
        :type="primaryAction.buttonType"
        :icon="Operation"
        v-permission="primaryAction.permission"
        @click="onBatch"
      >
        批量{{ primaryAction.label }} ({{ selections.length }})
      </el-button>
      <el-button :icon="Refresh" plain @click="doReload">刷新</el-button>
    </div>

    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="columns"
      :datasource="datasource"
      :pagination="{ pageSize: 20 }"
      :show-overflow-tooltip="true"
      v-model:selections="selections"
      :cache-key="`OperationFinancePool-${tabKey}`"
    >
      <template #docType="{ row }">
        <el-tag
          :type="(FIN_DOC_TYPE_MAP[row.docType]?.type as any) || 'info'"
          size="small"
        >
          {{ FIN_DOC_TYPE_MAP[row.docType]?.label }}
        </el-tag>
        <el-tag
          v-if="row.isFinal === 1"
          type="danger"
          size="small"
          effect="plain"
          style="margin-left: 4px"
        >
          终结
        </el-tag>
      </template>

      <template #status="{ row }">
        <el-tag
          :type="(FIN_STATUS_MAP[row.status]?.type as any) || 'info'"
          size="small"
        >
          {{ FIN_STATUS_MAP[row.status]?.label }}
        </el-tag>
      </template>

      <template #amounts="{ row }">
        <div style="font-variant-numeric: tabular-nums">
          计划 ¥ {{ Number(row.plannedAmount || 0).toFixed(2) }}
        </div>
        <div
          v-if="row.actualAmount !== null && row.actualAmount !== undefined"
          style="color: var(--el-color-success)"
        >
          实付 ¥ {{ Number(row.actualAmount).toFixed(2) }}
        </div>
      </template>

      <template #action="{ row }">
        <el-link
          type="primary"
          :underline="false"
          @click="emit('openDetail', row)"
        >
          详情
        </el-link>
        <template v-if="primaryAction">
          <el-divider direction="vertical" />
          <el-link
            :type="primaryAction.buttonType as any"
            :underline="false"
            v-permission="primaryAction.permission"
            @click="emit('action', row, primaryAction)"
          >
            {{ primaryAction.label }}
          </el-link>
        </template>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { computed, nextTick, ref, watch } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { Operation, Refresh } from '@element-plus/icons-vue';
  import { pageFinanceDocs } from '@/api/operation/task-finance';
  import type { TaskFinanceDocListItem } from '@/api/operation/task-finance/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    FIN_DOC_TYPE_MAP,
    FIN_DOC_TYPE_OPTIONS,
    FIN_STATUS_MAP
  } from '../../task-finance/status-config';
  import { FIN_ACTION_CONFIGS } from '../../task-finance/task-finance-actions';
  import type {
    FinanceActionConfig,
    FinanceActionKey
  } from '../../task-finance/task-finance-actions';

  const props = defineProps<{
    tabKey: string;
    status: number;
    primaryActionKey: FinanceActionKey | null;
    reloadToken?: number;
  }>();

  const emit = defineEmits<{
    (
      e: 'action',
      row: TaskFinanceDocListItem,
      action: FinanceActionConfig
    ): void;
    (
      e: 'batchAction',
      rows: TaskFinanceDocListItem[],
      action: FinanceActionConfig
    ): void;
    (e: 'openDetail', row: TaskFinanceDocListItem): void;
  }>();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<TaskFinanceDocListItem[]>([]);
  const keyword = ref('');
  const docType = ref<number | undefined>(undefined);

  const primaryAction = computed(() =>
    props.primaryActionKey ? FIN_ACTION_CONFIGS[props.primaryActionKey] : null
  );

  const columns = computed<Columns>(() => [
    { type: 'selection', width: 48, align: 'center' },
    { prop: 'docNo', label: '单据编号', minWidth: 160 },
    { prop: 'taskNo', label: '所属任务单', minWidth: 140 },
    {
      prop: 'docType',
      label: '类型',
      width: 140,
      align: 'center',
      slot: 'docType'
    },
    { prop: 'payeeName', label: '收款人', minWidth: 140 },
    {
      columnKey: 'amounts',
      label: '金额',
      width: 160,
      align: 'right',
      slot: 'amounts'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'plannedPayTime',
      label: '计划支付',
      width: 160,
      align: 'center',
      formatter: (row) => formatDateTime(row.plannedPayTime) || '--'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageFinanceDocs({
      ...pages,
      keyword: keyword.value || undefined,
      docType: docType.value,
      status: props.status
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const doReload = () => {
    nextTick(() => tableRef.value?.reload?.({ page: 1 }));
  };

  watch(
    () => props.reloadToken,
    () => doReload()
  );
  watch(
    () => [props.status, props.primaryActionKey] as const,
    () => doReload()
  );

  const onBatch = () => {
    if (!primaryAction.value || selections.value.length === 0) return;
    emit('batchAction', selections.value, primaryAction.value);
  };
</script>

<style lang="scss" scoped>
  .finance-pool {
    &__toolbar {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
    }
  }
</style>
