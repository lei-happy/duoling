<template>
  <el-dialog
    :title="isEdit ? '编辑分组' : '新建分组'"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-row :gutter="12">
        <el-col :span="24">
          <el-form-item prop="groupName">
            <floating-label
              label="请输入分组名称"
              type="input"
              v-model.trim="form.groupName"
              :maxlength="50"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="groupCode">
            <floating-label
              label="请输入分组编码（留空自动生成）"
              type="input"
              v-model.trim="form.groupCode"
              :maxlength="50"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <business-entity-select
              v-model="form.enterpriseId"
              placeholder="请选择所属经营主体（留空为企业级公共分组）"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="标签颜色" label-width="72px">
            <el-color-picker v-model="form.color" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="排序号" label-width="56px">
            <el-input-number
              v-model="form.sortOrder"
              :min="0"
              :max="9999"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="状态" label-width="48px">
            <el-switch
              v-model="form.status"
              :active-value="1"
              :inactive-value="0"
              inline-prompt
              active-text="启用"
              inactive-text="停用"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入备注"
              type="input"
              input-type="textarea"
              v-model.trim="form.remark"
              :maxlength="255"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import BusinessEntitySelect from '@/components/BusinessEntitySelect/index.vue';
  import {
    addCapacityGroup,
    updateCapacityGroup
  } from '@/api/capacity/self-capacity/group';
  import type { CapacityGroup } from '@/api/capacity/self-capacity/group/model';

  const props = defineProps<{
    visible: boolean;
    data: CapacityGroup | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<CapacityGroup>({ status: 1, sortOrder: 0 });

  const rules = reactive<FormRules>({
    groupName: [{ required: true, message: '请输入分组名称', trigger: 'blur' }]
  });

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        if (props.data) {
          Object.assign(form, { ...props.data });
        } else {
          Object.keys(form).forEach((k) => {
            (form as any)[k] = undefined;
          });
          form.status = 1;
          form.sortOrder = 0;
        }
        void nextTick(() => formRef.value?.clearValidate());
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const msg = isEdit.value
          ? await updateCapacityGroup(form)
          : await addCapacityGroup(form);
        EleMessage.success({ message: msg, plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>
