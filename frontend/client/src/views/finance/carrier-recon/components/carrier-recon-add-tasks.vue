<template>
  <el-dialog
    :model-value="visible"
    title="补挂任务"
    width="880px"
    top="8vh"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div class="finance-cand-head">
      <el-input
        v-model="keyword"
        placeholder="任务号/车牌"
        clearable
        style="width: 200px"
        @change="load"
      />
      <el-select v-model="billingBase" style="width: 130px">
        <el-option
          v-for="o in BILLING_BASE_OPTIONS"
          :key="o.value"
          :value="o.value"
          :label="o.label"
        />
      </el-select>
      <span class="finance-cand-tip">已选 {{ selected.length }} 个任务</span>
    </div>

    <el-table
      :data="rows"
      v-loading="loading"
      height="340"
      row-key="taskId"
      :highlight-current-row="true"
      @selection-change="(v: CarrierReconCandidate[]) => (selected = v)"
    >
      <el-table-column type="selection" width="42" />
      <el-table-column prop="taskNo" label="任务号" min-width="150" />
      <el-table-column prop="plateNumber" label="车牌" width="110" />
      <el-table-column
        prop="signedQuantity"
        label="台数"
        width="80"
        align="center"
      />
      <el-table-column label="运费成本" width="110" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.carrierCostAmount) }}
        </template>
      </el-table-column>
      <el-table-column label="已预付" width="100" align="right">
        <template #default="{ row }">
          <span v-if="row.prepaidOffsetAmount" class="offset">
            {{ formatMoney(row.prepaidOffsetAmount) }}
          </span>
          <span v-else class="muted">--</span>
        </template>
      </el-table-column>
      <el-table-column label="应付净额" width="110" align="right">
        <template #default="{ row }">
          <span class="strong">¥ {{ formatMoney(row.netAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="交车时间" width="160" align="center">
        <template #default="{ row }">{{
          formatDate(row.signedAt) || '--'
        }}</template>
      </el-table-column>
      <template #empty>
        <div class="finance-cand-empty">这个承运商已经没有可补挂的任务了</div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        加入对账单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addCarrierReconLines,
    listCarrierReconCandidates
  } from '@/api/finance/carrier-recon';
  import type { CarrierReconCandidate } from '@/api/finance/carrier-recon/model';
  import { formatDate } from '@/utils/date-util';
  import { BILLING_BASE_OPTIONS, formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    reconId: number;
    carrierId: number;
    periodStart?: string;
    periodEnd?: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const rows = ref<CarrierReconCandidate[]>([]);
  const selected = ref<CarrierReconCandidate[]>([]);
  const keyword = ref('');
  const billingBase = ref(1);
  const loading = ref(false);
  const saving = ref(false);

  const onOpen = () => {
    keyword.value = '';
    selected.value = [];
    load();
  };

  const load = async () => {
    loading.value = true;
    try {
      const res = await listCarrierReconCandidates({
        carrierId: props.carrierId,
        periodStart: props.periodStart?.slice(0, 10),
        periodEnd: props.periodEnd?.slice(0, 10),
        keyword: keyword.value || void 0,
        reconId: props.reconId
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
    if (!selected.value.length) {
      EleMessage.warning({ message: '请勾选要补挂的任务', plain: true });
      return;
    }
    saving.value = true;
    try {
      await addCarrierReconLines(
        props.reconId,
        selected.value.map((r) => r.taskId),
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
  @use '../../_shared/ui.scss';

  .strong {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  .offset {
    color: var(--el-color-info);
    font-variant-numeric: tabular-nums;
  }

  .muted {
    color: var(--el-text-color-secondary);
  }
</style>
