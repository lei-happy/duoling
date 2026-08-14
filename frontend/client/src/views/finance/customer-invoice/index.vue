<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-tabs v-model="activeTab" class="page-tabs">
        <el-tab-pane label="发票台账" name="list" />
        <el-tab-pane label="待开票池" name="pending" />
      </el-tabs>

      <ele-pro-table
        v-if="activeTab === 'list'"
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        cache-key="FinanceCustomerInvoiceTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="申请单号/发票号/客户"
                clearable
                style="width: 200px"
                @change="reload()"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.customerId"
                placeholder="客户"
                clearable
                filterable
                style="width: 170px"
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
                style="width: 120px"
                @change="reload()"
              >
                <el-option
                  v-for="o in CUSTOMER_INVOICE_STATUS_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                value-format="YYYY-MM-DD"
                start-placeholder="开票起"
                end-placeholder="开票止"
                style="width: 230px"
                @change="onDateChange"
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="where.onlyRed" @change="reload()">
                只看红字票
              </el-checkbox>
            </el-form-item>
            <el-form-item>
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
            </el-form-item>
          </el-form>
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
              (CUSTOMER_INVOICE_STATUS_MAP[row.status]?.type as any) || 'info'
            "
            size="small"
          >
            {{
              row.statusLabel || CUSTOMER_INVOICE_STATUS_MAP[row.status]?.label
            }}
          </el-tag>
        </template>

        <template #action="{ row }">
          <el-link
            type="primary"
            :underline="false"
            v-permission="'finance:cust-invoice:detail'"
            @click="openDetail(row.id)"
          >
            详情
          </el-link>
          <template v-if="row.status === 1">
            <el-divider direction="vertical" />
            <el-link
              type="success"
              :underline="false"
              v-permission="'finance:cust-invoice:issue'"
              @click="openDetail(row.id)"
            >
              登记开票
            </el-link>
          </template>
        </template>
      </ele-pro-table>

      <!-- 待开票池：结算单侧还差多少票没开，催开票用 -->
      <div v-else class="sub-panel">
        <div class="panel-tip">
          已审批或已收款、但票还没开齐的结算单。勾一张点「按此开票」就会带着结算单建申请。
        </div>
        <div class="panel-toolbar">
          <el-checkbox v-model="onlyRequired" @change="loadPending">
            只看客户要求开票的
          </el-checkbox>
          <el-button size="small" type="primary" plain @click="loadPending">
            刷新
          </el-button>
        </div>
        <el-table :data="pendingRows" v-loading="pendingLoading" size="small">
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
          <el-table-column label="操作" width="110" align="center">
            <template #default="{ row }">
              <el-link
                type="primary"
                :underline="false"
                v-permission="'finance:cust-invoice:create'"
                @click="openCreate(row.customerId)"
              >
                按此开票
              </el-link>
            </template>
          </el-table-column>
          <template #empty>
            <div class="empty-tip">票都开齐了，没有待开票的结算单</div>
          </template>
        </el-table>
      </div>
    </ele-card>

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
  import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import CustomerInvoiceCreate from './components/customer-invoice-create.vue';
  import CustomerInvoiceDetail from './components/customer-invoice-detail.vue';
  import {
    listPendingInvoicePool,
    pageCustomerInvoices
  } from '@/api/finance/customer-invoice';
  import type {
    CustomerInvoiceParam,
    PendingInvoiceSettle
  } from '@/api/finance/customer-invoice/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDate } from '@/utils/date-util';
  import {
    CUSTOMER_INVOICE_STATUS_MAP,
    CUSTOMER_INVOICE_STATUS_OPTIONS,
    formatMoney
  } from '../status-config';

  defineOptions({ name: 'FinanceCustomerInvoice' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const activeTab = ref('list');
  const where = reactive<CustomerInvoiceParam>({});
  const dateRange = ref<[string, string] | null>(null);
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
      width: 150,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageCustomerInvoices({ ...where, ...pages }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = () => {
    nextTick(() => tableRef.value?.reload?.());
  };

  const onDateChange = () => {
    where.dateFrom = dateRange.value?.[0];
    where.dateTo = dateRange.value?.[1];
    reload();
  };

  const openCreate = (customerId?: number) => {
    createCustomerId.value = customerId;
    createVisible.value = true;
  };

  const openDetail = (invoiceId: number) => {
    detailId.value = invoiceId;
    detailVisible.value = true;
  };

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
  .page-tabs {
    margin-bottom: 4px;

    :deep(.el-tabs__header) {
      margin-bottom: 8px;
    }
  }

  .sub-panel {
    padding-top: 4px;
  }

  .panel-tip {
    margin-bottom: 10px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
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
