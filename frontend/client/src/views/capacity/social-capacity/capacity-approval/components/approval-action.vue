<template>
  <el-dialog
    :title="mode === 'approve' ? '审核通过' : '审核驳回'"
    :model-value="visible"
    width="480px"
    append-to-body
    align-center
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      @submit.prevent=""
    >
      <el-form-item v-if="row" label="编号">
        <el-input :model-value="row.socialCode" readonly />
      </el-form-item>
      <el-form-item label="意见" prop="remark">
        <el-input
          v-model.trim="form.remark"
          type="textarea"
          :rows="4"
          :placeholder="mode === 'approve' ? '可选' : '请输入驳回理由（必填）'"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button
        :type="mode === 'approve' ? 'success' : 'danger'"
        :loading="saving"
        @click="confirm"
      >
        {{ mode === 'approve' ? '确认通过' : '确认驳回' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    approveSocialCapacity,
    rejectSocialCapacity
  } from '@/api/capacity/social-capacity/approval';
  import type { SocialCapacityListItem } from '@/api/capacity/social-capacity/list/model';

  const props = defineProps<{
    visible: boolean;
    mode: 'approve' | 'reject';
    row?: SocialCapacityListItem | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const formRef = ref<FormInstance | null>(null);
  const form = reactive({ remark: '' });
  const saving = ref(false);

  const rules = ref<FormRules>({});

  watch(
    () => [props.visible, props.mode] as const,
    ([v, m]) => {
      if (v) {
        form.remark = '';
        rules.value =
          m === 'reject'
            ? {
                remark: [
                  { required: true, message: '请填写驳回理由', trigger: 'blur' }
                ]
              }
            : {};
      }
    }
  );

  const confirm = async () => {
    if (!props.row?.id) return;
    if (props.mode === 'reject') {
      try {
        await formRef.value?.validate();
      } catch {
        return;
      }
    }
    saving.value = true;
    try {
      if (props.mode === 'approve') {
        await approveSocialCapacity(props.row.id, {
          remark: form.remark || undefined
        });
        EleMessage.success({ message: '审核通过', plain: true });
      } else {
        await rejectSocialCapacity(props.row.id, { remark: form.remark });
        EleMessage.success({ message: '审核驳回', plain: true });
      }
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '操作失败', plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>
