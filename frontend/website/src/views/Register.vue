<template>
  <div class="register-page">
    <!-- 左侧品牌区 -->
    <div class="register-brand">
      <div class="brand-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
        <div class="glow glow-2"></div>
      </div>
      <div class="brand-content">
        <div class="brand-header">
          <router-link
            to="/"
            class="register-back"
            aria-label="返回官网首页"
            title="返回官网"
          >
            <el-icon :size="16"><ArrowLeft /></el-icon>
          </router-link>
          <router-link to="/" class="brand-logo">
            <span class="logo-icon">Z</span>
            <span class="logo-text">智途</span>
          </router-link>
        </div>
        <h1>让每一台车、每一公里的利润都看得清楚</h1>
        <p class="brand-lead">
          免费注册，几分钟即可启用。我们帮轿运企业建立「利润确定性」——单车利润、线路盈亏、客户报价，有据可依。
        </p>
        <div class="brand-features">
          <div class="brand-feature-item">
            <span class="bf-check">✓</span>
            <span>快速开通，云端即用，无需本地部署</span>
          </div>
          <div class="brand-feature-item">
            <span class="bf-check">✓</span>
            <span>标准版 / 高级版按年计费，方案透明可选</span>
          </div>
          <div class="brand-feature-item">
            <span class="bf-check">✓</span>
            <span>企业独立数据库，数据安全可追溯，独立权限管控</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="register-form-area">
      <div class="form-container">
        <h2>企业注册</h2>
        <p class="form-subtitle">填写以下信息，立即创建您的企业账号</p>

        <!-- 推荐注册提示 -->
        <div v-if="referrerCode" class="referral-tip">
          <span class="referral-icon">🤝</span>
          来自企业推荐（推荐码：{{ referrerCode }}）
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          size="large"
          class="register-form"
          @submit.prevent="handleSubmit"
        >
          <el-form-item label="企业名称" prop="tenant_name">
            <el-input v-model="form.tenant_name" placeholder="请输入企业全称">
              <template #prefix>
                <el-icon class="input-prefix-icon"><OfficeBuilding /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="联系人" prop="contact_person">
            <el-input v-model="form.contact_person" placeholder="请输入联系人姓名">
              <template #prefix>
                <el-icon class="input-prefix-icon"><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="手机号" prop="contact_phone">
            <el-input
              v-model="form.contact_phone"
              placeholder="请输入手机号码"
              maxlength="11"
              @blur="onPhoneBlur"
              @input="onPhoneInput"
            >
              <template #prefix>
                <el-icon class="input-prefix-icon"><Phone /></el-icon>
              </template>
            </el-input>
            <el-alert
              v-if="phoneRegistered"
              type="warning"
              :closable="false"
              show-icon
              class="registered-alert"
            >
              <template #default>
                <span class="registered-alert-text">该手机号已注册，请前往客户端登录。</span>
                <el-button type="primary" link class="registered-alert-link" @click="goLogin">
                  立即登录
                </el-button>
              </template>
            </el-alert>
          </el-form-item>

          <el-form-item v-if="!phoneRegistered" label="短信验证码" prop="sms_code">
            <div class="sms-code-row">
              <el-input
                v-model="form.sms_code"
                placeholder="请输入6位验证码"
                maxlength="6"
                inputmode="numeric"
              />
              <el-button
                :disabled="phoneRegistered || smsCooldown > 0"
                @click="handleSendCode"
              >
                {{ smsCooldown > 0 ? `${smsCooldown}s` : '获取验证码' }}
              </el-button>
            </div>
            <p class="sms-sign-hint">
              验证码短信签名显示为「速通互联验证码」，请注意查收以此开头的短信。
            </p>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="submit-btn"
              :loading="loading"
              :disabled="phoneRegistered"
              @click="handleSubmit"
            >
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <p class="form-footer">
          注册即表示您同意 <a href="#">服务条款</a> 和 <a href="#">隐私政策</a>
        </p>

        <!-- 开户进度（不可关闭，直至成功或失败） -->
        <el-dialog
          v-model="showProgress"
          title="正在开通企业账号"
          width="460px"
          :show-close="false"
          :close-on-press-escape="false"
          :close-on-click-modal="false"
          class="progress-dialog"
        >
          <div class="progress-content">
            <p class="progress-hint">{{ progressMessage }}</p>
            <el-progress
              :percentage="Math.min(100, Math.max(0, progressPercent))"
              :stroke-width="10"
              striped
              striped-flow
            />
          </div>
        </el-dialog>

        <!-- 注册成功弹窗 -->
        <el-dialog
          v-model="showSuccess"
          title=""
          width="460px"
          :show-close="false"
          :close-on-click-modal="false"
          center
          class="success-dialog"
        >
          <div class="success-content">
            <div class="success-icon">✓</div>
            <h3>注册成功！</h3>
            <p>您的企业账户已创建成功，请使用以下信息登录客户端：</p>
            <div class="credential-box">
              <div class="credential-row">
                <span class="credential-label">登录账号</span>
                <span class="credential-value">{{ form.contact_phone }}</span>
              </div>
              <!-- 新用户：显示初始密码 -->
              <div v-if="!isExistingUser" class="credential-row">
                <span class="credential-label">初始密码</span>
                <span class="credential-value">123456</span>
              </div>
            </div>
            <!-- 不同用户类型的提示 -->
            <p v-if="isExistingUser" class="credential-tip credential-tip-info">
              该手机号已注册过账号，请使用已有密码直接登录
            </p>
            <p v-else class="credential-tip">首次登录后系统将要求您修改密码</p>
            <div class="success-actions">
              <el-button class="success-btn-outline" @click="goHome">返回首页</el-button>
              <el-button type="primary" class="success-btn" @click="goLogin">立即登录</el-button>
            </div>
          </div>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  OfficeBuilding,
  User,
  Phone,
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {
  registerTenant,
  getRegisterProgress,
  sendSmsCode,
  checkRegisterPhone,
} from '@/api'

