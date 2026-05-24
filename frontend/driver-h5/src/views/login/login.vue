<template>
  <div class="login-page">
    <div class="login-brand">
      <div class="brand-icon">
        <van-icon name="logistics" />
      </div>
      <h1 class="brand-title">智途·司机端</h1>
      <p class="brand-subtitle">让每一趟运输都看得清楚</p>
    </div>

    <van-form class="login-form" @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="phone"
          name="phone"
          label="手机号"
          placeholder="请输入 11 位手机号"
          type="tel"
          maxlength="11"
          clearable
          :rules="[
            { required: true, message: '请输入手机号' },
            { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }
          ]"
        />
        <van-field
          v-model="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :type="showPwd ? 'text' : 'password'"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <template #right-icon>
            <van-icon :name="showPwd ? 'eye-o' : 'closed-eye'" @click="showPwd = !showPwd" />
          </template>
        </van-field>
      </van-cell-group>

      <div class="login-actions">
        <van-button block round type="primary" :loading="submitting" native-type="submit">
          登录
        </van-button>
      </div>

      <div class="login-extra">
        <router-link to="/sms-login" class="link">验证码登录</router-link>
        <span class="divider">|</span>
        <a class="link" @click="showForgotTip">忘记密码？</a>
      </div>
    </van-form>

    <div class="login-footer">仅限驾驶员使用，由企业管理员开通账号</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { showDialog } from 'vant';
import { useAuth } from '@/composables/useAuth';

const phone = ref('');
const password = ref('');
const showPwd = ref(false);
const submitting = ref(false);

const { passwordLogin } = useAuth();

async function onSubmit() {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await passwordLogin(phone.value, password.value);
  } finally {
    submitting.value = false;
  }
}

function showForgotTip() {
  showDialog({
    title: '忘记密码',
    message:
      '请在登录页通过「验证码登录」直接进入，登录后可在「我的-修改密码」中重置；或联系企业管理员协助。'
  });
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #1d4ed8 0%, #3b82f6 35%, #f4f6fb 35%, #f4f6fb 100%);
  padding-top: calc(60px + #{$safe-area-top});
  padding-bottom: $safe-area-bottom;
  display: flex;
  flex-direction: column;
}

.login-brand {
  text-align: center;
  color: #fff;
  padding: 0 $spacing-xl 32px;

  .brand-icon {
    width: 72px;
    height: 72px;
    margin: 0 auto $spacing-md;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
  }

  .brand-title {
    font-size: 24px;
    font-weight: 600;
    letter-spacing: 1px;
  }

  .brand-subtitle {
    margin-top: 6px;
    font-size: 13px;
    opacity: 0.86;
  }
}

.login-form {
  margin: 0 $spacing-lg;
  background: #fff;
  border-radius: 16px;
  padding: $spacing-xl $spacing-md $spacing-lg;
  box-shadow: $shadow-elevated;
}

.login-actions {
  margin-top: $spacing-xl;
  padding: 0 $spacing-md;
}

.login-extra {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: $spacing-lg;
  .link {
    color: $brand-primary;
  }
  .divider {
    color: $text-muted;
  }
}

.login-footer {
  margin-top: auto;
  padding: $spacing-xl;
  text-align: center;
  font-size: $font-size-xs;
  color: $text-muted;
}
</style>
