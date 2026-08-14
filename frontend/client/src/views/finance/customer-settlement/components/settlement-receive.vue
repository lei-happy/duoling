<template>
  <el-dialog
    :model-value="visible"
    title="登记收款"
    width="520px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="tip"
      title="这里登记的是「这张单收到钱了」。银行流水先入账再核销的场景，请走出纳台的到账认领。"
    />
    <el-form :model="form" label-width="96px" v-loading="loading">
      <el-form-item label="结算单">
        <span>
          {{ detail?.docNo || '--' }}
          <span class="muted">{{ detail?.customerName }}</span>
        </span>
      </el-form-item>
      <el-form-item label="应收金额">
        <span class="num">¥ {{ formatMoney(detail?.plannedAmount) }}</span>
      </el-form-item>
      <el-form-item label="收款金额" required>
        <el-input-number
          v-model="form.actualAmount"
          :min="0.01"
          :precision="2"
          :controls="false"
          style="width: 180px"
        />
      </el-form-item>
      <el-form-item label="到账时间" required>
        <el-date-picker
          v-model="form.receivedAt"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="收款方式" required>
        <el-select v-model="form.receiveMethod" style="width: 100%">
          <el-option
            v-for="o in RECEIVE_METHOD_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="收款账户">
        <el-input
          v-model="form.receivedAccountLabel"
          maxlength="100"
          placeholder="选填，如：工行公户 1234"
        />
      </el-form-item>
      <el-form-item label="收款凭证">
        <el-input
          v-model="form.voucherUrl"
          maxlength="500"
          placeholder="选填，回单链接"
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
