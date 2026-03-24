<template>
  <div class="pricing-page">
    <!-- Hero -->
    <section class="page-hero">
      <div class="hero-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
      </div>
      <div class="container hero-content">
        <h1 class="scroll-animate">价格方案</h1>
        <p class="scroll-animate" data-delay="100">
          简单透明的定价，选择适合你车队规模的方案
        </p>
      </div>
    </section>

    <!-- 定价卡片 -->
    <section class="pricing-section">
      <div class="container">
        <div class="pricing-grid">
          <div
            v-for="(plan, idx) in plans"
            :key="plan.name"
            class="pricing-card scroll-animate"
            :class="{ recommended: plan.recommended }"
            :data-delay="idx * 120"
          >
            <div v-if="plan.recommended" class="recommend-badge">推荐</div>
            <div class="plan-header">
              <h3>{{ plan.name }}</h3>
              <p class="plan-desc">{{ plan.desc }}</p>
              <div class="plan-price">
                <span class="price-currency">¥</span>
                <span class="price-value">{{ plan.price.toLocaleString() }}</span>
                <span class="price-period">/年</span>
              </div>
            </div>
            <div class="plan-features">
              <div
                v-for="item in plan.features"
                :key="item.text"
                class="plan-feature-item"
                :class="{ disabled: !item.included }"
              >
                <span class="feature-check" :class="{ active: item.included }">
                  {{ item.included ? '✓' : '—' }}
                </span>
                <span>{{ item.text }}</span>
              </div>
            </div>
            <div class="plan-action">
              <router-link :to="plan.action.link">
                <el-button
                  :type="plan.recommended ? 'primary' : 'default'"
                  size="large"
                  class="plan-btn"
                  :class="{ 'plan-btn-primary': plan.recommended }"
                >
                  {{ plan.action.text }}
                </el-button>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="faq-section">
      <div class="container">
        <h2 class="section-title scroll-animate">常见问题</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          关于产品和定价的常见疑问解答
        </p>
        <div class="faq-list">
          <div
            v-for="(item, idx) in faqs"
            :key="item.q"
            class="faq-item scroll-animate"
            :data-delay="idx * 80"
          >
            <div class="faq-question" @click="toggleFaq(idx)">
              <span>{{ item.q }}</span>
              <span class="faq-toggle" :class="{ open: openFaq === idx }">+</span>
            </div>
            <div class="faq-answer" :class="{ open: openFaq === idx }">
              <p>{{ item.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useScrollAnimation } from '@/composables/useScrollAnimation'

useScrollAnimation()

const openFaq = ref<number | null>(null)

function toggleFaq(idx: number) {
  openFaq.value = openFaq.value === idx ? null : idx
}

const plans = [
  {
    name: '标准版',
    desc: '适合中小规模轿运车队，覆盖核心利润管理能力',
    price: 4999,
    recommended: false,
    features: [
      { text: '单车利润核算', included: true },
      { text: '运单全流程管理', included: true },
      { text: '基础线路盈亏分析', included: true },
      { text: '客户管理', included: true },
      { text: '成本录入与统计', included: true },
      { text: '基础数据报表', included: true },
      { text: '在线客服支持', included: true },
      { text: '线路盈利能力排名', included: false },
      { text: '客户利润深度分析', included: false },
      { text: '成本结构智能拆解', included: false },
      { text: '高级 BI 数据看板', included: false },
      { text: '报价优化建议', included: false },
      { text: '专属客户经理', included: false },
    ],
    action: { text: '立即开通', link: '/register' },
  },
  {
    name: '高级版',
    desc: '适合追求精细化经营的中大型车队',
    price: 9999,
    recommended: true,
    features: [
      { text: '单车利润核算', included: true },
      { text: '运单全流程管理', included: true },
      { text: '基础线路盈亏分析', included: true },
      { text: '客户管理', included: true },
      { text: '成本录入与统计', included: true },
      { text: '基础数据报表', included: true },
      { text: '在线客服支持', included: true },
      { text: '线路盈利能力排名', included: true },
      { text: '客户利润深度分析', included: true },
      { text: '成本结构智能拆解（油/路/人）', included: true },
      { text: '高级 BI 数据看板', included: true },
      { text: '报价优化建议', included: true },
      { text: '专属客户经理', included: true },
    ],
    action: { text: '立即开通', link: '/register' },
  },
]

const faqs = [
  {
    q: '可以先试用再决定吗？',
    a: '当然可以。我们提供免费试用期，您可以充分体验核心功能后再决定是否订阅。',
  },
  {
    q: '标准版和高级版的核心区别是什么？',
    a: '标准版覆盖单车利润核算和基础线路分析，满足日常经营需求；高级版在此基础上增加深度利润分析、报价优化建议、BI 数据看板等高级能力，帮助您做更精细化的经营决策。',
  },
  {
    q: '数据安全如何保障？',
    a: '我们采用银行级数据加密、多地域灾备、严格的权限管控，确保您的运单、车辆、财务等核心业务数据安全无忧。',
  },
  {
    q: '是否支持对接主机厂系统？',
    a: '支持。高级版提供标准 API 接口，可与主机厂 DMS、TMS 等系统对接，实现运输指令自动接收，并配备专属技术对接支持。',
  },
  {
    q: '可以随时升级版本吗？',
    a: '可以。您可以根据业务发展需要，随时在系统内升级到高级版，差价按剩余时长折算。',
  },
  {
    q: '如何获取技术支持？',
    a: '标准版提供在线客服支持；高级版配备专属客户经理，提供 7×24 小时技术响应。',
  },
]
</script>

<style scoped lang="scss">
/* ========== Page Hero ========== */
.page-hero {
  position: relative;
  padding: 160px 0 80px;
  text-align: center;
  background: var(--gradient-hero);
  overflow: hidden;

  .hero-bg {
    position: absolute;
    inset: 0;
  }

  .grid-lines {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
  }

  .glow-1 {
    position: absolute;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: var(--color-primary);
    filter: blur(100px);
    opacity: 0.25;
    top: -20%;
    left: 20%;
  }

  .hero-content {
    position: relative;
    z-index: 1;
  }

  h1 {
    font-size: 48px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 16px;
    letter-spacing: -0.02em;
  }

  p {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.6);
  }
}