const SMS_PURPOSE_REGISTER = 4

const route = useRoute()
const router = useRouter()

const clientLoginUrl = (import.meta.env.VITE_CLIENT_URL || 'http://localhost:5174') + '/login'

/** 从 URL 参数获取推荐码（如 /register?ref=1001） */
const referrerCode = ref<string | undefined>(
  (route.query.ref as string) || undefined
)

const formRef = ref<FormInstance>()
const loading = ref(false)
const showProgress = ref(false)
const progressMessage = ref('正在提交…')
const progressPercent = ref(0)
const showSuccess = ref(false)
const isExistingUser = ref(false)
const phoneRegistered = ref(false)
const smsCooldown = ref(0)
let smsCooldownTimer: ReturnType<typeof setInterval> | null = null

const POLL_INTERVAL_MS = 1500

const form = reactive({
  tenant_name: '',
  contact_person: '',
  contact_phone: '',
  sms_code: '',
})

const rules: FormRules = {
  tenant_name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' },
    { min: 2, max: 50, message: '企业名称长度 2-50 个字符', trigger: 'blur' },
  ],
  contact_person: [
    { required: true, message: '请输入联系人姓名', trigger: 'blur' },
  ],
  contact_phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号码',
      trigger: ['blur', 'change'],
    },
  ],
  sms_code: [
    { required: true, message: '请输入短信验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: ['blur', 'change'] },
  ],
}

function sleep(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms))
}

function onPhoneInput() {
  form.contact_phone = form.contact_phone.replace(/\D/g, '').slice(0, 11)
  phoneRegistered.value = false
}

async function onPhoneBlur() {
  const p = form.contact_phone.trim()
  if (!/^1[3-9]\d{9}$/.test(p)) {
    phoneRegistered.value = false
    return
  }
  try {
    const { registered } = await checkRegisterPhone(p)
    phoneRegistered.value = registered
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : '校验手机号失败'
    ElMessage.error(msg)
  }
}

function startSmsCooldown() {
  if (smsCooldownTimer) {
    clearInterval(smsCooldownTimer)
    smsCooldownTimer = null
  }
  smsCooldown.value = 60
  smsCooldownTimer = setInterval(() => {
    smsCooldown.value -= 1
    if (smsCooldown.value <= 0 && smsCooldownTimer) {
      clearInterval(smsCooldownTimer)
      smsCooldownTimer = null
    }
  }, 1000)
}

