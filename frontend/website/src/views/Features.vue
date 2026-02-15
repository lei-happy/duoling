<template>
  <div class="features-page">
    <!-- Hero -->
    <section class="page-hero">
      <div class="hero-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
      </div>
      <div class="container hero-content">
        <h1 class="scroll-animate">产品功能</h1>
        <p class="scroll-animate" data-delay="100">
          五大核心亮点，全方位赋能整车运输企业数字化升级
        </p>
      </div>
    </section>

    <!-- 功能亮点 -->
    <section
      v-for="(feature, idx) in features"
      :key="feature.title"
      class="feature-section"
      :class="{ reversed: idx % 2 === 1 }"
    >
      <div class="container feature-row">
        <div class="feature-text scroll-animate" :data-direction="idx % 2 === 0 ? 'left' : 'right'">
          <div class="feature-number">0{{ idx + 1 }}</div>
          <h2>{{ feature.title }}</h2>
          <p class="feature-desc">{{ feature.desc }}</p>
          <ul class="feature-list">
            <li v-for="item in feature.highlights" :key="item">
              <span class="check-icon">✓</span>
              {{ item }}
            </li>
          </ul>
          <div class="feature-keywords">
            <span v-for="kw in feature.keywords" :key="kw">{{ kw }}</span>
          </div>
        </div>
        <div class="feature-visual scroll-animate" :data-direction="idx % 2 === 0 ? 'right' : 'left'">
          <div class="visual-card" v-html="feature.svg"></div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card scroll-animate">
          <h2>体验全部功能</h2>
          <p>免费注册，立即解锁整车运输数字化管理新体验</p>
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

/* ---------- 5 大功能亮点 SVG 插画 ---------- */

// 1. AI助理 - 大脑+电路+轿运车
const svgAI = `<svg viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" rx="20" fill="#eff6ff"/>
  <!-- 中央大脑 -->
  <circle cx="200" cy="130" r="60" fill="url(#fa1)" opacity="0.12"/>
  <circle cx="200" cy="130" r="42" fill="url(#fa1)"/>
  <path d="M184 130c0-8.8 7.2-16 16-16s16 7.2 16 16" stroke="#fff" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M188 118c-4-6-2-14 4-18m20 18c4-6 2-14-4-18" stroke="#fff" stroke-width="2" stroke-linecap="round" fill="none"/>
  <circle cx="200" cy="138" r="4" fill="#fff"/>
  <!-- AI发散线 -->
  <line x1="200" y1="82" x2="200" y2="64" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
  <line x1="248" y1="106" x2="262" y2="96" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
  <line x1="152" y1="106" x2="138" y2="96" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
  <circle cx="200" cy="58" r="4" fill="#bfdbfe"/>
  <circle cx="268" cy="92" r="4" fill="#bfdbfe"/>
  <circle cx="132" cy="92" r="4" fill="#bfdbfe"/>
  <!-- 底部面板 -->
  <rect x="100" y="200" width="200" height="60" rx="10" fill="#fff" stroke="#dbeafe" stroke-width="1.5"/>
  <rect x="116" y="216" width="60" height="8" rx="4" fill="#bfdbfe"/>
  <rect x="116" y="232" width="40" height="8" rx="4" fill="#dbeafe"/>
  <rect x="224" y="212" width="56" height="24" rx="8" fill="url(#fa1)"/>
  <text x="252" y="228" text-anchor="middle" font-size="10" fill="#fff" font-weight="600">智能推荐</text>
  <!-- 连接线 -->
  <path d="M200 172v28" stroke="#93c5fd" stroke-width="2" stroke-dasharray="4 3"/>
  <defs><linearGradient id="fa1" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

// 2. 全链路 - 流程节点连线
const svgChain = `<svg viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" rx="20" fill="#eff6ff"/>
  <!-- 节点连线 -->
  <line x1="80" y1="150" x2="320" y2="150" stroke="#dbeafe" stroke-width="3"/>
  <!-- 节点1: 主机厂 -->
  <circle cx="80" cy="150" r="24" fill="url(#fb1)"/>
  <rect x="68" y="142" width="24" height="16" rx="3" fill="#fff" opacity="0.4"/>
  <text x="80" y="198" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">主机厂</text>
  <!-- 节点2: 调度 -->
  <circle cx="160" cy="150" r="24" fill="url(#fb1)" opacity="0.85"/>
  <path d="M152 150h16M160 142v16" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>
  <text x="160" y="198" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">调度</text>
  <!-- 节点3: 在途 -->
  <circle cx="240" cy="150" r="24" fill="url(#fb1)" opacity="0.85"/>
  <path d="M230 154h20l-4-4m4 4l-4 4" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="240" y="198" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">在途</text>
  <!-- 节点4: 交付 -->
  <circle cx="320" cy="150" r="24" fill="url(#fb1)"/>
  <path d="M312 150l5 5 11-11" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="320" y="198" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">交付</text>
  <!-- 箭头指示 -->
  <path d="M108 150l8-6v12z" fill="#bfdbfe"/>
  <path d="M188 150l8-6v12z" fill="#bfdbfe"/>
  <path d="M268 150l8-6v12z" fill="#bfdbfe"/>
  <!-- 上方标签 -->
  <rect x="130" y="80" width="140" height="32" rx="16" fill="#fff" stroke="#dbeafe" stroke-width="1.5"/>
  <text x="200" y="100" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">全链路实时在线</text>
  <path d="M200 112v14" stroke="#bfdbfe" stroke-width="1.5" stroke-dasharray="3 2"/>
  <defs><linearGradient id="fb1" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