/* ========== 定价卡片 ========== */
.pricing-section {
  padding: 100px 0;
  background: var(--color-bg-soft);
  margin-top: -40px;
  position: relative;
  z-index: 2;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  align-items: start;
  max-width: 880px;
  margin: 0 auto;
}

.pricing-card {
  position: relative;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 40px 32px;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
  }

  &.recommended {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 1px var(--color-primary), var(--shadow-lg);
    transform: scale(1.03);

    &:hover {
      transform: scale(1.03) translateY(-4px);
    }
  }
}

.recommend-badge {
  position: absolute;
  top: -1px;
  right: 24px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  padding: 6px 16px;
  border-radius: 0 0 8px 8px;
}

.plan-header {
  margin-bottom: 32px;

  h3 {
    font-size: 22px;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 8px;
  }

  .plan-desc {
    font-size: 14px;
    color: var(--color-text-secondary);
    margin-bottom: 24px;
    line-height: 1.6;
  }
}

.plan-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.price-currency {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
}

.price-value {
  font-size: 48px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1;
}

.price-period {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin-left: 4px;
}

.plan-features {
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.plan-feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--color-text);

  &.disabled {
    color: var(--color-text-muted);
  }
}

.feature-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
  background: var(--color-bg-muted);
  color: var(--color-text-muted);

  &.active {
    background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
    color: #fff;
  }
}

.plan-action {
  .plan-btn {
    width: 100%;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    height: 48px !important;
  }

  .plan-btn-primary {
    background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
    border: none !important;
    transition: transform 0.2s, box-shadow 0.2s !important;

    &:hover {
      box-shadow: 0 4px 20px rgba(29, 78, 216, 0.35) !important;
    }
  }
}

/* ========== FAQ ========== */
.faq-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.faq-list {
  max-width: 720px;
  margin: 0 auto;
}

.faq-item {
  border-bottom: 1px solid var(--color-border-light);

  &:first-child {
    border-top: 1px solid var(--color-border-light);
  }
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  cursor: pointer;
  user-select: none;

  span:first-child {
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text);
  }
}

.faq-toggle {
  font-size: 24px;
  color: var(--color-text-secondary);
  transition: transform 0.3s;
  flex-shrink: 0;
  width: 28px;
  text-align: center;

  &.open {
    transform: rotate(45deg);
  }
}

.faq-answer {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;

  &.open {
    max-height: 200px;
    padding-bottom: 20px;
  }

  p {
    font-size: 15px;
    color: var(--color-text-secondary);
    line-height: 1.7;
  }
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .pricing-grid {
    grid-template-columns: 1fr;
    max-width: 480px;
    margin: 0 auto;
  }

  .pricing-card.recommended {
    transform: none;

    &:hover {
      transform: translateY(-4px);
    }
  }
}

@media (max-width: 768px) {
  .page-hero {
    padding: 120px 0 60px;

    h1 {
      font-size: 36px;
    }
  }

  .pricing-section {
    padding: 64px 0;
  }

  .faq-section {
    padding: 64px 0;
  }

  .price-value {
    font-size: 40px;
  }
}
</style>
