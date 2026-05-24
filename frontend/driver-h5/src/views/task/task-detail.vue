<template>
  <PageContainer :title="task ? task.taskNo : '任务详情'">
    <div v-if="task" class="task-detail">
      <!-- 状态头 -->
      <div class="status-card">
        <div class="status-header">
          <StatusTag :label="statusInfo.label" :level="statusInfo.level" />
          <span class="task-name">{{ task.taskName || task.taskNo }}</span>
        </div>
        <div class="route">
          <div class="route-line">
            <div class="dot dot-from"></div>
            <div class="route-text">
              <div class="loc">{{ task.origin || '-' }}</div>
              <div class="time">计划装车：{{ formatDateTime(task.plannedLoadTime) }}</div>
            </div>
          </div>
          <div class="route-line">
            <div class="dot dot-to"></div>
            <div class="route-text">
              <div class="loc">{{ task.destination || '-' }}</div>
              <div class="time">计划到达：{{ formatDateTime(task.plannedArriveTime) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 货物 -->
      <div class="section card">
        <div class="section-title">货物明细（{{ task.items.length }} 行 / {{ task.totalQuantity || 0 }} 台）</div>
        <div class="item-row" v-for="it in task.items" :key="it.id">
          <div class="item-main">
            <div class="item-line">
              <span class="brand">{{ it.vehicleBrand || '-' }} {{ it.vehicleModel || '' }}</span>
              <StatusTag
                :label="getItemStatusInfo(it.status).label"
                :level="getItemStatusInfo(it.status).level"
              />
            </div>
            <div class="item-line meta">
              <span>{{ it.waybillNo || '-' }} · {{ it.customerName || '-' }} · {{ it.quantity }} 台</span>
            </div>
            <div v-if="it.dealerName" class="item-line meta">
              <van-icon name="shop-o" /> {{ it.dealerName }}
            </div>
          </div>
          <van-button
            v-if="task.status === 4 && it.status < 3"
            size="small"
            type="success"
            @click="onSignItem(it.id)"
          >签收</van-button>
        </div>
      </div>

      <!-- 分段 -->
      <div v-if="task.segments?.length > 1" class="section card">
        <div class="section-title">运输分段</div>
        <div v-for="seg in task.segments" :key="seg.id" class="segment-row">
          <span class="seg-no">{{ seg.segmentNo }}</span>
          <div class="seg-info">
            <div>{{ seg.fromLocation }} → {{ seg.toLocation }}</div>
            <div class="meta">
              装车 {{ formatDateTime(seg.plannedLoadTime) }} / 到达 {{ formatDateTime(seg.plannedArriveTime) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 司机/车辆信息 -->
      <div class="section card">
        <div class="section-title">承运资源</div>
        <van-cell title="主驾" :value="task.mainDriverName || '-'" />
        <van-cell title="车牌" :value="task.plateNumber || '-'" />
      </div>

      <!-- 财务概览 -->
      <div class="section card">
        <div class="section-title">财务概览</div>
        <div class="finance-row">
          <div>
            <div class="label">已预付</div>
            <div class="amount">¥{{ formatMoney(task.prepaidAmount || 0) }}</div>
          </div>
          <div>
            <div class="label">已结算</div>
            <div class="amount">¥{{ formatMoney(task.settledAmount || 0) }}</div>
          </div>
        </div>
        <van-cell
          title="查看费用单"
          is-link
          @click="$router.push(`/finance?taskId=${task.id}`)"
        />
      </div>

      <!-- 底部操作栏 -->
      <div class="action-bar" v-if="availableActions.length">
        <van-button
          v-for="a in availableActions"
          :key="a.key"
          :type="a.level || 'primary'"
          round
          block
          :loading="acting"
          @click="onAction(a.key)"
        >{{ a.label }}</van-button>
      </div>
    </div>

    <van-loading v-else class="loading" type="spinner" />

    <!-- 装车确认弹层 -->
    <van-dialog
      v-model:show="confirmDialog.show"
      :title="confirmDialog.title"
      show-cancel-button
      :before-close="onConfirmDialog"
    >
      <div class="dialog-body">
        <div class="tip">{{ confirmDialog.message }}</div>
        <van-field
          v-model="confirmDialog.remark"
          rows="2"
          autosize
          type="textarea"
          placeholder="备注（选填）"
        />
      </div>
    </van-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showFailToast, showToast } from 'vant';
import PageContainer from '@/components/PageContainer.vue';
import StatusTag from '@/components/StatusTag.vue';
import {
  confirmArrive,
  confirmLoad,
  depart,
  getTaskDetail,
  signItem,
  type TaskDetail
} from '@/api/task';
import { formatDateTime, formatMoney } from '@/utils/format';
import {
  getAvailableActions,
  getItemStatusInfo,
  getTaskStatusInfo,
  type DriverAction
} from './status-config';

const route = useRoute();
const router = useRouter();

const task = ref<TaskDetail | null>(null);
const acting = ref(false);

const statusInfo = computed(() =>
  task.value ? getTaskStatusInfo(task.value.status) : { label: '', level: 'default' as const }
);
const availableActions = computed<DriverAction[]>(() =>
  task.value ? getAvailableActions(task.value.status) : []
);

const confirmDialog = ref<{
  show: boolean;
  title: string;
  message: string;
  remark: string;
  action: DriverAction['key'] | '';
}>({ show: false, title: '', message: '', remark: '', action: '' });

async function load() {
  const id = Number(route.params.id);
  if (!id) {
    showFailToast('任务不存在');
    router.back();
    return;
  }
  try {
    task.value = await getTaskDetail(id);
  } catch (e) {
    console.error(e);
  }
}

onMounted(load);

function onAction(key: DriverAction['key']) {
  if (key === 'sign-items') {
    const next = task.value?.items.find((it) => it.status < 3);
    if (next) onSignItem(next.id);
    else showToast('暂无可签收的运单');
    return;
  }
  const dialogConfigs: Record<string, { title: string; message: string }> = {
    'confirm-load': { title: '确认装车', message: '请确认车辆已完成装车，状态将更新为「已装车」' },
    depart: { title: '确认出发', message: '请确认已发车上路，状态将更新为「在途」' },
    'confirm-arrive': { title: '确认到达', message: '请确认已抵达卸货点，状态将更新为「已到达」' }
  };
  const cfg = dialogConfigs[key];
  if (!cfg) return;
  confirmDialog.value = { show: true, title: cfg.title, message: cfg.message, remark: '', action: key };
}

async function onConfirmDialog(action: string) {
  if (action !== 'confirm') return true;
  if (!task.value) return true;
  acting.value = true;
  try {
    const taskId = task.value.id;
    const remark = confirmDialog.value.remark.trim() || undefined;
    if (confirmDialog.value.action === 'confirm-load') {
      await confirmLoad(taskId, { remark });
    } else if (confirmDialog.value.action === 'depart') {
      await depart(taskId, { remark });
    } else if (confirmDialog.value.action === 'confirm-arrive') {
      await confirmArrive(taskId, { remark });
    }
    showToast({ message: '操作成功', type: 'success' });
    await load();
    return true;
  } catch (e) {
    console.error(e);
    return false;
  } finally {
    acting.value = false;
  }
}

async function onSignItem(itemId: number) {
  acting.value = true;
  try {
    await signItem(itemId);
    showToast({ message: '签收成功', type: 'success' });
    await load();
  } finally {
    acting.value = false;
  }
}
</script>

<style lang="scss" scoped>
.task-detail {
  padding-bottom: 80px;
}
.status-card {
  margin: $spacing-md;
  background: $bg-card;
  border-radius: $border-radius-md;
  padding: $spacing-lg;
  box-shadow: $shadow-card;

  .status-header {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    margin-bottom: $spacing-md;
    .task-name {
      font-size: $font-size-lg;
      font-weight: 600;
    }
  }
  .route {
    position: relative;
    padding-left: 10px;
    &::before {
      content: '';
      position: absolute;
      left: 5px;
      top: 8px;
      bottom: 8px;
      width: 2px;
      background: $border-color;
    }
  }
  .route-line {
    position: relative;
    padding-left: 16px;
    padding-bottom: $spacing-md;
    &:last-child {
      padding-bottom: 0;
    }
    .dot {
      position: absolute;
      left: -3px;
      top: 4px;
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }
    .dot-from {
      background: $brand-primary;
    }
    .dot-to {
      background: $brand-success;
    }
    .loc {
      font-size: $font-size-md;
      font-weight: 500;
    }
    .time {
      font-size: $font-size-xs;
      color: $text-secondary;
      margin-top: 2px;
    }
  }
}
.section {
  margin: $spacing-md;
  padding: $spacing-md;
  .section-title {
    font-size: $font-size-md;
    font-weight: 600;
    margin-bottom: $spacing-sm;
    padding-bottom: $spacing-sm;
    border-bottom: 1px solid $border-color;
  }
}
.item-row {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-sm 0;
  border-bottom: 1px dashed $border-color;
  &:last-child {
    border-bottom: none;
  }
  .item-main {
    flex: 1;
    min-width: 0;
  }
  .item-line {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $spacing-sm;
    .brand {
      font-weight: 500;
    }
  }
  .meta {
    font-size: $font-size-xs;
    color: $text-secondary;
    margin-top: 2px;
  }
}
.segment-row {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-sm 0;
  border-bottom: 1px dashed $border-color;
  &:last-child {
    border-bottom: none;
  }
  .seg-no {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: $brand-primary;
    color: #fff;
    font-size: $font-size-xs;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .seg-info {
    flex: 1;
    .meta {
      color: $text-secondary;
      font-size: $font-size-xs;
      margin-top: 2px;
    }
  }
}
.finance-row {
  display: flex;
  gap: $spacing-lg;
  padding: $spacing-sm 0;
  .label {
    color: $text-secondary;
    font-size: $font-size-xs;
  }
  .amount {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $brand-primary;
    margin-top: 2px;
  }
}
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: $spacing-md $spacing-lg calc(#{$spacing-md} + #{$safe-area-bottom});
  background: #fff;
  box-shadow: 0 -2px 8px rgba(15, 23, 42, 0.06);
  display: flex;
  gap: $spacing-md;
}
.dialog-body {
  padding: $spacing-lg;
  .tip {
    color: $text-secondary;
    margin-bottom: $spacing-md;
    font-size: $font-size-sm;
  }
}
.loading {
  text-align: center;
  padding: 80px 0;
}
</style>