// 3. 运营成本 - 费用面板+趋势线
const svgCost = `<svg viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" rx="20" fill="#eff6ff"/>
  <!-- 左侧费用列表 -->
  <rect x="40" y="50" width="150" height="200" rx="12" fill="#fff" stroke="#dbeafe" stroke-width="1.5"/>
  <text x="60" y="78" font-size="12" fill="#1d4ed8" font-weight="700">费用明细</text>
  <rect x="56" y="92" width="80" height="8" rx="4" fill="#bfdbfe"/>
  <rect x="148" y="92" width="28" height="8" rx="4" fill="#dbeafe"/>
  <rect x="56" y="112" width="60" height="8" rx="4" fill="#bfdbfe"/>
  <rect x="148" y="112" width="28" height="8" rx="4" fill="#dbeafe"/>
  <rect x="56" y="132" width="70" height="8" rx="4" fill="#bfdbfe"/>
  <rect x="148" y="132" width="28" height="8" rx="4" fill="#dbeafe"/>
  <rect x="56" y="152" width="50" height="8" rx="4" fill="#bfdbfe"/>
  <rect x="148" y="152" width="28" height="8" rx="4" fill="#dbeafe"/>
  <!-- 异常标记 -->
  <rect x="56" y="176" width="118" height="28" rx="8" fill="#FEF2F2" stroke="#FECACA" stroke-width="1"/>
  <circle cx="72" cy="190" r="6" fill="#EF4444"/>
  <text x="70" y="193" text-anchor="middle" font-size="8" fill="#fff" font-weight="700">!</text>
  <text x="86" y="194" font-size="10" fill="#DC2626" font-weight="600">异常费用预警</text>
  <!-- 右侧趋势图 -->
  <rect x="210" y="50" width="150" height="200" rx="12" fill="#fff" stroke="#dbeafe" stroke-width="1.5"/>
  <text x="230" y="78" font-size="12" fill="#1d4ed8" font-weight="700">成本趋势</text>
  <path d="M230 200 L260 180 L290 190 L320 160 L340 140" stroke="url(#fc1)" stroke-width="2.5" stroke-linecap="round" fill="none"/>
  <circle cx="260" cy="180" r="3" fill="#1d4ed8"/>
  <circle cx="290" cy="190" r="3" fill="#1d4ed8"/>
  <circle cx="320" cy="160" r="3" fill="#1d4ed8"/>
  <circle cx="340" cy="140" r="3" fill="#2563eb"/>
  <path d="M230 200 L260 180 L290 190 L320 160 L340 140 L340 210 L230 210Z" fill="url(#fc1)" opacity="0.08"/>
  <!-- 底部汇总 -->
  <rect x="230" y="216" width="64" height="20" rx="10" fill="url(#fc1)"/>
  <text x="262" y="230" text-anchor="middle" font-size="9" fill="#fff" font-weight="600">环比↓12%</text>
  <defs><linearGradient id="fc1" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

// 4. 智能BI - 数据看板
const svgBI = `<svg viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" rx="20" fill="#eff6ff"/>
  <!-- 看板主体 -->
  <rect x="30" y="40" width="340" height="220" rx="12" fill="#fff" stroke="#dbeafe" stroke-width="1.5"/>
  <!-- 顶部指标 -->
  <rect x="50" y="60" width="90" height="50" rx="8" fill="#eff6ff"/>
  <text x="60" y="78" font-size="9" fill="#64748B">运量 (台)</text>
  <text x="60" y="98" font-size="18" fill="#1d4ed8" font-weight="800">1,286</text>
  <rect x="155" y="60" width="90" height="50" rx="8" fill="#eff6ff"/>
  <text x="165" y="78" font-size="9" fill="#64748B">收入 (万)</text>
  <text x="165" y="98" font-size="18" fill="#1d4ed8" font-weight="800">86.4</text>
  <rect x="260" y="60" width="90" height="50" rx="8" fill="#eff6ff"/>
  <text x="270" y="78" font-size="9" fill="#64748B">利润率</text>
  <text x="270" y="98" font-size="18" fill="#22C55E" font-weight="800">18.2%</text>
  <!-- 柱状图 -->
  <rect x="60" y="180" width="24" height="50" rx="4" fill="#dbeafe"/>
  <rect x="96" y="160" width="24" height="70" rx="4" fill="#bfdbfe"/>
  <rect x="132" y="140" width="24" height="90" rx="4" fill="url(#fd1)"/>
  <rect x="168" y="155" width="24" height="75" rx="4" fill="#bfdbfe"/>
  <rect x="204" y="130" width="24" height="100" rx="4" fill="url(#fd1)"/>
  <rect x="240" y="150" width="24" height="80" rx="4" fill="#bfdbfe"/>
  <!-- 右侧饼图 -->
  <circle cx="316" cy="185" r="36" fill="#dbeafe"/>
  <path d="M316 149 A36 36 0 0 1 348 201Z" fill="url(#fd1)"/>
  <path d="M316 149 A36 36 0 0 0 284 201Z" fill="#93c5fd"/>
  <circle cx="316" cy="185" r="18" fill="#fff"/>
  <defs><linearGradient id="fd1" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

