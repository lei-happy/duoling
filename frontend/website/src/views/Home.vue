<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
        <div class="glow glow-2"></div>
        <div class="particles">
          <div
            v-for="p in particles"
            :key="p.id"
            class="particle"
            :style="p.style"
          />
        </div>
      </div>
      <div class="container hero-content">
        <div class="hero-badge scroll-animate">
          <span class="badge-dot"></span>
          轿运车队的利润管理专家
        </div>
        <h1 class="scroll-animate" data-delay="100">
          让每一台车、每一公里的<span class="gradient-text">利润都看得清楚</span>
        </h1>
        <p class="hero-desc scroll-animate" data-delay="200">
          助力轿运企业建立“利润确定性”——看清每单赚没赚、每条线路值不值、每个客户划不划算。
        </p>
        <div class="hero-actions scroll-animate" data-delay="300">
          <router-link to="/register">
            <el-button type="primary" size="large" class="btn-hero-primary">
              免费体验
              <span class="btn-arrow">→</span>
            </el-button>
          </router-link>
          <router-link to="/features">
            <el-button size="large" class="btn-hero-secondary">了解更多</el-button>
          </router-link>
        </div>
      </div>
    </section>

    <!-- 痛点共鸣 -->
    <section class="pain-section">
      <div class="container">
        <h2 class="section-title scroll-animate">这些问题，是不是你每天都在面对？</h2>
        <div class="pain-grid">
          <div
            v-for="(item, idx) in painPoints"
            :key="item.question"
            class="pain-card scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="pain-icon" v-html="item.icon"></div>
            <h3>{{ item.question }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 解决方案 -->
    <section class="solutions-section">
      <div class="container">
        <h2 class="section-title scroll-animate">智途帮你做到的四件事</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          不是给你一套系统，而是帮你建立“利润确定性”
        </p>
        <div class="solutions-grid">
          <div
            v-for="(item, idx) in solutions"
            :key="item.title"
            class="solution-card scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="solution-number">{{ String(idx + 1).padStart(2, '0') }}</div>
            <div class="solution-illustration" v-html="item.svg"></div>
            <div class="solution-content">
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 产品能力 -->
    <section class="capabilities-section">
      <div class="container">
        <h2 class="section-title scroll-animate">用结果说话</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          不做功能堆叠，只看实际结果
        </p>
        <div class="capabilities-grid">
          <div
            v-for="(item, idx) in capabilities"
            :key="item.title"
            class="capability-card scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="capability-icon" v-html="item.icon"></div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 案例 -->
    <section class="case-section">
      <div class="container">
        <h2 class="section-title scroll-animate">他们已经看清了利润</h2>
        <div class="case-card scroll-animate" data-delay="100">
          <div class="case-info">
            <div class="case-label">客户案例</div>
            <h3>某轿运车队 · 30台板车 · 华东区域</h3>
            <p class="case-desc">
              使用智途 3 个月后，通过单车利润核算与线路盈亏分析，
              精准定位了亏损线路与低价客户，调整经营策略后利润显著提升。
            </p>
          </div>
          <div class="case-metrics">
            <div
              v-for="(m, idx) in caseMetrics"
              :key="m.label"
              class="metric-item scroll-animate"
              :data-delay="200 + idx * 120"
            >
              <div class="metric-value">{{ m.value }}</div>
              <div class="metric-label">{{ m.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card scroll-animate">
          <h2>从今天开始，让每一分利润都看得清楚</h2>
          <router-link to="/register">
            <el-button type="primary" size="large" class="cta-btn">
              立即注册
            </el-button>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useScrollAnimation } from '@/composables/useScrollAnimation'

useScrollAnimation()

const particles = Array.from({ length: 30 }, (_, i) => {
  const size = Math.random() * 3 + 1
  return {
    id: i,
    style: {
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      width: `${size}px`,
      height: `${size}px`,
      animationDelay: `${Math.random() * 8}s`,
      animationDuration: `${Math.random() * 6 + 6}s`,
    },
  }
})

/* ---------- 痛点图标 ---------- */
const iconRevenue = `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="18" fill="#fef3c7"/><text x="20" y="25" text-anchor="middle" font-size="18" fill="#d97706">¥</text></svg>`
const iconRoute = `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="18" fill="#fee2e2"/><path d="M12 28l6-8 5 4 7-12" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`
const iconPrice = `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="18" fill="#ede9fe"/><path d="M14 20h12M14 16h8M14 24h10" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"/></svg>`
const iconEfficiency = `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="18" fill="#dbeafe"/><path d="M20 12v8l5 3" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`
const iconScale = `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="18" fill="#d1fae5"/><path d="M12 28l5-6 4 3 5-7 4 2" stroke="#059669" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><circle cx="30" cy="20" r="2.5" fill="#059669"/></svg>`

const painPoints = [
  {
    icon: iconRevenue,
    question: '为什么你每个月有营收，却不知道赚没赚钱？',
    desc: '收入不等于利润，油费、路桥、人工、维修……算不清就看不清。',
  },
  {
    icon: iconRoute,
    question: '哪些线路在亏钱，你能看清吗？',
    desc: '有些线路看着忙，实际每趟都在亏，却一直在跑。',
  },
  {
    icon: iconPrice,
    question: '哪些客户报价过低，你能识别吗？',
    desc: '老客户的报价可能早已低于成本，但你不敢动、也没依据。',
  },
  {
    icon: iconEfficiency,
    question: '哪些环节可以提效，你能抓住吗？',
    desc: '空驶、等待、绕路……每一个低效环节都在吃利润。',
  },
  {
    icon: iconScale,
    question: '为什么规模越大，反而利润越不稳定？',
    desc: '车多了、线路多了、客户多了，管理复杂度指数级增长。',
  },
]

/* ---------- 解决方案 SVG ---------- */
const svgProfit = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <rect x="40" y="50" width="56" height="56" rx="8" fill="url(#sp1)"/>
  <text x="68" y="86" text-anchor="middle" font-size="28" fill="#fff" font-weight="700">¥</text>
  <rect x="112" y="50" width="52" height="10" rx="5" fill="#bfdbfe"/>
  <rect x="112" y="68" width="40" height="10" rx="5" fill="#93c5fd"/>
  <rect x="112" y="86" width="48" height="10" rx="5" fill="#bfdbfe"/>
  <path d="M112 108h22" stroke="#34d399" stroke-width="3" stroke-linecap="round"/>
  <text x="138" y="112" font-size="10" fill="#059669" font-weight="600">+¥</text>
  <defs><linearGradient id="sp1" x1="40" y1="50" x2="96" y2="106" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgLossRoute = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <path d="M40 110 C60 80, 80 60, 100 70 S140 40, 170 35" stroke="#93c5fd" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M40 100 C55 90, 70 95, 85 100 S120 80, 140 85" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" fill="none" stroke-dasharray="6 4"/>
  <circle cx="85" cy="100" r="12" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <path d="M81 96l8 8M89 96l-8 8" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
  <circle cx="170" cy="35" r="8" fill="url(#sr1)"/>
  <path d="M166 35l3 3 5-5" stroke="#fff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="40" cy="110" r="6" fill="#1d4ed8"/>
  <circle cx="40" cy="110" r="3" fill="#fff"/>
  <defs><linearGradient id="sr1" x1="162" y1="27" x2="178" y2="43" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgDecision = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <rect x="40" y="100" width="20" height="24" rx="4" fill="#bfdbfe"/>
  <rect x="68" y="80" width="20" height="44" rx="4" fill="#93c5fd"/>
  <rect x="96" y="60" width="20" height="64" rx="4" fill="url(#sd1)"/>
  <rect x="124" y="72" width="20" height="52" rx="4" fill="#93c5fd"/>
  <rect x="152" y="50" width="20" height="74" rx="4" fill="url(#sd1)"/>
  <path d="M46 96 L74 76 L102 56 L130 68 L158 46" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round" fill="none"/>
  <circle cx="102" cy="56" r="4" fill="#1d4ed8"/>
  <circle cx="158" cy="46" r="4" fill="#1d4ed8"/>
  <rect x="38" y="34" width="52" height="16" rx="8" fill="#1d4ed8"/>
  <text x="64" y="45" text-anchor="middle" font-size="8" fill="#fff" font-weight="600">决策依据</text>
  <defs><linearGradient id="sd1" x1="0" y1="0" x2="0" y2="160" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgPricing = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <rect x="40" y="42" width="120" height="32" rx="6" fill="#fff" stroke="#e2e8f0" stroke-width="1"/>
  <text x="52" y="62" font-size="10" fill="#64748b">客户A</text>
  <text x="118" y="62" font-size="10" fill="#ef4444" font-weight="600">偏低</text>
  <rect x="136" y="52" width="16" height="12" rx="3" fill="#fef2f2"/>
  <path d="M140 58l4-3 4 3" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" transform="rotate(180 144 56.5)"/>
  <rect x="40" y="82" width="120" height="32" rx="6" fill="#fff" stroke="#e2e8f0" stroke-width="1"/>
  <text x="52" y="102" font-size="10" fill="#64748b">客户B</text>
  <text x="118" y="102" font-size="10" fill="#059669" font-weight="600">合理</text>
  <rect x="136" y="92" width="16" height="12" rx="3" fill="#d1fae5"/>
  <path d="M140 98l4-3 4 3" stroke="#059669" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`

const solutions = [
  {
    svg: svgProfit,
    title: '看清单车利润',
    desc: '每一单运输赚了多少钱，收入、成本、利润自动核算，一目了然。',
  },
  {
    svg: svgLossRoute,
    title: '找出亏损线路',
    desc: '哪条线路赚钱、哪条亏钱，跑得多不等于赚得多，用数据说话。',
  },
  {
    svg: svgDecision,
    title: '提供决策依据',
    desc: '不再拍脑袋做决定，经营数据实时呈现，每一步都有据可依。',
  },
  {
    svg: svgPricing,
    title: '优化客户报价',
    desc: '识别哪些客户报价偏低、哪些还有空间，让每一单报价都合理。',
  },
]

/* ---------- 产品能力图标 ---------- */
const capIconCalc = `<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" rx="12" fill="#eff6ff"/>
  <rect x="12" y="12" width="24" height="24" rx="4" fill="url(#gc1)"/>
  <text x="24" y="29" text-anchor="middle" font-size="14" fill="#fff" font-weight="700">¥</text>
  <defs><linearGradient id="gc1" x1="12" y1="12" x2="36" y2="36" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const capIconRank = `<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" rx="12" fill="#eff6ff"/>
  <rect x="12" y="28" width="6" height="8" rx="1" fill="#93c5fd"/>
  <rect x="21" y="20" width="6" height="16" rx="1" fill="url(#gc2)"/>
  <rect x="30" y="24" width="6" height="12" rx="1" fill="#93c5fd"/>
  <defs><linearGradient id="gc2" x1="21" y1="20" x2="27" y2="36" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const capIconCustomer = `<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" rx="12" fill="#eff6ff"/>
  <circle cx="24" cy="20" r="6" fill="url(#gc3)"/>
  <path d="M14 36c0-5.523 4.477-10 10-10s10 4.477 10 10" stroke="#93c5fd" stroke-width="2" stroke-linecap="round" fill="none"/>
  <defs><linearGradient id="gc3" x1="18" y1="14" x2="30" y2="26" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const capIconCost = `<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" rx="12" fill="#eff6ff"/>
  <circle cx="24" cy="24" r="12" fill="none" stroke="#dbeafe" stroke-width="2"/>
  <path d="M24 12a12 12 0 0 1 10.39 6" stroke="#1d4ed8" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M34.39 18a12 12 0 0 1-3.08 14.56" stroke="#2563eb" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M31.31 32.56A12 12 0 0 1 12.27 21" stroke="#93c5fd" stroke-width="3" stroke-linecap="round" fill="none"/>
</svg>`

const capabilities = [
  {
    icon: capIconCalc,
    title: '单车利润自动核算',
    desc: '每台车、每趟运输的收入与成本自动归集，利润实时可见。',
  },
  {
    icon: capIconRank,
    title: '线路盈利能力排名',
    desc: '所有运营线路按利润率排序，亏损线路一眼定位。',
  },
  {
    icon: capIconCustomer,
    title: '客户利润分析',
    desc: '按客户维度统计利润贡献，识别低价客户与高价值客户。',
  },
  {
    icon: capIconCost,
    title: '成本结构拆解',
    desc: '油费、路桥费、司机工资……每一项成本自动归类，清晰透明。',
  },
]

const caseMetrics = [
  { value: '30%', label: '亏损线路发现' },
  { value: '5个', label: '低价客户识别' },
  { value: '12%', label: '利润提升' },
]
</script>

<style scoped lang="scss">
/* ========== Hero ========== */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--gradient-hero);
  padding: 120px 0 80px;
}

