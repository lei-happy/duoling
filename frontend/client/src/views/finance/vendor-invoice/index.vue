<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-tabs v-model="activeTab" class="page-tabs">
        <el-tab-pane label="发票台账" name="list" />
        <el-tab-pane label="待收票结算单" name="pending" />
        <el-tab-pane label="抵扣台账" name="deduct" />
      </el-tabs>

      <ele-pro-table
        v-if="activeTab === 'list'"
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        cache-key="FinanceVendorInvoiceTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="发票号/供应商"
                clearable
                style="width: 190px"
                @change="reload()"
              />
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
                  v-for="o in VENDOR_INVOICE_STATUS_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.vendorType"
                placeholder="供应商类型"
                clearable
                style="width: 130px"
                @change="reload()"
              >
                <el-option
                  v-for="o in VENDOR_TYPE_OPTIONS"
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
              <el-checkbox v-model="where.onlyUnsettled" @change="reload()">
                只看未核销完
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '登记收票',
                    permission: 'finance:vendor-invoice:create',
                    onClick: () => openEdit(null)
                  }
                ]"
              />
            </el-form-item>
          </el-form>
        </template>

        <template #vendor="{ row }">
          <div>{{ row.vendorName || row.sellerTitle || '--' }}</div>
          <div class="muted">{{ row.vendorTypeLabel }}</div>
        </template>

        <template #invoice="{ row }">
          <div>{{ row.invoiceNo }}</div>
          <div class="muted">
            {{ row.invoiceTypeLabel }}
            <span v-if="row.isMultiRate === 1">· 多税率</span>
          </div>
        </template>

        <template #amount="{ row }">
          <div class="num-cell strong">
            ¥ {{ formatMoney(row.amountInclTax) }}
          </div>
          <div class="muted">
            税额 {{ formatMoney(row.taxAmount) }}
            <span v-if="row.taxRate != null">· {{ row.taxRate }}%</span>
          </div>
        </template>

        <template #settled="{ row }">
          <div class="num-cell paid"
            >¥ {{ formatMoney(row.settledAmount) }}</div
          >
          <div v-if="row.unsettledAmount > 0" class="num-cell gap">
            待核销 {{ formatMoney(row.unsettledAmount) }}
          </div>
        </template>

        <template #deduct="{ row }">
          <el-tag
            :type="row.deductible === 1 ? 'success' : 'info'"
            size="small"
            effect="plain"
          >
            {{ row.deductible === 1 ? '可抵扣' : '不可抵扣' }}
          </el-tag>
          <div v-if="row.deductPeriod" class="muted">{{
            row.deductPeriod
          }}</div>
        </template>

        <template #status="{ row }">
          <el-tag
            :type="
              (VENDOR_INVOICE_STATUS_MAP[row.status]?.type as any) || 'info'
            "
            size="small"
          >
            {{
              row.statusLabel || VENDOR_INVOICE_STATUS_MAP[row.status]?.label
            }}
          </el-tag>
          <div
            v-if="row.verifyStatus === 2"
            class="verify-bad"
            :title="row.verifyStatusLabel"
          >
            验真不符
          </div>
        </template>

        <template #action="{ row }">
          <el-link
            type="primary"
            :underline="false"
            v-permission="'finance:vendor-invoice:detail'"
            @click="openDetail(row.id)"
          >
            详情
          </el-link>
          <template v-if="row.unsettledAmount > 0 && row.status !== 9">
            <el-divider direction="vertical" />
            <el-link
              type="success"
              :underline="false"
              v-permission="'finance:vendor-invoice:match'"
              @click="openDetail(row.id)"
            >
              核销
            </el-link>
          </template>
        </template>
      </ele-pro-table>

      <!-- 待收票：从付款侧看还差多少票，催票用 -->
      <div v-else-if="activeTab === 'pending'" class="sub-panel">
        <div class="panel-tip">
          已付款但票没收齐的结算单。发票到手后点「登记收票」，登记完在详情里核销到对应结算单。
        </div>
        <el-table :data="pendingRows" v-loading="pendingLoading" size="small">
          <el-table-column prop="docNo" label="结算单号" min-width="170" />
          <el-table-column prop="carrierName" label="承运商" min-width="150" />
          <el-table-column label="结算金额" width="130" align="right">
            <template #default="{ row }">
              <span class="num-cell"
                >¥ {{ formatMoney(row.plannedAmount) }}</span
              >
            </template>
          </el-table-column>
          <el-table-column label="已收票" width="130" align="right">
            <template #default="{ row }">
              <span class="num-cell">
                ¥ {{ formatMoney(row.invoiceAmountTotal) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="缺口" width="130" align="right">
            <template #default="{ row }">
              <span class="num-cell gap"
                >¥ {{ formatMoney(row.gapAmount) }}</span
              >
            </template>
          </el-table-column>
          <el-table-column label="付款时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDate(row.paidAt) || '--' }}
            </template>
          </el-table-column>
          <el-table-column label="已过天数" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ overdue: (row.paidDays || 0) > 30 }">
                {{ row.paidDays ?? '--' }}
              </span>
            </template>
          </el-table-column>
          <template #empty>
            <div class="empty-tip">票都收齐了，没有待催的结算单</div>
          </template>
        </el-table>
      </div>

      <!-- 抵扣台账：给会计报税时对数用 -->
      <div v-else class="sub-panel">
        <div class="panel-toolbar">
          <el-select v-model="deductGroupBy" size="small" style="width: 140px">
            <el-option value="period" label="按抵扣税期" />
            <el-option value="entity" label="按开票主体" />
            <el-option value="tax_rate" label="按税率" />
          </el-select>
          <el-date-picker
            v-model="deductPeriod"
            type="monthrange"
            value-format="YYYY-MM"
            start-placeholder="起始税期"
            end-placeholder="结束税期"
            size="small"
            style="width: 230px"
          />
          <el-button size="small" type="primary" plain @click="loadDeduct">
            查询
          </el-button>
        </div>
        <el-table :data="deductRows" v-loading="deductLoading" size="small">
          <el-table-column label="分组" min-width="160">
            <template #default="{ row }">
              {{ row.groupKey ?? '未填' }}
            </template>
          </el-table-column>
          <el-table-column
            prop="invoiceCount"
            label="发票数"
            width="100"
            align="center"
          />
          <el-table-column label="不含税额" width="150" align="right">
            <template #default="{ row }">
              <span class="num-cell"
                >¥ {{ formatMoney(row.amountExclTax) }}</span
              >
            </template>
          </el-table-column>
          <el-table-column label="税额" width="150" align="right">
            <template #default="{ row }">
              <span class="num-cell">¥ {{ formatMoney(row.taxAmount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="价税合计" width="150" align="right">
            <template #default="{ row }">
              <span class="num-cell strong">
                ¥ {{ formatMoney(row.amountInclTax) }}
              </span>
            </template>
          </el-table-column>
          <template #empty>
            <div class="empty-tip">这个区间还没有可抵扣的进项票</div>
          </template>
        </el-table>
      </div>
    </ele-card>

    <vendor-invoice-edit
      v-model:visible="editVisible"
      :invoice="editingInvoice"
      @done="onEdited"
    />

    <vendor-invoice-detail
      v-model:visible="detailVisible"
      :invoice-id="detailId"
      @changed="reload()"
      @edit="openEdit"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import VendorInvoiceDetail from './components/vendor-invoice-detail.vue';
  import VendorInvoiceEdit from './components/vendor-invoice-edit.vue';
  import {
    getDeductSummary,
    listPendingInvoiceSettles,
    pageVendorInvoices
  } from '@/api/finance/vendor-invoice';
  import type {
    DeductSummaryRow,
    PendingInvoiceSettle,
    VendorInvoiceDetail as InvoiceDetailModel,
    VendorInvoiceParam
  } from '@/api/finance/vendor-invoice/model';
  import { formatDate } from '@/utils/date-util';
  import {
    formatMoney,
    VENDOR_INVOICE_STATUS_MAP,
    VENDOR_INVOICE_STATUS_OPTIONS,
    VENDOR_TYPE_OPTIONS
  } from '../status-config';

  defineOptions({ name: 'FinanceVendorInvoice' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const activeTab = ref('list');
  const where = reactive<VendorInvoiceParam>({});
  const dateRange = ref<[string, string] | null>(null);

  const editVisible = ref(false);
  const editingInvoice = ref<InvoiceDetailModel | null>(null);
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);

  const pendingRows = ref<PendingInvoiceSettle[]>([]);
  const pendingLoading = ref(false);
  const deductRows = ref<DeductSummaryRow[]>([]);
  const deductLoading = ref(false);
  const deductGroupBy = ref('period');
  const deductPeriod = ref<[string, string] | null>(null);

  const columns = computed<Columns>(() => [
    {
      columnKey: 'invoice',
      label: '发票号',
      minWidth: 170,
      slot: 'invoice'
    },
    {
      columnKey: 'vendor',
      label: '供应商',
      minWidth: 160,
      slot: 'vendor'
    },
    {
      prop: 'invoiceDate',
      label: '开票日期',
      width: 120,
      align: 'center',
      formatter: (row) => formatDate(row.invoiceDate) || '--'
    },
    {
      columnKey: 'amount',
      label: '价税合计',
      width: 155,
      align: 'right',
      slot: 'amount'
    },
    {
      columnKey: 'settled',
      label: '已核销',
      width: 150,
      align: 'right',
      slot: 'settled'
    },
    {
      columnKey: 'deduct',
      label: '抵扣',
      width: 120,
      align: 'center',
      slot: 'deduct'
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
      width: 140,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageVendorInvoices({ ...where, ...pages }).then((res) => ({
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

  const openEdit = (invoice: InvoiceDetailModel | null) => {
    editingInvoice.value = invoice;
    editVisible.value = true;
  };

  const openDetail = (invoiceId: number) => {
    detailId.value = invoiceId;
    detailVisible.value = true;
  };

  const onEdited = (invoiceId?: number) => {
    reload();
    if (invoiceId && !detailVisible.value) openDetail(invoiceId);
  };

  const loadPending = async () => {
    pendingLoading.value = true;
    try {
      const res = await listPendingInvoiceSettles({ limit: 200 });
      pendingRows.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      pendingLoading.value = false;
    }
  };

  const loadDeduct = async () => {
    deductLoading.value = true;
    try {
      const res = await getDeductSummary({
        groupBy: deductGroupBy.value,
        periodFrom: deductPeriod.value?.[0],
        periodTo: deductPeriod.value?.[1]
      });
      deductRows.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      deductLoading.value = false;
    }
  };

  watch(activeTab, (tab) => {
    if (tab === 'pending' && !pendingRows.value.length) loadPending();
    if (tab === 'deduct' && !deductRows.value.length) loadDeduct();
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
    gap: 10px;
    margin-bottom: 10px;
  }

  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .paid {
    color: var(--el-color-success);
  }

  .gap {
    color: var(--el-color-warning);
    font-size: 12px;
  }

  .overdue {
    color: var(--el-color-danger);
    font-weight: 600;
  }

  .verify-bad {
    margin-top: 2px;
    color: var(--el-color-danger);
    font-size: 12px;
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .empty-tip {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
