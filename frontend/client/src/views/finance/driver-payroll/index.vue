<template>
  <ele-page>
    <payroll-search @search="(next) => reload(next, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="FinanceDriverPayrollTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新建工资单',
                permission: 'finance:driver-payroll:create',
                onClick: () => (createVisible = true)
              }
            ]"
          />
        </template>

        <template #driver="{ row }">
          <div>{{ row.driverName || '--' }}</div>
          <div v-if="row.driverPhone" class="muted">{{ row.driverPhone }}</div>
        </template>

        <template #period="{ row }">
          <div v-if="row.periodStart || row.periodEnd">
            {{ formatDate(row.periodStart) }} ~ {{ formatDate(row.periodEnd) }}
          </div>
          <div class="muted">
            {{ row.payrollModelLabel }} · {{ row.periodTypeLabel }}
          </div>
        </template>

        <template #gross="{ row }">
          <div class="num-cell">¥ {{ formatMoney(row.grossAmount) }}</div>
          <div class="muted">
            提成 {{ formatMoney(row.totalCommissionAmount) }}
          </div>
        </template>

        <template #deduction="{ row }">
          <div v-if="row.totalDeductionAmount" class="num-cell deduct">
            -{{ formatMoney(row.totalDeductionAmount) }}
          </div>
          <div v-if="row.totalPrepaidOffsetAmount" class="num-cell offset">
            抵账 {{ formatMoney(row.totalPrepaidOffsetAmount) }}
          </div>
          <span
            v-if="!row.totalDeductionAmount && !row.totalPrepaidOffsetAmount"
            class="muted"
          >
            无扣减
          </span>
        </template>

        <template #net="{ row }">
          <span class="num-cell strong" :class="{ danger: row.netAmount < 0 }">
            ¥ {{ formatMoney(row.netAmount) }}
          </span>
        </template>

        <template #status="{ row }">
          <el-tag
            :type="(PAYROLL_STATUS_MAP[row.status]?.type as any) || 'info'"
            size="small"
          >
            {{ row.statusLabel || PAYROLL_STATUS_MAP[row.status]?.label }}
          </el-tag>
        </template>

        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <payroll-create v-model:visible="createVisible" @done="onCreated" />

    <payroll-detail
      v-model:visible="detailVisible"
      :payroll-id="detailId"
      @changed="reload()"
    />

    <payroll-pay
      v-model:visible="payVisible"
      :payroll-id="payId"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    CheckCircleOutlined,
    CloudUploadOutlined,
    EyeOutlined,
    FundOutlined
  } from '@/components/icons';
  import PayrollCreate from './components/payroll-create.vue';
  import PayrollDetail from './components/payroll-detail.vue';
  import PayrollPay from './components/payroll-pay.vue';
  import PayrollSearch from './components/payroll-search.vue';
  import {
    approvePayroll,
    pagePayrolls,
    submitPayroll
  } from '@/api/finance/driver-payroll';
  import type {
    PayrollListItem,
    PayrollParam
  } from '@/api/finance/driver-payroll/model';
  import { formatDate } from '@/utils/date-util';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { formatMoney, PAYROLL_STATUS_MAP } from '../status-config';

  defineOptions({ name: 'FinanceDriverPayroll' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<PayrollParam>({});

  const createVisible = ref(false);
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);
  const payVisible = ref(false);
  const payId = ref<number | null>(null);

  const columns = computed<Columns>(() => [
    { prop: 'docNo', label: '工资单号', minWidth: 165 },
    {
      columnKey: 'driver',
      label: '司机',
      minWidth: 140,
      slot: 'driver'
    },
    {
      columnKey: 'period',
      label: '工资周期',
      width: 210,
      align: 'center',
      slot: 'period'
    },
    { prop: 'taskCount', label: '任务数', width: 84, align: 'center' },
    {
      columnKey: 'gross',
      label: '应发合计',
      width: 150,
      align: 'right',
      slot: 'gross'
    },
    {
      columnKey: 'deduction',
      label: '扣减 / 抵账',
      width: 150,
      align: 'right',
      slot: 'deduction'
    },
    {
      columnKey: 'net',
      label: '实发金额',
      width: 140,
      align: 'right',
      slot: 'net'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 160,
      align: 'center',
      formatter: (row) => formatDate(row.createdAt) || '--'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      minWidth: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where: tableWhere }) => {
    return pagePayrolls({ ...(tableWhere || where), ...pages }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = (next?: PayrollParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openDetail = (payrollId: number) => {
    detailId.value = payrollId;
    detailVisible.value = true;
  };

  const openPay = (payrollId: number) => {
    payId.value = payrollId;
    payVisible.value = true;
  };

  const onCreated = (payrollId?: number) => {
    reload();
    if (payrollId) openDetail(payrollId);
  };

  const actionItems = (row: PayrollListItem): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '详情',
        icon: EyeOutlined,
        permission: 'finance:driver-payroll:detail',
        onClick: () => openDetail(row.id)
      }
    ];
    if (row.status === 0) {
      visible.push({
        title: '提交审批',
        icon: CloudUploadOutlined,
        permission: 'finance:driver-payroll:submit',
        onClick: () => submitRow(row)
      });
    }
    if (row.status === 1) {
      visible.push({
        title: '审批通过',
        icon: CheckCircleOutlined,
        permission: 'finance:driver-payroll:approve',
        onClick: () => approveRow(row)
      });
    }
    if (row.status === 2) {
      visible.push({
        title: '登记发放',
        icon: FundOutlined,
        permission: 'finance:driver-payroll:pay',
        onClick: () => openPay(row.id)
      });
    }
    return buildActionColumnItems(visible);
  };

  const runRow = async (
    action: () => Promise<unknown>,
    texts: { loading: string; success: string; fail: string }
  ) => {
    const l = EleMessage.loading({ message: texts.loading, plain: true });
    try {
      await action();
      l.close();
      EleMessage.success({ message: texts.success, plain: true });
      reload();
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || texts.fail;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const submitRow = async (row: PayrollListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认提交工资单「${row.docNo}」进入审批？实发 ¥ ${formatMoney(
          row.netAmount
        )}。`,
        '提交审批',
        {
          type: 'warning',
          confirmButtonText: '提交',
          cancelButtonText: '取消',
          draggable: true
        }
      );
    } catch {
      return;
    }
    await runRow(() => submitPayroll(row.id), {
      loading: '正在提交审批，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approveRow = async (row: PayrollListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认审批通过工资单「${row.docNo}」？通过后即可发放。`,
        '审批通过',
        {
          type: 'warning',
          confirmButtonText: '通过',
          cancelButtonText: '取消',
          draggable: true
        }
      );
    } catch {
      return;
    }
    await runRow(() => approvePayroll(row.id), {
      loading: '正在审批，请稍候…',
      success: '已审批通过，可安排发放',
      fail: '审批失败，请稍后重试'
    });
  };
</script>

<style lang="scss" scoped>
  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .deduct {
    color: var(--el-color-danger);
    font-size: 12px;
  }

  .offset {
    color: var(--el-color-warning);
    font-size: 12px;
  }

  .danger {
    color: var(--el-color-danger);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
</style>
