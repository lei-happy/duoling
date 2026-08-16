<!--
  确认交车弹窗（item 级交车）

  说明：
  - 交车语义已下沉到「任务-计划挂接行（TaskWaybillItem）」维度，由调度员勾选具体
    item 触发 ``updateTaskWaybillItem(status=3)``；后端 ``_aggregate_task_status_from_items``
    在 item 全部交车后自动把 task.status 4→5。
  - 单任务场景：拉取该任务下的所有 item 让用户逐行勾选/批量交车；
  - 批量任务场景：仅做"对每张任务下所有未交车 item 一键交车"，不展示明细。

  详见《02.计划与任务单状态机联动设计.md》。
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    :width="isSingleTask ? '760px' : '520px'"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      :label-position="isSingleTask ? 'top' : 'right'"
    >
      <el-form-item v-if="!isSingleTask" label="任务单">
        <el-tag type="success" size="small">
          批量交车 {{ tasks.length }} 张任务
        </el-tag>
        <span class="action-sign__hint">
          将把每张任务下所有未交车的挂接货物一并交车
        </span>
      </el-form-item>

      <el-form-item label="交车时间" prop="signedAt" required>
        <el-date-picker
          v-model="form.signedAt"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          placeholder="选择客户交车时间"
          style="width: 320px"
        />
      </el-form-item>
      <el-form-item label="交接人">
        <el-input
          v-model="form.signedBy"
          placeholder="客户接车人姓名（可选）"
          style="width: 320px"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="交车过程中的其他信息（可选）"
        />
      </el-form-item>

      <el-form-item
        v-if="isSingleTask"
        label="待交车挂接货物"
        prop="selectedItemIds"
        :rules="[
          {
            required: true,
            validator: validateSelected,
            trigger: 'change'
          }
        ]"
      >
        <div class="action-sign__items">
          <el-alert
            v-if="loadingItems"
            type="info"
            :closable="false"
            title="加载挂接货物中..."
          />
          <el-alert
            v-else-if="!unsignedItems.length"
            type="warning"
            :closable="false"
            show-icon
            title="该任务下没有待交车的挂接货物"
            description="可能已全部交车（任务将自动进入「已交车」），或挂接货物未到达。"
          />
          <el-table
            v-else
            ref="tableRef"
            :data="unsignedItems"
            border
            size="small"
            row-key="id"
            max-height="320"
            @selection-change="onSelectionChange"
          >
            <el-table-column type="selection" width="40" align="center" />
            <el-table-column
              label="计划号"
              prop="waybillNo"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column
              label="客户"
              prop="customerName"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column
              label="品牌/车型"
              min-width="160"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
              </template>
            </el-table-column>
            <el-table-column
              label="台数"
              prop="quantity"
              width="64"
              align="center"
            />
            <el-table-column label="当前状态" width="92" align="center">
              <template #default="{ row }">
                <el-tag :type="itemStatusTag(row.status)" size="small">
                  {{ itemStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button
        type="success"
        :loading="submitting"
        :disabled="submitDisabled"
        @click="submit"
      >
        {{ submitLabel }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElTable } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    listTaskWaybillItems,
    updateTaskWaybillItem
  } from '@/api/operation/task';
  import type { Task, TaskWaybillItem } from '@/api/operation/task/model';
  import { ITEM_STATUS } from '../../task/status-config';

  const props = defineProps<{
    visible: boolean;
    tasks: Task[];
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const tableRef = ref<InstanceType<typeof ElTable> | null>(null);
  const submitting = ref(false);
  const loadingItems = ref(false);
  const items = ref<TaskWaybillItem[]>([]);
  const selectedItemIds = ref<number[]>([]);

  const form = reactive({
    signedAt: '',
    signedBy: '',
    remark: '',
    selectedItemIds: [] as number[]
  });

  const rules: FormRules = {
    signedAt: [{ required: true, message: '请选择交车时间' }]
  };

  const isSingleTask = computed(() => props.tasks.length === 1);

  const title = computed(() =>
    isSingleTask.value ? '确认交车' : '批量确认交车'
  );

  /** 未交车 = status < 已交车 且未取消 */
  const unsignedItems = computed(() =>
    items.value.filter(
      (it) =>
        (it.status ?? ITEM_STATUS.PENDING_LOAD) < ITEM_STATUS.SIGNED &&
        it.status !== ITEM_STATUS.CANCELLED
    )
  );

  const submitDisabled = computed(() => {
    if (isSingleTask.value) {
      return loadingItems.value || selectedItemIds.value.length === 0;
    }
    return false;
  });

  const submitLabel = computed(() => {
    if (!isSingleTask.value) {
      return `批量交车 (${props.tasks.length})`;
    }
    const n = selectedItemIds.value.length;
    return n > 0 ? `确认交车 (${n} 行)` : '确认交车';
  });

  const validateSelected = (
    _rule: unknown,
    _value: unknown,
    cb: (error?: Error) => void
  ) => {
    if (!isSingleTask.value) return cb();
    if (selectedItemIds.value.length === 0) {
      return cb(new Error('请至少勾选一行待交车的挂接货物'));
    }
    cb();
  };

  const itemStatusLabel = (s?: number) => {
    switch (s) {
      case 0:
        return '待装车';
      case 1:
        return '已装车';
      case 2:
        return '已卸车';
      case 3:
        return '已交车';
      case 9:
        return '已取消';
      default:
        return '--';
    }
  };
  const itemStatusTag = (s?: number) => {
    switch (s) {
      case 0:
        return 'info';
      case 1:
        return 'warning';
      case 2:
        return 'primary';
      case 3:
        return 'success';
      default:
        return 'info';
    }
  };

  const syncingSelection = ref(false);

  const onSelectionChange = (rows: TaskWaybillItem[]) => {
    if (syncingSelection.value) return;
    selectedItemIds.value = rows.map((r) => r.id!).filter(Boolean);
    form.selectedItemIds = selectedItemIds.value;
  };

  const applyDefaultUnsignedSelection = async () => {
    const ids = unsignedItems.value.map((it) => it.id!).filter(Boolean);
    selectedItemIds.value = ids;
    form.selectedItemIds = ids;
    await nextTick();
    const table = tableRef.value;
    if (!table) return;
    syncingSelection.value = true;
    table.clearSelection();
    for (const row of unsignedItems.value) {
      table.toggleRowSelection(row, true);
    }
    syncingSelection.value = false;
  };

  const fetchItems = async () => {
    if (!isSingleTask.value) {
      items.value = [];
      return;
    }
    const taskId = props.tasks[0]?.id;
    if (!taskId) return;
    loadingItems.value = true;
    try {
      items.value = (await listTaskWaybillItems(taskId)) || [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
      items.value = [];
    } finally {
      loadingItems.value = false;
    }
    // 等表格挂上后再勾，避免 toggleAllSelection 落空
    await applyDefaultUnsignedSelection();
  };

  const onOpen = () => {
    form.signedAt = new Date().toISOString().slice(0, 19);
    form.signedBy = '';
    form.remark = '';
    form.selectedItemIds = [];
    selectedItemIds.value = [];
    items.value = [];
    fetchItems();
  };

  watch(
    () => props.tasks,
    () => {
      if (props.visible) onOpen();
    }
  );

  const buildRemark = () => {
    const parts: string[] = [];
    parts.push(`[交车] ${form.signedAt}`);
    if (form.signedBy.trim()) parts.push(`交接人：${form.signedBy.trim()}`);
    if (form.remark.trim()) parts.push(form.remark.trim());
    return parts.join(' / ');
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (!props.tasks.length) {
      emit('update:visible', false);
      return;
    }
    submitting.value = true;
    const remark = buildRemark();
    try {
      let total = 0;
      let failed = 0;
      if (isSingleTask.value) {
        // 单任务：直接对勾选的 item 批量交车
        for (const id of selectedItemIds.value) {
          total += 1;
          try {
            await updateTaskWaybillItem(id, {
              status: ITEM_STATUS.SIGNED,
              signedAt: form.signedAt,
              remark
            });
          } catch {
            failed += 1;
          }
        }
      } else {
        // 批量任务：每张任务取所有未交车 item 一并交车
        for (const t of props.tasks) {
          if (!t.id) continue;
          let taskItems: TaskWaybillItem[] = [];
          try {
            taskItems = (await listTaskWaybillItems(t.id)) || [];
          } catch {
            failed += 1;
            continue;
          }
          for (const it of taskItems) {
            if (
              (it.status ?? ITEM_STATUS.PENDING_LOAD) >= ITEM_STATUS.SIGNED ||
              it.status === ITEM_STATUS.CANCELLED ||
              !it.id
            )
              continue;
            total += 1;
            try {
              await updateTaskWaybillItem(it.id, {
                status: ITEM_STATUS.SIGNED,
                signedAt: form.signedAt,
                remark
              });
            } catch {
              failed += 1;
            }
          }
        }
      }
      if (total === 0) {
        EleMessage.warning({ message: '没有可交车的挂接货物', plain: true });
      } else if (failed > 0) {
        EleMessage.warning({
          message: `已交车 ${total - failed} 行，失败 ${failed} 行`,
          plain: true
        });
      } else {
        EleMessage.success({
          message: `已交车 ${total} 行挂接货物`,
          plain: true
        });
      }
      emit('done');
      emit('update:visible', false);
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .action-sign__hint {
    margin-left: 12px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .action-sign__items {
    width: 100%;
  }
</style>
