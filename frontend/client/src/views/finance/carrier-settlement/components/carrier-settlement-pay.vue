<template>
  <el-dialog
    :model-value="visible"
    title="登记付款"
    width="540px"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div v-if="detail" class="finance-identity">
      <div class="finance-identity__name">{{ detail.docNo }}</div>
      <div class="finance-identity__meta">
        {{ detail.carrierName }} · 应付 ¥
        {{ formatMoney(detail.plannedAmount) }}
      </div>
    </div>
    <el-alert
      v-if="detail?.isOffsetOnly === 1"
      type="warning"
      :closable="false"
      show-icon
      class="offset-alert"
      title="本单是纯抵账单：预付已经覆盖全额，确认后直接置为已支付，不需要填凭证。"
    />
    <p v-else class="finance-form-tip">
      这里登记的是「这张单付出去了」。要按批次统一打款，请走出纳台的批量打款。
    </p>
    <el-form
      v-if="detail?.isOffsetOnly !== 1"
      :model="form"
      label-width="0"
      class="finance-edit-form"
      v-loading="loading"
    >
      <el-form-item>
        <floating-label
          v-model="form.actualAmount"
          label="请输入付款金额"
          type="input-number"
          :input-number-min="0.01"
          :input-number-precision="2"
          :input-number-step="100"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.paidAt"
          label="请选择付款时间"
          type="date"
          date-type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          :clearable="false"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.payMethod"
          label="请选择付款方式"
          type="select"
          :clearable="false"
        >
          <el-option
            v-for="o in PAY_METHOD_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.settlementAccountId"
          label="付款账户，留空沿用单上账户"
          type="select"
          clearable
        >
          <el-option
            v-for="a in accounts"
            :key="a.accountId"
            :value="a.accountId"
            :label="accountLabel(a)"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入付款凭证链接，选填"
          type="input"
          v-model="form.payVoucherUrl"
          :maxlength="500"
          clearable
        />
      </el-form-item>
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
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
  @use '../../_shared/ui.scss';

  .offset-alert {
    margin-bottom: 4px;
  }
</style>
