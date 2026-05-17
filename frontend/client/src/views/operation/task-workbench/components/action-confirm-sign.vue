<!--
  确认签收弹窗（任务单 status 4 → 5）

  作业语义：签收员/调度员在客户签收后录入签收时间和签收信息，把任务推进到"已签收"。
  后端 update_status 在 status=5 时无独立签收时间字段，签收时间会写入备注。
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
      <el-form-item label="签收时间" prop="signedAt" required>
        <el-date-picker
          v-model="form.signedAt"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          placeholder="选择客户签收时间"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="签收人">
        <el-input
          v-model="form.signedBy"
          placeholder="客户签收人姓名（可选）"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="签收过程中的其他信息（可选）"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="success" :loading="submitting" @click="submit">
        确认签收
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
    signedAt: '',
    signedBy: '',
    remark: ''
  });

  const rules: FormRules = {
    signedAt: [{ required: true, message: '请选择签收时间' }]
  };

  const title = computed(() =>
    props.tasks.length > 1 ? '批量确认签收' : '确认签收'
  );

  const onOpen = () => {
    form.signedAt = new Date().toISOString().slice(0, 19);
    form.signedBy = '';
    form.remark = '';
  };

  const buildRemark = () => {
    const parts: string[] = [];
    parts.push(`[签收] ${form.signedAt}`);
    if (form.signedBy.trim()) parts.push(`签收人：${form.signedBy.trim()}`);
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
    try {
      let failCount = 0;
      const remark = buildRemark();
      for (const t of props.tasks) {
        if (!t.id) continue;
        try {
          await updateTaskStatus(t.id, {
            status: 5,
            remark
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
        EleMessage.success({ message: '已确认签收', plain: true });
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
