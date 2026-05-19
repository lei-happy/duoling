<!--
  通用撤销弹窗（任务单单步反向跳转）

  适用：撤销装车 (2→1)、撤回出发 (3→2)、撤回到达 (4→3)、撤销签收 (5→4)。
  调用方通过 ``actionKey`` 传入具体动作语义；本组件统一调 POST /revert-status。

  作业语义：调度员发现上一步操作有误时撤回到上一态；后端会同步反向推 Item，
  并触发运单状态聚合（允许 downgrade）。原因必填，写入任务单备注（审计）。
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="520px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      type="warning"
      :closable="false"
      show-icon
      :title="bannerText"
      style="margin-bottom: 12px"
    />
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="任务单">
        <div class="action-task-info">
          <template v-if="tasks.length === 1">
            <b>{{ tasks[0].taskNo }}</b>
            <span class="ele-text-secondary" style="margin-left: 8px">
              {{ tasks[0].origin || '--' }} → {{ tasks[0].destination || '--' }}
            </span>
          </template>
          <template v-else>
            <el-tag type="warning" size="small">
              批量操作 {{ tasks.length }} 张任务单
            </el-tag>
          </template>
        </div>
      </el-form-item>
      <el-form-item label="撤销原因" prop="reason" required>
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="必填，例如：装车员误确认、客户临时变更地址等"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="warning" :loading="submitting" @click="submit">
        确认撤销
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { revertTaskStatus } from '@/api/operation/task';
  import type { Task } from '@/api/operation/task/model';
  import {
    TASK_ACTION_CONFIGS,
    type TaskActionKey
  } from '@/views/operation/task/task-actions';

  const props = defineProps<{
    visible: boolean;
    tasks: Task[];
    actionKey: TaskActionKey;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const submitting = ref(false);

  const form = reactive({ reason: '' });
  const rules: FormRules = {
    reason: [
      { required: true, message: '请填写撤销原因' },
      { min: 2, max: 500, message: '原因长度需在 2-500 字之间' }
    ]
  };

  const cfg = computed(() => TASK_ACTION_CONFIGS[props.actionKey]);
  const title = computed(() =>
    props.tasks.length > 1 ? `批量${cfg.value.label}` : cfg.value.label
  );

  const STATUS_LABELS: Record<number, string> = {
    [-1]: '待分配',
    0: '待派车',
    1: '已派车',
    2: '已装车',
    3: '在途',
    4: '已到达',
    5: '已签收'
  };

  const bannerText = computed(() => {
    const from = cfg.value.revertFrom;
    const to = cfg.value.revertTo;
    if (from === undefined || to === undefined) return '';
    return `将把任务从「${STATUS_LABELS[from]}」回退到「${STATUS_LABELS[to]}」；运单状态会自动联动回退。`;
  });

  const onOpen = () => {
    form.reason = '';
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    const target = cfg.value.revertTo;
    if (target === undefined) {
      EleMessage.error({ message: '动作配置缺少 revertTo', plain: true });
      return;
    }
    if (!props.tasks.length) {
      emit('update:visible', false);
      return;
    }
    submitting.value = true;
    try {
      let failCount = 0;
      for (const t of props.tasks) {
        if (!t.id) continue;
        try {
          await revertTaskStatus(t.id, {
            targetStatus: target,
            reason: form.reason.trim()
          });
        } catch {
          failCount += 1;
        }
      }
      if (failCount > 0) {
        EleMessage.warning({
          message: `已撤销 ${props.tasks.length - failCount} 张，失败 ${failCount} 张`,
          plain: true
        });
      } else {
        EleMessage.success({ message: `${cfg.value.label} 已完成`, plain: true });
      }
      emit('done');
      emit('update:visible', false);
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .action-task-info {
    line-height: 32px;
  }
</style>
