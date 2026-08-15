<template>
  <el-dialog
    :model-value="visible"
    title="登记收款"
    width="520px"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div v-if="detail" class="finance-identity">
      <div class="finance-identity__name">{{ detail.docNo }}</div>
      <div class="finance-identity__meta">
        {{ detail.customerName }} · 应收 ¥
        {{ formatMoney(detail.plannedAmount) }}
      </div>
    </div>
    <p class="finance-form-tip">
      这里登记的是「这张单收到钱了」。银行流水先入账再核销，请走出纳台的到账认领。
    </p>
    <el-form
      :model="form"
      label-width="0"
      class="finance-edit-form"
      v-loading="loading"
    >
      <el-form-item>
        <floating-label
          v-model="form.actualAmount"
          label="请输入收款金额"
          type="input-number"
          :input-number-min="0.01"
          :input-number-precision="2"
          :input-number-step="100"
          input-number-controls-position="right"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.receivedAt"
          label="请选择到账时间"
          type="date"
          date-type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          :clearable="false"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.receiveMethod"
          label="请选择收款方式"
          type="select"
          :clearable="false"
        >
          <el-option
            v-for="o in RECEIVE_METHOD_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入收款账户，选填"
          type="input"
          v-model.trim="form.receivedAccountLabel"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入收款凭证链接，选填"
          type="input"
          v-model.trim="form.voucherUrl"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        确认收款
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    getSettlement,
    receiveSettlement
  } from '@/api/finance/customer-settlement';
  import type { SettleDetail } from '@/api/finance/customer-settlement/model';
  import { formatMoney, RECEIVE_METHOD_OPTIONS } from '../../status-config';

  const props = defineProps<{ visible: boolean; settleId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const detail = ref<SettleDetail | null>(null);
  const form = ref<{
    actualAmount?: number;
    receivedAt?: string;
    receiveMethod: number;
    receivedAccountLabel?: string;
    voucherUrl?: string;
  }>({ receiveMethod: 1 });

  const nowText = () => {
    const d = new Date();
    const p = (n: number) => String(n).padStart(2, '0');
    return (
      `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ` +
      `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
    );
  };

  const onOpen = async () => {
    form.value = { receiveMethod: 1, receivedAt: nowText() };
    detail.value = null;
    if (!props.settleId) return;
    loading.value = true;
    try {
      const d = await getSettlement(props.settleId);
      detail.value = d ?? null;
      form.value.actualAmount =
        d?.unreceivedAmount || d?.plannedAmount || void 0;
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
    if (!form.value.actualAmount || form.value.actualAmount <= 0) {
      EleMessage.warning({ message: '请填写收款金额', plain: true });
      return;
    }
    if (!form.value.receivedAt) {
      EleMessage.warning({ message: '请选择到账时间', plain: true });
      return;
    }
    saving.value = true;
    try {
      await receiveSettlement(props.settleId, {
        actualAmount: form.value.actualAmount,
        receivedAt: form.value.receivedAt,
        receiveMethod: form.value.receiveMethod,
        receivedAccountLabel: form.value.receivedAccountLabel,
        voucherUrl: form.value.voucherUrl
      });
      EleMessage.success({ message: '已登记收款', plain: true });
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
</style>
