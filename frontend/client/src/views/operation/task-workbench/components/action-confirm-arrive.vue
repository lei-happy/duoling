<!--
  确认到达弹窗（任务单 status 3 → 4）

  作业语义：在途监控员/调度员在车辆到达后录入实际到达时间，把任务推进到"已到达"。
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="480px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
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
            <el-tag type="success" size="small">
              批量操作 {{ tasks.length }} 张任务单
            </el-tag>
          </template>
        </div>
      </el-form-item>
      <el-form-item label="实际到达时间" prop="actualArriveTime" required>
        <el-date-picker
          v-model="form.actualArriveTime"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          placeholder="选择实际到达时间"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="可选，会追加到任务单备注"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="success" :loading="submitting" @click="submit">
        确认到达
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { updateTaskStatus } from '@/api/operation/task';
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
    actualArriveTime: '',
    remark: ''
  });

  const rules: FormRules = {
    actualArriveTime: [{ required: true, message: '请选择实际到达时间' }]
  };

  const title = computed(() =>
    props.tasks.length > 1 ? '批量确认到达' : '确认到达'
  );

  const onOpen = () => {
    form.actualArriveTime = new Date().toISOString().slice(0, 19);
    form.remark = '';
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
          await updateTaskStatus(t.id, {
            status: 4,
            actualArriveTime: form.actualArriveTime,
            remark: form.remark || undefined
          });
        } catch {
          failCount += 1;
        }
      }
      if (failCount > 0) {
        EleMessage.warning({
          message: `已完成 ${props.tasks.length - failCount} 张，失败 ${failCount} 张`,
          plain: true
        });
      } else {
        EleMessage.success({ message: '已确认到达', plain: true });
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
