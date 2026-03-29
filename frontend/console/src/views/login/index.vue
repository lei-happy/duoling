<template>
  <div class="login-wrapper">
    <div class="login-main">
      <ele-card shadow="always" class="login-card">
        <div class="login-cover">
          <h1 class="login-title">{{ PROJECT_NAME }}</h1>
          <h4 class="login-subtitle">物流车队综合操作系统</h4>
        </div>
        <div class="login-body">
          <ele-text type="heading" style="font-size: 24px; margin-bottom: 18px">
            {{ t('login.title') }}
          </ele-text>

          <!-- 登录方式 Tab -->
          <div class="login-tabs">
            <span
              :class="['login-tab', { active: loginMode === 'password' }]"
              @click="loginMode = 'password'"
            >密码登录</span>
            <span class="login-tab-divider">|</span>
            <span
              :class="['login-tab', { active: loginMode === 'sms' }]"
              @click="loginMode = 'sms'"
            >验证码登录</span>
          </div>

          <!-- 密码登录表单 -->
          <el-form
            v-if="loginMode === 'password'"
            ref="formRef"
            size="large"
            :model="form"
            :rules="rules"
            @keyup.enter="submit"
            @submit.prevent=""
          >
            <el-form-item prop="phone">
              <el-input
                clearable
                v-model="form.phone"
                placeholder="请输入手机号"
                :prefix-icon="UserOutlined"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                show-password
                v-model="form.password"
                :placeholder="t('login.password')"
                :prefix-icon="LockOutlined"
              />
            </el-form-item>
            <el-form-item>
              <div style="display: flex; justify-content: space-between; width: 100%">
                <el-checkbox v-model="form.remember">
                  {{ t('login.remember') }}
                </el-checkbox>
                <a class="forgot-pwd-link" @click.prevent="showForgotPwdDialog = true">
                  忘记密码？
                </a>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button
                size="large"
                type="primary"
                :loading="loading"
                style="width: 100%"
                @click="submit"
              >
                {{ t('login.login') }}
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 验证码登录表单 -->
          <el-form
            v-else
            ref="smsFormRef"
            size="large"
            :model="smsForm"
            :rules="smsRules"
            @keyup.enter="submitSms"
            @submit.prevent=""
          >
            <el-form-item prop="phone">
              <el-input
                clearable
                v-model="smsForm.phone"
                placeholder="请输入手机号"
                :prefix-icon="UserOutlined"
              />
            </el-form-item>
            <el-form-item prop="code">
              <div style="display: flex; gap: 10px; width: 100%">
                <el-input
                  v-model="smsForm.code"
                  placeholder="请输入验证码"
                  :prefix-icon="LockOutlined"
                  style="flex: 1"
                />
                <el-button
                  size="large"
                  :disabled="smsCooldown > 0"
                  @click="handleSendCode(smsForm.phone, 1)"
                >
                  {{ smsCooldown > 0 ? `${smsCooldown}s` : '获取验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <div style="display: flex; justify-content: space-between; width: 100%">
                <el-checkbox v-model="smsForm.remember">
                  {{ t('login.remember') }}
                </el-checkbox>
                <a class="forgot-pwd-link" @click.prevent="showForgotPwdDialog = true">
                  忘记密码？
                </a>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button
                size="large"
                type="primary"
                :loading="loading"
                style="width: 100%"
                @click="submitSms"
              >
                {{ t('login.login') }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </ele-card>
    </div>
    <PageFooter style="padding-top: 0" />

    <!-- 忘记密码弹窗 -->
    <el-dialog
      v-model="showForgotPwdDialog"
      title="重置密码"
      width="420px"
      center
      @close="resetForgotPwdForm"
    >
      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        label-width="80px"
        @submit.prevent=""
      >
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="forgotForm.phone" placeholder="请输入注册手机号" />
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <div style="display: flex; gap: 10px; width: 100%">
            <el-input v-model="forgotForm.code" placeholder="请输入验证码" style="flex: 1" />
            <el-button
              :disabled="forgotCooldown > 0"
              @click="handleSendForgotCode"
            >
              {{ forgotCooldown > 0 ? `${forgotCooldown}s` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input show-password v-model="forgotForm.newPassword" placeholder="请输入新密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input show-password v-model="forgotForm.confirmPassword" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotPwdDialog = false">取消</el-button>
        <el-button type="primary" :loading="forgotLoading" @click="submitForgotPwd">
          确认重置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { UserOutlined, LockOutlined } from '@/components/icons';
  import PageFooter from '@/layout/components/page-footer.vue';
  import { useLogin } from '@/utils/use-login';
  import { sendSmsCode, resetPasswordBySms } from '@/api/login';
  import { useI18n } from 'vue-i18n';
  const PROJECT_NAME = import.meta.env.VITE_APP_NAME;

  const { login, smsLogin, checkLogin } = useLogin();
  const { t } = useI18n();

  const loginMode = ref<'password' | 'sms'>('password');
  const loading = ref(false);

  // ============================================================
  // 密码登录
  // ============================================================
  const formRef = ref<FormInstance | null>(null);
  const form = reactive({ phone: '', password: '', remember: true });
  const rules = computed<FormRules>(() => ({
    phone: [
      { required: true, message: '请输入手机号', type: 'string', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
    ],
    password: [
      { required: true, message: t('login.password'), type: 'string', trigger: 'blur' }
    ]
  }));

  const submit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      login(form).catch((e: Error) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
    });
  };

  // ============================================================
  // 验证码登录
  // ============================================================
  const smsFormRef = ref<FormInstance | null>(null);
  const smsForm = reactive({ phone: '', code: '', remember: true });
  const smsRules = computed<FormRules>(() => ({
    phone: [
      { required: true, message: '请输入手机号', type: 'string', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
    ],
    code: [
      { required: true, message: '请输入验证码', type: 'string', trigger: 'blur' },
      { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
    ]
  }));

  const smsCooldown = ref(0);
  let smsTimer: ReturnType<typeof setInterval> | null = null;

  const startCooldown = (target: typeof smsCooldown) => {
    target.value = 60;
    const timer = setInterval(() => {
      target.value--;
      if (target.value <= 0) clearInterval(timer);
    }, 1000);
    return timer;
  };

  const handleSendCode = async (phone: string, purpose: number) => {
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
      EleMessage.error({ message: '请输入正确的手机号', plain: true });
      return;
    }
    try {
      await sendSmsCode(phone, purpose);
      EleMessage.success({ message: '验证码已发送', plain: true });
      if (smsTimer) clearInterval(smsTimer);
      smsTimer = startCooldown(smsCooldown);
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const submitSms = () => {
    smsFormRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      smsLogin(smsForm.phone, smsForm.code, smsForm.remember)
        .catch((e: Error) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  // ============================================================
  // 忘记密码
  // ============================================================
  const showForgotPwdDialog = ref(false);
  const forgotLoading = ref(false);
  const forgotFormRef = ref<FormInstance | null>(null);
  const forgotCooldown = ref(0);

  const forgotForm = reactive({
    phone: '', code: '', newPassword: '', confirmPassword: ''
  });

  const forgotRules = computed<FormRules>(() => ({
    phone: [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
    ],
    code: [
      { required: true, message: '请输入验证码', trigger: 'blur' },
      { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
    ],
    newPassword: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '密码长度至少6位', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: '请再次输入新密码', trigger: 'blur' },
      {
        validator: (_rule: any, value: string, callback: any) => {
          if (value !== forgotForm.newPassword) {
            callback(new Error('两次输入的密码不一致'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ]
  }));

  const handleSendForgotCode = async () => {
    if (!forgotForm.phone || !/^1[3-9]\d{9}$/.test(forgotForm.phone)) {
      EleMessage.error({ message: '请输入正确的手机号', plain: true });
      return;
    }
    try {
      await sendSmsCode(forgotForm.phone, 2);
      EleMessage.success({ message: '验证码已发送', plain: true });
      startCooldown(forgotCooldown);
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const submitForgotPwd = () => {
    forgotFormRef.value?.validate?.((valid) => {
      if (!valid) return;
      forgotLoading.value = true;
      resetPasswordBySms(forgotForm.phone, forgotForm.code, forgotForm.newPassword)
        .then(() => {
          forgotLoading.value = false;
          showForgotPwdDialog.value = false;
          EleMessage.success({ message: '密码重置成功，请使用新密码登录', plain: true });
        })
        .catch((e: Error) => {
          forgotLoading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  const resetForgotPwdForm = () => {
    forgotForm.phone = '';
    forgotForm.code = '';
    forgotForm.newPassword = '';
    forgotForm.confirmPassword = '';
    forgotCooldown.value = 0;
  };

  checkLogin();
</script>

<style lang="scss" scoped>
  .login-wrapper {
    min-height: 100vh;
    min-height: 100dvh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    background-image: url('@/assets/login-bg.png');
    background-repeat: no-repeat;
    background-size: 100% 100%;

    .login-main {
      flex: auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
      padding: 20px;
    }

    .login-card {
      width: 920px;
      max-width: 100%;
      overflow: hidden;

      :deep(.ele-card-body) {
        display: flex;
        padding: 0;
        height: 462px;
      }
    }
  }

  .login-cover {
    flex: 1;
    padding: 32px 8px;
    box-sizing: border-box;
    background-color: #1681fd;
    background-image: url('@/assets/login-img.png');
    background-repeat: no-repeat;
    background-position: bottom;
    background-size: contain;
    text-align: center;
  }

  .login-body {
    width: 400px;
    flex-shrink: 0;
    padding: 32px 48px 0 48px;
    box-sizing: border-box;

    :deep(.el-checkbox) {
      height: auto;

      .el-checkbox__label {
        color: inherit;
      }
    }

    :deep(.el-input__prefix-inner > .el-icon) {
      margin-right: 12px;
      transform: scale(1.16);
    }
  }

  .login-title {
    color: rgba(255, 255, 255, 0.98);
    font-size: 28px;
    margin: 0 0 6px 0;
    font-weight: normal;
    letter-spacing: 1.2px;
    font-family:
      -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
      Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji',
      'Segoe UI Symbol', 'Noto Color Emoji';
  }

  .login-subtitle {
    color: rgba(255, 255, 255, 0.8);
    font-size: 16px;
    margin: 0;
    font-weight: normal;
    letter-spacing: 4px;
  }

  .login-tabs {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }

  .login-tab {
    font-size: 14px;
    color: #94a3b8;
    cursor: pointer;
    transition: color 0.2s;

    &.active {
      color: #1681fd;
      font-weight: 600;
    }

    &:hover {
      color: #1681fd;
    }
  }

  .login-tab-divider {
    color: #e2e8f0;
    font-size: 14px;
  }

  .forgot-pwd-link {
    font-size: 13px;
    color: #1681fd;
    cursor: pointer;
    text-decoration: none;
    line-height: 32px;

    &:hover {
      text-decoration: underline;
    }
  }

  @media screen and (max-width: 680px) {
    .login-wrapper {
      background: #fff;

      .login-main {
        padding: 0;
        display: block;
      }

      .login-card {
        width: 100%;
        background: none;
        box-shadow: none;
        border-radius: 0;

        :deep(.ele-card-body) {
          display: block;
          height: auto;
        }
      }
    }

    .login-cover {
      padding: 20px 12px 100px 12px;
      background-size: auto 100px;
    }

    .login-body {
      width: 100%;
    }
  }
</style>