onUnmounted(() => {
  if (smsCooldownTimer) clearInterval(smsCooldownTimer)
})

async function handleSendCode() {
  if (phoneRegistered.value || !formRef.value) return
  try {
    await formRef.value.validateField('contact_phone')
  } catch {
    return
  }
  try {
    await sendSmsCode(form.contact_phone.trim(), SMS_PURPOSE_REGISTER)
    ElMessage.success('验证码已发送')
    startSmsCooldown()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : '发送失败'
    ElMessage.error(msg)
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  if (phoneRegistered.value) {
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  showProgress.value = true
  progressMessage.value = '正在提交…'
  progressPercent.value = 0
  try {
    const preCheck = await checkRegisterPhone(form.contact_phone.trim())
    if (preCheck.registered) {
      phoneRegistered.value = true
      return
    }

    const res = await registerTenant({
      tenant_name: form.tenant_name,
      contact_person: form.contact_person,
      contact_phone: form.contact_phone.trim(),
      sms_code: form.sms_code.trim(),
      referrer_code: referrerCode.value || undefined,
    })
    const payload = res?.data
    if (payload?.code !== 0) {
      ElMessage.error(payload?.message || '注册失败，请稍后重试')
      return
    }
    const taskId = payload?.data?.task_id as string | undefined
    if (!taskId) {
      ElMessage.error('注册响应异常，请稍后重试')
      return
    }

    progressMessage.value = '即将开始初始化企业基础数据…'
    const maxPolls = 800
    for (let poll = 0; poll < maxPolls; poll++) {
      const progRes = await getRegisterProgress(taskId)
      const prog = progRes?.data
      if (prog?.code !== 0) {
        ElMessage.error(prog?.message || '查询进度失败')
        return
      }
      const p = prog.data as {
        status: string
        message: string
        percent: number
        result?: { is_existing_user?: boolean }
        error_message?: string | null
      }
      progressMessage.value = p.message || '处理中…'
      progressPercent.value = typeof p.percent === 'number' ? p.percent : 0

      if (p.status === 'success' && p.result) {
        isExistingUser.value = p.result.is_existing_user === true
        showProgress.value = false
        showSuccess.value = true
        return
      }
      if (p.status === 'failed') {
        const err =
          p.error_message && p.error_message !== 'timeout'
            ? p.error_message
            : p.message || '注册失败，请稍后重试'
        ElMessage.error(err)
        return
      }
      await sleep(POLL_INTERVAL_MS)
    }
    ElMessage.error('注册处理超时，请稍后重试或联系客服')
  } catch (err: any) {
    const msg =
      err?.response?.data?.message ||
      err?.response?.data?.detail ||
      '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
    showProgress.value = false
  }
}

/** 跳转到客户端登录 */
function goLogin() {
  window.open(clientLoginUrl, '_blank')
}

/** 返回首页 */
function goHome() {
  router.push('/')
}
</script>

<style scoped lang="scss">
.register-page {
  display: flex;
  min-height: 100vh;
}

/* 左侧品牌区内返回（与 Logo 同行） */
.register-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: rgba(255, 255, 255, 0.92);
  text-decoration: none;
  transition: background 0.15s, border-color 0.15s, color 0.15s;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.35);
    color: #fff;
  }

  &:focus-visible {
    outline: 2px solid rgba(255, 255, 255, 0.85);
    outline-offset: 2px;
  }
}

/* ========== 左侧品牌区 ========== */
.register-brand {
  flex: 1 1 58%;
  min-width: 480px;
  position: relative;
  background: var(--gradient-hero);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.brand-bg {
  position: absolute;
  inset: 0;

  .grid-lines {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
  }

  .glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
  }

  .glow-1 {
    width: 300px;
    height: 300px;
    background: var(--color-primary);
    opacity: 0.3;
    top: -10%;
    right: -10%;
  }

  .glow-2 {
    width: 250px;
    height: 250px;
    background: var(--color-accent);
    opacity: 0.25;
    bottom: -10%;
    left: -10%;
  }
}

.brand-content {
  position: relative;
  z-index: 1;
  padding: 60px 48px;
  color: #fff;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;

  .logo-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    color: #fff;
    font-size: 16px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-text {
    font-size: 19px;
    font-weight: 700;
    color: #fff;
  }
}

