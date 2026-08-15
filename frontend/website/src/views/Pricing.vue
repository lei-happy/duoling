<template>
  <div>
    <!-- Hero + 计价模型 -->
    <section class="band band-tight band-paper">
      <div class="wrap">
        <div class="sec-head sec-head--wide hero-head">
          <span class="eyebrow">价格</span>
          <h1 class="h-hero hero-title">
            基础服务费 + 资源包，<br /><span class="hl">用多少买多少</span>
          </h1>
          <p class="lede">
            系统本身按版本和周期订阅，这部分是固定的。AI
            用量、货源与运力大厅的接单接货按实际用量买资源包，不用就不花钱。旗舰版自带一份初始额度。
          </p>
        </div>

        <div class="model">
          <div
            v-for="(m, i) in MODEL"
            :key="m.title"
            class="model-card reveal"
            :data-stagger="i"
          >
            <span class="num">PART {{ String(i + 1).padStart(2, '0') }}</span>
            <h3>{{ m.title }}</h3>
            <p>{{ m.desc }}</p>
            <ul>
              <li v-for="t in m.items" :key="t">{{ t }}</li>
            </ul>
          </div>
        </div>

        <SectionHead
          class="sec-head--wide rationale-head"
          eyebrow="我们的定价逻辑"
          title="先把流程跑起来，再按管理深度加能力"
        >
          两个版本只按功能深度区分，不按账号数、车辆数设门槛。相对市面同类，把预算留给真正要用起来的模块，而不是先买一堆用不上的席位。
        </SectionHead>
        <div class="grid g-3">
          <div
            v-for="(c, i) in RATIONALE"
            :key="c.title"
            class="card card-tint reveal"
            :data-stagger="i"
          >
            <h3 class="h-card">{{ c.title }}</h3>
            <p>{{ c.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 版本 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <div class="plans-head">
          <div class="sec-head sec-head--flush reveal">
            <span class="eyebrow">选版本</span>
            <h2 class="h-sec plans-title">按管理深度选版本</h2>
          </div>
          <div class="reveal">
            <UiTabs
              v-model="cycle"
              :items="CYCLE_TABS"
              variant="switch"
              aria-label="切换付费周期"
            />
            <p class="cycle-note">
              {{
                cycle === 'year'
                  ? '年付约 8 折，相当于省 2 个多月'
                  : '月付更灵活，随时可以升到年付'
              }}
            </p>
          </div>
        </div>

        <div class="plans">
          <article
            v-for="(plan, i) in PLANS"
            :key="plan.name"
            class="plan reveal"
            :class="{ 'plan-pro': plan.featured }"
            :data-stagger="i"
          >
            <span v-if="plan.featured" class="plan-flag">多数企业的选择</span>

            <div class="plan-top">
              <h3>{{ plan.name }}</h3>
              <span class="tag" :class="{ 'tag-pro': plan.featured }">
                {{ plan.badge }}
              </span>
            </div>
            <p class="plan-for">{{ plan.forWhom }}</p>

            <div class="plan-price">
              <span class="cur">￥</span>
              <b class="num pending">{{ priceOf(plan) }}</b>
              <span class="per">{{ cycle === 'year' ? '/年' : '/月' }}</span>
            </div>
            <p class="muted price-note">价格示意，最终以商务报价为准</p>

            <ul class="plan-inc">
              <li v-for="item in plan.includes" :key="item.text">
                <i>{{ item.all ? '✓' : '+' }}</i>
                <span>
                  <b>{{ item.name }}</b><template v-if="item.text">：{{ item.text }}</template>
                </span>
              </li>
            </ul>

            <div class="plan-cta">
              <RouterLink
                class="btn btn-lg"
                :class="plan.featured ? 'btn-primary' : 'btn-line'"
                to="/assessment#lead"
              >
                {{ plan.cta }}
                <span v-if="plan.featured" class="arrow">→</span>
              </RouterLink>
            </div>

            <p class="plan-foot">
              <template v-if="plan.featured">
                不确定该选哪个？先做
                <RouterLink class="btn-text" to="/assessment">
                  10 题水位快测
                </RouterLink>
                ，按结果推荐。
              </template>
              <template v-else>不限账号与车辆数，按功能深度选版本即可。</template>
            </p>
          </article>
        </div>

        <div class="other-card reveal">
          <h3>你的承运商不用另买一套</h3>
          <p>
            邀请外协单位后，对方就能在企云的协同里管自己的车和司机、接任务、传回单。账号互通，这是租户端能力的一部分，不是单独卖的产品。
          </p>
        </div>
      </div>
    </section>

    <!-- 资源包 -->
    <section class="band band-paper">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="按用量购买" title="三类资源包">
          这些能力的成本随用量变化，所以单独计费。旗舰版会先给一份初始额度，用完再买。
        </SectionHead>

        <div class="grid g-3">
          <div
            v-for="(pack, i) in PACKS"
            :key="pack.title"
            class="pack reveal"
            :data-stagger="i"
          >
            <div class="ico" v-html="pack.icon" />
            <h3>{{ pack.title }}</h3>
            <p>{{ pack.desc }}</p>
            <div class="pack-price">
              <span class="pending">价格待定</span>
              <span class="pack-unit">计量单位：{{ pack.unit }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 版本对比 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead
          class="sec-head--wide"
          eyebrow="版本对比"
          title="两个版本的差别，主要在算钱和用 AI"
        >
          按模块列，不逐条罗列功能点。完整功能清单可以让顾问发你一份。
        </SectionHead>

        <div class="table-scroll reveal">
          <table class="ctable ctable-mid">
            <thead>
              <tr>
                <th>模块</th>
                <th class="cell-c">基础版</th>
                <th class="cell-c col-pro">旗舰版</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in COMPARE" :key="row.name">
                <td class="row-label">
                  <b>{{ row.name }}</b><span>{{ row.sub }}</span>
                </td>
                <td class="cell-c" :class="basicMark(row.basic)">
                  {{ row.basic }}
                </td>
                <td class="cell-c col-pro mark-pro">{{ row.pro }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- 实施与安全 -->
    <section class="band band-paper">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="上线之前先问清" title="自己就能上线，数据归你" />
        <div class="grid g-2">
          <div
            v-for="(c, i) in DELIVERY"
            :key="c.title"
            class="card card-tint reveal"
            :data-stagger="i"
          >
            <h3 class="h-card">{{ c.title }}</h3>
            <p>{{ c.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <div class="sec-head sec-head--wide sec-head--tight reveal">
          <span class="eyebrow">常见问题</span>
          <h2 class="h-sec faq-title">关于价格，你可能想问</h2>
        </div>
        <div class="reveal">
          <UiFaq :items="FAQ" />
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="band band-tight band-deep">
      <div class="wrap cta">
        <div>
          <h2 class="h-sec cta-title">给你算一份具体的账</h2>
          <p class="lede cta-lede">
            按你的车辆数、线路数和现有人手，我们算清一年省多少人工、多看清多少利润。
          </p>
        </div>
        <div class="btn-row">
          <RouterLink class="btn btn-primary btn-lg" to="/assessment#lead">
            找顾问算一算<span class="arrow">→</span>
          </RouterLink>
          <RouterLink class="btn btn-line btn-lg" to="/assessment">
            先做 10 题快测
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useReveal } from '@/composables/useReveal';
import SectionHead from '@/components/ui/SectionHead.vue';
import UiTabs from '@/components/ui/UiTabs.vue';
import UiFaq from '@/components/ui/UiFaq.vue';

useReveal();

const MODEL = [
  {
    title: '基础服务费',
    desc: '按版本订阅，包含系统使用、常规升级与在线支持。可月付或年付，年付更省。',
    items: [
      '基础版：把计划到结算跑成在线闭环，含能源账户与应付路径',
      '旗舰版：再加 AI、财务全套、能源消费分析与深度看板',
      '付费周期越长，单价越低'
    ]
  },
  {
    title: '资源包',
    desc: '按用量计费的能力单独买，避免为不常用的功能付固定钱。',
    items: [
      'AI 用量：录单识别、数据问答、智能配载调用',
      '货源大厅接货、运力大厅接单',
      '用完可续，剩余可结转（规则待定）'
    ]
  }
];

const RATIONALE = [
  {
    title: '为什么没有长期免费版',
    desc: '数字化要有人对结果负责。完全不花钱的试用，项目容易停在半路。基础版用一份可承受的订阅，换来「必须把流程跑起来」的共同约定。'
  },
  {
    title: '基础版扛住最紧的事',
    desc: '面向中小企业：把业务与财务基础流程搬上线——计划到回单、应付结算、能源账户。先在线上把活干完，账才有地方算。'
  },
  {
    title: '旗舰版加更深的管理',
    desc: '在基础版之上叠加 AI、全套财务、能源分析与深度看板。管理诉求到了再选，不必为用不上的席位先付钱。'
  }
];

/* --------------------------------------------------------------- 版本 */

const CYCLE_TABS = [
  { key: 'month', label: '月付' },
  { key: 'year', label: '年付' }
];

const cycle = ref('year');

interface Plan {
  name: string;
  badge: string;
  forWhom: string;
  month: number;
  year: number;
  featured?: boolean;
  cta: string;
  includes: { name: string; text?: string; all?: boolean }[];
}

const PLANS: Plan[] = [
  {
    name: '基础版',
    badge: '业务与财务基础流程',
    forWhom: '先把业务搬上线、把账算清楚。适合还在用 Excel 和微信群管调度的企业。',
    month: 349,
    year: 2999,
    cta: '申请试用',
    includes: [
      { name: '运营调度全流程', text: '计划、配载、调度、在途、回单签收' },
      { name: '运力中心', text: '自有、承运商、社会运力与证照监控' },
      { name: '客商中心', text: '客户、承运商、经销商门店与承运商互联' },
      {
        name: '计费与应付结算',
        text: '运价合同、路线；任务费用、承运商对账结算、司机工资单'
      },
      { name: '能源账户', text: '供应商与站点、账户、能源卡、充值入账' },
      { name: '审批中心与操作留痕' },
      { name: '经营驾驶舱利润总览' },
      { name: '服务平台', text: '大厅浏览、发布货源运力、在线成交' },
      { name: '开放平台与 MCP 连接器', text: '系统对接与自有 AI 接入' }
    ]
  },
  {
    name: '旗舰版',
    badge: '更深的管理能力',
    forWhom:
      '在基础版之上，把 AI、财务全套、能源消费分析与深度看板补齐，让经营节奏从月度变周度。',
    month: 1099,
    year: 9999,
    featured: true,
    cta: '预约演示',
    includes: [
      { name: '包含基础版全部能力', all: true },
      { name: 'AI 数字员工', text: 'AI 录单员、AI 数据分析员' },
      { name: '智能配载', text: '按车型板位推荐组合' },
      { name: '成本政策与承运商运费引擎', text: '成本自动摊到每趟' },
      {
        name: '能源中心全套',
        text: '消费接入、对账、异常风控、单车成本分析'
      },
      {
        name: '财务全套',
        text: '客户应收、出纳打款、进销项发票、经营核算'
      },
      { name: '数据洞察全套', text: '运营看板、数据报表、智能预测' },
      { name: '主动联系同行与服务大厅' },
      { name: '车辆维保台账' }
    ]
  }
];

function priceOf(plan: Plan) {
  return (cycle.value === 'year' ? plan.year : plan.month).toLocaleString('en-US');
}

/* --------------------------------------------------------------- 资源包 */

const PACKS = [
  {
    title: 'AI 用量包',
    desc: 'AI 录单员识别 Excel 与运单照片、数据分析员问答、智能配载调用，都从这份额度里扣。',
    unit: '按识别单据数 / 问答次数（待确认）',
    icon: '<svg viewBox="0 0 24 24"><path d="M12 4l1.7 4L18 9.7l-4.3 1.7L12 16l-1.7-4.6L6 9.7 10.3 8z"/></svg>'
  },
  {
    title: '货源大厅接货包',
    desc: '空板返程时去货源大厅接同行的货，按成功接单的次数扣额度。',
    unit: '按成交单量（待确认）',
    icon: '<svg viewBox="0 0 24 24"><path d="M3 10.5L12 4l9 6.5"/><path d="M5 10v10h14V10"/><path d="M9.5 20v-5h5v5"/></svg>'
  },
  {
    title: '运力大厅接单包',
    desc: '旺季自有车不够时，从运力大厅找同行的车，按成功派出的任务扣额度。',
    unit: '按成交任务数（待确认）',
    icon: '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="13" height="9" rx="2"/><path d="M16 10h3l2 3v3h-5z"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/></svg>'
  }
];

/* --------------------------------------------------------------- 对比表 */

/** 「—」灰掉，「✓/全部」标主色，其余是说明文字，保持正文色 */
function basicMark(value: string) {
  if (value === '—') {
    return 'mark-n';
  }
  return value.startsWith('✓') || value === '全部' ? 'mark-y' : '';
}

const COMPARE = [
  {
    name: '运营调度',
    sub: '计划、配载、调度、在途、回单',
    basic: '全部',
    pro: '全部'
  },
  { name: '智能配载', sub: '按车型板位推荐组合', basic: '—', pro: '✓' },
  {
    name: '运力中心',
    sub: '自有、承运商、社会运力、证照监控',
    basic: '全部',
    pro: '全部 + 车辆维保'
  },
  { name: '客商与承运商互联', sub: '邀请开户、账号互通', basic: '✓', pro: '✓' },
  { name: '计费中心', sub: '运价合同、路线管理', basic: '✓', pro: '✓' },
  {
    name: '成本政策与承运商运费引擎',
    sub: '成本自动摊到每趟',
    basic: '—',
    pro: '✓'
  },
  {
    name: '能源中心 · 账户',
    sub: '供应商站点、账户、卡、充值',
    basic: '✓',
    pro: '✓'
  },
  {
    name: '能源中心 · 消费与分析',
    sub: '消费接入、对账、风控、成本分析',
    basic: '—',
    pro: '✓'
  },
  {
    name: '应付结算',
    sub: '任务费用、承运商对账结算、司机工资单',
    basic: '✓',
    pro: '✓'
  },
  { name: '应收与对账工作台', sub: '客户对账、结算、账龄', basic: '—', pro: '✓' },
  {
    name: '出纳与银行账户',
    sub: '打款批次、到账认领、资金流水',
    basic: '—',
    pro: '✓'
  },
  { name: '进销项发票', sub: '客户开票、供应商收票与核销', basic: '—', pro: '✓' },
  { name: '经营核算', sub: '财务确认口径的收入成本毛利', basic: '—', pro: '✓' },
  { name: '经营驾驶舱', sub: '利润总览', basic: '✓', pro: '✓ 含计划总览' },
  {
    name: '运营看板、数据报表、智能预测',
    sub: '分岗位看数与预判',
    basic: '—',
    pro: '✓'
  },
  {
    name: 'AI 数字员工',
    sub: 'AI 录单员、AI 数据分析员',
    basic: '—',
    pro: '✓ 含初始额度'
  },
  {
    name: '服务平台',
    sub: '货源与运力大厅',
    basic: '浏览、发布、成交',
    pro: '再加主动联系同行'
  },
  {
    name: '开放平台与 MCP 连接器',
    sub: '系统对接 + 你自己的 AI 接入',
    basic: '✓ 全版本可用',
    pro: '✓ 全版本可用'
  },
  {
    name: '服务与支持',
    sub: '在线实施与响应',
    basic: '在线文档与支持',
    pro: '优先在线支持'
  }
];

const DELIVERY = [
  {
    title: '线上实施',
    desc: '开通后按引导配置线路、运价和人员，自己把第一单从计划跑到结算。全程在线上完成，不安排驻场实施。数据随时可导出，不做锁定。'
  },
  {
    title: '数据与安全',
    desc: '按租户隔离，按经营主体和角色分权。谁改过运费、谁确认过到货，操作记录里查得到。'
  }
];

const FAQ = [
  {
    q: '可以先试用再决定吗？',
    a: '可以。开通后按引导导入自己的线路、运价和人员，在线上跑一遍从建计划到出利润。确认好用再订阅。'
  },
  {
    q: '基础版和旗舰版怎么选？',
    a: '看管理深度，不看车辆台数。单据还不在线、回单收不齐，基础版就够把流程跑起来；成本算不清、对账要一周、能源对不上、想让 AI 分担录单和取数，直接上旗舰版。不确定的话，先做 10 题水位快测，结果页会按你的短板给建议。'
  },
  {
    q: '资源包怎么计费，不买会影响正常业务吗？',
    a: '不影响。计划、调度、回单、结算这些主流程都在基础服务费里，不消耗资源包。只有 AI 识别与问答、在大厅接货接单这类按量产生成本的动作才扣额度，额度用完会提前提醒，不会中断在跑的业务。'
  },
  {
    q: '用我们自己的 AI 通过 MCP 连进来，算不算 AI 用量？',
    a: '不算。AI 用量包只对系统内置的 AI 数字员工计费。通过 MCP 连接器接入的是你自己的 AI 工具，算力由你那边承担，我们只提供数据通道和授权控制，开放平台在所有版本里都可以用。'
  },
  {
    q: '我的承运商也要买账号吗？',
    a: '不用。你邀请之后，承运商就能进来接任务、管车和司机、传回单，双方账号互通。这是企云协同能力的一部分，不用单独买一套产品。'
  },
  {
    q: '中途可以升级吗？会不会重新开始算钱？',
    a: '可以随时从基础版升到旗舰版，差价按剩余时长折算，数据和配置全部保留，不需要重新导入。'
  },
  {
    q: '数据安全和归属怎么保证？',
    a: '数据归你所有，按经营主体和角色分权，关键操作全部留痕可审计。需要时可以导出完整业务数据，不做数据锁定。'
  }
];
</script>

<style scoped lang="scss">
/* --------------------------------------------------------------- hero */

.hero-head {
  max-width: none;
  margin-bottom: 36px;
}

.rationale-head {
  margin-top: 48px;
  margin-bottom: 28px;
}

.hero-title {
  font-size: clamp(30px, 3.6vw, 46px);
  margin: 16px 0 18px;
}

.model {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.model-card {
  background: var(--surface-tint);
  border-radius: var(--r-lg);
  padding: 26px 28px;

  .num {
    font-size: 11px;
    letter-spacing: 0.12em;
    color: var(--ink-3);
  }

  h3 {
    font-size: 20px;
    margin: 10px 0;
  }

  p {
    font-size: 15px;
    color: var(--ink-2);
  }

  ul {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--line-soft);
    display: grid;
    gap: 8px;
    font-size: 14px;
    color: var(--ink-2);
  }

  li {
    display: flex;
    gap: 8px;

    &::before {
      content: '·';
      color: var(--brand);
      font-weight: 700;
    }
  }
}

/* --------------------------------------------------------------- 版本卡 */

.plans-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.sec-head--flush {
  margin-bottom: 0;
}

.sec-head--tight {
  margin-bottom: 28px;
}

.plans-title {
  margin-top: 12px;
}

.faq-title {
  margin-top: 12px;
}

.cycle-note {
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 8px;
  text-align: right;
}

.plans {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.plan {
  background: var(--paper);
  border-radius: var(--r-xl);
  padding: 34px;
  position: relative;
}

/* 推荐版本用 tint 表面抬起来，不用品牌色描边圈住 */
.plan-pro {
  background: var(--surface-tint);
  box-shadow: var(--shadow);
}

.plan-flag {
  position: absolute;
  top: 0;
  right: 28px;
  transform: translateY(-50%);
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--brand);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.plan-top {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 10px;

  h3 {
    font-size: 24px;
  }
}

.plan-for {
  margin: 10px 0 22px;
  font-size: 15px;
  color: var(--ink-2);
  min-height: 46px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
  padding-bottom: 8px;

  .cur {
    font-size: 20px;
    font-weight: 600;
  }

  b {
    font-size: 46px;
    font-weight: 600;
    letter-spacing: -0.04em;
    line-height: 1;
  }

  .per {
    font-size: 15px;
    color: var(--ink-3);
  }
}

.price-note {
  margin-bottom: 22px;
  padding-bottom: 22px;
  border-bottom: 1px solid var(--line-soft);
}

.plan-inc {
  display: grid;
  gap: 11px;
  margin-bottom: 26px;

  li {
    display: grid;
    grid-template-columns: 18px 1fr;
    gap: 10px;
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.6;
  }

  i {
    font-style: normal;
    font-family: var(--mono);
    font-size: 13px;
    color: var(--brand);
    padding-top: 2px;
  }

  b {
    color: var(--ink-1);
    font-weight: 600;
  }
}

.plan-cta .btn {
  width: 100%;
}

.plan-foot {
  margin-top: 16px;
  font-size: 13px;
  color: var(--ink-3);
}

.other-card {
  margin-top: 24px;
  background: var(--surface-tint);
  border-radius: var(--r-lg);
  padding: 22px 24px;

  h3 {
    font-size: 16px;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: var(--ink-2);
  }
}

/* --------------------------------------------------------------- 资源包 */

.pack {
  background: var(--surface-tint);
  border-radius: var(--r-lg);
  padding: 24px;

  h3 {
    font-size: 17px;
    margin: 14px 0 8px;
  }

  p {
    font-size: 14px;
    color: var(--ink-2);
    margin-bottom: 14px;
  }
}

.pack-price {
  padding-top: 14px;
  border-top: 1px solid var(--line-soft);
  font-size: 14px;
  color: var(--ink-3);
}

.pack-unit {
  display: block;
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 4px;
}

/* --------------------------------------------------------------- CTA */

.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
}

.cta-title {
  font-size: 26px;
}

.cta-lede {
  margin-top: 10px;
}

/* --------------------------------------------------------------- 响应式 */

@media (max-width: 1024px) {
  .model,
  .plans {
    grid-template-columns: 1fr;
  }

  .cycle-note {
    text-align: left;
  }
}

@media (max-width: 768px) {
  .plan {
    padding: 26px 22px;
  }

  .plan-for {
    min-height: 0;
  }
}
</style>