.hero-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

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
  opacity: 0.4;
}

.glow-1 {
  width: 500px;
  height: 500px;
  background: var(--color-primary);
  top: -10%;
  right: -5%;
  animation: float 8s ease-in-out infinite, glow-color-1 10s ease-in-out infinite;
}

.glow-2 {
  width: 400px;
  height: 400px;
  background: var(--color-accent);
  bottom: -10%;
  left: -5%;
  animation: float 10s ease-in-out infinite reverse, glow-color-2 12s ease-in-out infinite;
}

@keyframes glow-color-1 {
  0%, 100% { background: #1d4ed8; }
  33% { background: #7c3aed; }
  66% { background: #2563eb; }
}

@keyframes glow-color-2 {
  0%, 100% { background: #2563eb; }
  33% { background: #db2777; }
  66% { background: #0891b2; }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
}

.particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  animation: particle-rise linear infinite;
  will-change: transform, opacity;
}

@keyframes particle-rise {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% { opacity: 0.8; }
  90% { opacity: 0.6; }
  100% {
    transform: translateY(-100vh) scale(0.5);
    opacity: 0;
  }
}

.hero-content {
  position: relative;
  text-align: center;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 100px;
  padding: 8px 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 32px;
  backdrop-filter: blur(8px);
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.hero h1 {
  font-size: 48px;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #fb923c, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 17px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.8;
  max-width: 720px;
  margin: 0 auto 40px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-hero-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 12px 32px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  transition: transform 0.2s, box-shadow 0.2s !important;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(29, 78, 216, 0.4) !important;
  }

  .btn-arrow {
    margin-left: 8px;
    transition: transform 0.2s;
  }

  &:hover .btn-arrow {
    transform: translateX(4px);
  }
}

.btn-hero-secondary {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
  border-radius: 10px !important;
  padding: 12px 32px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  backdrop-filter: blur(8px);
  transition: all 0.2s !important;

  &:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
  }
}

/* ========== 痛点共鸣 ========== */
.pain-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.pain-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 16px;
}

.pain-card {
  padding: 32px 28px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-soft);
  transition: all 0.3s ease;

  &:hover {
    background: var(--color-bg);
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
  }

  h3 {
    font-size: 17px;
    font-weight: 700;
    color: var(--color-text);
    line-height: 1.6;
    margin-bottom: 12px;
  }

  p {
    font-size: 14px;
    color: var(--color-text-secondary);
    line-height: 1.7;
  }
}

.pain-icon {
  width: 40px;
  height: 40px;
  margin-bottom: 16px;

  :deep(svg) {
    width: 100%;
    height: 100%;
  }
}

/* ========== 解决方案 ========== */
.solutions-section {
  padding: 100px 0;
  background: var(--color-bg-soft);
}

.solutions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.solution-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 24px;
  padding: 36px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--color-primary-light);
    box-shadow: var(--shadow-lg), 0 0 0 1px rgba(29, 78, 216, 0.06);
    transform: translateY(-4px);
  }

  .solution-content {
    flex: 1;
    min-width: 0;
  }

  h3 {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--color-text);
  }

  p {
    color: var(--color-text-secondary);
    font-size: 15px;
    line-height: 1.7;
  }
}

