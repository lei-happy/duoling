<!--
  规划路线弹窗（独立动作，不改 task.status）

  作业语义：
    - 为已存在的任务单补齐 / 重做运输分段路线。
    - 自有车任务：路线为必填（list/detail 入口高亮提示）。
    - 承运商 / 社会运力：可选，仅在"未规划过路线"时入口展示。
    - 起点 / 终点从地区库选择，选定后自动联想「计费中心 - 线路管理」里维护的里程。
  调用方式：行内 / 详情 / 派车成功回调中 v-model:visible 控制开关，并传入当前 task。
-->
<template>
  <el-dialog
    :model-value="visible"
    title="规划运输路线"
    width="960px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="task"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="`任务单 ${task.taskNo} · ${task.origin || '--'} → ${task.destination || '--'} · ${task.totalQuantity || 0} 台 · ${carrierLabel}`"
    />

    <task-segment-table v-model="segments" />

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button
        type="primary"
        :loading="submitting"
        @click="submit"
      >
        保存路线
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskSegmentTable from '../../task/components/task-segment-table.vue';
  import { planTaskRoute } from '@/api/operation/task';
  import type { Task, TaskSegment } from '@/api/operation/task/model';
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
  const segments = ref<TaskSegment[]>([]);

  const carrierLabel = computed(
    () => CARRIER_TYPE_MAP[props.task?.carrierType || 1]?.label || '--'
  );

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

  const onOpen = () => {
    if (!props.task) {
      segments.value = [];
      return;
    }
    const existing = props.task.segments || [];
    if (existing.length) {
      // 编辑已有分段
      segments.value = existing.map((s) => ({
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
      }));
    } else {
      // 首次规划：用任务单的起终点预填首段
      segments.value = buildDefaultSegments(props.task);
    }
  };

  const validate = (): string | null => {
    if (!segments.value.length) return '至少需要 1 段运输';
    for (const s of segments.value) {
      if (!s.fromLocation?.trim() || !s.toLocation?.trim()) {
        return `第 ${s.segmentNo} 段起点/终点不能为空`;
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
      const msg = (e as { message?: string }).message || '保存失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>
