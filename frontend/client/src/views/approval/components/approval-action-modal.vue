<template>
  <el-dialog
    :title="title"
    :model-value="visible"
    width="500px"
    append-to-body
    align-center
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="84px"
      @submit.prevent=""
    >
      <el-form-item
        v-if="mode === 'transfer' || mode === 'addsign'"
        label="目标审批人"
        prop="targetUserId"
      >
        <user-select v-model="form.targetUserId" placeholder="请选择审批人" />
      </el-form-item>
      <el-form-item v-if="mode === 'addsign'" label="加签位置">
        <el-radio-group v-model="form.signMode">
          <el-radio value="after">我之后</el-radio>
          <el-radio value="before">我之前</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="mode === 'cc'" label="抄送人" prop="ccUserIds">
        <user-select
          v-model="form.ccUserIds"
          multiple
          placeholder="请选择抄送人"
        />
      </el-form-item>
      <el-form-item
        v-if="mode !== 'cc'"
        :label="mode === 'reject' ? '驳回理由' : '审批意见'"
        prop="comment"
      >
        <el-input
          v-model.trim="form.comment"
          type="textarea"
          :rows="4"
          :placeholder="
            mode === 'reject' ? '请输入驳回理由（必填）' : '请输入意见（可选）'
          "
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button :type="confirmType" :loading="saving" @click="confirm">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import UserSelect from '@/components/UserSelect/index.vue';
  import {
    agreeTask,
    rejectTask,
    transferTask,
    addSignTask,
    ccInstance
  } from '@/api/approval';

  type ActionMode = 'agree' | 'reject' | 'transfer' | 'addsign' | 'cc';

  const props = defineProps<{
    visible: boolean;
    mode: ActionMode;
    taskId?: number;
    instanceId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const formRef = ref<FormInstance | null>(null);
  const form = reactive<{
    comment: string;
    targetUserId?: number;
    signMode: 'before' | 'after';
    ccUserIds: number[];
  }>({
    comment: '',
    targetUserId: undefined,
    signMode: 'after',
    ccUserIds: []
  });
  const saving = ref(false);

  const title = computed(() => {
    switch (props.mode) {
      case 'agree':
        return '同意';
      case 'reject':
        return '驳回';
      case 'transfer':
        return '转审';
      case 'addsign':
        return '加签';
      case 'cc':
        return '抄送';
      default:
        return '审批';
    }
  });

  const confirmType = computed(() =>
    props.mode === 'reject' ? 'danger' : 'primary'
  );

  const rules = computed<FormRules>(() => {
    const r: FormRules = {};
    if (props.mode === 'reject') {
      r.comment = [
        { required: true, message: '请填写驳回理由', trigger: 'blur' }
      ];
    }
    if (props.mode === 'transfer' || props.mode === 'addsign') {
      r.targetUserId = [
        { required: true, message: '请选择目标审批人', trigger: 'change' }
      ];
    }
    if (props.mode === 'cc') {
      r.ccUserIds = [
        { required: true, message: '请选择抄送人', trigger: 'change' }
      ];
    }
    return r;
  });

  watch(
    () => props.visible,
    (v) => {
      if (v) {
        form.comment = '';
        form.targetUserId = undefined;
        form.signMode = 'after';
        form.ccUserIds = [];
      }
    }
  );

  const confirm = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    saving.value = true;
    try {
      const { mode, taskId, instanceId } = props;
      if (mode === 'agree') {
        await agreeTask(taskId!, { comment: form.comment || undefined });
      } else if (mode === 'reject') {
        await rejectTask(taskId!, { comment: form.comment });
      } else if (mode === 'transfer') {
        await transferTask(taskId!, {
          targetUserId: form.targetUserId!,
          comment: form.comment || undefined
        });
      } else if (mode === 'addsign') {
        await addSignTask(taskId!, {
          targetUserId: form.targetUserId!,
          mode: form.signMode,
          comment: form.comment || undefined
        });
      } else if (mode === 'cc') {
        await ccInstance(instanceId!, { targetUserIds: form.ccUserIds });
      }
      EleMessage.success({ message: '操作成功', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '操作失败', plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>
