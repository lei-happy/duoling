<!--
  运单详情抽屉（精简版）

  展示：
  - 头部：运单号、状态标签（新语义化）、客户、起终地
  - 基本信息：起终地 / 计划装车/送达 / 经销商 / 计费金额 / 备注
  - 货物明细：cargo 列表
  - 挂接概要：hasActiveTaskItems / allocatedQuantity（按 cargo 求和）→ 给出操作建议

  本抽屉不提供编辑/删除入口；如需进一步操作，请回到任务台账查看相关任务挂接。
-->
<template>
  <el-drawer
    :model-value="visible"
    title="运单详情"
    direction="rtl"
    size="780px"
    :destroy-on-close="true"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
  >
    <div v-loading="loading" class="wb-detail">
      <template v-if="waybill">
        <!-- 头部摘要 -->
        <div class="wb-detail__header">
          <div>
            <div class="wb-detail__no">
              {{ waybill.waybillNo }}
              <waybill-status-tag
                :status="waybill.status"
                style="margin-left: 8px"
              />
              <el-tag
                v-if="waybill.hasActiveTaskItems"
                type="warning"
                effect="plain"
                size="small"
                style="margin-left: 4px"
              >
                有活跃任务挂接
              </el-tag>
            </div>
            <div class="wb-detail__meta">
              {{ waybill.customerName || '客户未填' }}
            </div>
          </div>
          <div class="wb-detail__route">
            <span>{{ waybill.origin || '--' }}</span>
            <el-icon style="margin: 0 6px"><Right /></el-icon>
            <span>{{ waybill.destination || '--' }}</span>
          </div>
        </div>

        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="客户">
            {{ waybill.customerName || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="计费金额">
            {{ formatAmount(waybill.freightAmount) }}
          </el-descriptions-item>
          <el-descriptions-item label="计划下发">
            {{ formatDateTime(waybill.planIssueTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="要求装车">
            {{ formatDateTime(waybill.requiredLoadTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="要求送达">
            {{ formatDateTime(waybill.requiredDeliverTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(waybill.createdAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="经销商" :span="2">
            {{ waybill.dealerName || '--' }}
            <span v-if="waybill.dealerContact" class="ele-text-secondary">
              / {{ waybill.dealerContact }}
            </span>
            <span v-if="waybill.dealerPhone" class="ele-text-secondary">
              / {{ waybill.dealerPhone }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ waybill.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 挂接概要 -->
        <el-divider content-position="left">任务挂接概要</el-divider>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="总台数">
            {{ totalQuantity }}
          </el-descriptions-item>
          <el-descriptions-item label="已分配台数">
            {{ waybill.allocatedQuantity ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="剩余可分配">
            {{ remainingQuantity }}
          </el-descriptions-item>
          <el-descriptions-item label="活跃挂接">
            <el-tag
              v-if="waybill.hasActiveTaskItems"
              type="warning"
              size="small"
            >
              存在
            </el-tag>
            <el-tag v-else type="info" size="small">无</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <el-alert
          v-if="waybill.hasActiveTaskItems"
          type="info"
          :closable="false"
          show-icon
          title="存在活跃任务挂接时，运单核心字段不可编辑"
          description="如需更改装车量/起终地等关键字段，请先在「任务台账」找到关联任务进行取消挂接。"
          style="margin-top: 12px"
        />

        <!-- 货物明细 -->
        <el-divider content-position="left">货物明细</el-divider>
        <el-table :data="waybill.cargoes || []" size="small" border>
          <el-table-column
            label="序号"
            type="index"
            width="60"
            align="center"
          />
          <el-table-column prop="vehicleBrand" label="品牌" min-width="100" />
          <el-table-column prop="vehicleModel" label="车型" min-width="120" />
          <el-table-column prop="vin" label="VIN" min-width="160" />
          <el-table-column
            prop="quantity"
            label="台数"
            width="80"
            align="center"
          />
        </el-table>
      </template>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { Right } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getWaybill } from '@/api/waybill';
  import type { Waybill } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';
  import WaybillStatusTag from './waybill-status-tag.vue';

  const props = defineProps<{
    visible: boolean;
    waybillId: number | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  const loading = ref(false);
  const waybill = ref<Waybill | null>(null);

  const totalQuantity = computed(() =>
    (waybill.value?.cargoes || []).reduce(
      (acc, c) => acc + Number(c.quantity || 0),
      0
    )
  );
  const remainingQuantity = computed(
    () => totalQuantity.value - Number(waybill.value?.allocatedQuantity ?? 0)
  );

  const formatAmount = (v?: number | null) => {
    if (v === null || v === undefined) return '--';
    return Number(v).toFixed(2);
  };

  watch(
    () => [props.visible, props.waybillId] as const,
    async ([v, id]) => {
      if (!v) {
        waybill.value = null;
        return;
      }
      if (!id) return;
      loading.value = true;
      try {
        waybill.value = await getWaybill(id);
      } catch (e: unknown) {
        const msg = (e as { message?: string }).message || '加载失败';
        EleMessage.error({ message: msg, plain: true });
      } finally {
        loading.value = false;
      }
    },
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .wb-detail {
    padding: 0 4px 16px;

    &__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 0 12px;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }

    &__no {
      font-size: 16px;
      font-weight: 600;
    }

    &__meta {
      margin-top: 4px;
      color: var(--el-text-color-secondary);
      font-size: 12px;
    }

    &__route {
      display: flex;
      align-items: center;
      color: var(--el-text-color-regular);
    }
  }
</style>
