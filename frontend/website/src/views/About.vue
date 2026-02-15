<template>
  <div class="about-page">
    <!-- Hero -->
    <section class="page-hero">
      <div class="hero-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
      </div>
      <div class="container hero-content">
        <h1 class="scroll-animate">关于我们</h1>
        <p class="scroll-animate" data-delay="100">
          用数字技术驱动汽车物流产业升级，让每一家轿运企业都能享受智能化带来的效率革命
        </p>
      </div>
    </section>

    <!-- 使命愿景 -->
    <section class="mvv-section">
      <div class="container">
        <div class="mvv-grid">
          <div class="mvv-card scroll-animate" data-delay="0">
            <div class="mvv-svg" v-html="svgMission"></div>
            <h3>使命</h3>
            <p>
              用数字技术驱动汽车物流产业升级，让每一家轿运企业都能享受智能化带来的效率革命。
              我们致力于帮助整车运输企业实现业务在线化、财务数字化、经营智能化，
              从根本上提升整车运输的管理效率与盈利能力。
            </p>
          </div>
          <div class="mvv-card scroll-animate" data-delay="120">
            <div class="mvv-svg" v-html="svgVision"></div>
            <h3>愿景</h3>
            <p>
              成为汽车物流行业最值得信赖的数字化伙伴，推动中国整车运输从经验驱动迈向数据驱动。
              我们相信，当每一台板车、每一台商品车、每一笔运费都在线可视可控，
              汽车物流行业将迎来全新的效率时代。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 价值观 -->
    <section class="values-section">
      <div class="container">
        <h2 class="section-title scroll-animate">核心价值观</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          这些信念指引我们的每一个产品决策和技术方向
        </p>
        <div class="values-grid">
          <div
            v-for="(val, idx) in values"
            :key="val.title"
            class="value-card scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="value-svg" v-html="val.svg"></div>
            <h3>{{ val.title }}</h3>
            <p>{{ val.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 团队介绍 -->
    <section class="team-section">
      <div class="container">
        <h2 class="section-title scroll-animate">核心团队</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          一支深耕汽车物流行业与前沿技术的复合型团队
        </p>
        <div class="team-grid">
          <div
            v-for="(member, idx) in team"
            :key="member.name"
            class="team-card scroll-animate"
            :data-delay="idx * 100"
          >
            <div class="member-avatar">
              <span>{{ member.name[0] }}</span>
            </div>
            <h3>{{ member.name }}</h3>
            <p class="member-title">{{ member.role }}</p>
            <p class="member-desc">{{ member.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 联系我们 -->
    <section class="contact-section">
      <div class="container">
        <h2 class="section-title scroll-animate">联系我们</h2>
        <p class="section-subtitle scroll-animate" data-delay="100">
          期待与您交流，共同探索汽车物流数字化的无限可能
        </p>
        <div class="contact-grid">
          <div class="contact-card scroll-animate" data-delay="0">
            <div class="contact-icon">📧</div>
            <h4>商务合作</h4>
            <p>contact@zhitu.com</p>
          </div>
          <div class="contact-card scroll-animate" data-delay="100">
            <div class="contact-icon">📞</div>
            <h4>咨询热线</h4>
            <p>400-XXX-XXXX</p>
          </div>
          <div class="contact-card scroll-animate" data-delay="200">
            <div class="contact-icon">📍</div>
            <h4>公司地址</h4>
            <p>中国 · 待更新</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card scroll-animate">
          <h2>加入我们，共建汽车物流数字化未来</h2>
          <p>无论您是轿运企业还是技术人才，我们都期待与您携手前行</p>
          <div class="cta-actions">
            <router-link to="/register">
              <el-button type="primary" size="large" class="cta-btn cta-btn-primary">
                免费注册
                <span class="btn-arrow">→</span>
              </el-button>
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useScrollAnimation } from '@/composables/useScrollAnimation'

useScrollAnimation()

/* ---- 使命 SVG ---- */
const svgMission = `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="36" fill="#eff6ff"/>
  <circle cx="40" cy="40" r="26" stroke="#bfdbfe" stroke-width="2" fill="none"/>
  <circle cx="40" cy="40" r="16" stroke="#93c5fd" stroke-width="2" fill="none"/>
  <circle cx="40" cy="40" r="6" fill="url(#gm1)"/>
  <line x1="40" y1="4" x2="40" y2="14" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/>
  <line x1="40" y1="66" x2="40" y2="76" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/>
  <line x1="4" y1="40" x2="14" y2="40" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/>
  <line x1="66" y1="40" x2="76" y2="40" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/>
  <defs><linearGradient id="gm1" x1="34" y1="34" x2="46" y2="46" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

/* ---- 愿景 SVG ---- */
const svgVision = `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="36" fill="#eff6ff"/>
  <circle cx="40" cy="38" r="18" stroke="url(#gv1)" stroke-width="2.5" fill="none"/>
  <circle cx="40" cy="38" r="8" fill="url(#gv1)"/>
  <circle cx="40" cy="38" r="4" fill="#fff"/>
  <path d="M12 38c0 0 12-18 28-18s28 18 28 18" stroke="#93c5fd" stroke-width="2" stroke-linecap="round" fill="none"/>
  <path d="M12 38c0 0 12 18 28 18s28-18 28-18" stroke="#93c5fd" stroke-width="2" stroke-linecap="round" fill="none"/>
  <line x1="40" y1="60" x2="40" y2="70" stroke="#bfdbfe" stroke-width="2" stroke-linecap="round"/>
  <line x1="34" y1="68" x2="46" y2="68" stroke="#bfdbfe" stroke-width="2" stroke-linecap="round"/>
  <defs><linearGradient id="gv1" x1="22" y1="20" x2="58" y2="56" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

/* ---- 价值观 SVGs ---- */
const svgCustomer = `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="28" fill="#eff6ff"/>
  <circle cx="24" cy="26" r="8" fill="#bfdbfe"/>
  <circle cx="40" cy="26" r="8" fill="#93c5fd"/>
  <path d="M12 48c0-8 8-14 20-14s20 6 20 14" fill="url(#gc1)" opacity="0.7"/>
  <path d="M28 36l4 4 4-4" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <defs><linearGradient id="gc1" x1="12" y1="34" x2="52" y2="48" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgTech = `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="28" fill="#eff6ff"/>
  <circle cx="32" cy="28" r="12" fill="url(#gt1)"/>
  <path d="M26 28l4 4 8-8" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M20 44h24" stroke="#bfdbfe" stroke-width="2" stroke-linecap="round"/>
  <path d="M16 50h32" stroke="#dbeafe" stroke-width="2" stroke-linecap="round"/>
  <line x1="32" y1="8" x2="32" y2="14" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
  <line x1="48" y1="16" x2="44" y2="20" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
  <line x1="16" y1="16" x2="20" y2="20" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
  <defs><linearGradient id="gt1" x1="20" y1="16" x2="44" y2="40" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgInnovate = `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="28" fill="#eff6ff"/>
  <path d="M24 38V22a8 8 0 0 1 16 0v16" stroke="url(#gi1)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="32" cy="22" r="4" fill="#93c5fd"/>
  <rect x="26" y="38" width="12" height="4" rx="2" fill="url(#gi1)"/>
  <rect x="28" y="44" width="8" height="3" rx="1.5" fill="#bfdbfe"/>
  <path d="M22 12l2 4M42 12l-2 4M14 22h4M46 22h4" stroke="#93c5fd" stroke-width="1.5" stroke-linecap="round"/>
  <defs><linearGradient id="gi1" x1="24" y1="14" x2="40" y2="42" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const svgGrowth = `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="28" fill="#eff6ff"/>
  <path d="M16 44 L26 34 L34 38 L48 20" stroke="url(#gg1)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <circle cx="48" cy="20" r="4" fill="url(#gg1)"/>
  <path d="M44 20h4v4" stroke="#fff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M16 44 L26 34 L34 38 L48 20 L48 44Z" fill="url(#gg1)" opacity="0.1"/>
  <line x1="16" y1="50" x2="48" y2="50" stroke="#dbeafe" stroke-width="2" stroke-linecap="round"/>
  <defs><linearGradient id="gg1" x1="16" y1="44" x2="48" y2="20" gradientUnits="userSpaceOnUse">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const values = [
  {
    svg: svgCustomer,
    title: '客户至上',
    desc: '深入理解轿运企业的真实痛点，不做脱离业务的技术空想，每一个功能都从客户的实际运营场景出发。',
  },
  {
    svg: svgTech,
    title: '技术驱动',
    desc: '以 AI 和大数据重新定义汽车物流效率，持续投入前沿技术研发，让技术真正服务于业务价值。',
  },
  {
    svg: svgInnovate,
    title: '务实创新',
    desc: '每一次创新都要落地到业务价值，拒绝花哨的概念包装，只做能帮轿运老板解决问题的产品。',
  },
  {
    svg: svgGrowth,
    title: '长期主义',
    desc: '与客户共同成长，持续创造价值。我们不追求短期利益，而是构建长期可信赖的合作伙伴关系。',
  },
]

const team = [
  {
    name: '创始人',
    role: 'CEO & 创始人',
    desc: '深耕汽车物流行业多年，致力于用技术推动整车运输产业的数字化转型升级。',
  },
  {
    name: '技术负责人',
    role: 'CTO',
    desc: '资深技术专家，擅长分布式系统与 AI 应用，主导智途核心技术架构设计与研发。',
  },
  {
    name: '产品负责人',
    role: 'CPO',
    desc: '汽车物流行业产品专家，深度理解整车运输业务场景，主导产品规划与用户体验设计。',
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
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: var(--color-accent);
    filter: blur(120px);
    opacity: 0.2;
    bottom: -30%;
    left: 30%;
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
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
  }
}

/* ========== 使命愿景 ========== */
.mvv-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.mvv-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

.mvv-card {
  padding: 48px 40px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--color-primary-light);
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
  }

  .mvv-svg {
    width: 72px;
    height: 72px;
    margin-bottom: 20px;

    :deep(svg) {
      width: 100%;
      height: 100%;
    }
  }

  h3 {
    font-size: 24px;
    font-weight: 800;
    color: var(--color-text);
    margin-bottom: 16px;
  }

  p {
    font-size: 16px;
    color: var(--color-text-secondary);
    line-height: 1.8;
  }
}

/* ========== 价值观 ========== */
.values-section {
  padding: 100px 0;
  background: var(--color-bg-soft);
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.value-card {
  text-align: center;
  padding: 40px 24px;
  border-radius: var(--radius-lg);
  background: var(--color-bg);
  border: 1px solid var(--color-border-light);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-4px);
  }

  .value-svg {
    width: 56px;
    height: 56px;
    margin: 0 auto 16px;

    :deep(svg) {
      width: 100%;
      height: 100%;
    }
  }

  h3 {
    font-size: 18px;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 12px;
  }

  p {
    font-size: 14px;
    color: var(--color-text-secondary);
    line-height: 1.7;
  }
}

/* ========== 团队 ========== */
.team-section {
  padding: 100px 0;
  background: var(--color-bg);
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.team-card {
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
}

.member-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;

  span {
    font-size: 28px;
    font-weight: 800;
    color: #fff;
  }
}

.team-card h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 4px;
}

