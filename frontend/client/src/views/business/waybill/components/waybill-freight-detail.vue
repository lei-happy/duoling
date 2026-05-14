<template>
  <el-drawer
    class="waybill-freight-drawer"
    title="运费计算明细"
    :model-value="visible"
    direction="rtl"
    size="920px"
    @update:model-value="updateVisible"
  >
    <div v-if="loading" class="empty-block" v-loading="loading"></div>
    <div v-else-if="!result" class="empty-block">
      <el-empty description="暂无计算结果" />
    </div>
    <div v-else class="freight-drawer-content">
      <el-card shadow="never" class="freight-meta-card">
        <template #header>
          <div class="freight-meta-card__header">
            <span class="freight-meta-card__title">计算摘要</span>
            <el-tag
              :type="statusType(result.calcStatus)"
              effect="light"
              size="small"
            >
              {{ calcStatusLabel(result.calcStatus) }}
            </el-tag>
          </div>
        </template>
        <el-row :gutter="[16, 14]">
          <el-col :xs="24" :sm="12" :md="8">
            <div class="kv">
              <span class="kv__l">结果 ID</span>
              <span class="kv__v">#{{ result.id }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="kv">
              <span class="kv__l">运单版本</span>
              <span class="kv__v">{{ result.waybillVersion }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="kv">
              <span class="kv__l">计算引擎</span>
              <span class="kv__v">{{ result.calcEngineVersion || '--' }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="kv">
              <span class="kv__l">计算时间</span>
              <span class="kv__v">{{ formatCalcTime(result.calcTime) }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="kv">
              <span class="kv__l">触发方式</span>
              <span class="kv__v">{{
                triggeredByLabel(result.triggeredBy)
              }}</span>
            </div>
          </el-col>
        </el-row>
        <div class="freight-total-banner">
          <span class="freight-total-banner__label">总运费</span>
          <span class="freight-total-banner__amt"
            >¥ {{ formatAmount(result.totalAmount) }}</span
          >
        </div>
      </el-card>

      <el-alert
        v-if="showExceptionNotice"
        type="warning"
        show-icon
        :closable="false"
        class="freight-exception-alert"
      >
        <div class="freight-exception-alert__body">
          <p class="freight-exception-alert__text">{{ displayErrorMessage }}</p>
          <div
            v-if="hasAbnormalDetailRows"
            class="freight-exception-alert__actions"
          >
            <el-button
              type="primary"
              size="small"
              plain
              @click="exceptionOnly = !exceptionOnly"
            >
              {{ exceptionOnly ? '显示全部明细' : '仅看异常/未成功明细' }}
            </el-button>
          </div>
        </div>
      </el-alert>

      <el-card shadow="never" class="freight-table-card">
        <template #header>
          <div class="freight-table-card__head">
            <span class="freight-table-card__title">货物明细</span>
            <el-text v-if="exceptionOnly" size="small" type="info">
              已筛选 {{ displayDetails.length }} 条
            </el-text>
          </div>
        </template>
        <el-table
          v-if="displayDetails.length"
          :data="displayDetails"
          border
          stripe
          size="small"
          class="freight-detail-table"
          max-height="420"
          :row-class-name="detailRowClassName"
        >
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="trace-block">
                <div class="trace-cap">匹配过程留痕</div>
                <pre class="trace-json">{{
                  formatJson(row.matchTraceJson)
                }}</pre>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="车型" min-width="160">
            <template #default="{ row }">
              {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
            </template>
          </el-table-column>
          <el-table-column
            prop="quantity"
            label="数量"
            width="64"
            align="center"
          />
          <el-table-column label="命中规则" min-width="120">
            <template #default="{ row }">
              <span v-if="row.matchedRuleId">
                规则 #{{ row.matchedRuleId }}
                <el-tag size="small" type="info"
                  >v{{ row.matchedRuleVersion }}</el-tag
                >
              </span>
              <el-tag v-else type="danger" size="small">未命中</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="合同" width="80" align="center">
            <template #default="{ row }">
              <span v-if="row.matchedContractId"
                >#{{ row.matchedContractId }}</span
              >
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
          <el-table-column label="方向" width="72" align="center">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="
                  isReverseDirection(row.direction) ? 'warning' : 'primary'
                "
              >
                {{ directionLabel(row.direction) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="评分" width="72" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="success">{{
                row.matchScore ?? 0
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="unitPrice"
            label="单价"
            width="92"
            align="right"
          >
            <template #default="{ row }">
              {{ formatAmount(row.unitPrice) }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="100" align="right">
            <template #default="{ row }">
              <strong>{{ formatAmount(row.amount) }}</strong>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="88" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="detailStatusType(row.calcStatus)">
                {{ detailCalcStatusLabel(row.calcStatus) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="当前筛选下无明细" />
      </el-card>
    </div>

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
      <el-button type="primary" :disabled="!waybillId" @click="onRecalc">
        立即重算
      </el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getWaybillFreightResult, recalculateWaybill } from '@/api/waybill';
  import { formatDateTime } from '@/utils/date-util';

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
    (e: 'sync-list'): void;
  }>();

  const FREIGHT_RECALC_SUBMIT_MSG =
    '已提交运费重新计算，请稍候在本抽屉查看结果；列表中的计算状态也会更新。';

  const loading = ref(false);
  const result = ref<FreightResult | null>(null);
  const exceptionOnly = ref(false);

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const formatAmount = (v?: number | null) =>
    v == null ? '--' : Number(v).toFixed(2);

  const formatCalcTime = (t?: string | null) => {
    if (!t) return '--';
    const d = formatDateTime(t);
    return d && d !== '--' ? d : t;
  };

  const formatJson = (val: unknown): string => {
    if (val == null) return '--';
    try {
      const obj = typeof val === 'string' ? JSON.parse(val) : val;
      return JSON.stringify(obj, null, 2);
    } catch (_) {
      return String(val);
    }
  };

  const TRIGGERED_BY_MAP: Record<string, string> = {
    waybill_changed: '运单变更',
    contract_changed: '合同变更',
    rule_changed: '运价规则变更',
    manual_recalc: '手动重算',
    batch_import: '批量导入'
  };

  const triggeredByLabel = (v?: string | null) => {
    if (v == null || v === '') return '--';
    return TRIGGERED_BY_MAP[v] ?? v;
  };

  const CALC_STATUS_MAP: Record<string, string> = {
    success: '成功',
    partial: '部分成功',
    partial_success: '部分成功',
    exception: '异常',
    failed: '失败',
    error: '错误'
  };

  const calcStatusLabel = (s?: string | null) => {
    if (s == null || s === '') return '--';
    return CALC_STATUS_MAP[s] ?? s;
  };

  const detailCalcStatusLabel = (s?: string | null) => {
    if (s == null || s === '') return '--';
    if (s === 'success') return '成功';
    return CALC_STATUS_MAP[s] ?? s;
  };

  const statusType = (s?: string | null) => {
    if (s === 'success') return 'success';
    if (s === 'partial' || s === 'partial_success') return 'warning';
    if (s === 'failed' || s === 'exception' || s === 'error') return 'danger';
    return 'info';
  };

  const detailStatusType = (s?: string | null) => {
    if (s === 'success') return 'success';
    if (s === 'partial' || s === 'partial_success') return 'warning';
    return 'danger';
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

  const isReverseDirection = (d?: string | null) =>
    d === 'reverse' || d === 'backward';

  const directionLabel = (d?: string | null) => {
    if (isReverseDirection(d)) return '反向';
    if (d === 'forward' || d == null || d === '') return '正向';
    return d;
  };

  const hasAbnormalDetailRows = computed(() =>
    (result.value?.details ?? []).some((r) => r.calcStatus !== 'success')
  );

  const displayErrorMessage = computed(() => {
    const raw = result.value?.errorMessage?.trim();
    if (raw) {
      if (/result_detail/i.test(raw)) {
        return '存在异常或未完全成功的明细行，对应数据在下方「货物明细」表中（即计算结果明细表）。可使用「仅看异常/未成功明细」快速筛选。';
      }
      return raw;
    }
    if (
      hasAbnormalDetailRows.value &&
      result.value &&
      result.value.calcStatus !== 'success'
    ) {
      return '计算未完全成功，请查看下方明细中状态非「成功」的行。';
    }
    return '';
  });

  const showExceptionNotice = computed(() => {
    if (!result.value) return false;
    if (result.value.errorMessage?.trim()) return true;
    return hasAbnormalDetailRows.value && result.value.calcStatus !== 'success';
  });

  const displayDetails = computed(() => {
    const list = result.value?.details ?? [];
    if (!exceptionOnly.value) return list;
    return list.filter((r) => r.calcStatus !== 'success');
  });

  const detailRowClassName = ({ row }: { row: FreightDetail }) =>
    row.calcStatus !== 'success' ? 'freight-detail-row--warn' : '';

  const load = async () => {
    if (!props.waybillId) return;
    loading.value = true;
    try {
      const data = (await getWaybillFreightResult(
        props.waybillId
      )) as FreightResult | null;
      result.value = data;
      exceptionOnly.value = false;
      if (data != null) {
        emit('sync-list');
      }
    } catch (_) {
      result.value = null;
    } finally {
      loading.value = false;
    }
  };

  const onRecalc = async () => {
    if (!props.waybillId) return;
    try {
      await recalculateWaybill(props.waybillId);
      EleMessage.success({
        message: FREIGHT_RECALC_SUBMIT_MSG,
        plain: true
      });
      emit('sync-list');
      setTimeout(() => void load(), 1200);
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) load();
      else {
        result.value = null;
        exceptionOnly.value = false;
      }
    }
  );
</script>

<style scoped lang="scss">
  .empty-block {
    padding: 32px 0;
    text-align: center;
    min-height: 200px;
  }

  .freight-drawer-content {
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding-bottom: 8px;
  }

  .freight-meta-card {
    border-radius: 10px;
    border: 1px solid var(--el-border-color-lighter);
    background: linear-gradient(
      180deg,
      var(--el-fill-color-blank) 0%,
      var(--el-fill-color-extra-light) 100%
    );

    :deep(.el-card__header) {
      padding: 12px 16px;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }

    :deep(.el-card__body) {
      padding: 16px;
    }
  }

  .freight-meta-card__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .freight-meta-card__title {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .kv {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-height: 44px;
  }

  .kv__l {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .kv__v {
    font-size: 14px;
    color: var(--el-text-color-primary);
    word-break: break-all;
  }

  .freight-total-banner {
    margin-top: 16px;
    padding: 12px 16px;
    border-radius: 8px;
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-7);
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
  }

  .freight-total-banner__label {
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-regular);
  }

  .freight-total-banner__amt {
    font-size: 22px;
    font-weight: 700;
    color: var(--el-color-primary);
    letter-spacing: 0.02em;
  }

  .freight-exception-alert {
    border-radius: 8px;

    :deep(.el-alert__content) {
      width: 100%;
    }
  }

  .freight-exception-alert__body {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .freight-exception-alert__text {
    margin: 0;
    font-size: 13px;
    line-height: 1.55;
    color: var(--el-text-color-regular);
  }

  .freight-exception-alert__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .freight-table-card {
    border-radius: 10px;
    border: 1px solid var(--el-border-color-lighter);

    :deep(.el-card__header) {
      padding: 10px 16px;
    }

    :deep(.el-card__body) {
      padding: 0 16px 16px;
    }
  }

  .freight-table-card__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .freight-table-card__title {
    font-size: 14px;
    font-weight: 600;
  }

  .freight-detail-table {
    width: 100%;
  }

  :deep(.freight-detail-row--warn) > td {
    background-color: var(--el-color-danger-light-9) !important;
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

<style lang="scss">
  .waybill-freight-drawer.el-drawer {
    .el-drawer__header {
      margin-bottom: 0;
      padding: 16px 20px 12px;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }

    .el-drawer__body {
      padding: 16px 20px 12px;
    }

    .el-drawer__footer {
      border-top: 1px solid var(--el-border-color-lighter);
      padding: 12px 20px;
    }
  }
</style>
