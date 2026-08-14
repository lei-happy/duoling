<template>
  <el-dialog
    :model-value="visible"
    title="补挂任务"
    width="860px"
    top="8vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div class="pick-head">
      <el-form-item label="计件口径" class="inline-item">
        <el-select v-model="billingBase" size="small" style="width: 120px">
          <el-option
            v-for="o in BILLING_BASE_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="提成单价" class="inline-item">
        <el-input-number
          v-model="unitPrice"
          :min="0"
          :precision="2"
          :controls="false"
          size="small"
          style="width: 120px"
        />
      </el-form-item>
      <span class="pick-tip">
        已选 {{ selected.length }} 个任务，共 {{ selectedQuantity }} 台
      </span>
    </div>

    <el-table
      :data="rows"
      v-loading="loading"
      height="340"
      row-key="taskId"
      size="small"
      @selection-change="(v: PayrollCandidate[]) => (selected = v)"
    >
      <el-table-column type="selection" width="42" />
      <el-table-column prop="taskNo" label="任务号" min-width="150" />
      <el-table-column prop="plateNumber" label="车牌" width="110" />
      <el-table-column label="起运 → 目的" min-width="170">
        <template #default="{ row }">
          {{ row.origin || '--' }} → {{ row.destination || '--' }}
        </template>
      </el-table-column>
      <el-table-column
        prop="signedQuantity"
        label="台数"
        width="80"
        align="center"
      />
      <el-table-column label="已预支" width="110" align="right">
        <template #default="{ row }">
          <span v-if="row.prepaidPaidAmount" class="offset">
            {{ formatMoney(row.prepaidPaidAmount) }}
          </span>
          <span v-else class="muted">--</span>
        </template>
      </el-table-column>
      <el-table-column label="交车时间" width="160" align="center">
        <template #default="{ row }">
          {{ formatDate(row.signedAt) || '--' }}
        </template>
      </el-table-column>
      <template #empty>
        <div class="pick-empty">这个司机暂时没有可补挂的任务</div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        补挂所选任务
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addPayrollTasks,
    listPayrollCandidates
  } from '@/api/finance/driver-payroll';
  import type { PayrollCandidate } from '@/api/finance/driver-payroll/model';
  import { formatDate } from '@/utils/date-util';
  import { BILLING_BASE_OPTIONS, formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    payrollId?: number | null;
    driverId?: number;
    periodStart?: string;
    periodEnd?: string;
    defaultUnitPrice?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const rows = ref<PayrollCandidate[]>([]);
  const selected = ref<PayrollCandidate[]>([]);
  const billingBase = ref(1);
  const unitPrice = ref<number | undefined>(void 0);

  const selectedQuantity = computed(() =>
    selected.value.reduce((sum, r) => sum + Number(r.signedQuantity || 0), 0)
  );

  const onOpen = async () => {
    rows.value = [];
    selected.value = [];
    billingBase.value = 1;
    unitPrice.value = props.defaultUnitPrice;
    if (!props.driverId) return;
    loading.value = true;
    try {
      const res = await listPayrollCandidates({
        driverId: props.driverId,
        periodStart: props.periodStart,
        periodEnd: props.periodEnd
      });
      rows.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '任务加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const save = async () => {
    if (!props.payrollId) return;
    if (!selected.value.length) {
      EleMessage.warning({ message: '请勾选要补挂的任务', plain: true });
      return;
    }
    saving.value = true;
    try {
      await addPayrollTasks(
        props.payrollId,
        selected.value.map((r) => r.taskId),
        unitPrice.value,
        billingBase.value
      );
      EleMessage.success({
        message: `已补挂 ${selected.value.length} 个任务`,
        plain: true
      });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '补挂失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .pick-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .inline-item {
    margin-bottom: 0;
  }

  .pick-tip {
    margin-left: auto;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .pick-empty {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
  }

  .offset {
    color: var(--el-color-warning);
    font-variant-numeric: tabular-nums;
  }

  .muted {
    color: var(--el-text-color-secondary);
  }
</style>
