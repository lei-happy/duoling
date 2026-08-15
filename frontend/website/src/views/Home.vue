<template>
  <div>
    <!-- Hero：左边说清定位，右边直接给一张真实的驾驶舱切片 -->
    <section class="band-deep hero">
      <div class="wrap hero-grid">
        <div>
          <span class="eyebrow">轿运行业 · 汽车物流</span>
          <h1 class="h-hero">企业的利润，<br />不该等到月底才知道</h1>
          <p class="lede">
            {{ BRAND.product
            }}面向轿运行业（汽车物流）——把商品车运输的计划、配载、调度、回单、对账、结算装进一条在线链路。
            它是企业的综合操作系统：流程、资金与成本分析收在一处，每台车、每条线、每个客户赚没赚，随时算得出来。
          </p>
          <div class="hero-actions">
            <RouterLink class="btn btn-primary btn-lg" to="/assessment#lead">
              预约演示<span class="arrow">→</span>
            </RouterLink>
            <RouterLink class="btn btn-line btn-lg" to="/assessment">
              3 分钟测我的数智化水位
            </RouterLink>
          </div>
          <div class="hero-foot">
            <span>专为轿运（商品车整车运输）打造</span>
            <span>外协承运商受邀即可协同</span>
            <span>{{ BRAND.driverProduct }}现场作业</span>
            <span>支持你的 AI 工具直连</span>
          </div>
        </div>

        <div class="mock" aria-hidden="true">
          <div class="mock-bar">
            <i /><i /><i />
            <b>经营驾驶舱 / 本月</b>
          </div>
          <div class="mock-body">
            <div class="mock-kpis">
              <div class="mock-kpi"><span>运输收入</span><b>486.2万</b></div>
              <div class="mock-kpi">
                <span>单车日均利润</span><b class="up">1,240</b>
              </div>
              <div class="mock-kpi">
                <span>亏损线路</span><b class="down">3 条</b>
              </div>
            </div>
            <div class="mock-flow">
              <span class="mock-node is-done">计划</span>
              <span class="mock-node is-done">配载</span>
              <span class="mock-node is-done">派车</span>
              <span class="mock-node is-live">在途 42</span>
              <span class="mock-node">回单</span>
              <span class="mock-node">对账</span>
              <span class="mock-node">结算</span>
            </div>
            <div class="mock-rows">
              <div class="mock-row is-head">
                <span>线路</span><span>趟次</span><span>单趟毛利</span
                ><span>状态</span>
              </div>
              <div class="mock-row">
                <span>上海 → 郑州</span><span class="num">38</span
                ><span class="num">￥2,180</span
                ><span class="tag tag-brand">优</span>
              </div>
              <div class="mock-row">
                <span>广州 → 长沙</span><span class="num">26</span
                ><span class="num">￥940</span><span class="tag">偏低</span>
              </div>
              <div class="mock-row">
                <span>成都 → 西安</span><span class="num">17</span
                ><span class="num">-￥310</span
                ><span class="tag tag-pro">亏损</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 痛点：标题通栏，条目横排，不再把正文锁进半栏 -->
    <section class="band band-paper">
      <div class="wrap">
        <div class="sec-head reveal">
          <span class="eyebrow">企业的日常</span>
          <h2 class="h-sec">这些事，多数企业每天都在重复</h2>
          <p class="lede">
            它们看起来是效率问题，实际上都是同一个问题：业务没有真正在线，数据也就不可能算得准。
          </p>
        </div>

        <ul class="pain-list reveal" data-delay="120">
          <li v-for="(pain, i) in PAINS" :key="pain.title">
            <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
            <b>{{ pain.title }}</b>
            <p>{{ pain.desc }}</p>
          </li>
        </ul>
      </div>
    </section>

    <!-- 四层能力 + 自测钩子 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <div class="stage-hook">
          <div class="reveal">
            <span class="eyebrow">先搞清概念，再花钱</span>
            <h2 class="h-sec stage-hook__title">
              信息化、数字化、智能化、数智化，<br />不是四个价位的软件
            </h2>
            <p class="lede">
              它们是四层能力：先让业务在线上跑通，再让经营算得清，然后让系统辅助判断，最后把智能嵌进经营机制。
              业务还不上线就先买 AI，钱多半花在演示上。
            </p>
            <p class="lede stage-hook__more">
              所以我们不劝你一次买全，而是先帮你量清水位，再决定这 90
              天该补哪一层。
            </p>
            <div class="btn-row stage-hook__actions">
              <RouterLink class="btn btn-dark" to="/assessment">
                开始 10 题快测<span class="arrow">→</span>
              </RouterLink>
              <RouterLink class="btn btn-text" to="/transformation#online-first">
                为什么先在线，再智能
              </RouterLink>
            </div>
          </div>

          <div class="hook-card reveal" data-delay="140">
            <span class="eyebrow">水位刻度</span>
            <p class="hook-card__title">从 L1 到 L8，你的企业在第几格？</p>
            <WaterLadder :index="3" pointer-label="多数企业" />
            <p class="hook-note">
              我们接触过的轿运企业，多数自评落在 L2–L4：系统买了，但对账、成本、利润仍要人工拼。
              短板会封顶档位，所以某一维很弱时，总分再高也上不去。
            </p>
          </div>
        </div>

        <div class="chain reveal" data-delay="80">
          <div
            v-for="(step, i) in CHAIN"
            :key="step.title"
            class="chain-step"
            :data-tier="i + 1"
          >
            <span class="num">STEP {{ String(i + 1).padStart(2, '0') }}</span>
            <h3>{{ step.title }}</h3>
            <p>{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 产品亮点 -->
    <section class="band band-paper">
      <div class="wrap">
        <SectionHead eyebrow="产品亮点" title="朵灵·企云在轿运企业里，具体解决什么">
          不做功能堆叠。下面每一项都对应一段真实存在的浪费。
        </SectionHead>

        <div class="feats">
          <article class="card card-tint feat-lead reveal">
            <div>
              <div class="ico">
                <svg viewBox="0 0 24 24">
                  <path d="M4 6h10M4 12h16M4 18h7" />
                  <circle cx="19" cy="6" r="2" />
                  <circle cx="14" cy="18" r="2" />
                </svg>
              </div>
              <h3 class="h-card">一张单子，从录入到收款不落地</h3>
              <p>
                客户需求进来就建计划，配载成任务单、派给车和司机，在途可查、回单在线签收，
                然后直接进对账和结算。中间不再落到 Excel，也不需要谁在群里催。
              </p>
              <div class="feat-tags">
                <span v-for="t in LEAD_FEAT_TAGS" :key="t" class="tag">
                  {{ t }}
                </span>
              </div>
            </div>
            <div class="mock" aria-hidden="true">
              <div class="mock-bar">
                <i /><i /><i />
                <b>任务单 DL-24081207 / 上海 → 郑州</b>
              </div>
              <div class="mock-body">
                <div class="mock-flow">
                  <span class="mock-node is-done">建计划</span>
                  <span class="mock-node is-done">配载</span>
                  <span class="mock-node is-done">派车</span>
                  <span class="mock-node is-live">在途</span>
                  <span class="mock-node">签收</span>
                  <span class="mock-node">结算</span>
                </div>
                <div class="mock-rows">
                  <div class="mock-row is-head">
                    <span>节点</span><span>操作人</span><span>时间</span
                    ><span>凭证</span>
                  </div>
                  <div class="mock-row">
                    <span>装车完成</span><span>王强（车队长）</span
                    ><span class="num">08-12 09:24</span
                    ><span class="tag tag-brand">6 张</span>
                  </div>
                  <div class="mock-row">
                    <span>到货签收</span><span>李师傅（司机）</span
                    ><span class="num">08-13 15:07</span
                    ><span class="tag tag-brand">已上传</span>
                  </div>
                  <div class="mock-row">
                    <span>运费确认</span><span>财务 · 待确认</span
                    ><span class="num">—</span><span class="tag">待处理</span>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <article
            v-for="(feat, i) in FEATURES"
            :key="feat.title"
            class="card card-tint card-lift reveal"
            :data-stagger="i % 2"
          >
            <div class="ico" v-html="feat.icon" />
            <h3 class="h-card">{{ feat.title }}</h3>
            <p>{{ feat.desc }}</p>
            <div class="feat-tags">
              <span
                v-for="t in feat.tags"
                :key="t.label"
                class="tag"
                :class="{ 'tag-pro': t.pro }"
              >
                {{ t.label }}
              </span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 开放平台 / MCP -->
    <section class="band band-soft band-line">
      <div class="wrap mcp-grid">
        <div class="reveal">
          <span class="eyebrow">面向 AI 时代的开放能力</span>
          <h2 class="h-sec mcp-title">你自己的 AI，<br />也能直接连进系统</h2>
          <p class="lede">
            系统里有我们内置的 AI 数字员工。但如果你的团队已经在用别的 AI 工具，
            不必再等我们做功能：开放平台会生成一段 MCP 连接配置，复制粘贴进去，
            AI 就能按你授权的范围读到系统里的客户、车辆和运单。
          </p>
          <ul class="mcp-points">
            <li v-for="(p, i) in MCP_POINTS" :key="p.title">
              <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
              <div>
                <b>{{ p.title }}</b>
                <p>{{ p.desc }}</p>
              </div>
            </li>
          </ul>
          <div class="btn-row mcp-actions">
            <RouterLink class="btn btn-dark" to="/features#open-platform">
              看开放平台怎么接<span class="arrow">→</span>
            </RouterLink>
          </div>
        </div>

        <div class="reveal" data-delay="120">
          <CodeCard
            filename="MCP 连接配置 / 一键复制"
            :html="MCP_CONFIG_HTML"
            :raw="MCP_CONFIG_RAW"
          >
            <template #foot>
              <span class="lbl">这条连接被授权的能力</span>
              <span class="tag tag-ro">连接自检</span>
              <span class="tag tag-ro">查询客户</span>
              <span class="tag tag-ro">查询车辆</span>
              <span class="tag tag-ro">查询运单</span>
              <span class="tag">只读</span>
            </template>
          </CodeCard>
          <p class="muted mcp-note">
            同一套能力目录也提供标准 REST 接口，用于和主机厂 DMS、客户 TMS
            做系统级对接。
          </p>
        </div>
      </div>
    </section>

    <!-- 补充能力 -->
    <section class="band band-tight band-paper">
      <div class="wrap">
        <div class="sec-head sec-head--tight reveal">
          <h2 class="h-sec h-sec--sm">还有这些，扩张的时候你会用到</h2>
        </div>
        <div class="grid g-4">
          <div
            v-for="(extra, i) in EXTRAS"
            :key="extra.title"
            class="card card-soft reveal"
            :data-stagger="i"
          >
            <h3 class="h-sub">{{ extra.title }}</h3>
            <p class="muted">{{ extra.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 成效 -->
    <section class="band band-tight band-paper band-line">
      <div class="wrap">
        <div class="sec-head sec-head--tight reveal">
          <span class="eyebrow">上线之后</span>
          <h2 class="h-sec h-sec--sm metric-title">变化通常先出现在这四个地方</h2>
        </div>
        <div class="stat-row reveal">
          <div v-for="s in METRICS" :key="s.label" class="stat">
            <div class="stat-val">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
        <p class="metric-note">
          以上为<span class="pending">示意数据，待真实客户案例校准</span>后再对外发布。
        </p>
      </div>
    </section>

    <!-- 定价预览 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead eyebrow="价格" title="基础服务费 + 资源包，用多少买多少">
          基础服务费按版本和周期订阅；AI 用量、货源与运力大厅的接单接货按资源包购买，旗舰版自带初始额度。
        </SectionHead>

        <div class="plans-mini">
          <div class="plan-mini reveal">
            <div class="plan-mini-head">
              <h3>基础版</h3>
              <span class="tag">中小企业</span>
            </div>
            <p class="muted">把计划到结算跑成在线闭环，含能源账户与应付路径。</p>
            <div class="price">
              <span>￥</span><b class="num pending">2,999</b><span>/年起</span>
            </div>
            <ul>
              <li>运营调度、运力中心、客商中心</li>
              <li>运价合同、应付结算与能源账户</li>
              <li>审批中心与驾驶舱利润总览</li>
              <li>货源与运力大厅（可发布、可成交）</li>
            </ul>
            <RouterLink class="btn btn-line plan-mini__cta" to="/pricing">
              看包含的模块
            </RouterLink>
          </div>

          <div class="plan-mini is-pro reveal" data-delay="100">
            <div class="plan-mini-head">
              <h3>旗舰版</h3>
              <span class="tag tag-pro">推荐</span>
            </div>
            <p class="muted">在基础版之上加 AI、财务全套、能源分析与深度看板。</p>
            <div class="price">
              <span>￥</span><b class="num pending">9,999</b><span>/年起</span>
            </div>
            <ul>
              <li>AI 数字员工与智能配载</li>
              <li>应收、出纳、发票、经营核算全套</li>
              <li>能源消费分析与成本政策引擎</li>
              <li>运营看板、数据报表、智能预测</li>
              <li>含初始 AI 用量额度</li>
            </ul>
            <RouterLink class="btn btn-primary plan-mini__cta" to="/pricing">
              对比两个版本<span class="arrow">→</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- 实施与安全 -->
    <section class="band band-paper">
      <div class="wrap">
        <SectionHead eyebrow="上线之前先问清" title="自己就能上线，数据归你" />
        <div class="grid g-2">
          <div class="card card-tint reveal">
            <h3 class="h-card">线上实施</h3>
            <p>
              开通后按引导配置线路、运价和人员，自己把第一单从计划跑到结算。全程在线上完成，不安排驻场实施。数据随时可导出，不做锁定。
            </p>
          </div>
          <div class="card card-tint reveal" data-stagger="1">
            <h3 class="h-card">数据与安全</h3>
            <p>
              按租户隔离，按经营主体和角色分权。谁改过运费、谁确认过到货，操作记录里查得到。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 客户见证占位 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead eyebrow="客户见证" title="先把真实案例写清楚，再对外说" />
        <div class="proof-empty reveal">
          <p>
            轿运企业的授权案例与成效数字校准后，会放在这里。现在不编造客户名，也不提前写百分比。
          </p>
          <div class="proof-marks">
            <span v-for="i in 3" :key="i">待客户授权</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 结尾 CTA -->
    <section id="cta" class="band band-deep">
      <div class="wrap cta-final">
        <span class="eyebrow">下一步</span>
        <h2 class="h-sec cta-final__title">先量水位，再决定花钱的顺序</h2>
        <p class="lede">
          我们更愿意先花 30 分钟看你现在的单据怎么流转、成本怎么算，再告诉你哪一层值得先补。
        </p>
        <div class="btn-row">
          <RouterLink class="btn btn-primary btn-lg" to="/assessment">
            开始 10 题快测<span class="arrow">→</span>
          </RouterLink>
          <RouterLink class="btn btn-line btn-lg" to="/assessment#lead">
            预约 30 分钟演示
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { BRAND } from '@/config/brand';
import { useReveal } from '@/composables/useReveal';
import SectionHead from '@/components/ui/SectionHead.vue';
import WaterLadder from '@/components/ui/WaterLadder.vue';
import CodeCard from '@/components/ui/CodeCard.vue';

useReveal();

const PAINS = [
  {
    title: '计划在微信，台账在 Excel',
    desc: '客户的运输需求发在群里，调度誊到表格，改一次要同步三个地方。'
  },
  {
    title: '回单靠拍照，齐不齐没人说得清',
    desc: '司机把回单发到群里，内勤回场统一补录，结算前才发现少了七八张。'
  },
  {
    title: '外协运费每月要算一周',
    desc: '承运商报的数和自己的记录对不上，扣款、押金、亏舱各算一套，扯皮到月中。'
  },
  {
    title: '亏损线路一直在跑',
    desc: '看着忙、看着有量，摊完油费路桥人工才发现每趟都在贴钱，但没有数据不敢停。'
  },
  {
    title: '旺季找不到车，淡季车找不到货',
    desc: '临时找运力只能打电话问同行，价格随行就市，成本控不住。'
  },
  {
    title: '老板看到的数，永远是上个月的',
    desc: '报表要人做，口径还常常不一致，决策只能靠经验和感觉。'
  }
];

const CHAIN = [
  {
    title: '流程上线',
    desc: '计划、派车、回单在线上跑通，节点有时间也有责任人。'
  },
  {
    title: '经营算清',
    desc: '收入与成本自动归到单车、单线路、单客户，全公司一套口径。'
  },
  {
    title: '智能研判',
    desc: '配载推荐、异常预警、运费校验由系统先算一遍，人只做决定。'
  },
  {
    title: '闭环运转',
    desc: '预警变任务、任务有结果、结果改回规则，形成持续循环。'
  }
];

const LEAD_FEAT_TAGS = [
  '计划中心',
  '配载建单',
  '调度工作台',
  '回单签收',
  '对账中心',
  '发票管理'
];

// 图标统一 24 viewBox、1.6 线宽，样式由 .ico 统一接管
const FEATURES = [
  {
    icon: '<svg viewBox="0 0 24 24"><path d="M4 19V5M4 19h16" /><path d="M7 15l4-5 3 3 5-7" /></svg>',
    title: '利润不是月底才知道',
    desc: '运价合同自动取价，成本政策把油费、路桥、外协、人工按规则摊到每一趟。单车、单线路、单客户的毛利随时能看，报价前就知道这单该不该接。',
    tags: [{ label: '运价合同' }, { label: '成本政策' }, { label: '利润分析' }]
  },
  {
    icon: '<svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="3" /><circle cx="17" cy="10" r="2.4" /><path d="M3 20c0-3 2.2-5 5-5s5 2 5 5" /><path d="M14 20c0-2.2 1.4-3.6 3-3.6S20 17.8 20 20" /></svg>',
    title: '五个角色都在线，流程不断点',
    desc: '司机用朵灵·司机接任务、拍回单、报异常；调度配载派车；车队长审批；财务对账开票；老板看驾驶舱。同一套数据，谁卡住了一眼看得出来。',
    tags: [{ label: '朵灵·司机' }, { label: '审批中心' }, { label: '经营驾驶舱' }]
  },
  {
    icon: '<svg viewBox="0 0 24 24"><circle cx="6.5" cy="12" r="3" /><circle cx="17.5" cy="12" r="3" /><path d="M9.5 12h5" /><path d="M6.5 5.5V9M17.5 15v3.5" /></svg>',
    title: '承运商邀请一下就能协同',
    desc: '发个邀请，外协单位就能进来接任务、管自己的车和司机、回传回单。账号互通，派给他的任务和运费都在线上流转，不用再一遍遍转发和口头确认。',
    tags: [{ label: '承运商管理' }, { label: '互联客户' }, { label: '承运商运费' }]
  },
  {
    icon: '<svg viewBox="0 0 24 24"><path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8z" /><path d="M17.5 15.5l.9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9z" /></svg>',
    title: 'AI 数字员工替人干重复活',
    desc: '录单员读客户发来的 Excel 和运单照片，直接生成运输计划；数据分析员听得懂「上月哪条线亏得最多」，当场把数摆出来。',
    tags: [
      { label: '旗舰版', pro: true },
      { label: 'AI 录单员' },
      { label: 'AI 数据分析员' },
      { label: '智能配载' }
    ]
  },
  {
    icon: '<svg viewBox="0 0 24 24"><path d="M3 10.5L12 4l9 6.5" /><path d="M5 10v10h14V10" /><path d="M9.5 20v-5h5v5" /></svg>',
    title: '货源大厅、运力大厅，资源可控',
    desc: '缺车的时候在运力大厅找同行，空板的时候去货源大厅接货。成交、评价、合作记录都留在系统里，慢慢沉淀成自己能调得动的运力池。',
    tags: [{ label: '货源大厅' }, { label: '运力大厅' }, { label: '我的合作' }]
  },
  {
    icon: '<svg viewBox="0 0 24 24"><path d="M12 4v3M12 17v3M4 12h3M17 12h3" /><circle cx="12" cy="12" r="4.2" /><path d="M6.4 6.4l1.9 1.9M15.7 15.7l1.9 1.9" /></svg>',
    title: '该提醒的事，不靠人记',
    desc: '证照到期、运费异常、回单超期、亏损线路，系统先发现再提醒，并能派成待办跟到底。旺季前还能预测缺多少车，提前筹备。',
    tags: [
      { label: '证照监控' },
      { label: '运营看板' },
      { label: '智能预测', pro: true }
    ]
  }
];

const MCP_POINTS = [
  {
    title: '复制一段配置就连上',
    desc: '生成连接地址与访问 Token，粘进支持远程 MCP 的 AI 工具即可，不需要写代码、不需要导表。'
  },
  {
    title: '能给它看什么，你说了算',
    desc: '按应用、按连接分别勾选能力，当前开放的都是只读查询，联系电话这类敏感字段自动打码。'
  },
  {
    title: '每一次调用都留痕',
    desc: '哪个 AI、什么时候、查了什么、耗时多少，调用记录里查得到，还能按连接限流。'
  }
];

const MCP_CONFIG_RAW = `{
  "mcpServers": {
    "朵灵企云助手": {
      "url": "https://api.zhitu.me/mcp/7f3a9c2e1b4d",
      "headers": {
        "Authorization": "Bearer mcp_····.mcpt_········"
      }
    }
  }
}`;

// 键 / 值 / 注释三色，手写高亮，不为一段示例配置引一整个 highlighter
const MCP_CONFIG_HTML = `{
  <span class="ck">"mcpServers"</span>: {
    <span class="ck">"朵灵企云助手"</span>: {
      <span class="ck">"url"</span>: <span class="cs">"https://api.zhitu.me/mcp/7f3a9c2e1b4d"</span>,
      <span class="ck">"headers"</span>: {
        <span class="ck">"Authorization"</span>: <span class="cs">"Bearer mcp_····.mcpt_········"</span>
      }
    }
  }
}
<span class="cp">// Token 仅在创建时展示一次，遗失后重新生成即可</span>`;

const EXTRAS = [
  {
    title: '多经营主体与数据权限',
    desc: '按主体、组织、角色分权，分公司之间数据不串。'
  },
  {
    title: '标准接口对接主机厂',
    desc: '与客户的 DMS、TMS 打通，运输指令自动进单，不用人工转录。'
  },
  {
    title: '车辆维保与合规台账',
    desc: '维保记录、证照资质集中管理，到期自动提醒。'
  },
  {
    title: '操作留痕与登录审计',
    desc: '谁改了运费、谁确认了到货，全部可追溯。'
  }
];

const METRICS = [
  { value: '-60%', label: '月度对账与结算的人工工时' },
  { value: 'T+1', label: '单车与线路利润的可见时效' },
  { value: '+25pt', label: '回单及时回收率' },
  { value: '-8pt', label: '空板位率' }
];
</script>

<style scoped lang="scss">
/* --------------------------------------------------------------- hero */

.hero {
  padding: 92px 0 100px;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 60px;
  align-items: center;
}

.hero h1 {
  margin: 20px 0 22px;
}

.hero .lede {
  color: rgba(244, 247, 252, 0.74);
  max-width: 640px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 32px 0 26px;
}

.hero-foot {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 26px;
  padding-top: 24px;
  border-top: 1px solid var(--line-dark);
  font-size: 14px;
  color: rgba(244, 247, 252, 0.6);

  span {
    display: flex;
    align-items: center;
    gap: 8px;

    &::before {
      content: '';
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--brand-on-dark);
    }
  }
}

/* --------------------------------------------------------------- 痛点 */

.sec-head--flush {
  margin-bottom: 0;
}

.sec-head--tight {
  margin-bottom: 28px;
}

.h-sec--sm {
  font-size: clamp(22px, 2vw, 26px);
}

.pain-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px 40px;

  li {
    display: grid;
    gap: 8px;
    align-content: start;
  }

  .num {
    font-size: 12px;
    color: var(--ink-3);
  }

  b {
    display: block;
    font-size: 17px;
    letter-spacing: -0.01em;
    line-height: 1.4;
  }

  p {
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.7;
  }
}

/* --------------------------------------------------------------- 演进与自测钩子 */

.stage-hook {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  align-items: center;
  margin-bottom: 44px;
}

.stage-hook__title {
  margin: 14px 0 18px;
}

.stage-hook__more {
  margin-top: 16px;
}

.stage-hook__actions {
  margin-top: 26px;
}

.hook-card {
  background: var(--paper);
  border-radius: var(--r-lg);
  padding: 30px 30px 26px;
  box-shadow: var(--shadow);
}

.hook-card__title {
  font-size: 17px;
  font-weight: 600;
  margin: 10px 0 26px;
}

.hook-note {
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--line-soft);
}

