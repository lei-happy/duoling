<!-- 角色编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="520"
    :title="isUpdate ? '修改角色' : '添加角色'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      @submit.prevent=""
    >
      <el-form-item prop="roleName">
        <floating-label
          label="请输入角色名称"
          type="input"
          v-model.trim="form.roleName"
          :maxlength="20"
          clearable
        />
      </el-form-item>
      <el-form-item v-if="isUpdate">
        <floating-label
          label="角色标识"
          type="input"
          v-model.trim="form.roleCode"
          disabled
        />
      </el-form-item>
      <el-form-item prop="personas" class="role-persona-item">
        <div class="role-persona">
          <div class="role-persona__label">岗位视图</div>
          <el-checkbox-group v-model="form.personas" class="role-persona__group">
            <el-checkbox-button
              v-for="item in ROLE_PERSONAS"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </el-checkbox-button>
          </el-checkbox-group>
          <p class="role-persona__hint">
            可多选。决定小程序能切换哪些工作台，电脑端权限仍按功能勾选。
          </p>
        </div>
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入角色描述"
          type="input"
          input-type="textarea"
          v-model.trim="form.comments"
          clearable
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => handleSave() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { addRole, updateRole } from '@/api/system/role';
  import { ROLE_PERSONAS, type Role } from '@/api/system/role/model';

  const props = defineProps<{
    /** 修改回显的数据 */
    data?: Role | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  /** 是否是修改 */
  const isUpdate = ref(false);

  /** 提交状态 */
  const loading = ref(false);

  /** 表单组件 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, _resetFields, assignFields] = useFormData<Role>({
    roleId: void 0,
    roleName: '',
    roleCode: '',
    personas: [],
    comments: ''
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    roleName: [
      {
        required: true,
        message: '请输入角色名称',
        type: 'string',
        trigger: 'blur'
      }
    ],
    personas: [
      {
        validator: (_rule, value, callback) => {
          if (!isUpdate.value && !(Array.isArray(value) && value.length)) {
            callback(new Error('请至少选择一个岗位视图'));
            return;
          }
          callback();
        },
        trigger: 'change'
      }
    ]
  });

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 保存编辑 */
  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      const payload: Role = isUpdate.value
        ? { ...form }
        : {
            roleName: form.roleName,
            comments: form.comments,
            personas: form.personas
          };
      const saveOrUpdate = isUpdate.value ? updateRole : addRole;
      saveOrUpdate(payload)
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg, plain: true });
          emit('done');
          handleCancel();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  /** 修改赋值 */
  if (props.data) {
    assignFields({
      ...props.data,
      personas: Array.isArray(props.data.personas) ? [...props.data.personas] : []
    });
    isUpdate.value = true;
  }
</script>

<style scoped>
  .role-persona {
    width: 100%;
  }

  .role-persona__label {
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .role-persona__group {
    display: flex;
    flex-wrap: wrap;
  }

  .role-persona__hint {
    margin: 8px 0 0;
    font-size: 12px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }
</style>