// 5. 移动办公 - 手机界面
const svgMobile = `<svg viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" rx="20" fill="#eff6ff"/>
  <!-- 手机1: 司机端 -->
  <rect x="80" y="40" width="100" height="200" rx="16" fill="url(#fe1)"/>
  <rect x="88" y="56" width="84" height="160" rx="8" fill="#fff" opacity="0.15"/>
  <rect x="96" y="68" width="68" height="12" rx="6" fill="#fff" opacity="0.3"/>
  <rect x="96" y="88" width="68" height="40" rx="8" fill="#fff" opacity="0.2"/>
  <text x="130" y="113" text-anchor="middle" font-size="10" fill="#fff" font-weight="600">待接运单</text>
  <rect x="96" y="136" width="68" height="28" rx="8" fill="#fff" opacity="0.35"/>
  <text x="130" y="154" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">一键接单</text>
  <rect x="96" y="172" width="30" height="24" rx="6" fill="#fff" opacity="0.2"/>
  <text x="111" y="188" text-anchor="middle" font-size="8" fill="#fff">拍照</text>
  <rect x="134" y="172" width="30" height="24" rx="6" fill="#fff" opacity="0.2"/>
  <text x="149" y="188" text-anchor="middle" font-size="8" fill="#fff">导航</text>
  <text x="130" y="254" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">司机端</text>
  <!-- 手机2: 管理端 -->
  <rect x="220" y="40" width="100" height="200" rx="16" fill="url(#fe1)" opacity="0.85"/>
  <rect x="228" y="56" width="84" height="160" rx="8" fill="#fff" opacity="0.15"/>
  <rect x="236" y="68" width="68" height="12" rx="6" fill="#fff" opacity="0.3"/>
  <rect x="236" y="88" width="32" height="32" rx="6" fill="#fff" opacity="0.2"/>
  <rect x="274" y="88" width="32" height="32" rx="6" fill="#fff" opacity="0.2"/>
  <rect x="236" y="126" width="32" height="32" rx="6" fill="#fff" opacity="0.2"/>
  <rect x="274" y="126" width="32" height="32" rx="6" fill="#fff" opacity="0.2"/>
  <rect x="236" y="168" width="68" height="28" rx="8" fill="#fff" opacity="0.25"/>
  <text x="270" y="186" text-anchor="middle" font-size="9" fill="#fff" font-weight="600">实时看板</text>
  <text x="270" y="254" text-anchor="middle" font-size="11" fill="#1d4ed8" font-weight="600">管理端</text>
  <!-- 中间连接 -->
  <path d="M184 140 C200 140, 200 140, 216 140" stroke="#bfdbfe" stroke-width="2" stroke-dasharray="4 3"/>
  <circle cx="200" cy="140" r="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>
  <path d="M196 140h8M200 136v8" stroke="#2563eb" stroke-width="1.5" stroke-linecap="round"/>
  <defs><linearGradient id="fe1" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="#1d4ed8"/><stop offset="1" stop-color="#2563eb"/>
  </linearGradient></defs>
</svg>`

