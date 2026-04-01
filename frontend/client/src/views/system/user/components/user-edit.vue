<!-- 用户编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="680"
    :title="isUpdate ? '修改用户' : '添加用户'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :sm="12" :xs="24">
          <el-form-item label="所属机构">
            <organization-select v-model="form.organizationId" />
          </el-form-item>
          <el-form-item label="姓名" prop="nickname">
            <el-input
              clearable
              :maxlength="20"
              v-model="form.nickname"
              placeholder="请输入姓名"
            />
          </el-form-item>
          <el-form-item label="性别" prop="sex">
            <dict-data code="sex" v-model="form.sex" placeholder="请选择性别" />
          </el-form-item>
          <el-form-item label="角色" prop="roles">
            <role-select v-model="form.roles" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input
              clearable
              :maxlength="100"
              v-model="form.email"
              placeholder="请输入邮箱"
            />
          </el-form-item>
        </el-col>
        <el-col :sm="12" :xs="24">
          <el-form-item label="手机号" prop="phone">
            <el-input
              clearable
              :maxlength="11"
              v-model="form.phone"
              placeholder="请输入手机号"
            />
          </el-form-item>
          <el-form-item label="出生日期">
            <el-date-picker
              v-model="form.birthday"
              value-format="YYYY-MM-DD"
              placeholder="请选择出生日期"
              class="ele-fluid"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-radio-group v-model="form.status">
              <el-radio :value="0" label="正常" />
              <el-radio :value="1" label="冻结" />
            </el-radio-group>
          </el-form-item>
          <el-form-item label="个人简介">
            <el-input
              type="textarea"
              :rows="3"
              :maxlength="200"
              v-model="form.introduction"
              placeholder="请输入个人简介"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, emailReg, phoneReg, useModal } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import RoleSelect from './role-select.vue';
  import OrganizationSelect from '@/views/system/organization/components/organization-select.vue';
  import { addUser, updateUser, checkExistence } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';

  const props = defineProps<{
    /** 修改回显的数据 */
    data?: User | null;
    /** 添加时机构id */
    organizationId?: number;
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
  const [form, _resetFields, assignFields] = useFormData<User>({
    userId: void 0,
    nickname: '',
    sex: void 0,
    roles: [],
    email: '',
    phone: '',
    introduction: '',
    birthday: '',
    organizationId: props.organizationId,
    status: 0
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    nickname: [
      {
        required: true,
        message: '请输入姓名',
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
    roles: [
      {
        required: true,
        message: '请选择角色',
        type: 'array',
        trigger: 'change'
      }
    ],
    email: [
      {
        pattern: emailReg,
        message: '邮箱格式不正确',
        type: 'string',
        trigger: 'blur'
      }
    ],
    phone: [
      {
        required: true,
        message: '请输入手机号',
        type: 'string',
        trigger: 'blur'
      },
      {
        pattern: phoneReg,
        message: '手机号格式不正确',
        type: 'string',
        trigger: 'blur'
      },
      {
        type: 'string',
        trigger: 'blur',
        validator: (_rule: any, value: string, callback: any) => {
          if (!value || !phoneReg.test(value)) {
            callback();
            return;
          }
          checkExistence('phone', value, form.userId)
            .then((exists) => {
              if (exists) {
                callback(new Error('该手机号已存在'));
              } else {
                callback();
              }
            })
            .catch(() => callback());
        }
      }
    ]
  });

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 保存编辑 */
  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      const saveOrUpdate = isUpdate.value ? updateUser : addUser;
      saveOrUpdate(form)
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
    assignFields({ ...props.data, password: '' });
    isUpdate.value = true;
  }
</script>
