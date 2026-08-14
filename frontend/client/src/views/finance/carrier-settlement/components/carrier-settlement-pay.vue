<template>
  <el-dialog
    :model-value="visible"
    title="登记付款"
    width="540px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="detail?.isOffsetOnly === 1"
      type="info"
      :closable="false"
      show-icon
      class="tip"
      title="本单是纯抵账单：预付已经覆盖全额，确认后直接置为已支付，不需要填凭证。"
    />
    <el-alert
      v-else
      type="info"
      :closable="false"
      show-icon
      class="tip"
      title="这里登记的是「这张单付出去了」。要按批次统一打款，请走出纳台的批量打款。"
    />

    <el-form :model="form" label-width="96px" v-loading="loading">
      <el-form-item label="结算单">
        <span>
          {{ detail?.docNo || '--' }}
          <span class="muted">{{ detail?.carrierName }}</span>
        </span>
      </el-form-item>
      <el-form-item label="应付金额">
        <span class="num">¥ {{ formatMoney(detail?.plannedAmount) }}</span>
      </el-form-item>
      <template v-if="detail?.isOffsetOnly !== 1">
        <el-form-item label="付款金额" required>
          <el-input-number
            v-model="form.actualAmount"
            :min="0.01"
            :precision="2"
            :controls="false"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="付款时间" required>
          <el-date-picker
            v-model="form.paidAt"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="付款方式" required>
          <el-select v-model="form.payMethod" style="width: 100%">
            <el-option
              v-for="o in PAY_METHOD_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="付款账户">
          <el-select
            v-model="form.settlementAccountId"
            placeholder="留空沿用单上账户"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="a in accounts"
              :key="a.accountId"
              :value="a.accountId"
              :label="accountLabel(a)"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="付款凭证">
          <el-input
            v-model="form.payVoucherUrl"
            maxlength="500"
            placeholder="选填，回单链接"
          />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        {{ detail?.isOffsetOnly === 1 ? '确认抵账' : '确认付款' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    getCarrierSettle,
    listCarrierAccounts,
    payCarrierSettle
  } from '@/api/finance/carrier-settlement';
  import type {
    CarrierAccount,
    CarrierSettleDetail
  } from '@/api/finance/carrier-settlement/model';
  import { formatMoney, PAY_METHOD_OPTIONS } from '../../status-config';

  const props = defineProps<{ visible: boolean; settleId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const detail = ref<CarrierSettleDetail | null>(null);
  const accounts = ref<CarrierAccount[]>([]);
  const form = ref<{
    actualAmount?: number;
    paidAt?: string;
    payMethod: number;
    settlementAccountId?: number;
    payVoucherUrl?: string;
  }>({ payMethod: 1 });

  const accountLabel = (a: CarrierAccount) =>
    [a.accountLabel, a.bankAccountMasked].filter(Boolean).join(' · ');

  const nowText = () => {
    const d = new Date();
    const p = (n: number) => String(n).padStart(2, '0');
    return (
      `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ` +
      `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
    );
  };

  const onOpen = async () => {
    form.value = { payMethod: 1, paidAt: nowText() };
    detail.value = null;
    accounts.value = [];
    if (!props.settleId) return;
    loading.value = true;
    try {
      const d = await getCarrierSettle(props.settleId);
      detail.value = d ?? null;
      form.value.actualAmount = d?.unpaidAmount || d?.plannedAmount || void 0;
      form.value.settlementAccountId = d?.settlementAccountId;
      if (d?.carrierId) {
        accounts.value = await listCarrierAccounts(d.carrierId);
      }
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '结算单加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const save = async () => {
    if (!props.settleId) return;
    const offsetOnly = detail.value?.isOffsetOnly === 1;
    if (!offsetOnly) {
      if (!form.value.actualAmount || form.value.actualAmount <= 0) {
        EleMessage.warning({ message: '请填写付款金额', plain: true });
        return;
      }
      if (!form.value.paidAt) {
        EleMessage.warning({ message: '请选择付款时间', plain: true });
        return;
      }
    }
    saving.value = true;
    try {
      await payCarrierSettle(
        props.settleId,
        offsetOnly
          ? {}
          : {
              actualAmount: form.value.actualAmount,
              paidAt: form.value.paidAt,
              payMethod: form.value.payMethod,
              settlementAccountId: form.value.settlementAccountId,
              payVoucherUrl: form.value.payVoucherUrl
            }
      );
      EleMessage.success({
        message: offsetOnly ? '已确认抵账' : '已登记付款',
        plain: true
      });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '登记失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .tip {
    margin-bottom: 14px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .muted {
    margin-left: 8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
</style>
