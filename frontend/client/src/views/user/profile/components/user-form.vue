<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    style="max-width: 580px; padding: 34px 16px 12px 0; box-sizing: border-box"
    @submit.prevent=""
  >
    <el-form-item label="手机号">
      <el-input :model-value="data.phone" disabled />
    </el-form-item>
    <el-form-item label="所属企业" v-if="data.tenantName">
      <el-input :model-value="data.tenantName" disabled />
    </el-form-item>
    <el-form-item label="用户类型">
      <el-input :model-value="userTypeName" disabled />
    </el-form-item>
    <el-form-item label="昵称" prop="nickname">
      <el-input
        clearable
        :maxlength="20"
        v-model="form.nickname"
        placeholder="请输入昵称"
      />
    </el-form-item>
    <el-form-item label="性别" prop="sex">
      <el-select
        clearable
        v-model="form.sex"
        placeholder="请选择性别"
        class="ele-fluid"
      >
        <el-option value="男" label="男" />
        <el-option value="女" label="女" />
      </el-select>
    </el-form-item>
    <el-form-item label="邮箱" prop="email">
      <el-input
        clearable
        :maxlength="100"
        v-model="form.email"
        placeholder="请输入邮箱"
      />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="loading" @click="save">
        {{ loading ? '保存中..' : '保存更改' }}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import { updateUserInfo } from '@/api/layout';
  import type { User } from '@/api/system/user/model';

  const USER_TYPE_MAP: Record<number, string> = {
    1: '管理员',
    2: '普通员工',
    3: '驾驶员'
  };

  const props = defineProps<{
    data: User;
  }>();

  const emit = defineEmits<{
    (e: 'done', value: User): void;
  }>();

  const userTypeName = computed(() => {
    return USER_TYPE_MAP[props.data.userType ?? 0] || '-';
  });

  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData<User>({
    nickname: '',
    sex: void 0,
    email: ''
  });

  const rules = reactive<FormRules>({
    nickname: [
      {
        required: true,
        message: '请输入昵称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      updateUserInfo({
        nickname: form.nickname,
        sex: form.sex,
        email: form.email
      })
        .then((data) => {
          loading.value = false;
          EleMessage.success({ message: '保存成功', plain: true });
          emit('done', data);
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  assignFields({
    nickname: props.data.nickname || '',
    sex: props.data.sex,
    email: props.data.email || ''
  });
</script>
