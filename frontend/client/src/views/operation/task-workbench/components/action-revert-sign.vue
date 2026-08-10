<!--
  撤销交车弹窗（item 级反向）

  业务（参考《02.计划与任务单状态机联动设计.md》§4.5.2 / §4.1bis）：
  - 误交车 / 客户拒收时，调度员选择已交车的挂接货物行，把 item.status 3→2（已卸车）；
    后端 ``_aggregate_task_status_from_items`` 在"非全部交车"时自动把 task 5→4，
    并由 ``WaybillStatusAggregator`` 反向聚合计划 5→4（allow_downgrade）。
  - 5→4 不走任务级 revert-status（该接口不接受 5→4），必须走 item 级撤销。
  - 独立性防护：若关联计划已「已回单(6)」，后端会拦截并提示先撤销回单。
  - 原因必填，写入 item.remark（审计）。

  单任务：拉取该任务下 status=3 的挂接行供勾选；批量：每张任务全部已交车行一并撤销。
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
    <el-alert
      type="warning"
      :closable="false"
      show-icon
      title="撤销交车会把对应货物退回「已卸车」，任务将自动由「已交车」回退到「已到达」，计划状态联动回退。"
      style="margin-bottom: 12px"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      :label-position="isSingleTask ? 'top' : 'right'"
    >
      <el-form-item v-if="!isSingleTask" label="任务单">
        <el-tag type="warning" size="small">
          批量撤销 {{ tasks.length }} 张任务
        </el-tag>
        <span class="action-revert-sign__hint">
          将把每张任务下所有已交车的挂接货物撤回到「已卸车」
        </span>
      </el-form-item>

      <el-form-item label="撤销原因" prop="reason" required>
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="必填，例如：客户拒收、误操作交车、收车门店信息有误等"
        />
      </el-form-item>

      <el-form-item
        v-if="isSingleTask"
        label="已交车货物"
        prop="selectedItemIds"
        :rules="[
          {
            required: true,
            validator: validateSelected,
            trigger: 'change'
          }
        ]"
      >
        <div class="action-revert-sign__items">
          <el-alert
            v-if="loadingItems"
            type="info"
            :closable="false"
            title="加载挂接货物中..."
          />
          <el-alert
            v-else-if="!signedItems.length"
            type="warning"
            :closable="false"
            show-icon
            title="该任务下没有已交车的挂接货物"
            description="可能尚未交车，或已被撤销。"
          />
          <el-table
            v-else
            ref="tableRef"
            :data="signedItems"
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
          </el-table>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button
        type="warning"
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
  import { computed, reactive, ref, watch } from 'vue';
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
    reason: '',
    selectedItemIds: [] as number[]
  });

  const rules: FormRules = {
    reason: [
      { required: true, message: '请填写撤销原因' },
      { min: 2, max: 500, message: '原因长度需在 2-500 字之间' }
    ]
  };

  const isSingleTask = computed(() => props.tasks.length === 1);

  const title = computed(() =>
    isSingleTask.value ? '撤销交车' : '批量撤销交车'
  );

  /** 已交车 = status === 已交车 */
  const signedItems = computed(() =>
    items.value.filter(
      (it) => (it.status ?? ITEM_STATUS.PENDING_LOAD) === ITEM_STATUS.SIGNED
    )
  );

  const submitDisabled = computed(() => {
    if (isSingleTask.value) {
      return loadingItems.value || signedItems.value.length === 0;
    }
    return false;
  });

  const submitLabel = computed(() => {
    if (!isSingleTask.value) {
      return `批量撤销交车 (${props.tasks.length})`;
    }
    const n = selectedItemIds.value.length;
    return n > 0 ? `确认撤销 (${n} 行)` : '确认撤销';
  });

  const validateSelected = (
    _rule: unknown,
    _value: unknown,
    cb: (error?: Error) => void
  ) => {
    if (!isSingleTask.value) return cb();
    if (selectedItemIds.value.length === 0) {
      return cb(new Error('请至少勾选一行已交车的挂接货物'));
    }
    cb();
  };

  const onSelectionChange = (rows: TaskWaybillItem[]) => {
    selectedItemIds.value = rows.map((r) => r.id!).filter(Boolean);
    form.selectedItemIds = selectedItemIds.value;
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
      await Promise.resolve();
      tableRef.value?.toggleAllSelection?.();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
      items.value = [];
    } finally {
      loadingItems.value = false;
    }
  };

  const onOpen = () => {
    form.reason = '';
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

  const buildRemark = () => `[撤销交车] ${form.reason.trim()}`;

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
        for (const id of selectedItemIds.value) {
          total += 1;
          try {
            await updateTaskWaybillItem(id, {
              status: ITEM_STATUS.UNLOADED,
              remark
            });
          } catch {
            failed += 1;
          }
        }
      } else {
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
              (it.status ?? ITEM_STATUS.PENDING_LOAD) !== ITEM_STATUS.SIGNED ||
              !it.id
            )
              continue;
            total += 1;
            try {
              await updateTaskWaybillItem(it.id, {
                status: ITEM_STATUS.UNLOADED,
                remark
              });
            } catch {
              failed += 1;
            }
          }
        }
      }
      if (total === 0) {
        EleMessage.warning({ message: '没有可撤销的已交车货物', plain: true });
      } else if (failed > 0) {
        EleMessage.warning({
          message: `已撤销 ${total - failed} 行，失败 ${failed} 行`,
          plain: true
        });
      } else {
        EleMessage.success({
          message: `已撤销 ${total} 行交车`,
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
  .action-revert-sign__hint {
    margin-left: 12px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .action-revert-sign__items {
    width: 100%;
  }
</style>
