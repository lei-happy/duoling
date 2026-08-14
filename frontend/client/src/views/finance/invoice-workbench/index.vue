<!--
  票据工作台（文档 08）

  开票员一天要盯的三件事：客户催的票开了没、供应商的票收齐没、收到的票核销了没。
  这一页只做「看和跳转」，具体开票 / 收票动作回各自台账页完成，避免两处逻辑分叉。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '12px' }">
      <finance-kpi-cards :cards="kpiCards" @select="onKpiSelect" />

      <el-tabs v-model="activeTab" class="page-tabs">
        <el-tab-pane label="待开票（销项）" name="out">
          <div class="panel-tip">
            结算单已审批但票没开齐的部分。点「去开票」会带着客户跳到销项发票页。
          </div>
          <el-table
            :data="pendingOut"
            v-loading="loadingOut"
            size="small"
            max-height="440"
          >
            <el-table-column prop="docNo" label="结算单号" min-width="170" />
            <el-table-column prop="customerName" label="客户" min-width="150" />
            <el-table-column label="结算金额" width="130" align="right">
              <template #default="{ row }">
                <span class="num">¥ {{ formatMoney(row.plannedAmount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="已开票" width="130" align="right">
              <template #default="{ row }">
                <span class="num">¥ {{ formatMoney(row.invoicedAmount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="缺口" width="130" align="right">
              <template #default="{ row }">
                <span class="num gap">¥ {{ formatMoney(row.gapAmount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="账期" width="110" align="center">
              <template #default="{ row }">{{ row.dueDate || '--' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-link
                  type="primary"
                  :underline="false"
                  @click="goCustomerInvoice(row.customerId)"
                >
                  去开票
                </el-link>
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-tip">销项票都开齐了</div>
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="待收票（进项）" name="in">
          <div class="panel-tip">
            已付款但供应商票还没收齐的结算单。收到票后去进项发票页登记并核销。
          </div>
          <el-table
            :data="pendingIn"
            v-loading="loadingIn"
            size="small"
            max-height="440"
          >
            <el-table-column prop="docNo" label="结算单号" min-width="170" />
            <el-table-column
              prop="carrierName"
              label="承运商"
              min-width="150"
            />
            <el-table-column label="结算金额" width="130" align="right">
              <template #default="{ row }">
                <span class="num">¥ {{ formatMoney(row.plannedAmount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="已收票" width="130" align="right">
              <template #default="{ row }">
                <span class="num">
                  ¥ {{ formatMoney(row.invoiceAmountTotal) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="缺口" width="130" align="right">
              <template #default="{ row }">
                <span class="num gap">¥ {{ formatMoney(row.gapAmount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="付款后天数" width="120" align="center">
              <template #default="{ row }">
                <span :class="{ 'over-days': (row.paidDays || 0) > 30 }">
                  {{ row.paidDays != null ? `${row.paidDays} 天` : '--' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-link
                  type="primary"
                  :underline="false"
                  @click="goVendorInvoice(row.carrierId)"
                >
                  去收票
                </el-link>
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-tip">进项票都收齐了</div>
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="待审批的开票申请" name="apply">
          <div class="panel-tip">
            业务提交的开票申请，登记发票号后关联结算单会自动锁定。
          </div>
          <el-table
            :data="applying"
            v-loading="loadingApply"
            size="small"
            max-height="440"
          >
            <el-table-column prop="docNo" label="申请单号" min-width="175" />
            <el-table-column prop="customerName" label="客户" min-width="150" />
            <el-table-column
              prop="invoiceTypeLabel"
              label="发票类型"
              width="150"
            />
            <el-table-column label="价税合计" width="140" align="right">
              <template #default="{ row }">
                <span class="num strong">
                  ¥ {{ formatMoney(row.amountInclTax) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="提交时间" width="165" align="center">
              <template #default="{ row }">
                {{ formatDateTime(row.applicantAt) || '--' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110" align="center">
              <template #default="{ row }">
                <el-link
                  type="primary"
                  :underline="false"
                  @click="goCustomerInvoice(row.customerId)"
                >
                  去登记
                </el-link>
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-tip">没有待登记的开票申请</div>
            </template>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import {
    listPendingInvoicePool,
    pageCustomerInvoices
  } from '@/api/finance/customer-invoice';
  import type {
    CustomerInvoiceListItem,
    PendingInvoiceSettle as PendingOutSettle
  } from '@/api/finance/customer-invoice/model';
  import { listPendingInvoiceSettles } from '@/api/finance/vendor-invoice';
  import type { PendingInvoiceSettle as PendingInSettle } from '@/api/finance/vendor-invoice/model';
  import { formatDateTime } from '@/utils/date-util';
  import { formatMoney } from '../status-config';

  defineOptions({ name: 'FinanceInvoiceWorkbench' });

  const router = useRouter();
  const activeTab = ref('out');

  const pendingOut = ref<PendingOutSettle[]>([]);
  const pendingIn = ref<PendingInSettle[]>([]);
  const applying = ref<CustomerInvoiceListItem[]>([]);
  const loadingOut = ref(false);
  const loadingIn = ref(false);
  const loadingApply = ref(false);

  const sumBy = <T,>(rows: T[], pick: (r: T) => number) =>
    rows.reduce((s, r) => s + Number(pick(r) || 0), 0);

  const kpiCards = computed<FinanceKpiCard[]>(() => [
    {
      key: 'out',
      label: '待开票缺口',
      value: formatMoney(sumBy(pendingOut.value, (r) => r.gapAmount)),
      unit: '元',
      type: 'warning',
      clickable: true,
      hint: `${pendingOut.value.length} 张结算单等开票`
    },
    {
      key: 'in',
      label: '待收票缺口',
      value: formatMoney(sumBy(pendingIn.value, (r) => r.gapAmount)),
      unit: '元',
      type: 'danger',
      clickable: true,
      hint: `${pendingIn.value.length} 张结算单等供应商票`
    },
    {
      key: 'apply',
      label: '待登记开票申请',
      value: applying.value.length,
      unit: '份',
      type: 'primary',
      clickable: true,
      hint: `价税合计 ${formatMoney(
        sumBy(applying.value, (r) => r.amountInclTax)
      )} 元`
    }
  ]);

  const onKpiSelect = (key: string) => {
    activeTab.value = key;
  };

  const goCustomerInvoice = (customerId?: number) => {
    router.push({
      path: '/finance/customer-invoice',
      query: customerId ? { customerId: String(customerId) } : void 0
    });
  };

  const goVendorInvoice = (carrierId?: number) => {
    router.push({
      path: '/finance/vendor-invoice',
      query: carrierId ? { vendorId: String(carrierId) } : void 0
    });
  };

  const loadOut = async () => {
    loadingOut.value = true;
    try {
      const res = await listPendingInvoicePool({
        onlyRequired: true,
        limit: 200
      });
      pendingOut.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message:
          (e as { message?: string }).message || '待开票加载失败，请重试',
        plain: true
      });
    } finally {
      loadingOut.value = false;
    }
  };

  const loadIn = async () => {
    loadingIn.value = true;
    try {
      const res = await listPendingInvoiceSettles({ limit: 200 });
      pendingIn.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message:
          (e as { message?: string }).message || '待收票加载失败，请重试',
        plain: true
      });
    } finally {
      loadingIn.value = false;
    }
  };

  const loadApplying = async () => {
    loadingApply.value = true;
    try {
      const res = await pageCustomerInvoices({
        status: 1,
        page: 1,
        limit: 100
      });
      applying.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message:
          (e as { message?: string }).message || '开票申请加载失败，请重试',
        plain: true
      });
    } finally {
      loadingApply.value = false;
    }
  };

  onMounted(() => {
    loadOut();
    loadIn();
    loadApplying();
  });
</script>

<style lang="scss" scoped>
  .page-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 10px;
    }
  }

  .panel-tip {
    margin-bottom: 10px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .gap {
    color: var(--el-color-warning);
  }

  .over-days {
    color: var(--el-color-danger);
    font-weight: 600;
  }

  .empty-tip {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
