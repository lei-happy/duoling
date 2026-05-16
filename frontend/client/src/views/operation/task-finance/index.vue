<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        cache-key="OperationTaskFinanceTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="单据号/收款人"
                clearable
                style="width: 200px"
                @change="reload()"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.docType"
                placeholder="单据类型"
                clearable
                style="width: 120px"
                @change="reload()"
              >
                <el-option
                  v-for="o in FIN_DOC_TYPE_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                style="width: 120px"
                @change="reload()"
              >
                <el-option
                  v-for="o in FIN_STATUS_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.payeeType"
                placeholder="收款类型"
                clearable
                style="width: 120px"
                @change="reload()"
              >
                <el-option
                  v-for="o in PAYEE_TYPE_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </template>

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
          <el-link type="primary" :underline="false" @click="openDetail(row)">
            详情/操作
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>

    <finance-edit
      v-if="currentTask"
      v-model:visible="editVisible"
      :task="currentTask"
      :doc-id="editingDocId"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FinanceEdit from './components/finance-edit.vue';
  import { pageFinanceDocs } from '@/api/operation/task-finance';
  import type {
    TaskFinanceDocListItem,
    TaskFinanceDocParam
  } from '@/api/operation/task-finance/model';
  import { getTask } from '@/api/operation/task';
  import type { Task } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    FIN_DOC_TYPE_MAP,
    FIN_DOC_TYPE_OPTIONS,
    FIN_STATUS_MAP,
    FIN_STATUS_OPTIONS,
    PAYEE_TYPE_OPTIONS
  } from './status-config';

  defineOptions({ name: 'OperationTaskFinance' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<TaskFinanceDocParam>({});

  const editVisible = ref(false);
  const editingDocId = ref<number | null>(null);
  const currentTask = ref<Task | null>(null);

  const columns = computed<Columns>(() => [
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
      prop: 'actualPayTime',
      label: '实际支付',
      width: 160,
      align: 'center',
      formatter: (row) => formatDateTime(row.actualPayTime) || '--'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 160,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt) || '--'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 110,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageFinanceDocs({ ...where, ...pages }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = () => {
    nextTick(() => tableRef.value?.reload?.());
  };

  const openDetail = async (row: TaskFinanceDocListItem) => {
    try {
      // 先取所属任务单（编辑组件需要 task 信息）
      const t = await getTask(row.taskId);
      currentTask.value = t;
      editingDocId.value = row.id;
      editVisible.value = true;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '打开失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };
</script>