.member-title {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 600;
  margin-bottom: 16px;
}

.member-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

/* ========== 联系我们 ========== */
.contact-section {
  padding: 100px 0;
  background: var(--color-bg-soft);
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.contact-card {
  text-align: center;
  padding: 40px 24px;
  border-radius: var(--radius-lg);
  background: var(--color-bg);
  border: 1px solid var(--color-border-light);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }

  .contact-icon {
    font-size: 32px;
    margin-bottom: 16px;
  }

  h4 {
    font-size: 16px;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 8px;
  }

  p {
    font-size: 15px;
    color: var(--color-text-secondary);
  }
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

.cta-actions {
  position: relative;
}

.cta-btn-primary {
  background: #fff !important;
  color: var(--color-primary) !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 14px 36px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  height: auto !important;
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
  .mvv-grid {
    grid-template-columns: 1fr;
  }

  .values-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .team-grid {
    grid-template-columns: 1fr;
    max-width: 400px;
    margin: 0 auto;
  }

  .contact-grid {
    grid-template-columns: 1fr;
    max-width: 400px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .page-hero {
    padding: 120px 0 60px;

    h1 {
      font-size: 36px;
    }
  }

  .mvv-section,
  .values-section,
  .team-section,
  .contact-section,
  .cta-section {
    padding: 64px 0;
  }

  .values-grid {
    grid-template-columns: 1fr;
  }

  .cta-card {
    padding: 48px 24px;

    h2 {
      font-size: 28px;
    }
  }
}
</style>
