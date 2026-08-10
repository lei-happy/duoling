<!--
  常规取消任务单弹窗（cancel_task：-1/0/1/2 → 9）

  作业语义：调度阶段（待分配/待派车/待装车/已装车）撤掉整张任务单。
  - 释放任务下所有计划挂接（cargo.allocated_quantity 退回）；
  - 自动撤销该任务下"未支付"的费用单（已支付费用单由财务侧另行处理）；
  - 关联计划聚合允许下降（详见 02.计划与任务单状态机联动设计.md §4.5）。

  与强制取消（force_cancel）的区别：本动作仅作用于 2 之前 / 已装车的常规闭环，
  ≥3 在途 / 4 已到达 走「强制取消」走专项通道；≥ 5 已交车 一律不允许。
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
      title="取消任务单将释放该任务下的所有计划挂接"
      description="未支付的费用单会被自动撤销；已支付费用单需财务侧另行处理。已交车 / 已关闭 任务请勿使用此入口。"
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
      <el-form-item label="取消原因" prop="reason">
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="选填：例如客户撤单、调度调整等；将记录到任务单备注"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="warning" :loading="submitting" @click="submit">
        确认取消任务
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { cancelTask } from '@/api/operation/task';
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

  const form = reactive({ reason: '' });
  const rules: FormRules = {
    reason: [{ max: 500, message: '原因最长 500 字' }]
  };

  const title = computed(() =>
    props.tasks.length > 1 ? '批量取消任务单' : '取消任务单'
  );

  const onOpen = () => {
    form.reason = '';
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
          await cancelTask(t.id, form.reason.trim() || undefined);
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
        EleMessage.success({
          message: props.tasks.length > 1 ? '批量取消已完成' : '已取消任务单',
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
  .action-task-info {
    line-height: 32px;
  }
</style>
