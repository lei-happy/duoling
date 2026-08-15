<template>
  <ele-page>
    <carrier-settlement-search
      :carriers="carriers"
      @search="(next) => reload(next, 1)"
    />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="FinanceCarrierSettlementTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新建结算单',
                permission: 'finance:carrier-settle:create',
                onClick: () => (createVisible = true)
              }
            ]"
          />
        </template>

        <template #amount="{ row }">
          <div class="num-cell">¥ {{ formatMoney(row.plannedAmount) }}</div>
          <div v-if="row.isOffsetOnly === 1" class="num-cell offset-tag">
            纯抵账，不实付
          </div>
        </template>

        <template #unpaid="{ row }">
          <span
            class="num-cell"
            :class="{ danger: row.unpaidAmount > 0 && isOverdue(row) }"
          >
            ¥ {{ formatMoney(row.unpaidAmount) }}
          </span>
        </template>

        <template #dueDate="{ row }">
          <span v-if="row.dueDate" :class="{ danger: isOverdue(row) }">
            {{ row.dueDate }}
          </span>
          <span v-else class="muted">未设到期日</span>
        </template>

        <template #account="{ row }">
          <div>{{ row.settlementAccountLabel || '--' }}</div>
          <div v-if="row.bankAccountMasked" class="muted">
            {{ row.bankAccountMasked }}
          </div>
        </template>

        <template #invoice="{ row }">
          <el-tag
            v-if="row.invoiceMatched === 1"
            type="success"
            size="small"
            effect="plain"
          >
            票款相符
          </el-tag>
          <el-tooltip
            v-else
            :content="`还差 ¥ ${formatMoney(row.invoiceGapAmount)} 的进项票`"
          >
            <el-tag type="warning" size="small" effect="plain"> 待收票 </el-tag>
          </el-tooltip>
        </template>

        <template #status="{ row }">
          <el-tag
            :type="
              (CARRIER_SETTLE_STATUS_MAP[row.status]?.type as any) || 'info'
            "
            size="small"
          >
            {{
              row.statusLabel || CARRIER_SETTLE_STATUS_MAP[row.status]?.label
            }}
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

    <carrier-settlement-create
      v-model:visible="createVisible"
      :carriers="carriers"
      @done="onCreated"
    />

    <carrier-settlement-detail
      v-model:visible="detailVisible"
      :settle-id="detailId"
      @changed="reload()"
    />

    <carrier-settlement-pay
      v-model:visible="payVisible"
      :settle-id="payId"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
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
  import CarrierSettlementCreate from './components/carrier-settlement-create.vue';
  import CarrierSettlementDetail from './components/carrier-settlement-detail.vue';
  import CarrierSettlementPay from './components/carrier-settlement-pay.vue';
  import CarrierSettlementSearch from './components/carrier-settlement-search.vue';
  import {
    approveCarrierSettle,
    pageCarrierSettles,
    submitCarrierSettle
  } from '@/api/finance/carrier-settlement';
  import type {
    CarrierSettleListItem,
    CarrierSettleParam
  } from '@/api/finance/carrier-settlement/model';
  import { selectCarriers } from '@/api/partner/carrier';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import { formatDate } from '@/utils/date-util';
  import { buildActionColumnItems } from '../_shared/action-column';
  import {
    CARRIER_SETTLE_STATUS_MAP,
    formatMoney
  } from '../status-config';

  defineOptions({ name: 'FinanceCarrierSettlement' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<CarrierSettleParam>({});
  const carriers = ref<CarrierSelectItem[]>([]);

  const createVisible = ref(false);
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);
  const payVisible = ref(false);
  const payId = ref<number | null>(null);

  const today = new Date().toISOString().slice(0, 10);

  /** 已过到期日且还有未付金额 = 逾期，列表里标红提醒排款 */
  const isOverdue = (row: CarrierSettleListItem) =>
    !!row.dueDate && row.dueDate < today && row.unpaidAmount > 0;

  const columns = computed<Columns>(() => [
    { prop: 'docNo', label: '结算单号', minWidth: 170 },
    { prop: 'carrierName', label: '承运商', minWidth: 170 },
    { prop: 'reconCount', label: '对账单', width: 84, align: 'center' },
    {
      columnKey: 'amount',
      label: '应付金额',
      width: 150,
      align: 'right',
      slot: 'amount'
    },
    {
      columnKey: 'unpaid',
      label: '未付金额',
      width: 130,
      align: 'right',
      slot: 'unpaid'
    },
    {
      prop: 'dueDate',
      label: '到期日',
      width: 130,
      align: 'center',
      slot: 'dueDate'
    },
    {
      columnKey: 'account',
      label: '付款账户',
      minWidth: 150,
      slot: 'account'
    },
    {
      columnKey: 'invoice',
      label: '收票',
      width: 100,
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
    return pageCarrierSettles({ ...(tableWhere || where), ...pages }).then(
      (res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      })
    );
  };

  const reload = (next?: CarrierSettleParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openDetail = (settleId: number) => {
    detailId.value = settleId;
    detailVisible.value = true;
  };

  const openPay = (settleId: number) => {
    payId.value = settleId;
    payVisible.value = true;
  };

  const onCreated = (settleId?: number) => {
    reload();
    if (settleId) openDetail(settleId);
  };

  const actionItems = (row: CarrierSettleListItem): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '详情',
        icon: EyeOutlined,
        permission: 'finance:carrier-settle:detail',
        onClick: () => openDetail(row.id)
      }
    ];
    if (row.status === 0) {
      visible.push({
        title: '提交审批',
        icon: CloudUploadOutlined,
        permission: 'finance:carrier-settle:submit',
        onClick: () => submitRow(row)
      });
    }
    if (row.status === 1) {
      visible.push({
        title: '审批通过',
        icon: CheckCircleOutlined,
        permission: 'finance:carrier-settle:approve',
        onClick: () => approveRow(row)
      });
    }
    if (row.status === 2) {
      visible.push({
        title: '登记付款',
        icon: FundOutlined,
        permission: 'finance:carrier-settle:pay',
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

  const submitRow = async (row: CarrierSettleListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认提交结算单「${row.docNo}」进入审批？`,
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
    await runRow(() => submitCarrierSettle(row.id), {
      loading: '正在提交审批，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approveRow = async (row: CarrierSettleListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认审批通过结算单「${row.docNo}」？通过后即可安排付款。`,
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
    await runRow(() => approveCarrierSettle(row.id), {
      loading: '正在审批，请稍候…',
      success: '已审批通过，可安排付款',
      fail: '审批失败，请稍后重试'
    });
  };

  onMounted(async () => {
    try {
      carriers.value = (await selectCarriers()) || [];
    } catch {
      // 下拉拉取失败不影响列表，仍可用关键词搜索
    }
  });
</script>

<style lang="scss" scoped>
  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .offset-tag {
    color: var(--el-color-info);
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
