<!-- 修改密码弹窗（短信验证码重置） -->
<template>
  <ele-modal
    form
    :width="420"
    title="修改密码"
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
      <el-form-item label="手机号">
        <el-input :model-value="phone" disabled />
      </el-form-item>
      <el-form-item label="验证码" prop="code">
        <div style="display: flex; gap: 10px; width: 100%">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            :maxlength="6"
            style="flex: 1"
          />
          <el-button :disabled="cooldown > 0" @click="handleSendCode">
            {{ cooldown > 0 ? `${cooldown}s` : '获取验证码' }}
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="新密码" prop="password">
        <el-input
          show-password
          type="password"
          :maxlength="20"
          v-model="form.password"
          placeholder="请输入新密码"
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="password2">
        <el-input
          show-password
          type="password"
          :maxlength="20"
          v-model="form.password2"
          placeholder="请再次输入新密码"
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
  import { ref, reactive, computed, onBeforeUnmount } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { useUserStore } from '@/store/modules/user';
  import { sendSmsCode, resetPasswordBySms } from '@/api/login';

  const { modalProps, closeModal } = useModal();
  const userStore = useUserStore();

  const phone = computed(() => userStore.info?.phone ?? '');

  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);
  const cooldown = ref(0);
  let cooldownTimer: ReturnType<typeof setInterval> | null = null;

  const form = reactive({
    code: '',
    password: '',
    password2: ''
  });

  const rules = reactive<FormRules>({
    code: [
      { required: true, message: '请输入验证码', trigger: 'blur' },
      { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      {
        pattern: /^[\S]{6,18}$/,
        message: '密码必须为6-18位非空白字符',
        trigger: 'blur'
      }
    ],
    password2: [
      { required: true, message: '请再次输入新密码', trigger: 'blur' },
      {
        trigger: 'blur',
        validator: (_rule: any, value: string, callback: any) => {
          if (value && value !== form.password) {
            return callback(new Error('两次输入密码不一致'));
          }
          callback();
        }
      }
    ]
  });

  const startCooldown = () => {
    cooldown.value = 60;
    cooldownTimer = setInterval(() => {
      cooldown.value--;
      if (cooldown.value <= 0 && cooldownTimer) {
        clearInterval(cooldownTimer);
        cooldownTimer = null;
      }
    }, 1000);
  };

  onBeforeUnmount(() => {
    if (cooldownTimer) {
      clearInterval(cooldownTimer);
    }
  });

  const handleSendCode = async () => {
    if (!phone.value) {
      EleMessage.error({ message: '无法获取当前手机号', plain: true });
      return;
    }
    try {
      await sendSmsCode(phone.value, 2);
      EleMessage.success({ message: '验证码已发送', plain: true });
      startCooldown();
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      resetPasswordBySms(phone.value, form.code, form.password)
        .then(() => {
          loading.value = false;
          EleMessage.success({ message: '密码重置成功', plain: true });
          handleCancel();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };
</script>
