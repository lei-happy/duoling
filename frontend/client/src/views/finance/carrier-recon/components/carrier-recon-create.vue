<template>
  <el-dialog
    :model-value="visible"
    title="新建承运商对账单"
    width="940px"
    top="6vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="88px">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="承运商" required>
            <el-select
              v-model="form.carrierId"
              placeholder="请选择承运商"
              filterable
              style="width: 100%"
              @change="loadCandidates"
            >
              <el-option
                v-for="c in carriers"
                :key="c.id"
                :value="c.id"
                :label="c.carrierName"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="对账周期" required>
            <el-date-picker
              v-model="period"
              type="daterange"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%"
              @change="loadCandidates"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="计费基础">
            <el-select v-model="form.billingBase" style="width: 100%">
              <el-option
                v-for="o in BILLING_BASE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="备注">
            <el-input
              v-model="form.remark"
              placeholder="选填，会显示在对账单上"
              maxlength="200"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div class="cand-head">
      <span class="cand-title">可对账任务</span>
      <el-input
        v-model="keyword"
        placeholder="任务号/车牌"
        clearable
        size="small"
        style="width: 200px"
        @change="loadCandidates"
      />
      <span class="cand-tip">
        已选 {{ selected.length }} 个任务，应付净额 ¥
        {{ formatMoney(selectedNet) }}
      </span>
    </div>

    <el-table
      ref="tableRef"
      :data="candidates"
      v-loading="loading"
      height="320"
      row-key="taskId"
      size="small"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="42" reserve-selection />
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
        <template #default="{ row }">
          {{ formatDate(row.signedAt) || '--' }}
        </template>
      </el-table-column>
      <template #empty>
        <div class="cand-empty">
          {{
            form.carrierId
              ? '这个承运商在所选周期内没有可对账的任务，换个周期看看'
              : '先选承运商与对账周期，这里会列出可对账的任务'
          }}
        </div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        生成对账单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addCarrierRecon,
    listCarrierReconCandidates
  } from '@/api/finance/carrier-recon';
  import type { CarrierReconCandidate } from '@/api/finance/carrier-recon/model';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import { formatDate } from '@/utils/date-util';
  import { BILLING_BASE_OPTIONS, formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    carrierId?: number;
    carriers: CarrierSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', reconId?: number): void;
  }>();

  const tableRef = ref();
  const loading = ref(false);
  const saving = ref(false);
  const keyword = ref('');
  const period = ref<[string, string] | null>(null);
  const candidates = ref<CarrierReconCandidate[]>([]);
  const selected = ref<CarrierReconCandidate[]>([]);

  const form = ref<{
    carrierId?: number;
    billingBase: number;
    remark?: string;
  }>({ billingBase: 1 });

  const selectedNet = computed(() =>
    selected.value.reduce((sum, r) => sum + Number(r.netAmount || 0), 0)
  );

  const defaultPeriod = (): [string, string] => {
    const now = new Date();
    const first = new Date(now.getFullYear(), now.getMonth(), 1);
    const last = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    const fmt = (d: Date) =>
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
        d.getDate()
      ).padStart(2, '0')}`;
    return [fmt(first), fmt(last)];
  };

  const onOpen = () => {
    form.value = { carrierId: props.carrierId, billingBase: 1 };
    period.value = defaultPeriod();
    keyword.value = '';
    candidates.value = [];
    selected.value = [];
    tableRef.value?.clearSelection?.();
    if (props.carrierId) {
      loadCandidates();
    }
  };

  const onSelectionChange = (rows: CarrierReconCandidate[]) => {
    selected.value = rows;
  };

  const loadCandidates = async () => {
    if (!form.value.carrierId) {
      candidates.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listCarrierReconCandidates({
        carrierId: form.value.carrierId,
        periodStart: period.value?.[0],
        periodEnd: period.value?.[1],
        keyword: keyword.value || void 0
      });
      candidates.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '任务加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const save = async () => {
    if (!form.value.carrierId) {
      EleMessage.warning({ message: '请选择承运商', plain: true });
      return;
    }
    if (!period.value?.[0] || !period.value?.[1]) {
      EleMessage.warning({ message: '请选择对账周期', plain: true });
      return;
    }
    if (!selected.value.length) {
      EleMessage.warning({ message: '请勾选要对账的任务', plain: true });
      return;
    }
    saving.value = true;
    try {
      const detail = await addCarrierRecon({
        carrierId: form.value.carrierId,
        periodStart: period.value[0],
        periodEnd: period.value[1],
        taskIds: selected.value.map((r) => r.taskId),
        billingBase: form.value.billingBase,
        remark: form.value.remark
      });
      EleMessage.success({
        message: `已生成对账单，共 ${selected.value.length} 个任务`,
        plain: true
      });
      emit('update:visible', false);
      emit('done', detail?.id);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '生成失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .cand-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .cand-title {
    font-weight: 600;
  }

  .cand-tip {
    margin-left: auto;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .cand-empty {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
  }

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
