<!--
  承运商邀请着陆页（白名单免登录）
  路径 B：未注册手机号点击短信链接进入 → 输入企业名 + 真实姓名 + 短信验证码 → 自动开通 lite
-->
<template>
  <div class="invite-landing">
    <div class="card">
      <div class="header">
        <h1>承运商互联激活</h1>
        <p class="subtitle">智途物流 - 您正在被邀请加入承运商互联生态</p>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading">
        <el-icon class="rotating" size="32"><Loading /></el-icon>
        <p>正在加载邀请信息…</p>
      </div>

      <!-- 错误 / 失效 -->
      <div v-else-if="errorMsg || (info && info.expired)" class="error-state">
        <el-icon size="48" color="#e6a23c"><WarningFilled /></el-icon>
        <h2>邀请已失效</h2>
        <p>{{
          errorMsg || '该邀请已过期或已被处理，请联系邀请方重新发送。'
        }}</p>
      </div>

      <!-- 已注册（路径 B 不允许） -->
      <div v-else-if="info && info.userExisted" class="error-state">
        <el-icon size="48" color="#909399"><InfoFilled /></el-icon>
        <h2>该手机号已注册账号</h2>
        <p>
          路径 B 仅适用于未注册用户。当前手机号已存在平台账号，请直接登录后由
          <a :href="loginUrl">管理员审核 / 接受邀请</a>
          （C1/C2/C3 路径，本期暂未开放）。
        </p>
      </div>

      <!-- 正常激活表单 -->
      <div v-else-if="info" class="activate-form">
        <div class="invite-summary">
          <div class="row">
            <span class="label">邀请方：</span>
            <span class="value">{{ info.sourceTenantName }}</span>
          </div>
          <div class="row">
            <span class="label">承运商名称：</span>
            <span class="value">{{ info.expectedCarrierName }}</span>
          </div>
          <div class="row">
            <span class="label">被邀请手机号：</span>
            <span class="value">{{ info.invitePhoneMasked }}</span>
          </div>
          <div class="row">
            <span class="label">有效期至：</span>
            <span class="value">{{ formatDateTime(info.expiresAt) }}</span>
          </div>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          @submit.prevent=""
        >
          <el-form-item prop="contactPhone">
            <floating-label
              label="请输入完整手机号（与短信接收号一致）"
              type="input"
              v-model.trim="form.contactPhone"
              clearable
            />
          </el-form-item>
          <el-form-item prop="smsCode">
            <div class="sms-row">
              <floating-label
                label="6位短信验证码"
                type="input"
                v-model.trim="form.smsCode"
                clearable
              />
              <el-button
                type="primary"
                plain
                :disabled="cooldown > 0 || sending"
                @click="sendSms"
              >
                {{ cooldown > 0 ? `${cooldown}s` : '获取验证码' }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item prop="realName">
            <floating-label
              label="请输入您的真实姓名"
              type="input"
              v-model.trim="form.realName"
              clearable
            />
          </el-form-item>
          <el-form-item prop="tenantName">
            <floating-label
              label="自定义企业名称（默认值=邀请方录入）"
              type="input"
              v-model.trim="form.tenantName"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="企业简称（选填）"
              type="input"
              v-model.trim="form.shortName"
              clearable
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            class="submit-btn"
            @click="handleSubmit"
          >
            激活并进入系统
          </el-button>
        </el-form>

        <p class="footer-tip">
          点击激活即表示您同意《智途物流用户协议》。激活后将自动为您开通免费的轻量版账号，
          仅用于运力管理与承运商互联，可随时升级到标准版/专业版。
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { Loading, WarningFilled, InfoFilled } from '@element-plus/icons-vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    getInviteInfo,
    activateInvite,
    type CarrierInviteInfo
  } from '@/api/open/carrier-invite';
  import { sendSmsCode } from '@/api/login';
  import { setToken, setRefreshToken } from '@/utils/token-util';
  import { formatDateTime } from '@/utils/date-util';
  import { LOGIN_PATH, LAYOUT_PATH } from '@/config/setting';

  const route = useRoute();
  const router = useRouter();
  const loading = ref(true);
  const submitting = ref(false);
  const sending = ref(false);
  const cooldown = ref(0);
  const errorMsg = ref('');
  const info = ref<CarrierInviteInfo | null>(null);
  const loginUrl = LOGIN_PATH;

  const formRef = ref<FormInstance>();
  const form = reactive({
    contactPhone: '',
    smsCode: '',
    realName: '',
    tenantName: '',
    shortName: '' as string | undefined
  });

  const rules = reactive<FormRules>({
    contactPhone: [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      {
        pattern: /^1[3-9]\d{9}$/,
        message: '请输入正确的手机号',
        trigger: 'blur'
      }
    ],
    smsCode: [
      { required: true, message: '请输入短信验证码', trigger: 'blur' },
      { pattern: /^\d{6}$/, message: '请输入 6 位数字', trigger: 'blur' }
    ],
    realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
    tenantName: [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
  });

  onMounted(async () => {
    const code = route.params.code as string;
    if (!code) {
      errorMsg.value = '邀请链接无效';
      loading.value = false;
      return;
    }
    try {
      info.value = await getInviteInfo(code);
      if (info.value) {
        form.tenantName = info.value.expectedCarrierName ?? '';
      }
    } catch (e: any) {
      errorMsg.value = e.message || '邀请加载失败';
    } finally {
      loading.value = false;
    }
  });

  const startCooldown = () => {
    cooldown.value = 60;
    const timer = setInterval(() => {
      cooldown.value -= 1;
      if (cooldown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  };

  // 路径 B 落地页：被邀请人是"未注册手机号开新企业"场景，
  // 必须使用 PURPOSE_TENANT_REGISTER=4（与官网注册一致）。
  // 用 PURPOSE_LOGIN=1 会被后端 _check_phone_exists 直接拒绝（未注册不可登录）。
  const PURPOSE_TENANT_REGISTER = 4;

  const sendSms = async () => {
    if (!form.contactPhone || !/^1[3-9]\d{9}$/.test(form.contactPhone)) {
      EleMessage.error({ message: '请先输入正确的手机号', plain: true });
      return;
    }
    sending.value = true;
    try {
      await sendSmsCode(form.contactPhone, PURPOSE_TENANT_REGISTER);
      EleMessage.success({ message: '验证码已发送', plain: true });
      startCooldown();
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      sending.value = false;
    }
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid || !info.value) return;
      submitting.value = true;
      try {
        const res = await activateInvite({
          inviteCode: info.value.inviteCode,
          contactPhone: form.contactPhone,
          smsCode: form.smsCode,
          realName: form.realName,
          tenantName: form.tenantName,
          shortName: form.shortName || undefined
        });
        if (res?.accessToken) {
          setToken(res.accessToken, true);
          if (res.refreshToken) setRefreshToken(res.refreshToken, true);
          EleMessage.success({
            message: '激活成功，正在进入系统…',
            plain: true
          });
          await router.replace(LAYOUT_PATH);
        }
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        submitting.value = false;
      }
    });
  };
</script>

<style scoped>
  .invite-landing {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 24px;
  }
  .card {
    background: #fff;
    border-radius: 12px;
    padding: 36px 36px 28px;
    max-width: 480px;
    width: 100%;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.18);
  }
  .header {
    text-align: center;
    margin-bottom: 24px;
  }
  .header h1 {
    margin: 0 0 6px;
    font-size: 24px;
  }
  .subtitle {
    color: #999;
    margin: 0;
    font-size: 13px;
  }
  .loading {
    text-align: center;
    padding: 36px 0;
    color: #666;
  }
  .rotating {
    animation: rot 1s linear infinite;
  }
  @keyframes rot {
    to {
      transform: rotate(360deg);
    }
  }
  .error-state {
    text-align: center;
    padding: 24px 8px;
  }
  .error-state h2 {
    margin: 12px 0 8px;
  }
  .error-state p {
    color: #666;
    line-height: 1.6;
  }
  .invite-summary {
    background: #f7f9fc;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 16px;
    font-size: 13px;
  }
  .invite-summary .row {
    display: flex;
    margin: 4px 0;
  }
  .invite-summary .label {
    color: #999;
    width: 96px;
    flex-shrink: 0;
  }
  .invite-summary .value {
    color: #333;
    word-break: break-all;
  }
  .sms-row {
    display: flex;
    gap: 8px;
    width: 100%;
  }
  .sms-row > :first-child {
    flex: 1;
  }
  .submit-btn {
    width: 100%;
    margin-top: 8px;
  }
  .footer-tip {
    margin-top: 16px;
    color: #999;
    font-size: 12px;
    line-height: 1.6;
  }
</style>
