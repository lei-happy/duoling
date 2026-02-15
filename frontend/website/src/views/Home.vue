<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
        <div class="glow glow-2"></div>
      </div>
      <div class="container hero-content">
        <div class="hero-badge scroll-animate">
          <span class="badge-dot"></span>
          AI 驱动的汽车物流管理平台
        </div>
        <h1 class="scroll-animate" data-delay="100">
          智途，汽车物流企业的<span class="gradient-text">AI操作系统</span>
        </h1>
        <p class="hero-desc scroll-animate" data-delay="200">
          让整车运输更智能。从主机厂发运到经销商交付，以AI技术重新定义汽车物流效率，帮助每一家轿运企业实现业务在线化、财务数字化、经营智能化。
        </p>
        <div class="hero-actions scroll-animate" data-delay="300">
          <router-link to="/register">
            <el-button type="primary" size="large" class="btn-hero-primary">
              免费体验
              <span class="btn-arrow">→</span>
            </el-button>
          </router-link>
          <router-link to="/features">
            <el-button size="large" class="btn-hero-secondary">了解产品</el-button>
          </router-link>
        </div>
      </div>
    </section>

    <!-- 核心功能 -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title scroll-animate">核心功能</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          覆盖整车运输全场景，让发运、在途、交付每个环节都在线可控
        </p>
        <div class="features-grid">
          <div
            v-for="(item, idx) in coreFeatures"
            :key="item.title"
            class="feature-card scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="feature-illustration" v-html="item.svg"></div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <div class="feature-tags">
              <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据统计 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div
            v-for="(stat, idx) in stats"
            :key="stat.label"
            class="stat-item scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="stat-number">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 为什么选择智途 -->
    <section class="why-section">
      <div class="container">
        <h2 class="section-title scroll-animate">为什么选择智途</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          专注汽车物流行业，以技术创新助力轿运企业数字化转型
        </p>
        <div class="why-grid">
          <div
            v-for="(item, idx) in advantages"
            :key="item.title"
            class="why-card scroll-animate"
            :data-delay="idx * 120"
          >
            <div class="why-illustration" v-html="item.svg"></div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card scroll-animate">
          <h2>立即开启整车运输数字化之旅</h2>
          <p>免费注册，快速体验 AI 驱动的汽车物流管理平台</p>
          <router-link to="/register">
            <el-button type="primary" size="large" class="cta-btn">
              免费注册
              <span class="btn-arrow">→</span>
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