/* --------------------------------------------------------------- 亮点 */

.feats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.feat-lead {
  grid-column: span 2;
  display: grid;
  grid-template-columns: 1fr 1.15fr;
  gap: 40px;
  align-items: center;
}

.feat-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--line-soft);
}

/* --------------------------------------------------------------- 开放平台 */

.mcp-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  align-items: center;
}

.mcp-title {
  margin: 14px 0 18px;
}

.mcp-points {
  display: grid;
  gap: 18px;
  margin-top: 26px;

  li {
    display: grid;
    grid-template-columns: 32px 1fr;
    gap: 14px;
  }

  .num {
    font-size: 12px;
    color: var(--brand);
    padding-top: 3px;
  }

  b {
    display: block;
    font-size: 16px;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: var(--ink-2);
  }
}

.mcp-actions {
  margin-top: 26px;
}

.mcp-note {
  margin-top: 14px;
}

/* --------------------------------------------------------------- 成效 */

.metric-title {
  margin-top: 12px;
}

.metric-note {
  margin-top: 16px;
  font-size: 13px;
  color: var(--ink-3);
}

/* --------------------------------------------------------------- 定价预览 */

.plans-mini {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.plan-mini {
  background: var(--paper);
  border-radius: var(--r-lg);
  padding: 28px;

  /* 推荐版用 tint 表面抬起来，不用品牌色描边圈住 */
  &.is-pro {
    background: var(--surface-tint);
    box-shadow: var(--shadow);
  }

  h3 {
    font-size: 20px;
  }

  ul {
    display: grid;
    gap: 9px;
    margin-bottom: 22px;
    font-size: 15px;
    color: var(--ink-2);
  }

  li {
    display: flex;
    gap: 9px;

    &::before {
      content: '—';
      color: var(--ink-3);
      font-family: var(--mono);
      font-size: 12px;
      padding-top: 3px;
    }
  }

  &.is-pro li::before {
    content: '+';
    color: var(--brand);
  }
}

.plan-mini-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.price {
  display: flex;
  align-items: baseline;
  gap: 3px;
  margin: 14px 0 18px;

  b {
    font-size: 34px;
    font-weight: 600;
  }

  span {
    font-size: 14px;
    color: var(--ink-3);
  }
}

.plan-mini__cta {
  width: 100%;
}

/* --------------------------------------------------------------- 结尾 */

.cta-final {
  text-align: center;
  max-width: 680px;
  margin: 0 auto;

  .btn-row {
    justify-content: center;
    margin-top: 28px;
  }
}

.cta-final__title {
  margin: 16px 0;
}

/* --------------------------------------------------------------- 响应式 */

@media (max-width: 1024px) {
  .hero {
    padding: 64px 0 72px;
  }

  .hero-grid,
  .pain-list,
  .stage-hook,
  .mcp-grid,
  .feat-lead {
    grid-template-columns: 1fr;
    gap: 36px;
  }

  .feats,
  .plans-mini {
    grid-template-columns: 1fr;
  }

  .feat-lead {
    grid-column: span 1;
  }
}
</style>
