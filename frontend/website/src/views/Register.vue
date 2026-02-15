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
        <router-link to="/" class="brand-logo">
          <span class="logo-icon">Z</span>
          <span class="logo-text">智途</span>
        </router-link>
        <h1>开启整车运输<br>数字化之旅</h1>
        <p>免费注册，即刻体验 AI 驱动的汽车物流管理平台</p>
        <div class="brand-features">
          <div class="brand-feature-item">
            <span class="bf-check">✓</span>
            <span>30秒快速注册，无需安装部署</span>
          </div>
          <div class="brand-feature-item">
            <span class="bf-check">✓</span>
            <span>免费版永久免费，随时可升级</span>
          </div>
          <div class="brand-feature-item">
            <span class="bf-check">✓</span>
            <span>银行级数据加密，安全无忧</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="register-form-area">
      <div class="form-container">
        <h2>企业注册</h2>
        <p class="form-subtitle">填写以下信息，立即创建您的企业账户</p>

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
            <el-input
              v-model="form.tenant_name"
              placeholder="请输入企业全称"
              prefix-icon="OfficeBuilding"
            />
          </el-form-item>

          <el-form-item label="联系人" prop="contact_person">
            <el-input
              v-model="form.contact_person"
              placeholder="请输入联系人姓名"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="手机号" prop="contact_phone">
            <el-input
              v-model="form.contact_phone"
              placeholder="请输入手机号码"
              prefix-icon="Phone"
              maxlength="11"
            />
          </el-form-item>

          <el-form-item label="邮箱（选填）" prop="contact_email">
            <el-input
              v-model="form.contact_email"
              placeholder="请输入电子邮箱"
              prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="submit-btn"
              :loading="loading"
              @click="handleSubmit"
            >
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <p class="form-footer">
          注册即表示您同意 <a href="#">服务条款</a> 和 <a href="#">隐私政策</a>
        </p>

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
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { registerTenant } from '@/api'

const route = useRoute()
const router = useRouter()

const clientLoginUrl = (import.meta.env.VITE_CLIENT_URL || 'http://localhost:5174') + '/login'

/** 从 URL 参数获取推荐码（如 /register?ref=1001） */
const referrerCode = ref<string | undefined>(
  (route.query.ref as string) || undefined
)

const formRef = ref<FormInstance>()
const loading = ref(false)
const showSuccess = ref(false)
const isExistingUser = ref(false)

const form = reactive({
  tenant_name: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
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
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' },
  ],
  contact_email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const res = await registerTenant({
      tenant_name: form.tenant_name,
      contact_person: form.contact_person,
      contact_phone: form.contact_phone,
      contact_email: form.contact_email || undefined,
      referrer_code: referrerCode.value || undefined,
    })
    // 检测后端返回的 is_existing_user 标记
    isExistingUser.value = res?.data?.data?.is_existing_user === true
    showSuccess.value = true
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
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

/* ========== 左侧品牌区 ========== */
.register-brand {
  flex: 0 0 480px;
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

.brand-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  margin-bottom: 48px;

  .logo-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    color: #fff;
    font-size: 18px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-text {
    font-size: 22px;
    font-weight: 700;
    color: #fff;
  }
}

.brand-content h1 {
  font-size: 36px;
  font-weight: 800;
  line-height: 1.3;
  margin-bottom: 16px;
}

.brand-content > p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.6;
  margin-bottom: 40px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.brand-feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.8);
}

.bf-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: #34d399;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ========== 右侧表单区 ========== */
.register-form-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--color-bg);
}

.form-container {
  width: 100%;
  max-width: 460px;

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
    flex: 0 0 360px;
  }

  .brand-content {
    padding: 40px 32px;
  }

  .brand-content h1 {
    font-size: 28px;
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

  .brand-logo {
    justify-content: center;
    margin-bottom: 32px;
  }

  .brand-features {
    align-items: center;
  }

  .register-form-area {
    padding: 40px 24px;
  }
}
</style>
