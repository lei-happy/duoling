<template>
  <PageContainer title="费用单详情">
    <div v-if="doc" class="finance-detail">
      <div class="header card">
        <div class="header-row">
          <span class="doc-no">{{ doc.docNo }}</span>
          <StatusTag
            :label="FINANCE_STATUS[doc.status]?.label || '未知'"
            :level="FINANCE_STATUS[doc.status]?.level || 'default'"
          />
        </div>
        <div class="amount-block">
          <span class="amount-label">{{ FINANCE_DOC_TYPE[doc.docType] }}金额</span>
          <span class="amount-val">¥{{ formatMoney(doc.actualAmount ?? doc.plannedAmount) }}</span>
        </div>
        <div class="meta">
          <van-cell title="关联任务" :value="doc.taskNo || doc.taskId" />
          <van-cell title="收款人" :value="doc.payeeName || '-'" />
          <van-cell title="支付方式" :value="doc.payMethod ? PAY_METHOD[doc.payMethod] : '-'" />
          <van-cell title="计划支付时间" :value="formatDateTime(doc.plannedPayTime)" />
          <van-cell title="实际支付时间" :value="formatDateTime(doc.actualPayTime)" />
        </div>
      </div>

      <div class="card">
        <div class="section-title">费用明细</div>
        <div v-for="it in doc.items" :key="it.id" class="item-row">
          <div class="item-left">
            <div class="item-name">{{ it.itemName || it.itemType }}</div>
            <div class="item-meta">
              <template v-if="it.quantity">
                {{ it.quantity }} {{ it.unit || '' }} × ¥{{ formatMoney(it.unitPrice || 0) }}
              </template>
            </div>
          </div>
          <div class="item-amount">¥{{ formatMoney(it.amount) }}</div>
        </div>
        <van-empty v-if="!doc.items?.length" description="暂无费用项" />
      </div>

      <div v-if="doc.payVoucherUrl" class="card">
        <div class="section-title">支付凭证</div>
        <van-image :src="doc.payVoucherUrl" fit="contain" width="100%" />
      </div>

      <div v-if="doc.remark" class="card">
        <div class="section-title">备注</div>
        <p class="remark">{{ doc.remark }}</p>
      </div>
    </div>
    <van-loading v-else class="loading" type="spinner" />
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import PageContainer from '@/components/PageContainer.vue';
import StatusTag from '@/components/StatusTag.vue';
import { getFinanceDetail, type FinanceDocDetail } from '@/api/finance';
import { FINANCE_DOC_TYPE, FINANCE_STATUS, PAY_METHOD } from '@/views/task/status-config';
import { formatDateTime, formatMoney } from '@/utils/format';

const route = useRoute();
const doc = ref<FinanceDocDetail | null>(null);

onMounted(async () => {
  const id = Number(route.params.id);
  if (!id) return;
  doc.value = await getFinanceDetail(id);
});
</script>

<style lang="scss" scoped>
.finance-detail {
  padding-bottom: $spacing-xl;
}
.card {
  margin: $spacing-md;
  padding: $spacing-md $spacing-lg;
  background: #fff;
  border-radius: $border-radius-md;
  box-shadow: $shadow-card;
}
.header {
  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .doc-no {
      font-weight: 600;
    }
  }
  .amount-block {
    margin-top: $spacing-md;
    .amount-label {
      color: $text-secondary;
      font-size: $font-size-sm;
      margin-right: $spacing-sm;
    }
    .amount-val {
      font-size: 26px;
      font-weight: 600;
      color: $brand-primary;
    }
  }
  .meta {
    margin-top: $spacing-md;
    border-top: 1px solid $border-color;
    padding-top: $spacing-sm;
    :deep(.van-cell) {
      padding: 8px 0;
    }
  }
}
.section-title {
  font-size: $font-size-md;
  font-weight: 600;
  margin-bottom: $spacing-sm;
}
.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-sm 0;
  border-bottom: 1px dashed $border-color;
  &:last-child {
    border-bottom: none;
  }
  .item-meta {
    font-size: $font-size-xs;
    color: $text-secondary;
    margin-top: 2px;
  }
  .item-amount {
    font-weight: 600;
    color: $brand-primary;
  }
}
.remark {
  color: $text-secondary;
  font-size: $font-size-sm;
  line-height: 1.6;
}
.loading {
  text-align: center;
  padding: 80px 0;
}
</style>
