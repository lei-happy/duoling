<!--
  客户信用提示条

  给业务页面（运单录入、派车确认等）用的一行提示：选中客户后显示该客户的逾期与额度
  情况。**只提示不阻断**——停不停单是业务决策，不由系统拦（见需求文档 12 §四）。

  文案与等级都由后端 `customer-brief` 给出，调用方不需要知道分桶阈值。
-->
<template>
  <el-alert
    v-if="brief?.alertMessage"
    :type="alertType"
    :closable="false"
    show-icon
    class="credit-tip"
  >
    <template #title>
      <span>{{ brief?.alertMessage }}</span>
      <el-link
        v-if="showLink"
        type="primary"
        :underline="false"
        class="credit-tip__link"
        @click="gotoAging"
      >
        看应收明细
      </el-link>
    </template>
  </el-alert>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import { getCustomerCreditBrief } from '@/api/finance/ar-aging';
  import type { CustomerCreditBrief } from '@/api/finance/ar-aging/model';
  import { ALERT_LEVEL_MAP } from '../status-config';

  const props = withDefaults(
    defineProps<{
      customerId?: number | null;
      /** 留痕场景，决定高危预警写进哪条审计记录 */
      scene?:
        | 'waybill_create'
        | 'task_dispatch'
        | 'recon_confirm'
        | 'settle_submit';
      /** 是否显示「看应收明细」跳转 */
      showLink?: boolean;
    }>(),
    { showLink: true }
  );

  const router = useRouter();
  const brief = ref<CustomerCreditBrief | null>(null);

  const alertType = computed(() => {
    const t = ALERT_LEVEL_MAP[brief.value?.alertLevel ?? 0]?.type || 'info';
    return (t === 'danger' ? 'error' : t) as
      | 'success'
      | 'info'
      | 'warning'
      | 'error';
  });

  const load = async (customerId?: number | null) => {
    if (!customerId) {
      brief.value = null;
      return;
    }
    try {
      brief.value =
        (await getCustomerCreditBrief(customerId, props.scene)) ?? null;
    } catch {
      // 信用提示是附加信息，拉不到就不显示，绝不影响主流程
      brief.value = null;
    }
  };

  const gotoAging = () => {
    router.push({
      path: '/finance/ar-aging',
      query: { customerId: props.customerId ?? void 0 }
    });
  };

  watch(() => props.customerId, load, { immediate: true });
</script>

<style lang="scss" scoped>
  .credit-tip {
    margin-bottom: 16px;

    &__link {
      margin-left: 8px;
      vertical-align: baseline;
    }
  }
</style>
