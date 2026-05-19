<!--
  强制取消弹窗（任务单 2/3/4 → 9，线下取消）

  作业语义：装车后、运输中、到达后这三个阶段，因客户取消/事故等线下原因，
  无法走常规取消的路径时，使用本动作直接置为「已取消」。
  - 所有挂接货物会被推到 9 已取消，cargo 占用台数释放；
  - 默认连带撤销该任务下所有"未支付"费用单（用户可关掉）。

  权限：``operation:task:force-cancel``
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="560px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      type="error"
      :closable="false"
      show-icon
      title="强制取消是不可逆的高危操作"
      description="将释放所有运单挂接，已签收/已结算的任务请勿使用此入口。"
      style="margin-bottom: 12px"
    />
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="任务单">
        <div class="action-task-info">
          <template v-if="tasks.length === 1">
            <b>{{ tasks[0].taskNo }}</b>
            <span class="ele-text-secondary" style="margin-left: 8px">
              {{ tasks[0].origin || '--' }} → {{ tasks[0].destination || '--' }}
            </span>
          </template>
          <template v-else>
            <el-tag type="danger" size="small">
              批量操作 {{ tasks.length }} 张任务单
            </el-tag>
          </template>
        </div>
      </el-form-item>
      <el-form-item label="取消原因" prop="reason" required>
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="必填，建议写清原因 + 处置方式（含客户沟通结论）"
        />
      </el-form-item>
      <el-form-item label="未支付费用单">
        <el-switch
          v-model="form.cancelUnpaidFinanceDocs"
          active-text="一并撤销"
          inactive-text="保留"
        />
        <div class="ele-text-secondary" style="font-size: 12px; margin-top: 4px">
          仅"待审批/已审批/草稿"的费用单会被撤销；已支付费用单不会受影响。
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="danger" :loading="submitting" @click="submit">
        强制取消任务
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { forceCancelTask } from '@/api/operation/task';
  import type { Task } from '@/api/operation/task/model';

  const props = defineProps<{
    visible: boolean;
    tasks: Task[];
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const submitting = ref(false);

  const form = reactive({
    reason: '',
    cancelUnpaidFinanceDocs: true
  });

  const rules: FormRules = {
    reason: [
      { required: true, message: '请填写取消原因' },
      { min: 2, max: 500, message: '原因长度需在 2-500 字之间' }
    ]
  };

  const title = computed(() =>
    props.tasks.length > 1 ? '批量强制取消' : '强制取消任务'
  );

  const onOpen = () => {
    form.reason = '';
    form.cancelUnpaidFinanceDocs = true;
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
    try {
      let failCount = 0;
      for (const t of props.tasks) {
        if (!t.id) continue;
        try {
          await forceCancelTask(t.id, {
            reason: form.reason.trim(),
            cancelUnpaidFinanceDocs: form.cancelUnpaidFinanceDocs
          });
        } catch {
          failCount += 1;
        }
      }
      if (failCount > 0) {
        EleMessage.warning({
          message: `已取消 ${props.tasks.length - failCount} 张，失败 ${failCount} 张`,
          plain: true
        });
      } else {
        EleMessage.success({ message: '强制取消已完成', plain: true });
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
