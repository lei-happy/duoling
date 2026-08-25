<!-- 计划列表：关联任务明细（只读，供协调取消挂接） -->
<template>
  <inspect-dialog
    :visible="visible"
    title="关联任务"
    :subtitle="headerWaybillNo"
    :copyable-subtitle="!!headerWaybillNo"
    copy-subtitle-success="已复制计划号"
    copy-subtitle-empty="无可复制的计划号"
    copy-subtitle-label="复制计划号"
    width="680px"
    :loading="loading"
    @update:visible="updateVisible"
  >
    <div v-if="waybill">
      <section class="wbi-hero" aria-label="线路摘要">
        <div class="wbi-hero__who">{{ customerDisplay }}</div>
        <div class="wbi-hero__route">
          <div class="wbi-hero__end">
            <span class="wbi-hero__kicker">起运</span>
            <span class="wbi-hero__city">{{ originDisplay }}</span>
          </div>
          <div class="wbi-hero__spine" aria-hidden="true">
            <span class="wbi-hero__rail"></span>
          </div>
          <div class="wbi-hero__end wbi-hero__end--to">
            <span class="wbi-hero__kicker">送达</span>
            <span class="wbi-hero__city">{{ destDisplay }}</span>
          </div>
          <div
            class="wbi-hero__stamp"
            :title="`已调度 ${allocatedDisplay} / ${totalDisplay} 台`"
          >
            <span class="wbi-hero__stamp-num">{{ allocatedDisplay }}</span>
            <span class="wbi-hero__stamp-unit">已调</span>
          </div>
        </div>
      </section>

      <p class="wbi-note">
        以下任务正在占用本计划。如需改台数或起终地，请先到「任务台账」取消挂接。
      </p>

      <section class="wbi-section">
        <h3 class="wbi-section__title">
          调度占用 · {{ allocatedDisplay }} / {{ totalDisplay }} 台
        </h3>
        <div v-if="tasks.length" class="wbi-group">
          <div v-for="task in tasks" :key="task.taskId" class="wbi-card">
            <div class="wbi-card__head">
              <div class="wbi-card__id">
                <span class="wbi-card__no">{{ task.taskNo }}</span>
                <inspect-copy-button
                  :text="task.taskNo"
                  success-tip="已复制任务单号"
                  empty-tip="无可复制的任务单号"
                  aria-label="复制任务单号"
                />
              </div>
              <el-tag
                :type="(taskStatusType(task.taskStatus) as any) || 'info'"
                size="small"
                effect="light"
              >
                {{ taskStatusLabel(task.taskStatus) }}
              </el-tag>
            </div>

            <div class="wbi-card__meta">
              <span v-if="carrierLine(task)">{{ carrierLine(task) }}</span>
              <span class="wbi-card__meta-strong">
                本计划占用 {{ task.allocatedQuantity }} 台
              </span>
            </div>

            <ul v-if="task.items.length" class="wbi-chip-list">
              <li
                v-for="item in task.items"
                :key="item.id"
                class="wbi-chip-row"
              >
                <span class="wbi-chip-row__main">{{ formatVehicle(item) }}</span>
                <span class="wbi-chip-row__side">×{{ item.quantity }}</span>
              </li>
            </ul>

            <div v-if="canViewTask" class="wbi-card__action">
              <el-button
                type="primary"
                link
                @click="goTaskWorkbench(task.taskNo)"
              >
                查看任务
              </el-button>
            </div>
          </div>
        </div>
        <div v-else-if="!loading" class="wbi-group">
          <el-empty description="暂无活跃的任务挂接" :image-size="72" />
        </div>
      </section>

      <p v-if="!canViewTask && tasks.length" class="wbi-note">
        暂无任务查看权限，可复制任务单号联系相关同事处理。
      </p>
    </div>

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
    </template>
  </inspect-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    Waybill,
    WaybillLinkedTask,
    WaybillLinkedTaskItem
  } from '@/api/waybill/model';
  import { listWaybillLinkedTasks } from '@/api/waybill';
  import { usePermission } from '@/utils/use-permission';
  import { TASK_STATUS_MAP } from '@/views/operation/task/status-config';
  import InspectDialog from '@/components/InspectDialog/index.vue';
  import InspectCopyButton from '@/components/InspectDialog/copy-button.vue';

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

