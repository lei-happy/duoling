<template>
  <div class="login-page">
    <!-- ================= 左侧：今日运营看板 ================= -->
    <MotionConfig :reduced-motion="'user'">
      <section class="brand-panel">
        <div class="brand-grid" aria-hidden="true"></div>

        <!-- 品牌：固定左上角，对齐常见产品官网位置 -->
        <Motion
          as="div"
          class="brand-logo"
          :initial="{ opacity: 0, y: -12 }"
          :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.5, ease: EASE }"
        >
          <img class="brand-logo-img" src="@/assets/logo.svg" alt="logo" />
          <div class="brand-logo-text">
            <span class="brand-logo-name">{{ PROJECT_NAME }}</span>
            <span class="brand-logo-sub">数字化经营操作系统</span>
          </div>
        </Motion>

        <div class="brand-content">
          <div class="brand-hero">
            <Motion
              as="h1"
              class="brand-title"
              :initial="{ opacity: 0, y: 18 }"
              :animate="{ opacity: 1, y: 0 }"
              :transition="{ duration: 0.6, delay: 0.08, ease: EASE }"
            >
              把运输经营装进一块看板，<br />
              让每天的决策<span class="ink-underline">有数可依</span>。
            </Motion>
            <Motion
              as="p"
              class="brand-desc"
              :initial="{ opacity: 0, y: 18 }"
              :animate="{ opacity: 1, y: 0 }"
              :transition="{ duration: 0.6, delay: 0.16, ease: EASE }"
            >
              打通计划、配载、调度、在途到回单结算，收入、成本、利润与时效实时归集，异常自动预警。
            </Motion>
          </div>

          <!-- 运输链路（业务全程在线） -->
          <Motion
            as="div"
            class="chain"
            :initial="{ opacity: 0, y: 18 }"
            :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: 0.6, delay: 0.28, ease: EASE }"
          >
            <div class="block-head">
              <span class="block-title">运输链路</span>
              <span class="block-note">全流程在线协同</span>
            </div>
            <div class="chain-track">
              <span class="chain-rail"></span>
              <span
                class="chain-rail-done"
                :class="{ 'no-anim': chainInstant }"
                :style="{ width: chainDoneWidth }"
              ></span>
              <!-- 与节点联动的流转光点 -->
              <span
                v-show="chainFlowVisible"
                class="chain-flow"
                :style="{ left: chainFlowLeft }"
              ></span>
              <div class="chain-stops">
                <Motion
                  v-for="(stop, i) in stops"
                  :key="stop"
                  as="div"
                  class="chain-stop"
                  :class="{
                    done: i < activeStop,
                    active: i === activeStop
                  }"
                  :initial="{ opacity: 0, y: 8 }"
                  :animate="{ opacity: 1, y: 0 }"
                  :transition="{
                    duration: 0.34,
                    delay: 0.5 + i * 0.09,
                    ease: EASE
                  }"
                >
                  <span class="stop-dot"></span>
                  <span class="stop-label">{{ stop }}</span>
                </Motion>
              </div>
            </div>
          </Motion>

          <!-- 今日经营（经营实时透明） -->
          <Motion
            as="div"
            class="board"
            :initial="{ opacity: 0, y: 18 }"
            :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: 0.6, delay: 0.36, ease: EASE }"
          >
            <div class="block-head">
              <span class="block-title">今日经营</span>
              <span class="live"><i class="live-dot"></i>实时更新</span>
            </div>
            <div class="board-grid">
              <div v-for="(m, i) in metrics" :key="m.label" class="metric">
                <div class="metric-label">{{ m.label }}</div>
                <div class="metric-value">
                  <span
                    :ref="(el) => setMetricRef(el, i)"
                    class="metric-num"
                    >{{ m.value }}</span
                  ><span class="metric-unit">{{ m.unit }}</span>
                </div>
                <div class="metric-delta" :class="m.trend">
                  <el-icon><CaretTop /></el-icon>{{ m.delta }}
                </div>
              </div>
            </div>
          </Motion>

          <!-- AI 建议轮播（决策有据可依） -->
          <Motion
            as="div"
            class="alert"
            :initial="{ opacity: 0, y: 16 }"
            :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: 0.55, delay: 0.46, ease: EASE }"
          >
            <span class="alert-ai">AI</span>
            <transition name="alert-swap" mode="out-in">
              <div class="alert-swap-inner" :key="alertIndex">
                <div class="alert-body">
                  <span class="alert-text">
                    <b>{{ currentAlert.lead }}</b>{{ currentAlert.text }}
                  </span>
                  <span class="alert-sub">{{ currentAlert.sub }}</span>
                </div>
                <span class="alert-tag" :class="currentAlert.level">
                  {{ currentAlert.tag }}
                </span>
              </div>
            </transition>
          </Motion>
        </div>
      </section>
    </MotionConfig>

    <!-- ================= 右侧登录表单 ================= -->
    <section class="form-panel">
      <div class="form-wrapper">
        <div class="form-head">
          <h2 class="form-head-title">欢迎登录</h2>
        </div>

        <!-- 登录方式 Tab -->
        <div class="login-tabs">
          <span
            :class="['login-tab', { active: loginMode === 'password' }]"
            @click="loginMode = 'password'"
            >密码登录</span
          >
          <span
            :class="['login-tab', { active: loginMode === 'sms' }]"
            @click="loginMode = 'sms'"
            >验证码登录</span
          >
        </div>

        <div class="form-body">
          <transition name="slide-fade" mode="out-in">
          <!-- 密码登录表单 -->
          <el-form
            v-if="loginMode === 'password'"
            key="password"
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
                :prefix-icon="MobileOutlined"
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
              <div
                style="
                  display: flex;
                  justify-content: space-between;
                  width: 100%;
                "
              >
                <el-checkbox v-model="form.remember">
                  {{ t('login.remember') }}
                </el-checkbox>
                <a
                  class="forgot-pwd-link"
                  @click.prevent="showForgotPwdDialog = true"
                >
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
            key="sms"
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
                :prefix-icon="MobileOutlined"
              />
            </el-form-item>
            <el-form-item prop="code">
              <div style="display: flex; gap: 10px; width: 100%">
                <el-input
                  v-model="smsForm.code"
                  placeholder="请输入验证码"
                  :prefix-icon="MessageOutlined"
                  style="flex: 1"
                />
                <el-button
                  size="large"
                  :disabled="smsCooldown > 0"
                  @click="handleSendCode(1)"
                >
                  {{ smsCooldown > 0 ? `${smsCooldown}s` : '获取验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <!-- 占位行：与密码登录的"记住密码"行等高，保证切换时按钮不位移 -->
            <el-form-item class="form-row-placeholder" />
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
          </transition>
        </div>

        <div class="form-safe-tip">
          <el-icon><Lock /></el-icon>
          <span>安全、稳定、实时的企业经营平台</span>
        </div>
      </div>

      <PageFooter class="form-footer" />
    </section>

    <!-- 企业选择弹窗 -->
    <el-dialog
      v-model="showTenantDialog"
      title="请选择要进入的企业"
      width="420px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      center
    >
      <div class="tenant-list">
        <div
          v-for="item in tenantList"
          :key="item.tenantCode"
          class="tenant-item"
          @click="selectTenant(item.tenantCode)"
        >
          <div class="tenant-item-icon">
            <el-icon :size="20"><OfficeBuilding /></el-icon>
          </div>
          <div class="tenant-item-info">
            <div class="tenant-item-name">{{ item.tenantName }}</div>
            <div class="tenant-item-code">企业编码：{{ item.tenantCode }}</div>
          </div>
          <el-icon class="tenant-item-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-dialog>

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
            <el-input
              v-model="forgotForm.code"
              placeholder="请输入验证码"
              style="flex: 1"
            />
            <el-button
              :disabled="forgotCooldown > 0"
              @click="handleSendForgotCode"
            >
              {{ forgotCooldown > 0 ? `${forgotCooldown}s` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            show-password
            v-model="forgotForm.newPassword"
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            show-password
            v-model="forgotForm.confirmPassword"
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotPwdDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="forgotLoading"
          @click="submitForgotPwd"
        >
          确认重置
        </el-button>
      </template>
    </el-dialog>

    <!-- 强制修改密码弹窗 -->
    <el-dialog
      v-model="showChangePwdDialog"
      title="首次登录，请修改密码"
      width="420px"
      :show-close="false"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      center
    >
      <el-form
        ref="pwdFormRef"
        :model="pwdForm"
        :rules="pwdRules"
        label-width="90px"
        @submit.prevent=""
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            show-password
            v-model="pwdForm.oldPassword"
            placeholder="请输入当前密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            show-password
            v-model="pwdForm.newPassword"
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            show-password
            v-model="pwdForm.confirmPassword"
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button
          type="primary"
          :loading="changePwdLoading"
          style="width: 100%"
          @click="submitChangePwd"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import {
    OfficeBuilding,
    ArrowRight,
    CaretTop,
    Lock
  } from '@element-plus/icons-vue';
  import { Motion, MotionConfig } from 'motion-v';
  import { CountUp } from 'countup.js';
  import { EleMessage } from 'ele-admin-plus';
  import {
    MobileOutlined,
    LockOutlined,
    MessageOutlined
  } from '@/components/icons';
  import PageFooter from '@/layout/components/page-footer.vue';
  import { useLogin } from '@/utils/use-login';
  import { sendSmsCode, changePassword, resetPasswordBySms } from '@/api/login';
  import type { TenantOption } from '@/api/login/model';
  import { useI18n } from 'vue-i18n';
  const PROJECT_NAME = import.meta.env.VITE_APP_NAME;

  /** 动画统一缓动曲线 */
  const EASE: [number, number, number, number] = [0.22, 1, 0.36, 1];

  const prefersReduce = () =>
    !!window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;

  const timers: number[] = [];

  // ============================================================
  // 区域一：运输链路（节点与流转光点联动循环）
  // ============================================================
  const stops = ['计划', '配载', '调度', '在途', '回单', '结算'];
  // -1 = 全部未开始；0..n-1 = 当前激活节点；n = 全部完成
  const activeStop = ref(-1);
  // 节点圆点直径 12px，轨道两端各内缩 6px 与首/末节点圆心对齐
  const chainFrac = computed(() => {
    const clamped = Math.min(Math.max(activeStop.value, 0), stops.length - 1);
    return clamped / (stops.length - 1);
  });
  const chainDoneWidth = computed(() =>
    activeStop.value < 0 ? '0px' : `calc(${chainFrac.value} * (100% - 12px))`
  );
  const chainFlowLeft = computed(
    () => `calc(6px + ${chainFrac.value} * (100% - 12px))`
  );
  const chainFlowVisible = computed(
    () => activeStop.value >= 0 && activeStop.value <= stops.length - 1
  );
  // 重置时关闭过渡，避免进度条“退回”动画
  const chainInstant = ref(false);

  const startChainLoop = () => {
    if (prefersReduce()) {
      activeStop.value = 3;
      return;
    }
    const timer = window.setInterval(() => {
      if (activeStop.value >= stops.length) {
        // 全部完成后：瞬间置灰（无退回动画），再从左侧开始新一轮
        chainInstant.value = true;
        activeStop.value = -1;
        window.setTimeout(() => {
          chainInstant.value = false;
        }, 60);
      } else {
        activeStop.value += 1;
      }
    }, 3000);
    timers.push(timer);
  };

  // ============================================================
  // 区域二：今日经营（数字翻牌 + 定时随机向上跳动）
  // ============================================================
  interface Metric {
    label: string;
    value: string;
    unit: string;
    delta: string;
    trend: 'up' | 'down';
    decimals: number;
    step: [number, number];
    max?: number;
  }
  const metrics: Metric[] = [
    {
      label: '在途运单',
      value: '128',
      unit: '单',
      delta: '12',
      trend: 'up',
      decimals: 0,
      step: [1, 4]
    },
    {
      label: '准时率',
      value: '98.6',
      unit: '%',
      delta: '0.4',
      trend: 'up',
      decimals: 1,
      step: [0.1, 0.4],
      max: 99.9
    },
    {
      label: '今日签收',
      value: '342',
      unit: '单',
      delta: '37',
      trend: 'up',
      decimals: 0,
      step: [3, 12]
    },
    {
      label: '今日收入',
      value: '86.4',
      unit: '万',
      delta: '8.2%',
      trend: 'up',
      decimals: 1,
      step: [0.3, 1.8]
    }
  ];

  const metricRefs: (HTMLElement | null)[] = [];
  const counters: (CountUp | null)[] = [];
  const currentVals = metrics.map((m) => parseFloat(m.value));
  const setMetricRef = (el: unknown, i: number) => {
    metricRefs[i] = (el as HTMLElement) ?? null;
  };

  const rand = (min: number, max: number) => min + Math.random() * (max - min);
  const roundTo = (n: number, d: number) =>
    Math.round(n * 10 ** d) / 10 ** d;

  const bumpMetric = (i: number) => {
    const counter = counters[i];
    const m = metrics[i];
    if (!counter) return;
    let next = currentVals[i] + rand(m.step[0], m.step[1]);
    if (m.max != null) next = Math.min(next, m.max);
    next = roundTo(next, m.decimals);
    if (next === currentVals[i]) return;
    currentVals[i] = next;
    counter.update(next);
  };

  const scheduleMetricLoop = () => {
    const timer = window.setTimeout(
      () => {
        // 随机挑选 1~4 个指标向上跳动，整体向好
        let changed = false;
        metrics.forEach((_, i) => {
          if (Math.random() < 0.6) {
            bumpMetric(i);
            changed = true;
          }
        });
        if (!changed) bumpMetric(Math.floor(Math.random() * metrics.length));
        scheduleMetricLoop();
      },
      rand(2600, 5200)
    );
    timers.push(timer);
  };

  const startMetrics = () => {
    const reduce = prefersReduce();
    metrics.forEach((m, i) => {
      const el = metricRefs[i];
      if (!el) return;
      if (reduce) {
        el.textContent = m.value;
        counters[i] = null;
        return;
      }
      const counter = new CountUp(el, parseFloat(m.value), {
        startVal: 0,
        decimalPlaces: m.decimals,
        duration: 1.6,
        useEasing: true,
        separator: ''
      });
      counters[i] = counter;
      window.setTimeout(() => counter.start(), 480 + i * 90);
    });
    if (!reduce) scheduleMetricLoop();
  };

  // ============================================================
  // 区域三：AI 建议轮播
  // ============================================================
  interface AlertItem {
    lead: string;
    text: string;
    sub: string;
    tag: string;
    level: 'warn' | 'info' | 'good';
  }
  const alerts: AlertItem[] = [
    {
      lead: '3 单',
      text: '临近时效，AI 建议优先调度就近运力',
      sub: '异常预警 · 决策不遗漏',
      tag: '待处理',
      level: 'warn'
    },
    {
      lead: '2 条线路',
      text: '运费高于区域均值，AI 建议复核报价',
      sub: '成本优化 · 守住利润',
      tag: '可优化',
      level: 'info'
    },
    {
      lead: '明日运量',
      text: '预计上涨 18%，AI 建议提前锁定运力',
      sub: '趋势预测 · 提前决策',
      tag: '预测',
      level: 'good'
    },
    {
      lead: '1 家客户',
      text: '回款周期延长，AI 建议重点跟进应收',
      sub: '经营透明 · 现金无忧',
      tag: '提醒',
      level: 'info'
    }
  ];
  const alertIndex = ref(0);
  const currentAlert = computed(() => alerts[alertIndex.value]);

  const startAlertLoop = () => {
    if (prefersReduce()) return;
    const timer = window.setInterval(() => {
      alertIndex.value = (alertIndex.value + 1) % alerts.length;
    }, 4200);
    timers.push(timer);
  };

  onMounted(() => {
    startChainLoop();
    startMetrics();
    startAlertLoop();
  });

  onBeforeUnmount(() => {
    timers.forEach((t) => {
      window.clearInterval(t);
      window.clearTimeout(t);
    });
  });

  const { login, smsLogin, checkLogin, redirectAfterLogin } = useLogin();
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
      {
        required: true,
        message: '请输入手机号',
        type: 'string',
        trigger: 'blur'
      },
      {
        pattern: /^1[3-9]\d{9}$/,
        message: '请输入正确的手机号',
        trigger: 'blur'
      }
    ],
    password: [
      {
        required: true,
        message: t('login.password'),
        type: 'string',
        trigger: 'blur'
      }
    ]
  }));

  const submit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      login(form)
        .then((result) => {
          loading.value = false;
          if (result.needSelectTenant && result.tenants?.length) {
            tenantList.value = result.tenants;
            showTenantDialog.value = true;
            pendingLoginMode.value = 'password';
          } else if (result.forceChangePwd) {
            showChangePwdDialog.value = true;
          }
        })
        .catch((e: Error) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  // ============================================================
  // 验证码登录
  // ============================================================
  const smsFormRef = ref<FormInstance | null>(null);
  const smsForm = reactive({ phone: '', code: '' });
  const smsRules = computed<FormRules>(() => ({
    phone: [
      {
        required: true,
        message: '请输入手机号',
        type: 'string',
        trigger: 'blur'
      },
      {
        pattern: /^1[3-9]\d{9}$/,
        message: '请输入正确的手机号',
        trigger: 'blur'
      }
    ],
    code: [
      {
        required: true,
        message: '请输入验证码',
        type: 'string',
        trigger: 'blur'
      },
      { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
    ]
  }));

  const smsCooldown = ref(0);

  const startCooldown = (target: typeof smsCooldown) => {
    target.value = 60;
    const timer = setInterval(() => {
      target.value--;
      if (target.value <= 0) clearInterval(timer);
    }, 1000);
    return timer;
  };

  const handleSendCode = async (purpose: number) => {
    try {
      await smsFormRef.value?.validateField('phone');
    } catch {
      return;
    }
    try {
      await sendSmsCode(smsForm.phone, purpose);
      EleMessage.success({ message: '验证码已发送', plain: true });
      startCooldown(smsCooldown);
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const submitSms = () => {
    smsFormRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      smsLogin(smsForm.phone, smsForm.code, undefined, true)
        .then((result) => {
          loading.value = false;
          if (result.needSelectTenant && result.tenants?.length) {
            tenantList.value = result.tenants;
            showTenantDialog.value = true;
            pendingLoginMode.value = 'sms';
          } else if (result.forceChangePwd) {
            showChangePwdDialog.value = true;
          }
        })
        .catch((e: Error) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  // ============================================================
  // 企业选择
  // ============================================================
  const showTenantDialog = ref(false);
  const tenantList = ref<TenantOption[]>([]);
  const pendingLoginMode = ref<'password' | 'sms'>('password');

  const selectTenant = async (tenantCode: string) => {
    showTenantDialog.value = false;
    loading.value = true;
    try {
      let result;
      if (pendingLoginMode.value === 'sms') {
        result = await smsLogin(smsForm.phone, smsForm.code, tenantCode, true);
      } else {
        result = await login({
          phone: form.phone,
          password: form.password,
          tenant_code: tenantCode,
          remember: form.remember
        });
      }
      if (result.forceChangePwd) {
        showChangePwdDialog.value = true;
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  // ============================================================
  // 强制修改密码
  // ============================================================
  const showChangePwdDialog = ref(false);
  const changePwdLoading = ref(false);
  const pwdFormRef = ref<FormInstance | null>(null);

  const pwdForm = reactive({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const pwdRules = computed<FormRules>(() => ({
    oldPassword: [
      { required: true, message: '请输入当前密码', trigger: 'blur' }
    ],
    newPassword: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: '请再次输入新密码', trigger: 'blur' },
      {
        validator: (_rule: any, value: string, callback: any) => {
          if (value !== pwdForm.newPassword) {
            callback(new Error('两次输入的密码不一致'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ]
  }));

  const submitChangePwd = () => {
    pwdFormRef.value?.validate?.((valid) => {
      if (!valid) return;
      changePwdLoading.value = true;
      changePassword({
        oldPassword: pwdForm.oldPassword,
        newPassword: pwdForm.newPassword
      })
        .then(() => {
          changePwdLoading.value = false;
          showChangePwdDialog.value = false;
          EleMessage.success({ message: '密码修改成功', plain: true });
          redirectAfterLogin();
        })
        .catch((e: Error) => {
          changePwdLoading.value = false;
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
    phone: '',
    code: '',
    newPassword: '',
    confirmPassword: ''
  });

  const forgotRules = computed<FormRules>(() => ({
    phone: [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      {
        pattern: /^1[3-9]\d{9}$/,
        message: '请输入正确的手机号',
        trigger: 'blur'
      }
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
    try {
      await forgotFormRef.value?.validateField('phone');
    } catch {
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
      resetPasswordBySms(
        forgotForm.phone,
        forgotForm.code,
        forgotForm.newPassword
      )
        .then(() => {
          forgotLoading.value = false;
          showForgotPwdDialog.value = false;
          EleMessage.success({
            message: '密码重置成功，请使用新密码登录',
            plain: true
          });
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
  .login-page {
    height: 100vh;
    height: 100dvh;
    display: flex;
    box-sizing: border-box;
    overflow: hidden;
    background: #fff;

    /* 设计 Token —— 品牌主色 #0065FF，重置 Element Plus 主色 */
    --brand: #0065ff;
    --brand-strong: #0052cc;
    --ink: #16211d;
    --muted: #5b665f;
    --line: #e6eae5;
    --el-color-primary: #0065ff;
    --el-color-primary-dark-2: #0052cc;
    --el-color-primary-light-3: #4d94ff;
    --el-color-primary-light-5: #80b3ff;
    --el-color-primary-light-7: #b3d1ff;
    --el-color-primary-light-8: #cce0ff;
    --el-color-primary-light-9: #e6f0ff;
  }

  /* ============ 左侧：今日运营看板 ============ */
  .brand-panel {
    position: relative;
    flex: 1 1 54%;
    min-width: 0;
    height: 100%;
    overflow: hidden;
    display: flex;
    align-items: center;
    color: #fff;
    background:
      radial-gradient(
        120% 90% at 12% 6%,
        rgba(255, 255, 255, 0.16),
        transparent 55%
      ),
      linear-gradient(155deg, #0a4bc9 0%, #0065ff 52%, #2a7bff 100%);
  }

  /* 极淡坐标网格：暗示「看板 / 图纸」的秩序，非发光装饰 */
  .brand-grid {
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.07) 1px, transparent 1px);
    background-size: 40px 40px;
    -webkit-mask-image: linear-gradient(115deg, #000 28%, transparent 92%);
    mask-image: linear-gradient(115deg, #000 28%, transparent 92%);
  }

  .brand-content {
    position: relative;
    z-index: 1;
    width: min(780px, 100%);
    height: 100%;
    margin: 0 auto;
    padding: clamp(64px, 9vh, 96px) clamp(40px, 5.5vw, 96px)
      clamp(30px, 5.5vh, 66px);
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: clamp(18px, 2.8vh, 34px);
  }

  .brand-logo {
    position: absolute;
    top: clamp(22px, 3.2vh, 36px);
    left: clamp(28px, 3.2vw, 48px);
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 11px;
  }

  .brand-logo-img {
    width: 34px;
    height: 34px;
    filter: brightness(0) invert(1);
  }

  .brand-logo-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
    line-height: 1.2;
  }

  .brand-logo-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.3px;
  }

  .brand-logo-sub {
    font-size: 11px;
    letter-spacing: 2px;
    color: rgba(255, 255, 255, 0.6);
  }

  .brand-hero {
    margin: 0;
  }

  .brand-title {
    margin: 0 0 14px;
    font-size: clamp(24px, 2.2vw, 34px);
    font-weight: 700;
    line-height: 1.45;
    letter-spacing: 0.3px;
    color: #fff;
  }

  /* 记忆点：亮色墨线下划，强调「有数可依」 */
  .ink-underline {
    position: relative;
    white-space: nowrap;
    color: #aecdff;
    z-index: 0;
  }

  .ink-underline::after {
    content: '';
    position: absolute;
    left: -2px;
    right: -2px;
    bottom: 3px;
    height: 8px;
    z-index: -1;
    background: rgba(174, 205, 255, 0.28);
    border-radius: 2px;
  }

  .brand-desc {
    margin: 0;
    max-width: 36em;
    font-size: 14px;
    line-height: 1.85;
    color: rgba(255, 255, 255, 0.72);
  }

  /* 区块小标题 */
  .block-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 14px;
  }

  .block-title {
    font-size: 13px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.92);
    letter-spacing: 0.5px;
  }

  .block-note {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.55);
  }

  .live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.85);
  }

  .live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #8fd0ff;
    animation: live-pulse 2.4s ease-out infinite;
  }

  /* ---- 运输链路（业务全程在线） ---- */
  .chain-track {
    position: relative;
    padding: 3px 0 24px;
  }

  .chain-rail,
  .chain-rail-done {
    position: absolute;
    top: 9px;
    height: 2px;
    border-radius: 2px;
  }

  .chain-rail {
    left: 6px;
    right: 6px;
    background: rgba(255, 255, 255, 0.24);
  }

  .chain-rail-done {
    left: 6px;
    width: 0;
    background: #fff;
    transition: width 1.8s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .chain-rail-done.no-anim {
    transition: none;
  }

  /* 与节点联动的流转光点：飞到当前激活节点 */
  .chain-flow {
    position: absolute;
    top: 4px;
    z-index: 3;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #fff;
    transform: translateX(-50%);
    box-shadow:
      0 0 0 4px rgba(255, 255, 255, 0.22),
      0 0 12px rgba(255, 255, 255, 0.65);
    transition: left 1.8s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .chain-stops {
    position: relative;
    z-index: 1;
    display: flex;
    justify-content: space-between;
  }

  .chain-stop {
    position: relative;
    flex: 0 0 12px;
    width: 12px;
    display: flex;
    justify-content: center;
  }

  .stop-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    box-sizing: border-box;
    background: transparent;
    border: 2px solid rgba(255, 255, 255, 0.4);
    transition:
      background 0.4s ease,
      border-color 0.4s ease,
      box-shadow 0.4s ease;
  }

  .stop-label {
    position: absolute;
    top: 21px;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    transition:
      color 0.4s ease,
      font-weight 0.4s ease;
  }

  .chain-stop.done .stop-dot {
    background: #fff;
    border-color: #fff;
  }

  .chain-stop.active .stop-dot {
    background: rgba(255, 255, 255, 0.2);
    border-color: #fff;
    box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.22);
  }

  .stop-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.55);
  }

  .chain-stop.done .stop-label {
    color: rgba(255, 255, 255, 0.8);
  }

  .chain-stop.active .stop-label {
    color: #fff;
    font-weight: 600;
  }

  /* ---- 今日经营看板（经营实时透明） ---- */
  .board {
    padding: 17px 20px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 14px;
    box-shadow: 0 18px 36px -24px rgba(0, 20, 60, 0.6);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }

  .board-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
  }

  .metric {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-right: 12px;
    border-right: 1px solid rgba(255, 255, 255, 0.14);
  }

  .metric:last-child {
    padding-right: 0;
    border-right: none;
  }

  .metric-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }

  .metric-value {
    font-family:
      'DIN Alternate', 'Roboto Mono', ui-monospace, SFMono-Regular, Menlo,
      Consolas, monospace;
    font-size: clamp(20px, 1.7vw, 25px);
    font-weight: 700;
    line-height: 1;
    color: #fff;
    font-variant-numeric: tabular-nums;
  }

  .metric-unit {
    margin-left: 2px;
    font-size: 12px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.55);
  }

  .metric-delta {
    display: inline-flex;
    align-items: center;
    gap: 1px;
    font-size: 12px;
    font-weight: 600;

    .el-icon {
      font-size: 12px;
    }

    &.up {
      color: #6ee7b0;
    }

    &.down {
      color: #ffb267;

      .el-icon {
        transform: rotate(180deg);
      }
    }
  }

  /* ---- AI 建议轮播（决策有据可依） ---- */
  .alert {
    position: relative;
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: 62px;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    overflow: hidden;
    perspective: 600px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }

  /* AI 徽标：多彩渐变炫光 */
  .alert-ai {
    position: relative;
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #fff;
    border-radius: 10px;
    background: linear-gradient(
      120deg,
      #4f6bff,
      #8a5cff,
      #ff5cc8,
      #ff8a4c,
      #4f6bff
    );
    background-size: 300% 300%;
    animation: ai-glow 6s ease infinite;
  }

  @keyframes ai-glow {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }

  .alert-swap-inner {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    transform-origin: center;
  }

  .alert-body {
    flex: 1;
    min-width: 0;
  }

  .alert-text {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.92);

    b {
      color: #fff;
      font-weight: 700;
    }
  }

  .alert-sub {
    display: block;
    margin-top: 2px;
    font-size: 11.5px;
    color: rgba(255, 255, 255, 0.6);
  }

  .alert-tag {
    flex-shrink: 0;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 999px;
    white-space: nowrap;
    color: #dbe8ff;
    background: rgba(255, 255, 255, 0.16);

    &.warn {
      color: #ffd9a8;
      background: rgba(255, 168, 74, 0.22);
    }

    &.good {
      color: #a9edcb;
      background: rgba(80, 210, 150, 0.22);
    }
  }

  /* AI 建议翻转切换 */
  .alert-swap-enter-active,
  .alert-swap-leave-active {
    transition:
      opacity 0.4s ease,
      transform 0.45s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .alert-swap-enter-from {
    opacity: 0;
    transform: translateY(9px) rotateX(-32deg);
  }

  .alert-swap-leave-to {
    opacity: 0;
    transform: translateY(-9px) rotateX(32deg);
  }

  /* ============ 右侧表单面板 ============ */
  .form-panel {
    flex: 1 1 44%;
    min-width: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    box-sizing: border-box;
    position: relative;

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

  .form-wrapper {
    width: 100%;
    max-width: 380px;
    margin: auto;
  }

  .form-head {
    margin-bottom: 34px;
  }

  .form-head-title {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
  }

  .form-body {
    min-height: 244px;
  }

  .form-row-placeholder {
    margin-bottom: 18px;

    :deep(.el-form-item__content) {
      min-height: 24px;
    }
  }

  .form-safe-tip {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin-top: 4px;
    font-size: 12.5px;
    color: #94a3b8;
  }

  .form-footer {
    position: absolute;
    left: 0;
    bottom: 18px;
    width: 100%;
    padding: 0 20px;
    box-sizing: border-box;
  }

  .login-tabs {
    display: flex;
    align-items: baseline;
    gap: 24px;
    margin-bottom: 28px;
  }

  .login-tab {
    position: relative;
    font-size: 17px;
    line-height: 1;
    padding: 0 0 10px 0;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);

    &.active {
      color: #0f172a;
      font-size: 20px;
      font-weight: 500;

      &::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: -4px;
        width: 100%;
        height: 3px;
        border-radius: 2px;
        background: var(--brand);
        transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
      }
    }

    &:hover {
      color: #0f172a;
    }
  }

  @keyframes live-pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(0, 101, 255, 0.4);
    }
    70%,
    100% {
      box-shadow: 0 0 0 6px rgba(0, 101, 255, 0);
    }
  }

  /* 尊重系统「减少动态效果」偏好 */
  @media (prefers-reduced-motion: reduce) {
    .live-dot,
    .alert-ai {
      animation: none !important;
    }

    .chain-flow,
    .chain-rail-done {
      transition: none !important;
    }

    .alert-swap-enter-active,
    .alert-swap-leave-active {
      transition: none !important;
    }
  }

  .slide-fade-enter-active {
    transition: all 0.3s ease-out;
  }

  .slide-fade-leave-active {
    transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
  }

  .slide-fade-enter-from {
    transform: translateX(20px);
    opacity: 0;
  }

  .slide-fade-leave-to {
    transform: translateX(-20px);
    opacity: 0;
  }

  .forgot-pwd-link {
    font-size: 13px;
    color: var(--brand);
    cursor: pointer;
    text-decoration: none;
    line-height: 32px;

    &:hover {
      text-decoration: underline;
    }

  }

  .tenant-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .tenant-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #0065ff;
      background: rgba(0, 101, 255, 0.04);
    }
  }

  .tenant-item-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: #e6f0ff;
    color: #0065ff;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .tenant-item-info {
    flex: 1;
    min-width: 0;
  }

  .tenant-item-name {
    font-size: 15px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2px;
  }

  .tenant-item-code {
    font-size: 13px;
    color: #94a3b8;
  }

  .tenant-item-arrow {
    color: #cbd5e1;
    font-size: 16px;
    flex-shrink: 0;
  }

  /* 超宽屏：内容区再放宽，避免大片留白 */
  @media screen and (min-width: 1440px) {
    .brand-content {
      width: min(880px, 100%);
      padding-left: clamp(56px, 6vw, 112px);
      padding-right: clamp(56px, 6vw, 112px);
    }
  }

  /* 中等屏幕：收窄看板面板 */
  @media screen and (max-width: 1180px) {
    .brand-content {
      padding: clamp(56px, 8vh, 80px) clamp(28px, 3.6vw, 52px)
        clamp(28px, 5vh, 52px);
    }

    .brand-logo {
      left: clamp(24px, 3vw, 36px);
    }

    .form-panel {
      flex-basis: 42%;
    }
  }

  /* 矮屏：压缩说明，避免出现纵向滚动 */
  @media screen and (max-height: 720px) {
    .brand-desc {
      display: none;
    }

    .metric-value {
      font-size: 21px;
    }
  }

  /* 小屏 / 移动端：隐藏看板面板，仅保留表单 */
  @media screen and (max-width: 900px) {
    .brand-panel {
      display: none;
    }

    .form-panel {
      flex: 1 1 100%;
    }
  }

  /* 窄面板：经营指标改为 2×2，链路文字缩小 */
  @media screen and (max-width: 1080px) {
    .board-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 14px 6px;
    }

    .metric:nth-child(2) {
      border-right: none;
      padding-right: 0;
    }
  }

  @media screen and (max-width: 480px) {
    .form-panel {
      padding: 24px 20px;
    }

    .form-head-title {
      font-size: 24px;
    }
  }
</style>
