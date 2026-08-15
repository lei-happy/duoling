<template>
  <ele-page>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="发票台账" name="list">
        <vendor-invoice-search @search="(next) => reload(next, 1)" />
        <ele-card :body-style="{ paddingTop: '8px' }">
          <ele-pro-table
            ref="tableRef"
            row-key="id"
            :columns="columns"
            :datasource="datasource"
            :pagination="{ pageSize: 20 }"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            cache-key="FinanceVendorInvoiceTable"
          >
            <template #toolbar>
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

      <el-tab-pane label="待收票结算单" name="pending">
        <ele-card :body-style="{ paddingTop: '8px' }">
          <p class="panel-tip">
            已付款但票没收齐的结算单。发票到手后点「登记收票」，登记完在详情里核销到对应结算单。
          </p>
          <el-table
            :data="pendingRows"
            v-loading="pendingLoading"
            :highlight-current-row="true"
          >
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
        </ele-card>
      </el-tab-pane>

      <el-tab-pane label="抵扣台账" name="deduct">
        <ele-card search-form>
          <el-form label-width="0" @submit.prevent="">
            <el-row :gutter="8">
              <el-col :lg="6" :md="8" :sm="12" :xs="24">
                <floating-label
                  v-model="deductGroupBy"
                  label="分组方式"
                  type="select"
                  :clearable="false"
                >
                  <el-option value="period" label="按抵扣税期" />
                  <el-option value="entity" label="按开票主体" />
                  <el-option value="tax_rate" label="按税率" />
                </floating-label>
              </el-col>
              <el-col :lg="8" :md="10" :sm="12" :xs="24">
                <floating-label
                  v-model="deductPeriod"
                  label="抵扣税期"
                  type="date"
                  date-type="monthrange"
                  value-format="YYYY-MM"
                  start-placeholder="起始税期"
                  end-placeholder="结束税期"
                />
              </el-col>
              <el-col :lg="6" :md="8" :sm="12" :xs="24">
                <el-form-item label-width="0px">
                  <btn-items
                    :wrap="false"
                    :items="[
                      { preset: 'search', onClick: () => loadDeduct() }
                    ]"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </ele-card>
        <ele-card :body-style="{ paddingTop: '8px' }">
          <el-table
            :data="deductRows"
            v-loading="deductLoading"
            :highlight-current-row="true"
          >
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
        </ele-card>
      </el-tab-pane>
    </el-tabs>

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
  import { computed, reactive, ref, watch } from 'vue';
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
  import { ConnectionOutlined, EyeOutlined } from '@/components/icons';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import VendorInvoiceDetail from './components/vendor-invoice-detail.vue';
  import VendorInvoiceEdit from './components/vendor-invoice-edit.vue';
  import VendorInvoiceSearch from './components/vendor-invoice-search.vue';
  import {
    getDeductSummary,
    listPendingInvoiceSettles,
    pageVendorInvoices
  } from '@/api/finance/vendor-invoice';
  import type {
    DeductSummaryRow,
    PendingInvoiceSettle,
    VendorInvoiceDetail as InvoiceDetailModel,
    VendorInvoiceListItem,
    VendorInvoiceParam
  } from '@/api/finance/vendor-invoice/model';
  import { formatDate } from '@/utils/date-util';
  import { buildActionColumnItems } from '../_shared/action-column';
  import {
    formatMoney,
    VENDOR_INVOICE_STATUS_MAP
  } from '../status-config';

  defineOptions({ name: 'FinanceVendorInvoice' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const activeTab = ref('list');
  const where = reactive<VendorInvoiceParam>({});

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
    return pageVendorInvoices({ ...(tableWhere || where), ...pages }).then(
      (res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      })
    );
  };

  const reload = (next?: VendorInvoiceParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openEdit = (invoice: InvoiceDetailModel | null) => {
    editingInvoice.value = invoice;
    editVisible.value = true;
  };

  const openDetail = (invoiceId: number) => {
    detailId.value = invoiceId;
    detailVisible.value = true;
  };

  const actionItems = (row: VendorInvoiceListItem): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '详情',
        icon: EyeOutlined,
        permission: 'finance:vendor-invoice:detail',
        onClick: () => openDetail(row.id)
      }
    ];
    if (row.unsettledAmount > 0 && row.status !== 9) {
      visible.push({
        title: '核销',
        icon: ConnectionOutlined,
        permission: 'finance:vendor-invoice:match',
        onClick: () => openDetail(row.id)
      });
    }
    return buildActionColumnItems(visible);
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
  .panel-tip {
    margin: 0 0 12px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
    line-height: 1.7;
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
