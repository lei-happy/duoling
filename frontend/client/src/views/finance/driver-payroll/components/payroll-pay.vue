<template>
  <el-dialog
    :model-value="visible"
    title="登记工资发放"
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
      title="登记后这批任务不能再改动。要按批次统一发薪，请走出纳台的批量打款。"
    />
    <el-form :model="form" label-width="96px" v-loading="loading">
      <el-form-item label="工资单">
        <span>
          {{ detail?.docNo || '--' }}
          <span class="muted">{{ detail?.driverName }}</span>
        </span>
      </el-form-item>
      <el-form-item label="实发合计">
        <span class="num">¥ {{ formatMoney(detail?.netAmount) }}</span>
      </el-form-item>
      <el-form-item label="发放金额" required>
        <el-input-number
          v-model="form.actualAmount"
          :min="0.01"
          :precision="2"
          :controls="false"
          style="width: 180px"
        />
      </el-form-item>
      <el-form-item label="发放时间" required>
        <el-date-picker
          v-model="form.paidAt"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="发放方式" required>
        <el-select v-model="form.payMethod" style="width: 100%">
          <el-option
            v-for="o in PAY_METHOD_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="发薪账户">
        <el-select
          v-model="form.accountId"
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
      <el-form-item label="发放凭证">
        <el-input
          v-model="form.payVoucherUrl"
          maxlength="500"
          placeholder="选填，回单链接"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        确认发放
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    getPayroll,
    listDriverAccounts,
    payPayroll
  } from '@/api/finance/driver-payroll';
  import type {
    DriverAccount,
    PayrollDetail
  } from '@/api/finance/driver-payroll/model';
  import { formatMoney, PAY_METHOD_OPTIONS } from '../../status-config';

  const props = defineProps<{ visible: boolean; payrollId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const detail = ref<PayrollDetail | null>(null);
  const accounts = ref<DriverAccount[]>([]);
  const form = ref<{
    actualAmount?: number;
    paidAt?: string;
    payMethod: number;
    accountId?: number;
    payVoucherUrl?: string;
  }>({ payMethod: 1 });

  const accountLabel = (a: DriverAccount) =>
    [a.accountTypeLabel, a.accountName, a.accountNoMasked]
      .filter(Boolean)
      .join(' · ');

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
    if (!props.payrollId) return;
    loading.value = true;
    try {
      const d = await getPayroll(props.payrollId);
      detail.value = d ?? null;
      form.value.actualAmount = d?.netAmount || void 0;
      form.value.accountId = d?.accountId;
      if (d?.driverId) {
        accounts.value = await listDriverAccounts(d.driverId);
      }
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '工资单加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const save = async () => {
    if (!props.payrollId) return;
    if (!form.value.actualAmount || form.value.actualAmount <= 0) {
      EleMessage.warning({ message: '请填写发放金额', plain: true });
      return;
    }
    if (!form.value.paidAt) {
      EleMessage.warning({ message: '请选择发放时间', plain: true });
      return;
    }
    saving.value = true;
    try {
      await payPayroll(props.payrollId, {
        actualAmount: form.value.actualAmount,
        paidAt: form.value.paidAt,
        payMethod: form.value.payMethod,
        accountId: form.value.accountId,
        payVoucherUrl: form.value.payVoucherUrl
      });
      EleMessage.success({ message: '已登记发放', plain: true });
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
