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
            <el-form-item>
              <el-text type="info" size="small">
                常用审批/支付作业请前往
                <el-link type="primary" :underline="false" @click="goWorkbench">
                  「费用工作台」
                </el-link>
              </el-text>
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
            详情
          </el-link>
          <template v-if="getPrimaryAction(row)">
            <el-divider direction="vertical" />
            <el-link
              :type="getPrimaryAction(row)!.buttonType as any"
              :underline="false"
              v-permission="getPrimaryAction(row)!.permission"
              @click="triggerAction(row, getPrimaryAction(row)!)"
            >
              {{ getPrimaryAction(row)!.label }}
            </el-link>
          </template>
          <template v-if="canCancel(row)">
            <el-divider direction="vertical" />
            <el-link
              type="danger"
              :underline="false"
              v-permission="'operation:task-finance:cancel'"
              @click="cancelRow(row)"
            >
              撤销
            </el-link>
          </template>
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

    <!-- 标记已支付弹窗（行内主按钮触发） -->
    <action-pay
      v-model:visible="payVisible"
      :docs="payTargetDocs"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FinanceEdit from './components/finance-edit.vue';
  import ActionPay from '../task-finance-workbench/components/action-pay.vue';
  import {
    approveFinanceDoc,
    cancelFinanceDoc,
    pageFinanceDocs,
    submitFinanceDoc
  } from '@/api/operation/task-finance';
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
  import { getPrimaryFinanceAction } from './task-finance-actions';
  import type { FinanceActionConfig } from './task-finance-actions';

  defineOptions({ name: 'OperationTaskFinance' });

  const router = useRouter();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<TaskFinanceDocParam>({});

  const editVisible = ref(false);
  const editingDocId = ref<number | null>(null);
  const currentTask = ref<Task | null>(null);

  const payVisible = ref(false);
  const payTargetDocs = ref<TaskFinanceDocListItem[]>([]);

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
      width: 200,
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

  const goWorkbench = () => {
    router.push('/operation/task-finance-workbench');
  };

  const openDetail = async (row: TaskFinanceDocListItem) => {
    try {
      const t = await getTask(row.taskId);
      currentTask.value = t;
      editingDocId.value = row.id;
      editVisible.value = true;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '打开失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  // ============================================
  // 行内语义化动作
  // ============================================
  const getPrimaryAction = (
    row: TaskFinanceDocListItem
  ): FinanceActionConfig | null => {
    return getPrimaryFinanceAction(row.status);
  };

  const canCancel = (row: TaskFinanceDocListItem) =>
    row.status === 0 || row.status === 1 || row.status === 2;

  const triggerAction = async (
    row: TaskFinanceDocListItem,
    act: FinanceActionConfig
  ) => {
    if (act.dialog === 'pay') {
      payTargetDocs.value = [row];
      payVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction(row, act);
    }
  };

  const runConfirmAction = async (
    row: TaskFinanceDocListItem,
    act: FinanceActionConfig
  ) => {
    const confirmMessages: Record<string, string> = {
      submit: `确认提交费用单「${row.docNo}」进行审批？`,
      approve: `确认审批通过费用单「${row.docNo}」？`
    };
    try {
      await ElMessageBox.confirm(
        confirmMessages[act.key] || `确认执行「${act.label}」？`,
        '操作确认',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    try {
      if (act.key === 'submit') {
        await submitFinanceDoc(row.id);
      } else if (act.key === 'approve') {
        await approveFinanceDoc(row.id);
      }
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      reload();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const cancelRow = async (row: TaskFinanceDocListItem) => {
    try {
      const { value: reason } = await ElMessageBox.prompt(
        '请输入撤销原因（可选）',
        '撤销费用单',
        { confirmButtonText: '确定', cancelButtonText: '不撤销' }
      );
      await cancelFinanceDoc(row.id, reason || undefined);
      EleMessage.success({ message: '已撤销', plain: true });
      reload();
    } catch (err: unknown) {
      const e = err as { message?: string } | string | undefined;
      if (e === 'cancel') return;
      const msg = (typeof e === 'object' && e?.message) || '';
      if (msg) EleMessage.error({ message: msg, plain: true });
    }
  };
</script>
