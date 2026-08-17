<!--
  规划路线弹窗（独立动作，不改 task.status）

  作业语义：
    - 为已存在的任务单补齐 / 重做运输分段路线。
    - 自有车任务：路线为必填（list/detail 入口高亮提示）。
    - 承运商 / 社会运力：可选，仅在"未规划过路线"时入口展示。
    - 打开时拉任务详情回填起终点；行程单按节点编辑，选定后联想线路里程。
  调用方式：行内 / 详情 / 派车成功回调中 v-model:visible 控制开关，并传入当前 task。
-->
<template>
  <el-dialog
    :model-value="visible"
    width="680px"
    destroy-on-close
    :close-on-click-modal="false"
    class="plan-route-dialog"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <template #header>
      <div class="plan-route-head">
        <div class="plan-route-head__title">规划运输路线</div>
        <div v-if="headerTask" class="plan-route-head__meta">
          {{ headerTask.taskNo }} · {{ headerTask.totalQuantity || 0 }} 台 ·
          {{ carrierLabel }}
        </div>
      </div>
    </template>

    <div v-loading="loading" class="plan-route-body">
      <div v-if="headerTask" class="cargo-ref">
        <div class="cargo-ref__top">
          <span class="cargo-ref__label">配载线路</span>
          <span v-if="diverged" class="cargo-ref__hint">已相对配载线路调整</span>
        </div>
        <div class="cargo-ref__route" :title="cargoFullTitle || undefined">
          <div class="cargo-ref__end">
            <span class="cargo-ref__city">{{ cargoOriginView.cityDistrict }}</span>
            <span v-if="cargoOriginView.province" class="cargo-ref__province">
              {{ cargoOriginView.province }}
            </span>
          </div>
          <span class="cargo-ref__arrow" aria-hidden="true">→</span>
          <div class="cargo-ref__end">
            <span class="cargo-ref__city">{{ cargoDestView.cityDistrict }}</span>
            <span v-if="cargoDestView.province" class="cargo-ref__province">
              {{ cargoDestView.province }}
            </span>
          </div>
        </div>
      </div>

      <task-route-itinerary v-model="segments" />
    </div>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        保存路线
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskRouteItinerary from '../../task/components/task-route-itinerary.vue';
  import { getTask, planTaskRoute } from '@/api/operation/task';
  import type { Task, TaskSegment } from '@/api/operation/task/model';
  import {
    formatRouteTitle,
    parseRegionDisplay
  } from '@/utils/region-display';
  import { CARRIER_TYPE_MAP } from '../../task/status-config';

  const props = defineProps<{
    visible: boolean;
    task: Task | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const submitting = ref(false);
  const loading = ref(false);
  const segments = ref<TaskSegment[]>([]);
  const detailTask = ref<Task | null>(null);

  const headerTask = computed(() => detailTask.value || props.task);

  const carrierLabel = computed(
    () => CARRIER_TYPE_MAP[headerTask.value?.carrierType || 1]?.label || '--'
  );

  const cargoOrigin = computed(
    () => detailTask.value?.origin || props.task?.origin || ''
  );
  const cargoDestination = computed(
    () => detailTask.value?.destination || props.task?.destination || ''
  );

  const cargoOriginView = computed(() => parseRegionDisplay(cargoOrigin.value));
  const cargoDestView = computed(() =>
    parseRegionDisplay(cargoDestination.value)
  );
  const cargoFullTitle = computed(() =>
    formatRouteTitle(cargoOrigin.value, cargoDestination.value)
  );

  const samePlace = (a?: string | null, b?: string | null) =>
    (a || '').trim() === (b || '').trim();

  const diverged = computed(() => {
    const first = segments.value[0];
    const last = segments.value[segments.value.length - 1];
    if (!first || !last) return false;
    const origin = cargoOrigin.value;
    const dest = cargoDestination.value;
    if (!origin && !dest) return false;
    return (
      !samePlace(first.fromLocation, origin) ||
      !samePlace(last.toLocation, dest)
    );
  });

  const cloneSegment = (s: TaskSegment): TaskSegment => ({
    segmentNo: s.segmentNo,
    fromLocation: s.fromLocation,
    fromCode: s.fromCode,
    fromRegionId: s.fromRegionId,
    toLocation: s.toLocation,
    toCode: s.toCode,
    toRegionId: s.toRegionId,
    mileage: s.mileage,
    plannedLoadTime: s.plannedLoadTime,
    plannedArriveTime: s.plannedArriveTime,
    remark: s.remark
  });

  const buildDefaultSegments = (task: Task): TaskSegment[] => [
    {
      segmentNo: 1,
      fromLocation: task.origin || '',
      fromCode: task.originCode,
      fromRegionId: task.originRegionId ?? undefined,
      toLocation: task.destination || '',
      toCode: task.destinationCode,
      toRegionId: task.destinationRegionId ?? undefined,
      mileage: undefined,
      plannedLoadTime: task.plannedLoadTime,
      plannedArriveTime: task.plannedArriveTime
    }
  ];

  const onOpen = async () => {
    if (!props.task) {
      segments.value = [];
      detailTask.value = null;
      return;
    }
    detailTask.value = props.task;
    segments.value = buildDefaultSegments(props.task);
    if (!props.task.id) return;
    loading.value = true;
    try {
      const detail = await getTask(props.task.id);
      if (!detail) return;
      detailTask.value = detail;
      const existing = detail.segments || [];
      segments.value = existing.length
        ? existing.map(cloneSegment)
        : buildDefaultSegments(detail);
    } catch {
      EleMessage.error({
        message: '任务信息加载失败，请关闭后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const validate = (): string | null => {
    if (!segments.value.length) return '请先规划至少 1 段运输';
    for (const s of segments.value) {
      if (!s.fromLocation?.trim() || !s.toLocation?.trim()) {
        return `第 ${s.segmentNo} 段还没选齐起点和终点`;
      }
    }
    return null;
  };

  const buildPayload = () =>
    segments.value.map((s) => ({
      segmentNo: s.segmentNo,
      fromLocation: s.fromLocation,
      fromCode: s.fromCode,
      fromRegionId: s.fromRegionId,
      toLocation: s.toLocation,
      toCode: s.toCode,
      toRegionId: s.toRegionId,
      mileage: s.mileage ?? undefined,
      plannedLoadTime: s.plannedLoadTime,
      plannedArriveTime: s.plannedArriveTime,
      remark: s.remark
    }));

  const submit = async () => {
    if (!props.task?.id) return;
    const err = validate();
    if (err) {
      EleMessage.warning({ message: err, plain: true });
      return;
    }
    submitting.value = true;
    try {
      await planTaskRoute(props.task.id, { segments: buildPayload() });
      EleMessage.success({ message: '路线已保存', plain: true });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .plan-route-head {
    padding-right: 28px;
  }

  .plan-route-head__title {
    font-size: 16px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--el-text-color-primary);
  }

  .plan-route-head__meta {
    margin-top: 4px;
    font-size: 12px;
    line-height: 1.4;
    color: var(--el-text-color-secondary);
  }

  .plan-route-body {
    min-height: 200px;
  }

  .cargo-ref {
    margin-bottom: 16px;
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .cargo-ref__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
  }

  .cargo-ref__label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .cargo-ref__hint {
    font-size: 12px;
    color: var(--el-color-warning);
  }

  .cargo-ref__route {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    min-width: 0;
  }

  .cargo-ref__end {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    flex: 1;
  }

  .cargo-ref__city {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cargo-ref__province {
    font-size: 12px;
    line-height: 1.3;
    color: var(--el-text-color-secondary);
  }

  .cargo-ref__arrow {
    flex-shrink: 0;
    padding-top: 2px;
    font-size: 13px;
    line-height: 1.3;
    color: var(--el-text-color-secondary);
  }
</style>
