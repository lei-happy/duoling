<template>
  <ele-page>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="发票台账" name="list">
        <invoice-search
          :customers="customers"
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
            cache-key="FinanceCustomerInvoiceTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新建开票申请',
                    permission: 'finance:cust-invoice:create',
                    onClick: () => openCreate()
                  }
                ]"
              />
            </template>

            <template #doc="{ row }">
              <div>{{ row.docNo }}</div>
              <div class="muted">
                {{ row.invoiceTypeLabel }}
                <span v-if="row.isRedFlush === 1" class="red-mark">红字票</span>
              </div>
            </template>

            <template #invoice="{ row }">
              <div>{{ row.invoiceNo || '未开票' }}</div>
              <div class="muted">{{ formatDate(row.invoiceDate) || '--' }}</div>
            </template>

            <template #amount="{ row }">
              <div class="num-cell strong">
                ¥ {{ formatMoney(row.amountInclTax) }}
              </div>
              <div class="muted">
                不含税 {{ formatMoney(row.amountExclTax) }}
                <span v-if="row.taxRate != null">· {{ row.taxRate }}%</span>
              </div>
            </template>

            <template #status="{ row }">
              <el-tag
                :type="
                  (CUSTOMER_INVOICE_STATUS_MAP[row.status]?.type as any) ||
                  'info'
                "
                size="small"
              >
                {{
                  row.statusLabel ||
                  CUSTOMER_INVOICE_STATUS_MAP[row.status]?.label
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
      </el-tab-pane>

      <el-tab-pane label="待开票池" name="pending">
        <ele-card :body-style="{ paddingTop: '8px' }">
          <p class="panel-tip">
            已审批或已收款、但票还没开齐的结算单。勾一张点「按此开票」就会带着结算单建申请。
          </p>
          <div class="panel-toolbar">
            <el-checkbox v-model="onlyRequired" @change="loadPending">
              只看客户要求开票的
            </el-checkbox>
            <btn-items
              :items="[{ preset: 'search', title: '刷新', onClick: loadPending }]"
            />
          </div>
          <el-table
            :data="pendingRows"
            v-loading="pendingLoading"
            :highlight-current-row="true"
          >
            <el-table-column prop="docNo" label="结算单号" min-width="170" />
            <el-table-column prop="customerName" label="客户" min-width="150" />
            <el-table-column label="结算金额" width="130" align="right">
              <template #default="{ row }">
                <span class="num-cell"
                  >¥ {{ formatMoney(row.plannedAmount) }}</span
                >
              </template>
            </el-table-column>
            <el-table-column label="已开票" width="130" align="right">
              <template #default="{ row }">
                <span class="num-cell"
                  >¥ {{ formatMoney(row.invoicedAmount) }}</span
                >
              </template>
            </el-table-column>
            <el-table-column label="缺口" width="130" align="right">
              <template #default="{ row }">
                <span class="num-cell gap"
                  >¥ {{ formatMoney(row.gapAmount) }}</span
                >
              </template>
            </el-table-column>
            <el-table-column label="账期" width="120" align="center">
              <template #default="{ row }">
                {{ row.dueDate || '--' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <btn-items
                  divider
                  type="link"
                  :wrap="false"
                  :items="pendingActions(row)"
                />
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-tip">票都开齐了，没有待开票的结算单</div>
            </template>
          </el-table>
        </ele-card>
      </el-tab-pane>
    </el-tabs>

    <customer-invoice-create
      v-model:visible="createVisible"
      :customer-id="createCustomerId"
      :customers="customers"
      @done="onCreated"
    />

    <customer-invoice-detail
      v-model:visible="detailVisible"
      :invoice-id="detailId"
      @changed="onChanged"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref, watch } from 'vue';
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
  import { EyeOutlined, FormOutlined } from '@/components/icons';
  import CustomerInvoiceCreate from './components/customer-invoice-create.vue';
  import CustomerInvoiceDetail from './components/customer-invoice-detail.vue';
  import InvoiceSearch from './components/invoice-search.vue';
  import {
    listPendingInvoicePool,
    pageCustomerInvoices
  } from '@/api/finance/customer-invoice';
  import type {
    CustomerInvoiceListItem,
    CustomerInvoiceParam,
    PendingInvoiceSettle
  } from '@/api/finance/customer-invoice/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDate } from '@/utils/date-util';
  import { buildActionColumnItems } from '../_shared/action-column';
  import {
    CUSTOMER_INVOICE_STATUS_MAP,
    formatMoney
  } from '../status-config';

  defineOptions({ name: 'FinanceCustomerInvoice' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const activeTab = ref('list');
  const where = reactive<CustomerInvoiceParam>({});
  const customers = ref<CustomerSelectItem[]>([]);

  const createVisible = ref(false);
  const createCustomerId = ref<number | undefined>();
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);

  const pendingRows = ref<PendingInvoiceSettle[]>([]);
  const pendingLoading = ref(false);
  const onlyRequired = ref(true);

  const columns = computed<Columns>(() => [
    { columnKey: 'doc', label: '申请单号', minWidth: 175, slot: 'doc' },
    { prop: 'customerName', label: '客户', minWidth: 150 },
    { columnKey: 'invoice', label: '发票号', minWidth: 150, slot: 'invoice' },
    {
      columnKey: 'amount',
      label: '价税合计',
      width: 165,
      align: 'right',
      slot: 'amount'
    },
    {
      prop: 'settleCount',
      label: '关联结算单',
      width: 110,
      align: 'center',
      formatter: (row) => `${row.settleCount || 0} 张`
    },
    {
      prop: 'status',
      label: '状态',
      width: 110,
      align: 'center',
      slot: 'status'
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
    return pageCustomerInvoices({ ...(tableWhere || where), ...pages }).then(
      (res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      })
    );
  };

  const reload = (next?: CustomerInvoiceParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openCreate = (customerId?: number) => {
    createCustomerId.value = customerId;
    createVisible.value = true;
  };

  const openDetail = (invoiceId: number) => {
    detailId.value = invoiceId;
    detailVisible.value = true;
  };

  const actionItems = (row: CustomerInvoiceListItem): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '详情',
        icon: EyeOutlined,
        permission: 'finance:cust-invoice:detail',
        onClick: () => openDetail(row.id)
      }
    ];
    if (row.status === 1) {
      visible.push({
        title: '登记开票',
        icon: FormOutlined,
        permission: 'finance:cust-invoice:issue',
        onClick: () => openDetail(row.id)
      });
    }
    return buildActionColumnItems(visible);
  };

  const pendingActions = (row: PendingInvoiceSettle): ButtonItem[] =>
    buildActionColumnItems([
      {
        title: '按此开票',
        icon: FormOutlined,
        permission: 'finance:cust-invoice:create',
        onClick: () => openCreate(row.customerId)
      }
    ]);

  const onCreated = (invoiceId?: number) => {
    activeTab.value = 'list';
    reload();
    if (invoiceId) openDetail(invoiceId);
  };

  const onChanged = () => {
    reload();
    if (activeTab.value === 'pending') loadPending();
  };

  const loadPending = async () => {
    pendingLoading.value = true;
    try {
      const res = await listPendingInvoicePool({
        onlyRequired: onlyRequired.value,
        limit: 200
      });
      pendingRows.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载失败，请重试',
        plain: true
      });
    } finally {
      pendingLoading.value = false;
    }
  };

  watch(activeTab, (tab) => {
    if (tab === 'pending' && !pendingRows.value.length) loadPending();
  });

  onMounted(async () => {
    try {
      customers.value = (await selectCustomers()) || [];
    } catch {
      // 客户下拉失败不影响台账查询
    }
  });
</script>

<style lang="scss" scoped>
  .panel-tip {
    margin: 0 0 12px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
    line-height: 1.7;
  }

  .panel-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }

  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .gap {
    color: var(--el-color-warning);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .red-mark {
    margin-left: 4px;
    color: var(--el-color-danger);
  }

  .empty-tip {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