.solution-number {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 48px;
  font-weight: 900;
  color: var(--color-primary);
  opacity: 0.06;
  line-height: 1;
}

.solution-illustration {
  flex: 0 0 140px;
  width: 140px;

  :deep(svg) {
    width: 100%;
    height: auto;
  }
}

/* ========== 产品能力 ========== */
.capabilities-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.capability-card {
  text-align: center;
  padding: 40px 24px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-soft);
  transition: all 0.3s ease;

  &:hover {
    background: var(--color-bg);
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
  }

  h3 {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 10px;
    color: var(--color-text);
  }

  p {
    font-size: 14px;
    color: var(--color-text-secondary);
    line-height: 1.7;
  }
}

.capability-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 20px;

  :deep(svg) {
    width: 100%;
    height: 100%;
  }
}

/* ========== 案例 ========== */
.case-section {
  padding: 100px 0;
  background: var(--color-bg-soft);
}

.case-card {
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 60px;
  border-radius: var(--radius-xl);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
}

.case-info {
  flex: 1;
}

.case-label {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 4px 12px;
  border-radius: 100px;
  margin-bottom: 16px;
}

.case-info h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 16px;
}

.case-desc {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.case-metrics {
  display: flex;
  gap: 40px;
  flex-shrink: 0;
}

.metric-item {
  text-align: center;
}

.metric-value {
  font-size: 42px;
  font-weight: 800;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
  line-height: 1;
}

.metric-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* ========== CTA ========== */
.cta-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.cta-card {
  text-align: center;
  padding: 80px 40px;
  border-radius: var(--radius-xl);
  background: var(--gradient-hero);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  h2 {
    font-size: 36px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 16px;
    position: relative;
  }

  p {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 36px;
    position: relative;
  }
}

.cta-btn {
  background: #fff !important;
  color: var(--color-primary) !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 14px 36px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  height: auto !important;
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s !important;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(255, 255, 255, 0.2) !important;
  }

  .btn-arrow {
    margin-left: 8px;
    transition: transform 0.2s;
  }

  &:hover .btn-arrow {
    transform: translateX(4px);
  }
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .solutions-grid {
    grid-template-columns: 1fr;
  }

  .capabilities-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .case-card {
    flex-direction: column;
    gap: 40px;
    padding: 40px;
  }

  .case-metrics {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 120px 0 60px;
    min-height: auto;
  }

  .hero h1 {
    font-size: 28px;
  }

  .hero-desc {
    font-size: 15px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .pain-grid {
    grid-template-columns: 1fr;
  }

  .solution-card {
    flex-direction: column;
    gap: 16px;
  }

  .solution-illustration {
    flex: none;
    width: 100%;
    max-width: 160px;
    margin: 0 auto;
  }

  .capabilities-grid {
    grid-template-columns: 1fr;
  }

  .case-card {
    padding: 32px 24px;
  }

  .case-metrics {
    flex-direction: column;
    gap: 24px;
  }

  .metric-value {
    font-size: 32px;
  }

  .solutions-section,
  .pain-section,
  .capabilities-section,
  .case-section,
  .cta-section {
    padding: 64px 0;
  }

  .cta-card {
    padding: 48px 24px;

    h2 {
      font-size: 28px;
    }
  }
}
</style>