.brand-content h1 {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.35;
  margin-bottom: 14px;
  letter-spacing: -0.02em;
}

.brand-lead {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.65;
  margin-bottom: 32px;
  max-width: 460px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.brand-feature-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.82);
}

.bf-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: #34d399;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

/* ========== 右侧表单区 ========== */
.register-form-area {
  flex: 1 1 42%;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 48px;
  background: var(--color-bg);
}

.form-container {
  width: 100%;
  max-width: 400px;

  h2 {
    font-size: 28px;
    font-weight: 800;
    color: var(--color-text);
    margin-bottom: 8px;
  }
}

.form-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin-bottom: 36px;
}

.registered-alert {
  margin-top: 10px;
  width: 100%;

  .registered-alert-text {
    margin-right: 8px;
  }

  .registered-alert-link {
    vertical-align: baseline;
    padding: 0;
    height: auto;
    font-weight: 600;
  }
}

.sms-code-row {
  display: flex;
  gap: 12px;
  width: 100%;
  align-items: center;

  .el-input {
    flex: 1;
    min-width: 0;
  }

  .el-button {
    flex-shrink: 0;
  }
}

.sms-sign-hint {
  margin: 8px 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--color-text-muted, #64748b);
}

.referral-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 24px;
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 10px;
  font-size: 14px;
  color: #16a34a;
  font-weight: 500;

  .referral-icon {
    font-size: 18px;
  }
}

.register-form {
  :deep(.el-form-item__label) {
    font-weight: 600;
    color: var(--color-text);
    font-size: 14px;
  }

  :deep(.el-input__wrapper) {
    border-radius: 10px;
    padding: 4px 12px;
  }

  .input-prefix-icon {
    font-size: 18px;
    color: var(--color-text-muted);
  }
}

.submit-btn {
  width: 100%;
  height: 48px !important;
  border-radius: 10px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
  border: none !important;
  transition: all 0.2s !important;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(29, 78, 216, 0.35) !important;
  }
}

.progress-dialog {
  :deep(.el-dialog__header) {
    padding-bottom: 8px;
  }
}

.progress-content {
  padding: 8px 0 4px;
}

.progress-hint {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0 0 20px;
  line-height: 1.5;
  min-height: 1.5em;
}

.form-footer {
  text-align: center;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 20px;

  a {
    color: var(--color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

/* ========== 成功弹窗 ========== */
.success-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.success-content h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 12px;
}

.success-content > p {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.credential-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px 24px;
  margin-bottom: 12px;
  text-align: left;
}

.credential-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;

  &:not(:last-child) {
    border-bottom: 1px solid #e2e8f0;
  }
}

.credential-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.credential-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  font-family: 'SF Mono', 'Menlo', monospace;
  letter-spacing: 0.5px;
}

.credential-tip {
  font-size: 13px;
  color: #f59e0b;
  margin-bottom: 24px;
}

.credential-tip-info {
  color: #3b82f6;
}

.success-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.success-btn {
  border-radius: 10px !important;
  padding: 10px 32px !important;
  font-weight: 600 !important;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
  border: none !important;
}

.success-btn-outline {
  border-radius: 10px !important;
  padding: 10px 32px !important;
  font-weight: 600 !important;
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .register-brand {
    flex: 1 1 50%;
    min-width: 400px;
  }

  .register-form-area {
    flex: 1 1 50%;
    padding: 40px 32px;
  }

  .form-container {
    max-width: 380px;
  }

  .brand-content {
    padding: 40px 32px;
  }

  .brand-content h1 {
    font-size: 22px;
  }

  .brand-lead {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .register-page {
    flex-direction: column;
  }

  .register-brand {
    flex: none;
    padding: 100px 24px 40px;
  }

  .brand-content {
    padding: 0;
    text-align: center;
  }

  .brand-header {
    justify-content: center;
    margin-bottom: 24px;
  }

  .brand-logo {
    justify-content: center;
  }

  .brand-features {
    align-items: center;
    text-align: left;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
  }

  .register-form-area {
    padding: 40px 24px;
  }
}
</style>
