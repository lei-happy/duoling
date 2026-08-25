<template>
  <inspect-dialog
    :visible="visible"
    title="计算明细"
    :subtitle="waybillNo || ''"
    :copyable-subtitle="!!waybillNo"
    copy-subtitle-success="已复制计划号"
    copy-subtitle-empty="无可复制的计划号"
    copy-subtitle-label="复制计划号"
    width="920px"
    :loading="loading"
    dialog-class="wbi-dialog--freight"
    @update:visible="updateVisible"
  >
    <template #header-extra>
      <el-tag
        v-if="result"
        :type="statusType(result.calcStatus)"
        effect="light"
        size="small"
      >
        {{ calcStatusLabel(result.calcStatus) }}
      </el-tag>
    </template>

    <div v-if="result" class="wbf">
      <section class="wbi-hero wbi-hero--freight" aria-label="运费摘要">
        <div class="wbi-hero__who">运费结果</div>
        <div class="wbi-hero__amount-row">
          <div>
            <span class="wbi-hero__kicker">总运费</span>
            <div class="wbi-hero__amount">
              ¥ {{ formatAmount(result.totalAmount) }}
            </div>
          </div>
        </div>
      </section>

      <section class="wbi-section">
        <h3 class="wbi-section__title">计算信息</h3>
        <div class="wbi-group">
          <div class="wbi-row">
            <span class="wbi-row__label">计划版本</span>
            <span class="wbi-row__value">{{ result.waybillVersion }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">计价版本</span>
            <span class="wbi-row__value">{{
              result.calcEngineVersion || '—'
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">计算时间</span>
            <span class="wbi-row__value">{{
              formatCalcTime(result.calcTime)
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">触发原因</span>
            <span class="wbi-row__value">{{
              triggeredByLabel(result.triggeredBy)
            }}</span>
          </div>
        </div>
      </section>

      <el-alert
        v-if="showExceptionNotice"
        type="warning"
        show-icon
        :closable="false"
        class="wbf-alert"
      >
        <div class="wbf-alert__body">
          <p class="wbf-alert__text">{{ displayErrorMessage }}</p>
          <div v-if="hasAbnormalDetailRows" class="wbf-alert__actions">
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

      <section class="wbi-section">
        <div class="wbf-table-head">
          <h3 class="wbi-section__title">商品车明细</h3>
          <el-text v-if="exceptionOnly" size="small" type="info">
            已筛选 {{ displayDetails.length }} 条
          </el-text>
        </div>
        <div class="wbi-group wbf-table-wrap">
          <el-table
            v-if="displayDetails.length"
            :data="displayDetails"
            border
            stripe
            size="small"
            class="wbf-table"
            max-height="420"
            :row-class-name="detailRowClassName"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="wbf-trace">
                  <div class="wbf-trace__cap">匹配过程留痕</div>
                  <pre class="wbf-trace__json">{{
                    formatJson(row.matchTraceJson)
                  }}</pre>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="车型" min-width="160">
              <template #default="{ row }">
                {{ row.vehicleBrand || '—' }} / {{ row.vehicleModel || '—' }}
              </template>
            </el-table-column>
            <el-table-column
              prop="quantity"
              label="台数"
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
                <span v-else>—</span>
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
          <el-empty v-else description="当前筛选下无明细" :image-size="72" />
        </div>
      </section>
    </div>
    <el-empty
      v-else-if="!loading"
      description="暂无计算结果"
      :image-size="80"
    />

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
      <el-button type="primary" :disabled="!waybillId" @click="onRecalc">
        立即重算
      </el-button>
    </template>
  </inspect-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getWaybillFreightResult, recalculateWaybill } from '@/api/waybill';
  import { formatDateTime } from '@/utils/date-util';
  import InspectDialog from '@/components/InspectDialog/index.vue';

  defineOptions({ name: 'WaybillFreightDetail' });

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
    waybillNo?: string | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'sync-list'): void;
  }>();

  const FREIGHT_RECALC_SUBMIT_MSG =
    '已提交运费重新计算，请稍候在本弹框查看结果；列表中的计算状态也会更新。';

  const loading = ref(false);
  const result = ref<FreightResult | null>(null);
  const exceptionOnly = ref(false);

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const formatAmount = (v?: number | null) =>
    v == null ? '—' : Number(v).toFixed(2);

  const formatCalcTime = (t?: string | null) => {
    if (!t) return '—';
    const d = formatDateTime(t);
    return d && d !== '--' ? d : t;
  };

  const formatJson = (val: unknown): string => {
    if (val == null) return '—';
    try {
      const obj = typeof val === 'string' ? JSON.parse(val) : val;
      return JSON.stringify(obj, null, 2);
    } catch (_) {
      return String(val);
    }
  };

  const TRIGGERED_BY_MAP: Record<string, string> = {
    waybill_changed: '计划变更',
    contract_changed: '合同变更',
    rule_changed: '运价规则变更',
    manual_recalc: '手动重算',
    batch_import: '批量导入'
  };

  const triggeredByLabel = (v?: string | null) => {
    if (v == null || v === '') return '—';
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
    if (s == null || s === '') return '—';
    return CALC_STATUS_MAP[s] ?? s;
  };

  const detailCalcStatusLabel = (s?: string | null) => {
    if (s == null || s === '') return '—';
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
    return t || '—';
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
        return '存在异常或未完全成功的明细行，对应数据在下方「商品车明细」中。可使用「仅看异常/未成功明细」快速筛选。';
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
    row.calcStatus !== 'success' ? 'wbf-row--warn' : '';

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
  .wbf-alert {
    margin-top: 16px;
    border-radius: 10px;

    :deep(.el-alert__content) {
      width: 100%;
    }
  }

  .wbf-alert__body {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .wbf-alert__text {
    margin: 0;
    font-size: 13px;
    line-height: 1.55;
    color: var(--el-text-color-regular);
  }

  .wbf-alert__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .wbf-table-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
  }

  .wbf-table-wrap {
    overflow: hidden;
  }

  .wbf-table {
    width: 100%;
  }

  :deep(.wbf-row--warn) > td {
    background-color: var(--el-color-danger-light-9) !important;
  }

  .wbf-trace {
    padding: 8px 16px;
  }

  .wbf-trace__cap {
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
  }

  .wbf-trace__json {
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