/* ---------- SVG 插画 ---------- */
const svgDispatch = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="30" width="160" height="100" rx="12" fill="#eff6ff"/>
  <rect x="32" y="48" width="80" height="10" rx="5" fill="#bfdbfe"/>
  <rect x="32" y="66" width="56" height="10" rx="5" fill="#93c5fd"/>
  <rect x="32" y="84" width="68" height="10" rx="5" fill="#bfdbfe"/>
  <rect x="32" y="102" width="44" height="10" rx="5" fill="#93c5fd"/>
  <circle cx="148" cy="60" r="20" fill="url(#gd1)"/>
  <path d="M140 60l6 6 12-12" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="148" cy="96" r="14" fill="#dbeafe"/>
  <path d="M142 96h12M148 90v12" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/>
  <defs><linearGradient id="gd1" x1="128" y1="40" x2="168" y2="80" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgRoute = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <path d="M50 110 C60 70, 100 50, 110 80 S150 50, 160 40" stroke="url(#gd2)" stroke-width="3" stroke-linecap="round" fill="none" stroke-dasharray="6 4"/>
  <circle cx="50" cy="110" r="8" fill="#1d4ed8"/>
  <circle cx="50" cy="110" r="4" fill="#fff"/>
  <circle cx="110" cy="80" r="6" fill="#2563eb" opacity="0.6"/>
  <circle cx="160" cy="40" r="8" fill="#2563eb"/>
  <circle cx="160" cy="40" r="4" fill="#fff"/>
  <rect x="30" y="40" width="36" height="20" rx="6" fill="#1d4ed8" opacity="0.12"/>
  <text x="48" y="54" text-anchor="middle" font-size="9" fill="#1d4ed8" font-weight="600">GPS</text>
  <rect x="120" y="90" width="50" height="20" rx="6" fill="#2563eb" opacity="0.12"/>
  <text x="145" y="104" text-anchor="middle" font-size="8" fill="#2563eb" font-weight="600">在途跟踪</text>
  <defs><linearGradient id="gd2" x1="50" y1="110" x2="160" y2="40" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgFleet = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <rect x="40" y="75" width="72" height="28" rx="6" fill="#1d4ed8" opacity="0.15"/>
  <rect x="40" y="78" width="72" height="8" rx="2" fill="#1d4ed8" opacity="0.3"/>
  <rect x="50" y="62" width="52" height="14" rx="3" fill="#bfdbfe"/>
  <rect x="56" y="56" width="40" height="8" rx="2" fill="#93c5fd"/>
  <circle cx="52" cy="105" r="6" fill="#1d4ed8"/>
  <circle cx="52" cy="105" r="3" fill="#eff6ff"/>
  <circle cx="100" cy="105" r="6" fill="#1d4ed8"/>
  <circle cx="100" cy="105" r="3" fill="#eff6ff"/>
  <rect x="130" y="46" width="40" height="50" rx="8" fill="url(#gd3)"/>
  <circle cx="150" cy="62" r="10" fill="rgba(255,255,255,0.2)"/>
  <path d="M146 62l3 3 5-6" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
  <rect x="138" y="78" width="24" height="3" rx="1.5" fill="rgba(255,255,255,0.4)"/>
  <rect x="138" y="84" width="18" height="3" rx="1.5" fill="rgba(255,255,255,0.3)"/>
  <defs><linearGradient id="gd3" x1="130" y1="46" x2="170" y2="96" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgAnalytics = `<svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="160" height="120" rx="12" fill="#eff6ff"/>
  <rect x="40" y="100" width="20" height="24" rx="4" fill="#bfdbfe"/>
  <rect x="68" y="80" width="20" height="44" rx="4" fill="#93c5fd"/>
  <rect x="96" y="60" width="20" height="64" rx="4" fill="url(#gd4)"/>
  <rect x="124" y="72" width="20" height="52" rx="4" fill="#93c5fd"/>
  <rect x="152" y="50" width="20" height="74" rx="4" fill="url(#gd4)"/>
  <path d="M46 96 L74 76 L102 56 L130 68 L158 46" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round" fill="none"/>
  <circle cx="46" cy="96" r="3" fill="#1d4ed8"/>
  <circle cx="74" cy="76" r="3" fill="#1d4ed8"/>
  <circle cx="102" cy="56" r="3" fill="#1d4ed8"/>
  <circle cx="130" cy="68" r="3" fill="#1d4ed8"/>
  <circle cx="158" cy="46" r="3" fill="#1d4ed8"/>
  <rect x="38" y="34" width="48" height="16" rx="8" fill="#1d4ed8"/>
  <text x="62" y="45" text-anchor="middle" font-size="8" fill="#fff" font-weight="600">实时预警</text>
  <defs><linearGradient id="gd4" x1="0" y1="0" x2="0" y2="160" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgAI = `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="32" fill="#eff6ff"/>
  <circle cx="40" cy="40" r="20" fill="url(#gda)"/>
  <path d="M32 40h4m8 0h4M40 32v4m0 8v4" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
  <circle cx="40" cy="40" r="4" fill="#fff"/>
  <path d="M22 22l6 6M58 22l-6 6M22 58l6-6M58 58l-6-6" stroke="#93c5fd" stroke-width="1.5" stroke-linecap="round"/>
  <defs><linearGradient id="gda" x1="20" y1="20" x2="60" y2="60" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgCloud = `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="32" fill="#eff6ff"/>
  <path d="M28 50a10 10 0 0 1-2-19.8A14 14 0 0 1 52 28a10 10 0 0 1 2 19.8" fill="url(#gdb)" opacity="0.9"/>
  <path d="M34 46v8M40 44v10M46 46v8" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
  <defs><linearGradient id="gdb" x1="24" y1="24" x2="56" y2="52" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgMobile = `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="32" fill="#eff6ff"/>
  <rect x="28" y="18" width="24" height="44" rx="4" fill="url(#gdc)"/>
  <rect x="31" y="24" width="18" height="28" rx="2" fill="#fff" opacity="0.2"/>
  <circle cx="40" cy="58" r="2" fill="#fff" opacity="0.5"/>
  <rect x="34" y="28" width="12" height="3" rx="1.5" fill="#fff" opacity="0.5"/>
  <rect x="34" y="34" width="8" height="3" rx="1.5" fill="#fff" opacity="0.35"/>
  <rect x="34" y="40" width="10" height="3" rx="1.5" fill="#fff" opacity="0.35"/>
  <path d="M56 32l6-4m-6 10h6m-6 8l6 4" stroke="#93c5fd" stroke-width="1.5" stroke-linecap="round"/>
  <defs><linearGradient id="gdc" x1="28" y1="18" x2="52" y2="62" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const coreFeatures = [
  {
    svg: svgDispatch,
    title: '发运计划与运单管理',
    desc: '从主机厂接单到经销商交付，整车运单全流程数字化管理。支持批量VIN录入、多点配载，告别纸质交接单。',
    tags: ['VIN管理', '批量发运', '电子回单'],
  },
  {
    svg: svgRoute,
    title: '在途追踪与路线管理',
    desc: '实时追踪板车位置与运输轨迹，智能规划多点配送路线，偏离预警确保商品车安全准时到达。',
    tags: ['GPS追踪', '路线优化', '偏离预警'],
  },
  {
    svg: svgFleet,
    title: '板车与驾驶员管理',
    desc: '轿运车资产全生命周期管理，驾驶员档案与证照到期提醒。运力资源一目了然，调度更高效。',
    tags: ['运力管理', '证照提醒', '调度排班'],
  },
  {
    svg: svgAnalytics,
    title: '数据分析与预警推送',
    desc: '运量趋势、线路利润、单车成本多维度数据实时汇聚，异常指标智能识别，让经营决策有据可依。',
    tags: ['智能报表', '异常预警', '利润分析'],
  },
]

