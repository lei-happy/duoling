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
        cache-key="FinanceCustomerSettlementTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="结算单号/客户"
                clearable
                style="width: 190px"
                @change="reload()"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.customerId"
                placeholder="客户"
                clearable
                filterable
                style="width: 200px"
                @change="reload()"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :value="c.id"
                  :label="c.customerName"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                style="width: 110px"
                @change="reload()"
              >
                <el-option
                  v-for="o in SETTLE_STATUS_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-date-picker
                v-model="where.dueBefore"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="到期日早于"
                style="width: 160px"
                @change="reload()"
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="where.onlyUnreceived" @change="reload()">
                只看未收齐
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新建结算单',
                    permission: 'finance:cust-settle:create',
                    onClick: () => (createVisible = true)
                  }
                ]"
              />
            </el-form-item>
          </el-form>
        </template>

        <template #amount="{ row }">
          <div class="num-cell">¥ {{ formatMoney(row.plannedAmount) }}</div>
          <div v-if="row.receivedAmountTotal" class="num-cell sub-received">
            已收 {{ formatMoney(row.receivedAmountTotal) }}
          </div>
        </template>

        <template #unreceived="{ row }">
          <span
            class="num-cell"
            :class="{ danger: row.unreceivedAmount > 0 && isOverdue(row) }"
          >
            ¥ {{ formatMoney(row.unreceivedAmount) }}
          </span>
        </template>

        <template #dueDate="{ row }">
          <span v-if="row.dueDate" :class="{ danger: isOverdue(row) }">
            {{ row.dueDate }}
          </span>
          <span v-else class="muted">按客户账期</span>
        </template>

        <template #invoice="{ row }">
          <el-tag
            v-if="row.invoiceRequired === 1"
            :type="row.invoiceCount ? 'success' : 'warning'"
            size="small"
            effect="plain"
          >
            {{ row.invoiceCount ? `已开 ${row.invoiceCount} 张` : '待开票' }}
          </el-tag>
          <span v-else class="muted">不开票</span>
        </template>

        <template #status="{ row }">
          <el-tag
            :type="(SETTLE_STATUS_MAP[row.status]?.type as any) || 'info'"
            size="small"
          >
            {{ row.statusLabel || SETTLE_STATUS_MAP[row.status]?.label }}
          </el-tag>
        </template>

        <template #action="{ row }">
          <el-link
            type="primary"
            :underline="false"
            v-permission="'finance:cust-settle:detail'"
            @click="openDetail(row.id)"
          >
            详情
          </el-link>
          <template v-if="row.status === 0">
            <el-divider direction="vertical" />
            <el-link
              type="warning"
              :underline="false"
              v-permission="'finance:cust-settle:submit'"
              @click="submitRow(row)"
            >
              提交审批
            </el-link>
          </template>
          <template v-if="row.status === 1">
            <el-divider direction="vertical" />
            <el-link
              type="success"
              :underline="false"
              v-permission="'finance:cust-settle:approve'"
              @click="approveRow(row)"
            >
              审批通过
            </el-link>
          </template>
          <template v-if="row.status === 2">
            <el-divider direction="vertical" />
            <el-link
              type="primary"
              :underline="false"
              v-permission="'finance:cust-settle:receive'"
              @click="openReceive(row.id)"
            >
              登记收款
            </el-link>
          </template>
        </template>
      </ele-pro-table>
    </ele-card>

    <settlement-create
      v-model:visible="createVisible"
      :customers="customers"
      @done="onCreated"
    />

    <settlement-detail
      v-model:visible="detailVisible"
      :settle-id="detailId"
      @changed="reload()"
    />

    <settlement-receive
      v-model:visible="receiveVisible"
      :settle-id="receiveId"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import SettlementCreate from './components/settlement-create.vue';
  import SettlementDetail from './components/settlement-detail.vue';
  import SettlementReceive from './components/settlement-receive.vue';
  import {
    approveSettlement,
    pageSettlements,
    submitSettlement
  } from '@/api/finance/customer-settlement';
  import type {
    SettleListItem,
    SettleParam
  } from '@/api/finance/customer-settlement/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDate } from '@/utils/date-util';
  import {
    formatMoney,
    SETTLE_STATUS_MAP,
    SETTLE_STATUS_OPTIONS
  } from '../status-config';

  defineOptions({ name: 'FinanceCustomerSettlement' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<SettleParam>({});
  const customers = ref<CustomerSelectItem[]>([]);

  const createVisible = ref(false);
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);
  const receiveVisible = ref(false);
  const receiveId = ref<number | null>(null);

  const today = new Date().toISOString().slice(0, 10);

  /** 已过到期日且还有未收金额 = 逾期，列表里标红提醒催收 */
  const isOverdue = (row: SettleListItem) =>
    !!row.dueDate && row.dueDate < today && row.unreceivedAmount > 0;

  const columns = computed<Columns>(() => [
    { prop: 'docNo', label: '结算单号', minWidth: 170 },
    { prop: 'customerName', label: '客户', minWidth: 180 },
    { prop: 'reconCount', label: '对账单', width: 90, align: 'center' },
    {
      columnKey: 'amount',
      label: '结算金额',
      width: 160,
      align: 'right',
      slot: 'amount'
    },
    {
      columnKey: 'unreceived',
      label: '未收金额',
      width: 130,
      align: 'right',
      slot: 'unreceived'
    },
    {
      prop: 'dueDate',
      label: '到期日',
      width: 130,
      align: 'center',
      slot: 'dueDate'
    },
    {
      columnKey: 'invoice',
      label: '开票',
      width: 110,
      align: 'center',
      slot: 'invoice'
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
      width: 180,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageSettlements({ ...where, ...pages }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = () => {
    nextTick(() => tableRef.value?.reload?.());
  };

  const openDetail = (settleId: number) => {
    detailId.value = settleId;
    detailVisible.value = true;
  };

  const openReceive = (settleId: number) => {
    receiveId.value = settleId;
    receiveVisible.value = true;
  };

  const onCreated = (settleId?: number) => {
    reload();
    if (settleId) openDetail(settleId);
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

  const submitRow = async (row: SettleListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认提交结算单「${row.docNo}」进入审批？`,
        '提交审批',
        { type: 'warning', confirmButtonText: '提交', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await runRow(() => submitSettlement(row.id), {
      loading: '正在提交审批，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approveRow = async (row: SettleListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认审批通过结算单「${row.docNo}」？通过后即可收款。`,
        '审批通过',
        { type: 'warning', confirmButtonText: '通过', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await runRow(() => approveSettlement(row.id), {
      loading: '正在审批，请稍候…',
      success: '已审批通过',
      fail: '审批失败，请稍后重试'
    });
  };

  onMounted(async () => {
    try {
      customers.value = (await selectCustomers()) || [];
    } catch {
      // 下拉拉取失败不影响列表，仍可用关键词搜索
    }
  });
</script>

<style lang="scss" scoped>
  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .sub-received {
    color: var(--el-color-success);
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
