<template>
  <div class="change-pwd">
    <van-nav-bar title="修改密码" :left-arrow="!forceMode" @click-left="$router.back()" />

    <div v-if="forceMode" class="tip card">
      <van-icon name="warning-o" class="tip-icon" />
      <div>
        <div class="tip-title">首次登录请先修改密码</div>
        <div class="tip-desc">为了账号安全，请将初始密码改为只有您本人知道的强密码</div>
      </div>
    </div>

    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="oldPassword"
          type="password"
          label="旧密码"
          placeholder="请输入当前密码"
          :rules="[{ required: true, message: '请输入旧密码' }]"
        />
        <van-field
          v-model="newPassword"
          type="password"
          label="新密码"
          placeholder="至少 8 位，建议字母+数字"
          :rules="[
            { required: true, message: '请输入新密码' },
            { pattern: /^.{8,32}$/, message: '密码长度应为 8-32 位' }
          ]"
        />
        <van-field
          v-model="confirmPassword"
          type="password"
          label="确认密码"
          placeholder="请再次输入新密码"
          :rules="[
            { required: true, message: '请确认新密码' },
            { validator: (v) => v === newPassword, message: '两次密码不一致' }
          ]"
        />
      </van-cell-group>

      <div class="actions">
        <van-button block round type="primary" :loading="submitting" native-type="submit">
          确认修改
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { showToast } from 'vant';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';

const oldPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const submitting = ref(false);

const user = useUserStore();
const router = useRouter();

const forceMode = computed(() => user.needForceChangePwd);

async function onSubmit() {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await user.doChangePassword({
      oldPassword: oldPassword.value,
      newPassword: newPassword.value
    });
    showToast({ message: '密码修改成功', type: 'success' });
    await router.replace('/home');
  } finally {
    submitting.value = false;
  }
}
</script>

<style lang="scss" scoped>
.change-pwd {
  min-height: 100vh;
  background: $bg-page;
}
.tip {
  margin: $spacing-lg;
  display: flex;
  gap: $spacing-md;
  align-items: flex-start;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  .tip-icon {
    font-size: 22px;
    color: $brand-warning;
  }
  .tip-title {
    font-weight: 600;
    margin-bottom: 4px;
  }
  .tip-desc {
    color: $text-secondary;
    font-size: $font-size-sm;
  }
}
.actions {
  margin: $spacing-xl $spacing-lg;
}
</style>