const stats = [
  { value: '99.9%', label: '系统可用性' },
  { value: '50%+', label: '调度效率提升' },
  { value: '7×24h', label: '技术支持' },
  { value: '30s', label: '快速部署' },
]

const advantages = [
  {
    svg: svgAI,
    title: 'AI 深度融合',
    desc: 'AI 助理贯穿发运、调度、在途全流程，智能推荐配载方案与最优路线，让运营效率提升到新高度。',
  },
  {
    svg: svgCloud,
    title: 'SaaS 云端部署',
    desc: '零部署成本、零运维负担，注册即用。业务数据云端安全存储，总部与外勤随时随地协同。',
  },
  {
    svg: svgMobile,
    title: '移动端全覆盖',
    desc: '调度员派车、司机接单验车、经销商签收，多角色移动端适配，板车在路上也能高效办公。',
  },
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
  animation: float 8s ease-in-out infinite;
}

.glow-2 {
  width: 400px;
  height: 400px;
  background: var(--color-accent);
  bottom: -10%;
  left: -5%;
  animation: float 10s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
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
  font-size: 52px;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
  white-space: nowrap;
}

.gradient-text {
  background: linear-gradient(135deg, #93c5fd 0%, #60a5fa 50%, #38bdf8 100%);
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

/* ========== 核心功能 ========== */
.features-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.feature-card {
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
    margin-bottom: 20px;
  }
}

.feature-illustration {
  width: 100%;
  max-width: 200px;
  margin-bottom: 20px;

  :deep(svg) {
    width: 100%;
    height: auto;
  }
}

.feature-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;

  span {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 100px;
    background: var(--color-bg-muted);
    color: var(--color-text-secondary);
    font-weight: 500;
  }
}

/* ========== 数据统计 ========== */
.stats-section {
  padding: 80px 0;
  background: var(--color-bg-soft);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 42px;
  font-weight: 800;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 15px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* ========== 为什么选择智途 ========== */
.why-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.why-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.why-card {
  text-align: center;
  padding: 48px 32px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-soft);
  transition: all 0.3s ease;

  &:hover {
    background: var(--color-bg);
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
  }

  h3 {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--color-text);
  }

  p {
    font-size: 15px;
    color: var(--color-text-secondary);
    line-height: 1.7;
  }
}

.why-illustration {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;

  :deep(svg) {
    width: 100%;
    height: 100%;
  }
}

/* ========== CTA ========== */
.cta-section {
  padding: 100px 0;
  background: var(--color-bg-soft);
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
  .features-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .why-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 120px 0 60px;
    min-height: auto;
  }

  .hero h1 {
    font-size: 28px;
    white-space: normal;
  }

  .hero-desc {
    font-size: 15px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .features-section,
  .why-section,
  .cta-section {
    padding: 64px 0;
  }

  .stats-section {
    padding: 48px 0;
  }

  .stat-number {
    font-size: 32px;
  }

  .cta-card {
    padding: 48px 24px;

    h2 {
      font-size: 28px;
    }
  }
}
</style>
