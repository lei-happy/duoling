<template>
  <el-drawer
    title="运费计算明细"
    :model-value="visible"
    direction="rtl"
    size="900px"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <div v-if="loading" class="empty-block" v-loading="loading"></div>
    <div v-else-if="!result" class="empty-block">
      <el-empty description="暂无计算结果" />
    </div>
    <template v-else>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="结果ID">#{{ result.id }}</el-descriptions-item>
        <el-descriptions-item label="运单版本">{{ result.waybillVersion }}</el-descriptions-item>
        <el-descriptions-item label="计算引擎">{{ result.calcEngineVersion }}</el-descriptions-item>
        <el-descriptions-item label="计算时间">{{ result.calcTime }}</el-descriptions-item>
        <el-descriptions-item label="触发方式">{{ result.triggeredBy }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(result.calcStatus)" size="small">
            {{ result.calcStatus }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总运费" :span="3">
          <span class="total-amount">¥ {{ formatAmount(result.totalAmount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="result.errorMessage" label="错误" :span="3">
          {{ result.errorMessage }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="detail-cap">货物明细</div>
      <el-table
        :data="result.details"
        border
        stripe
        size="small"
        max-height="380"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="trace-block">
              <div class="trace-cap">匹配过程留痕</div>
              <pre class="trace-json">{{ formatJson(row.matchTraceJson) }}</pre>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="车型" min-width="160">
          <template #default="{ row }">
            {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="64" align="center" />
        <el-table-column label="命中规则" min-width="120">
          <template #default="{ row }">
            <span v-if="row.matchedRuleId">
              规则 #{{ row.matchedRuleId }}
              <el-tag size="small" type="info">v{{ row.matchedRuleVersion }}</el-tag>
            </span>
            <el-tag v-else type="danger" size="small">未命中</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="合同" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.matchedContractId">#{{ row.matchedContractId }}</span>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column label="车型匹配" width="92" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="modelMatchType(row.modelMatchType)">
              {{ modelMatchText(row.modelMatchType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="方向" width="64" align="center">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="row.direction === 'reverse' ? 'warning' : 'primary'"
            >
              {{ row.direction === 'reverse' ? '反向' : '正向' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="72" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.matchScore ?? 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unitPrice" label="单价" width="92" align="right">
          <template #default="{ row }">
            {{ formatAmount(row.unitPrice) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">
            <strong>{{ formatAmount(row.amount) }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="row.calcStatus === 'success' ? 'success' : 'danger'"
            >
              {{ row.calcStatus }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
      <el-button type="primary" :disabled="!waybillId" @click="onRecalc">
        立即重算
      </el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getWaybillFreightResult, recalculateWaybill } from '@/api/waybill';

  interface FreightDetail {
    id: number;
    vehicleBrand?: string;
    vehicleModel?: string;
    quantity: number;
    matchedContractId?: number | null;
    matchedRuleId?: number | null;
    matchedRuleVersion?: number | null;
    direction?: string | null;
    modelMatchType?: string | null;
    unitPrice?: number | null;
    amount?: number | null;
    matchScore?: number | null;
    matchTraceJson?: unknown;
    calcStatus?: string | null;
    errorType?: string | null;
    errorMessage?: string | null;
  }

  interface FreightResult {
    id: number;
    waybillId: number;
    waybillVersion: number;
    totalAmount?: number | null;
    calcStatus?: string | null;
    calcEngineVersion?: string | null;
    calcTime?: string | null;
    errorMessage?: string | null;
    triggeredBy?: string | null;
    details: FreightDetail[];
  }

  const props = defineProps<{
    visible: boolean;
    waybillId: number | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const loading = ref(false);
  const result = ref<FreightResult | null>(null);

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const formatAmount = (v?: number | null) =>
    v == null ? '--' : Number(v).toFixed(2);

  const formatJson = (val: unknown): string => {
    if (val == null) return '--';
    try {
      const obj = typeof val === 'string' ? JSON.parse(val) : val;
      return JSON.stringify(obj, null, 2);
    } catch (_) {
      return String(val);
    }
  };

  const statusType = (s?: string | null) => {
    if (s === 'success') return 'success';
    if (s === 'partial_success') return 'warning';
    if (s === 'failed' || s === 'exception') return 'danger';
    return 'info';
  };

  const modelMatchType = (t?: string | null) => {
    if (t === 'series') return 'success';
    if (t === 'brand') return 'primary';
    if (t === 'general') return 'info';
    return 'info';
  };
  const modelMatchText = (t?: string | null) => {
    if (t === 'series') return '车系';
    if (t === 'brand') return '品牌';
    if (t === 'general') return '通用';
    return t || '--';
  };

  const load = async () => {
    if (!props.waybillId) return;
    loading.value = true;
    try {
      const data = (await getWaybillFreightResult(props.waybillId)) as FreightResult | null;
      result.value = data;
    } catch (_) {
      result.value = null;
    } finally {
      loading.value = false;
    }
  };

  const onOpen = () => load();

  const onRecalc = async () => {
    if (!props.waybillId) return;
    try {
      await recalculateWaybill(props.waybillId);
      EleMessage.success({ message: '已入队，等待 worker 处理', plain: true });
      setTimeout(load, 1000);
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) load();
      else result.value = null;
    }
  );
</script>

<style scoped lang="scss">
  .empty-block {
    padding: 32px 0;
    text-align: center;
    min-height: 200px;
  }
  .total-amount {
    font-size: 18px;
    font-weight: 700;
    color: var(--el-color-primary);
  }
  .detail-cap {
    margin: 16px 0 8px;
    font-size: 14px;
    font-weight: 600;
  }
  .trace-block {
    padding: 8px 16px;
  }
  .trace-cap {
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
  }
  .trace-json {
    background: var(--el-fill-color-light);
    border-radius: 6px;
    padding: 8px;
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 320px;
    overflow: auto;
  }
</style>