const features = [
  {
    svg: svgAI,
    title: 'AI 助理集成业务过程',
    desc: '将 AI 智能深度融入整车运输全业务流程——从订单匹配、板车调度、配载优化到在途异常处理。智途 AI 助理如同一位永不休息的调度专家，全天候为您智能识别运输风险、自动推荐最优装载与路线方案，让日常调度效率实现质的飞跃。',
    highlights: [
      '智能调度：基于板车位置、装载能力和交付时限，自动匹配最优运力资源',
      '异常识别：AI 实时监控运输全程，超时停留、路线偏离、恶劣天气提前预警',
      '配载推荐：根据车型尺寸与目的地，自动生成最优装载方案，提高板车利用率',
    ],
    keywords: ['智能调度', '异常识别', '配载优化'],
  },
  {
    svg: svgChain,
    title: '业务全链路在线管理',
    desc: '从主机厂下发运输指令、调度中心派车、板车装车出发、在途实时跟踪，到经销商验车签收、回单确认，整车运输全业务链路在线化管理。告别纸质验车单和电话问位置，让每一台商品车的运输状态实时可视、多方协同。',
    highlights: [
      '全流程在线：运输指令、装车清单、验车报告全部电子化，VIN 码扫码即录',
      '实时协同：主机厂、调度中心、司机、经销商四方在线协作，信息零延迟',
      '无纸化交接：电子验车签收，在线对账结算，大幅降低人工成本与纠纷',
    ],
    keywords: ['全流程', '实时协同', '无纸化'],
  },
  {
    svg: svgCost,
    title: '运营成本实时在线',
    desc: '油费、过路费、维修费、保险费等运营成本实时归集到每一票运单、每台板车、每条线路。每一笔费用清晰可追溯，异常支出自动预警，帮助轿运企业从根本上做到降本增效，清晰掌握每条线路的真实利润。',
    highlights: [
      '费用归集：按运单、板车、线路多维度自动归集，单车运输成本一目了然',
      '异常预警：超出预算或偏离历史水平的费用自动标记提醒，杜绝跑冒滴漏',
      '利润透视：实时查看每条线路、每个客户的真实利润率，辅助报价与经营决策',
    ],
    keywords: ['费用管控', '异常预警', '利润透视'],
  },
  {
    svg: svgBI,
    title: '智能 BI 报表',
    desc: '自动生成运营分析报表，从运量趋势、收入结构、线路盈利到客户贡献，多维度数据钻取分析。告别手工统计与 Excel 汇总，让管理层实时掌握企业经营全貌，每一个决策都有数据支撑。',
    highlights: [
      '可视化看板：运量、收入、成本、利润核心指标一目了然，实时数据大屏',
      '多维分析：按时间、线路、主机厂、经销商等维度自由组合，深度钻取分析',
      '决策支持：历史对标与趋势预测，辅助报价策略制定与运力投入决策',
    ],
    keywords: ['数据看板', '多维分析', '决策支持'],
  },
  {
    svg: svgMobile,
    title: '移动办公更快捷、更高效',
    desc: '手机端随时随地处理整车运输业务。司机在线接单、装车拍照、交车验收、费用申报一键完成；管理者随时审批、查看实时运营数据。移动办公打破时间和空间限制，板车在路上也能高效协同。',
    highlights: [
      '司机端：一键接单、装车拍照记录、交车扫码验收、费用提交，全在手机完成',
      '管理端：随时审批、查看实时运营看板、异常通知即时处理，移动决策不延迟',
      '消息推送：发运指令、到车通知、异常预警自动推送，不遗漏任何关键节点',
    ],
    keywords: ['随时随地', '移动协同', '效率翻倍'],
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
    background: var(--color-accent);
    filter: blur(100px);
    opacity: 0.3;
    top: -20%;
    right: 10%;
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

/* ========== Feature Sections ========== */
.feature-section {
  padding: 100px 0;
  background: var(--color-bg);

  &:nth-child(odd) {
    background: var(--color-bg-soft);
  }
}

.feature-row {
  display: flex;
  align-items: center;
  gap: 64px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.reversed .feature-row {
  flex-direction: row-reverse;
}

.feature-text {
  flex: 1;
}

.feature-number {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 0.1em;
  margin-bottom: 12px;
  font-family: var(--font-mono);
}

.feature-text h2 {
  font-size: 32px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.feature-desc {
  font-size: 16px;
  color: var(--color-text-secondary);
  line-height: 1.8;
  margin-bottom: 28px;
}

.feature-list {
  list-style: none;
  margin-bottom: 24px;

  li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 15px;
    color: var(--color-text);
    line-height: 1.6;
    margin-bottom: 12px;
  }
}

.check-icon {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.feature-keywords {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;

  span {
    font-size: 13px;
    padding: 6px 16px;
    border-radius: 100px;
    background: var(--color-bg-muted);
    color: var(--color-primary);
    font-weight: 600;
  }
}

/* ========== Visual Card (SVG 插画) ========== */
.feature-visual {
  flex: 0 0 420px;
}

.visual-card {
  width: 100%;
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    filter: drop-shadow(0 8px 24px rgba(29, 78, 216, 0.12));
  }

  :deep(svg) {
    width: 100%;
    height: auto;
    display: block;
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
  .feature-row,
  .reversed .feature-row {
    flex-direction: column;
    gap: 40px;
  }

  .feature-visual {
    flex: none;
    width: 100%;
    max-width: 420px;
  }
}

@media (max-width: 768px) {
  .page-hero {
    padding: 120px 0 60px;

    h1 {
      font-size: 36px;
    }
  }

  .feature-section {
    padding: 64px 0;
  }

  .feature-text h2 {
    font-size: 26px;
  }

  .cta-section {
    padding: 64px 0;
  }

  .cta-card {
    padding: 48px 24px;

    h2 { font-size: 28px; }
  }
}
</style>
