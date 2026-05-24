<template>
  <div class="sms-login">
    <van-nav-bar title="验证码登录" left-arrow @click-left="$router.back()" />

    <van-form class="login-form" @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号"
          type="tel"
          maxlength="11"
          clearable
          :rules="[
            { required: true, message: '请输入手机号' },
            { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }
          ]"
        />
        <van-field
          v-model="code"
          name="code"
          label="验证码"
          placeholder="请输入 6 位验证码"
          maxlength="6"
          :rules="[{ required: true, message: '请输入验证码' }]"
        >
          <template #button>
            <van-button
              size="small"
              type="primary"
              plain
              :disabled="countdown > 0 || sending"
              :loading="sending"
              @click="onSendCode"
            >
              {{ countdown > 0 ? `${countdown}s 后重试` : '获取验证码' }}
            </van-button>
          </template>
        </van-field>
      </van-cell-group>

      <div class="login-actions">
        <van-button block round type="primary" :loading="submitting" native-type="submit">
          登录
        </van-button>
      </div>

      <div class="login-extra">
        <router-link to="/login" class="link">密码登录</router-link>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from 'vue';
import { showFailToast, showToast } from 'vant';
import { sendSmsCode } from '@/api/auth';
import { useAuth } from '@/composables/useAuth';

const phone = ref('');
const code = ref('');
const sending = ref(false);
const submitting = ref(false);
const countdown = ref(0);
let timer: number | null = null;

const { smsLogin } = useAuth();

function startCountdown(s = 60) {
  countdown.value = s;
  if (timer) window.clearInterval(timer);
  timer = window.setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0 && timer) {
      window.clearInterval(timer);
      timer = null;
    }
  }, 1000);
}

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});

async function onSendCode() {
  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    showFailToast('请输入正确的手机号');
    return;
  }
  sending.value = true;
  try {
    // purpose=1：登录验证码
    await sendSmsCode({ phone: phone.value, purpose: 1 });
    showToast('验证码已发送');
    startCountdown(60);
  } catch (e) {
    showFailToast((e as Error)?.message || '发送失败');
  } finally {
    sending.value = false;
  }
}

async function onSubmit() {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await smsLogin(phone.value, code.value);
  } finally {
    submitting.value = false;
  }
}
</script>

<style lang="scss" scoped>
.sms-login {
  min-height: 100vh;
  background: $bg-page;
}
.login-form {
  margin-top: $spacing-xl;
  padding: $spacing-lg 0;
}
.login-actions {
  margin: $spacing-xl $spacing-lg 0;
}
.login-extra {
  text-align: center;
  margin-top: $spacing-lg;
  font-size: $font-size-sm;
  .link {
    color: $brand-primary;
  }
}
</style>
