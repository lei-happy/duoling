<!-- 计划列表：关联任务明细（只读，供协调取消挂接） -->
<template>
  <el-dialog
    :model-value="visible"
    width="680px"
    draggable
    align-center
    append-to-body
    destroy-on-close
    :close-on-click-modal="true"
    class="waybill-task-items-detail-dialog"
    :show-close="true"
    @update:model-value="updateVisible"
  >
    <template #header>
      <div class="wtd-header">
        <div class="wtd-header__title">关联任务</div>
        <div v-if="headerWaybillNo" class="wtd-header__sub-row">
          <span class="wtd-header__sub">{{ headerWaybillNo }}</span>
          <el-button
            type="primary"
            link
            class="wtd-header__copy"
            :icon="DocumentCopy"
            aria-label="复制计划号"
            @click.stop="copyWaybillNo"
          />
        </div>
      </div>
    </template>

    <div v-loading="loading" class="wtd-body">
      <div v-if="waybill" class="wtd-summary">
        <div class="wtd-summary__customer">
          <el-icon class="wtd-summary__icon"><User /></el-icon>
          <span class="wtd-summary__customer-text">{{ customerDisplay }}</span>
        </div>
        <div class="wtd-summary__route">
          <span class="wtd-route-chip wtd-route-chip--from">
            <el-icon><Location /></el-icon>
            <span class="wtd-route-chip__text">{{ originDisplay }}</span>
          </span>
          <span class="wtd-route-arrow" aria-hidden="true">→</span>
          <span class="wtd-route-chip wtd-route-chip--to">
            <el-icon><Location /></el-icon>
            <span class="wtd-route-chip__text">{{ destDisplay }}</span>
          </span>
        </div>
        <div class="wtd-summary__meta">
          <span class="wtd-pill">
            已调度 {{ allocatedDisplay }} / {{ totalDisplay }} 台
          </span>
        </div>
      </div>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="wtd-tip"
        title="以下任务正在占用本计划"
        description="如需修改计划，请先联系相关同事在任务台账取消挂接。"
      />

      <el-scrollbar v-if="tasks.length" max-height="420px" class="wtd-scroll">
        <ul class="wtd-list">
          <li v-for="task in tasks" :key="task.taskId" class="wtd-card">
            <div class="wtd-card__head">
              <div class="wtd-card__no-row">
                <span class="wtd-card__no">{{ task.taskNo }}</span>
                <el-button
                  type="primary"
                  link
                  class="wtd-card__copy"
                  :icon="DocumentCopy"
                  title="复制任务单号"
                  aria-label="复制任务单号"
                  @click.stop="copyTaskNo(task.taskNo)"
                />
              </div>
              <div class="wtd-card__status">
                <span class="wtd-card__status-label">任务状态</span>
                <el-tag
                  :type="(taskStatusType(task.taskStatus) as any) || 'info'"
                  size="small"
                  effect="light"
                >
                  {{ taskStatusLabel(task.taskStatus) }}
                </el-tag>
              </div>
            </div>

            <div class="wtd-card__meta">
              <span v-if="carrierLine(task)" class="wtd-card__meta-item">
                {{ carrierLine(task) }}
              </span>
              <span class="wtd-card__meta-item wtd-card__meta-item--strong">
                本计划占用 {{ task.allocatedQuantity }} 台
              </span>
            </div>

            <ul v-if="task.items.length" class="wtd-item-list">
              <li
                v-for="item in task.items"
                :key="item.id"
                class="wtd-item-row"
              >
                <span class="wtd-item-row__vehicle">
                  {{ formatVehicle(item) }}
                </span>
                <span class="wtd-item-row__qty">×{{ item.quantity }}</span>
              </li>
            </ul>

            <div v-if="canViewTask" class="wtd-card__actions">
              <el-button
                type="primary"
                link
                @click="goTaskWorkbench(task.taskNo)"
              >
                查看任务
              </el-button>
            </div>
          </li>
        </ul>
      </el-scrollbar>

      <el-empty
        v-else-if="!loading"
        description="暂无活跃的任务挂接"
        class="wtd-empty"
      />

      <p v-if="!canViewTask && tasks.length" class="wtd-perm-hint">
        暂无任务查看权限，可复制任务单号联系相关同事处理。
      </p>
    </div>

    <template #footer>
      <el-button type="primary" @click="updateVisible(false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import { DocumentCopy, Location, User } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    Waybill,
    WaybillLinkedTask,
    WaybillLinkedTaskItem
  } from '@/api/waybill/model';
  import { listWaybillLinkedTasks } from '@/api/waybill';
  import { usePermission } from '@/utils/use-permission';
  import {
    TASK_STATUS_MAP
  } from '@/views/operation/task/status-config';

  defineOptions({ name: 'WaybillTaskItemsDetail' });

  const props = defineProps<{
    visible: boolean;
    waybill: Waybill | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const router = useRouter();
  const { hasPermission } = usePermission();
  const canViewTask = computed(() => hasPermission('operation:task:list'));

  const loading = ref(false);
  const tasks = ref<WaybillLinkedTask[]>([]);

  const updateVisible = (v: boolean) => {
    emit('update:visible', v);
  };

  const headerWaybillNo = computed(() => props.waybill?.waybillNo?.trim() || '');

  const customerDisplay = computed(() => {
    const n = props.waybill?.customerName?.trim();
    return n || '未填写客户';
  });

  const originDisplay = computed(() => props.waybill?.origin?.trim() || '—');
  const destDisplay = computed(() => props.waybill?.destination?.trim() || '—');

  const totalDisplay = computed(() => props.waybill?.quantity ?? 0);
  const allocatedDisplay = computed(() => {
    if (props.waybill?.allocatedQuantity != null) {
      return props.waybill.allocatedQuantity;
    }
    return tasks.value.reduce((s, t) => s + (t.allocatedQuantity || 0), 0);
  });

  const copyText = async (
    raw: string | undefined | null,
    emptyTip: string,
    successTip: string
  ) => {
    const t = raw?.trim();
    if (!t) {
      EleMessage.warning({ message: emptyTip, plain: true });
      return;
    }
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(t);
      } else {
        const ta = document.createElement('textarea');
        ta.value = t;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      EleMessage.success({ message: successTip, plain: true });
    } catch {
      EleMessage.error({ message: '复制失败，请重试', plain: true });
    }
  };

  const copyWaybillNo = () =>
    copyText(props.waybill?.waybillNo, '无可复制的计划号', '已复制计划号');

  const copyTaskNo = (no?: string) =>
    copyText(no, '无可复制的任务单号', '已复制任务单号');

  const taskStatusLabel = (status?: number) =>
    status != null ? TASK_STATUS_MAP[status]?.label || '—' : '—';

  const taskStatusType = (status?: number) =>
    status != null ? TASK_STATUS_MAP[status]?.type || 'info' : 'info';

  const formatVehicle = (item: WaybillLinkedTaskItem) => {
    const brand = item.vehicleBrand?.trim() || '—';
    const model = item.vehicleModel?.trim();
    return model ? `${brand} / ${model}` : brand;
  };

  const carrierLine = (task: WaybillLinkedTask) => {
    const parts: string[] = [];
    if (task.mainDriverName?.trim()) parts.push(task.mainDriverName.trim());
    if (task.plateNumber?.trim()) parts.push(task.plateNumber.trim());
    return parts.join(' · ');
  };

  const goTaskWorkbench = (taskNo?: string) => {
    const no = taskNo?.trim();
    if (!no) return;
    updateVisible(false);
    router.push({
      path: '/operation/task-workbench',
      query: { keyword: no }
    });
  };

  const loadLinkedTasks = async () => {
    const id = props.waybill?.id;
    if (!id) {
      tasks.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listWaybillLinkedTasks(id);
      tasks.value = res?.tasks ?? [];
    } catch (e: unknown) {
      tasks.value = [];
      const msg = (e as { message?: string }).message || '加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => [props.visible, props.waybill?.id] as const,
    ([visible, id]) => {
      if (!visible || !id) {
        tasks.value = [];
        return;
      }
      loadLinkedTasks();
    },
    { immediate: true }
  );
</script>

<style scoped>
  .wtd-header {
    padding-right: 28px;
  }

  .wtd-header__title {
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--el-text-color-primary);
  }

  .wtd-header__sub-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
    flex-wrap: wrap;
  }

  .wtd-header__sub {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    font-family: ui-monospace, monospace;
  }

  .wtd-header__copy {
    padding: 0 4px;
    min-height: auto;
    font-size: 16px;
  }

  .wtd-body {
    margin-top: -6px;
  }

  .wtd-summary {
    padding: 16px 18px;
    border-radius: 12px;
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-light) 48%,
      var(--el-bg-color) 100%
    );
    border: 1px solid var(--el-border-color-lighter);
    margin-bottom: 12px;
  }

  .wtd-summary__customer {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 10px;
  }

  .wtd-summary__icon {
    margin-top: 2px;
    color: var(--el-color-primary);
    flex-shrink: 0;
  }

  .wtd-summary__customer-text {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.4;
  }

  .wtd-summary__route {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 10px;
    margin-bottom: 12px;
  }

  .wtd-route-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    max-width: 100%;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 13px;
    background: var(--el-bg-color-overlay);
    border: 1px solid var(--el-border-color-extra-light);
    color: var(--el-text-color-regular);
  }

  .wtd-route-chip .el-icon {
    flex-shrink: 0;
    color: var(--el-color-primary);
  }

  .wtd-route-chip__text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .wtd-route-arrow {
    color: var(--el-text-color-placeholder);
    font-size: 14px;
    user-select: none;
  }

  .wtd-summary__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .wtd-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    background: var(--el-color-primary);
    color: var(--el-color-white);
  }

  .wtd-tip {
    margin-bottom: 14px;
  }

  .wtd-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .wtd-card {
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .wtd-card__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 8px;
  }

  .wtd-card__status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }

  .wtd-card__status-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
  }

  .wtd-card__no-row {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    min-width: 0;
  }

  .wtd-card__no {
    font-size: 15px;
    font-weight: 600;
    font-family: ui-monospace, monospace;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .wtd-card__copy {
    flex-shrink: 0;
    padding: 2px 4px;
    min-height: auto;
  }

  .wtd-card__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    margin-bottom: 10px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .wtd-card__meta-item--strong {
    color: var(--el-color-primary);
    font-weight: 600;
  }

  .wtd-item-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .wtd-item-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 8px;
    background: var(--el-fill-color-lighter);
    font-size: 13px;
  }

  .wtd-item-row__vehicle {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--el-text-color-regular);
  }

  .wtd-item-row__qty {
    flex-shrink: 0;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    color: var(--el-text-color-primary);
  }

  .wtd-card__actions {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px dashed var(--el-border-color-lighter);
  }

  .wtd-perm-hint {
    margin: 12px 0 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .wtd-empty {
    padding: 24px 0;
  }
</style>

<style>
  .waybill-task-items-detail-dialog .el-dialog__header {
    padding-bottom: 8px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    margin-right: 0;
  }

  .waybill-task-items-detail-dialog .el-dialog__body {
    padding-top: 12px;
  }
</style>
