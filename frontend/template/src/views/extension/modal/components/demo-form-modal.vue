<template>
  <ele-modal
    form
    :width="400"
    :title="isUpdate ? '修改用户' : '添加用户'"
    :loading="loading"
    v-bind="modalProps"
  >
    <template #header>
      <el-icon style="vertical-align: -3px; margin-right: 8px">
        <ControlOutlined />
      </el-icon>
      <btn-items :items="[{ title: '我是自定义顶栏', type: 'link' }]" />
    </template>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="70px"
      @submit.prevent=""
    >
      <el-form-item label="用户名" prop="nickname">
        <el-input
          clearable
          v-model="form.nickname"
          placeholder="请输入用户名"
        />
      </el-form-item>
      <el-form-item label="性别" prop="sex">
        <el-select
          clearable
          v-model="form.sex"
          placeholder="请选择性别"
          class="ele-fluid"
        >
          <el-option value="男">男</el-option>
          <el-option value="女">女</el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input clearable v-model="form.phone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input clearable v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="个人简介">
        <el-input
          :rows="4"
          type="textarea"
          v-model="form.introduction"
          placeholder="请输入个人简介"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { title: '我是自定义按钮', onClick: () => handleClick() },
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
  import { ControlOutlined } from '@/components/icons';
  import { useFormData } from '@/utils/use-form-data';
  import type { User } from '@/api/system/user/model';

  const props = defineProps<{
    /** 修改回显的数据 */
    data?: User | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  /** 是否是修改 */
  const isUpdate = ref(false);

  /** 提交状态 */
  const loading = ref(false);

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, _resetFields, assignFields] = useFormData({
    nickname: '',
    sex: void 0,
    phone: '',
    email: '',
    introduction: ''
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    nickname: [
      {
        required: true,
        message: '请输入用户名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    sex: [
      {
        required: true,
        message: '请选择性别',
        type: 'string',
        trigger: 'change'
      }
    ],
    phone: [
      {
        required: true,
        message: '请输入手机号',
        type: 'string',
        trigger: 'blur'
      }
    ],
    email: [
      {
        required: true,
        message: '请输入邮箱',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  /** 取消按钮点击事件 */
  const handleCancel = () => {
    closeModal();
  };

  /** 保存按钮点击事件 */
  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      setTimeout(() => {
        loading.value = false;
        emit('done');
        handleCancel();
      }, 1500);
    });
  };

  /** 按钮点击事件 */
  const handleClick = () => {
    EleMessage.info({ message: '点击了自定义按钮', plain: true });
  };

  /** 回显数据 */
  if (props.data) {
    assignFields(props.data);
    isUpdate.value = true;
  }
</script>
