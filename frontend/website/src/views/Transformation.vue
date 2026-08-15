<template>
  <div>
    <!-- Hero：主文占满栏宽，引用落在下方通栏，不再锁进 400px 侧栏 -->
    <section class="band band-paper">
      <div class="wrap">
        <span class="eyebrow">给企业管理者的 5 分钟</span>
        <h1 class="h-hero intro-title">
          四个词分不清，<br /><span class="hl">钱就会花错层</span>
        </h1>
        <p class="lede intro-lede">
          信息化、数字化、智能化、数智化，经常被当成四个价位的软件来卖。其实它们是四层能力：解决的问题不同，需要的前提也不同。分不清的代价很具体：业务还在微信和 Excel 里转，就先上 AI 助手；回单还在群里发就先买大屏。最后系统买了一堆，月底还是靠人拉表。
        </p>

        <div class="quote">
          <span class="quote-mark" aria-hidden="true">L</span>
          <div>
            <p>业务不上线，AI 再强也只能做演示</p>
            <span>
              想让 AI 替你干活、帮你做判断，先把计划、派车、回单、结算跑进系统。在线是燃料，智能是引擎。
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- 演进路径 -->
    <section class="band band-tight band-soft band-line">
      <div class="wrap">
        <div class="sec-head sec-head--tight reveal">
          <span class="eyebrow">演进路径</span>
          <h2 class="h-sec path-title">每上一层，管的事不一样</h2>
        </div>

        <div
          class="path reveal"
          aria-label="四层能力演进：信息化、数字化、智能化、数智化"
        >
          <ol class="path-rail">
            <li
              v-for="(layer, i) in LAYERS"
              :key="layer.name"
              :data-tier="i + 1"
            >
              <i class="path-dot" aria-hidden="true" />
              <span class="path-band">{{ layer.band }}</span>
              <b>{{ layer.name }}</b>
              <em>{{ layer.axis }}</em>
            </li>
          </ol>

          <div
            v-for="dim in PATH_DIMS"
            :key="dim.label"
            class="path-dim"
            :data-kind="dim.kind"
          >
            <p class="path-kicker">{{ dim.label }}</p>
            <div class="path-cells">
              <p v-for="(text, i) in dim.texts" :key="LAYERS[i].name">
                {{ text }}
              </p>
            </div>
          </div>
        </div>

        <div class="path-stack reveal">
          <article
            v-for="(layer, i) in LAYERS"
            :key="layer.name"
            :data-tier="i + 1"
          >
            <header>
              <i class="path-dot" aria-hidden="true" />
              <span class="path-band">{{ layer.band }}</span>
              <b>{{ layer.name }}</b>
              <em>{{ layer.axis }}</em>
            </header>
            <div v-for="row in layer.rows" :key="row.label" class="path-row">
              <span>{{ row.label }}</span>
              <p>{{ row.text }}</p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 先在线，再智能 -->
    <section id="online-first" class="band band-paper">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="AI 预算花在哪才值">
          <template #title>
            想让 AI 真正值钱，先问一句：业务在不在线上跑？
          </template>
          AI 很热，但很多项目最后只剩演示。不是模型不够强，而是公司日常业务还在微信、电话、Excel 里完成——AI 拿不到连续、可信的过程，也就没法稳定替你干活。
        </SectionHead>

        <ol class="fuel-logic reveal">
          <li v-for="(item, i) in FUEL_LOGIC" :key="item.title">
            <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
            <b>{{ item.title }}</b>
            <p>{{ item.desc }}</p>
          </li>
        </ol>

        <div class="fuel-compare reveal" data-delay="100">
          <div
            v-for="pane in FUEL_PANES"
            :key="pane.label"
            class="fuel-pane"
            :data-tone="pane.tone"
          >
            <span class="pane-label">{{ pane.label }}</span>
            <h3>{{ pane.title }}</h3>
            <ul>
              <li v-for="t in pane.items" :key="t">{{ t }}</li>
            </ul>
          </div>
        </div>

        <div class="fuel-thesis reveal" data-delay="140">
          <p>
            <b>一句话：在线是燃料管，智能是引擎。</b>
            先把计划到结算跑进系统，再叠加 AI——这不是保守，是让每一分 AI
            预算都花在真业务上。{{ BRAND.product }}的路径，就是按这个顺序建。
          </p>
          <RouterLink class="btn btn-primary" to="/features">
            看在线链路怎么跑<span class="arrow">→</span>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 四层详解 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="逐层看" title="对照一下，你的企业在哪一层">
          左右翻看四层。每一层先看卡住的代价，再看{{ BRAND.product }}在这一层接住什么。第一层「信息化」，就是把业务真正跑在线上。
        </SectionHead>

        <div class="reveal">
          <UiBanner :count="TIERS.length" label="四层能力逐层详解">
            <template
              v-for="(tier, i) in TIERS"
              :key="tier.name"
              #[`slide-${i}`]
            >
              <div class="tier">
                <span class="tag tag-brand">
                  第{{ CN_ORDINAL[i] }}层 · {{ tier.band }}
                </span>
                <h3 class="tier-title">{{ tier.name }}</h3>
                <p class="tier-one">{{ tier.summary }}</p>

                <p class="tier-cost">
                  <b>卡住的代价：</b>{{ tier.cost }}
                </p>

                <div class="tier-body">
                  <div>
                    <h4>这一层的企业什么样</h4>
                    <ul class="tier-list">
                      <li v-for="t in tier.symptoms" :key="t">{{ t }}</li>
                    </ul>
                  </div>
                  <div class="tier-value">
                    <h4>{{ BRAND.product }}在这一层接住什么</h4>
                    <ul class="tier-list">
                      <li v-for="t in tier.value" :key="t">{{ t }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </template>
          </UiBanner>
        </div>
      </div>
    </section>

    <!-- 速查表 -->
    <section class="band band-paper">
      <div class="wrap">
        <SectionHead
          class="sec-head--wide check-head"
          eyebrow="管理者速查"
          title="同样一句「我们已经数字化了」，怎么验真假"
        >
          验收任何一层的投入时，只问一句：它改善了哪个经营指标，怎么验证。
        </SectionHead>

        <div class="table-scroll reveal">
          <table class="ctable ctable-mid">
            <thead>
              <tr>
                <th class="col-layer">这一层</th>
                <th>典型动作</th>
                <th>常见假象</th>
                <th>算真做到的标准</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in CHECK_TABLE" :key="row.name">
                <td class="row-label">
                  <b>{{ row.name }}</b><span>{{ row.band }}</span>
                </td>
                <td>{{ row.action }}</td>
                <td>{{ row.illusion }}</td>
                <td>{{ row.standard }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- 避坑 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="避坑" title="四种最常见的花错钱方式" />
        <div class="grid g-2">
          <div
            v-for="(p, i) in PITFALLS"
            :key="p.title"
            class="card reveal"
            :data-stagger="i"
          >
            <h3 class="h-card">{{ p.title }}</h3>
            <p>{{ p.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 90 天小闭环 -->
    <section class="band band-paper">
      <div class="wrap loop-grid">
        <div class="reveal">
          <span class="eyebrow">怎么开始</span>
          <h2 class="h-sec loop-title">从一个小闭环开始，别从大平台开始</h2>
          <p class="lede">
            挑一条主力线路或一个大客户，把「数据采集 → 算出利润 → 发现异常 →
            派人处理 → 结果反馈 →
            改回规则」跑通一遍。一个真的转起来的小闭环，比一个三年建不完的大平台有用得多。
          </p>
          <p class="lede loop-more">
            跑通之后再复制到其他线路、其他分公司。每一轮都要能回答：这次改善了哪个数字。
          </p>
          <div class="btn-row loop-actions">
            <RouterLink class="btn btn-dark" to="/assessment">
              先测我的水位<span class="arrow">→</span>
            </RouterLink>
            <RouterLink class="btn btn-text" to="/features">
              看每层对应的模块
            </RouterLink>
          </div>
        </div>

        <div class="reveal" data-delay="120">
          <svg
            class="loop"
            viewBox="-16 0 592 320"
            role="img"
            aria-label="经营闭环示意：数据采集、算出利润、发现异常、派人处理、结果反馈，最后改回规则形成循环"
          >
            <!--
              椭圆 cx=280 cy=156 rx=210 ry=104。
              五个节点按 72° 均匀落在椭圆上，虚线与圆点共用同一条轨迹。
            -->
            <ellipse
              cx="280"
              cy="156"
              rx="210"
              ry="104"
              fill="none"
              stroke="#e8ebf0"
              stroke-width="1.4"
              stroke-dasharray="5 6"
            />

            <g>
              <circle cx="280" cy="52" r="8" fill="#0065ff" />
              <circle cx="480" cy="124" r="8" fill="#3384ff" />
              <circle cx="403" cy="240" r="8" fill="#3384ff" />
              <circle cx="157" cy="240" r="8" fill="#80b3ff" />
              <circle cx="80" cy="124" r="8" fill="#80b3ff" />
            </g>

            <g font-size="14" font-weight="600" fill="#1a2233">
              <text x="280" y="36" text-anchor="middle">数据采集</text>
              <text x="502" y="110" text-anchor="start">算出利润</text>
              <text x="403" y="266" text-anchor="middle">发现异常</text>
              <text x="157" y="266" text-anchor="middle">派人处理</text>
              <text x="58" y="110" text-anchor="end">结果反馈</text>
            </g>
            <g font-size="12" fill="#8a94a6">
              <text x="280" y="308" text-anchor="middle">
                跑通一条线路，再复制到全公司
              </text>
            </g>

            <g>
              <rect x="196" y="130" width="168" height="52" rx="10" fill="#0065ff" />
              <text
                x="280"
                y="154"
                text-anchor="middle"
                font-size="14"
                font-weight="700"
                fill="#ffffff"
              >
                改回规则
              </text>
              <text
                x="280"
                y="172"
                text-anchor="middle"
                font-size="11"
                fill="#cfe0ff"
              >
                运价 · 成本政策 · 预警阈值
              </text>
            </g>

            <!-- 沿椭圆上沿从「结果反馈」回到「数据采集」 -->
            <g stroke="#0065ff" stroke-width="1.4" fill="none">
              <path d="M88 116 C 110 70, 190 48, 268 52" />
              <path d="M261 47 L268 52 L261 57" />
            </g>
          </svg>
        </div>
      </div>
    </section>

    <!-- 三问 -->
    <section class="band band-deep">
      <div class="wrap">
        <div class="sec-head sec-head--flush reveal">
          <span class="eyebrow">回到三个问题</span>
          <h2 class="h-sec asks-title">立项之前，先把这三句话回答清楚</h2>
          <p class="lede">答不出来的项目，无论方案多漂亮，大概率还停在概念阶段。</p>
        </div>

        <div class="asks reveal" data-delay="100">
          <div v-for="(ask, i) in ASKS" :key="ask.title" class="ask">
            <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
            <h3>{{ ask.title }}</h3>
            <p>{{ ask.desc }}</p>
          </div>
        </div>

        <div class="btn-row asks-actions">
          <RouterLink class="btn btn-primary btn-lg" to="/assessment">
            用 10 题回答第一问<span class="arrow">→</span>
          </RouterLink>
          <RouterLink class="btn btn-line btn-lg" to="/assessment#lead">
            要一份完整转型报告
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
import UiBanner from '@/components/ui/UiBanner.vue';

useReveal();

const CN_ORDINAL = ['一', '二', '三', '四'];

const LAYERS = [
  {
    band: 'L1–L2',
    name: '信息化',
    axis: '流程上线',
    rows: [
      {
        label: '这一层解决什么',
        text: '让计划、派车、回单在线上跑通，节点留下时间和责任人。'
      },
      {
        label: '企业日常会变成什么样',
        text: '调度不再誊表，司机当场交回单，改单能倒查到人。'
      },
      { label: '典型投入误区', text: '系统买了，一线仍在微信和 Excel 里绕路。' }
    ]
  },
  {
    band: 'L3–L4',
    name: '数字化',
    axis: '经营算清',
    rows: [
      {
        label: '这一层解决什么',
        text: '统一口径，把收入和成本算到单车、单线路、单客户。'
      },
      {
        label: '企业日常会变成什么样',
        text: '开会先看数：哪条线亏、哪个客户报价低，当场能对上。'
      },
      { label: '典型投入误区', text: '大屏做了几块，决策仍靠经验和感觉。' }
    ]
  },
  {
    band: 'L5–L6',
    name: '智能化',
    axis: '智能研判',
    rows: [
      {
        label: '这一层解决什么',
        text: '让系统先做推荐、预警和校验，人只确认关键决定。'
      },
      {
        label: '企业日常会变成什么样',
        text: '录单、配载、取数不再全靠人盯，效果能回头核对。'
      },
      { label: '典型投入误区', text: '接了大模型只会聊天，没进真实业务流程。' }
    ]
  },
  {
    band: 'L7–L8',
    name: '数智化',
    axis: '闭环运转',
    rows: [
      {
        label: '这一层解决什么',
        text: '预警变任务、任务有结果、结果改回规则，经营闭环运转。'
      },
      {
        label: '企业日常会变成什么样',
        text: '经营节奏从月度变周度，扩线路时管理方式可以复制。'
      },
      { label: '典型投入误区', text: '项目很多，却没有人感知到反馈循环。' }
    ]
  }
];

const PATH_DIMS = [
  {
    kind: 'solve',
    label: '这一层解决什么',
    texts: LAYERS.map((layer) => layer.rows[0].text)
  },
  {
    kind: 'daily',
    label: '企业日常会变成什么样',
    texts: LAYERS.map((layer) => layer.rows[1].text)
  },
  {
    kind: 'pitfall',
    label: '典型投入误区',
    texts: LAYERS.map((layer) => layer.rows[2].text)
  }
];

const FUEL_LOGIC = [
  {
    title: '你真正想买的，不是「会聊天」',
    desc: '决策者关心的是：少人录单、更快配载、异常更早发现、利润随时问得清。这些都要 AI 嵌进业务流程，而不是停在旁路聊天窗口。'
  },
  {
    title: 'AI 吃的是过程，不是事后汇报',
    desc: '计划何时建、谁派了哪台车、在途改了什么、回单何时签、费用怎么摊——只有这些动作在系统里发生，AI 才有燃料。月底汇总表喂不饱它。'
  },
  {
    title: '业务不上线，AI 只能猜，不能管',
    desc: '单据散落、口径不一、责任人不清时，模型给出的结论看起来合理，却无法核对、无法追责、无法改回规则。投入很容易变成演示费用。'
  }
];

const FUEL_PANES = [
  {
    tone: 'off',
    label: '业务不在线',
    title: 'AI 多半停在旁路',
    items: [
      '录单前还要人先整理 Excel 和聊天记录',
      '配载建议出不来，出来了调度也不敢信',
      '问利润只能得到「大概」，对不上台账',
      '预警找不到责任人，看完仍无人处理'
    ]
  },
  {
    tone: 'on',
    label: '业务在线之后',
    title: 'AI 才能嵌进经营',
    items: [
      '计划、任务、回单本身就是 AI 能直接用的过程',
      '推荐配载可直接进入调度动作，有人确认、有结果',
      '经营问答对着同一套口径，数字说得清、查得回',
      '异常能派成待办，处理结果再改回规则'
    ]
  }
];

const TIERS = [
  {
    band: 'L1–L2',
    name: '信息化',
    summary:
      '让计划、派车、回单在线上跑通。核心成果是业务被系统承载，关键节点留下时间和责任人。',
    cost: '没有稳定的在线业务，后面所有分析和 AI 都建在沙子上。',
    symptoms: [
      '客户需求发在微信群，调度誊到 Excel 台账',
      '派车打电话，改单口头通知，事后再补录',
      '回单拍照发群，结算前才发现少了几张',
      '系统买了，但一线还在系统外绕路'
    ],
    value: [
      '计划中心在线建单，需求不再散落',
      '配载建单与调度工作台，派车进系统',
      '朵灵·司机现场接单、拍回单、报异常',
      '操作记录与审批留痕，改单有人负责'
    ]
  },
  {
    band: 'L3–L4',
    name: '数字化',
    summary:
      '用数据重新认识业务。核心成果是数据能算出经营结果，并且真的改变了动作。',
    cost: '数据只用于事后汇报，报价、砍线、换承运商仍然是拍脑袋。',
    symptoms: [
      '调度的车次、财务的运费、老板的利润三张表对不上',
      '成本要月底人工摊，摊完已是下个月中',
      '报表不少，但决策还是凭经验和感觉',
      '知道整体在赚钱，不知道哪条线在亏'
    ],
    value: [
      '客户、车辆、线路、门店统一建档，一套口径',
      '运价合同自动取价，成本政策自动摊费用',
      '对账中心把客户对账与承运商结算并到一处',
      '经营驾驶舱看单车、单线路、单客户利润'
    ]
  },
  {
    band: 'L5–L6',
    name: '智能化',
    summary:
      '系统从按规则执行，升级为基于数据做研判：预测、推荐、预警、自动校验。前提是前两层已经稳。',
    cost: 'AI 停在旁路工具，投入变成演示费用，业务节奏没有变化。',
    symptoms: [
      '接了智能助手，但只是聊天，没进业务流程',
      '演示很顺，上线后调度还是按老办法配载',
      '说不清 AI 到底省了多少人、多少钱',
      '没有反馈机制，模型错了也没人纠'
    ],
    value: [
      'AI 录单员读 Excel 与运单照片直接建计划',
      '智能配载按车型、板位、线路推荐组合',
      'AI 数据分析员回答经营问题，直接出数',
      '证照到期、运费异常主动预警'
    ]
  },
  {
    band: 'L7–L8',
    name: '数智化',
    summary:
      '数据和智能进入经营机制：预警变任务、任务有结果、结果改回规则。强调的是体系，而不是某一个功能。',
    cost: '项目很多，却没有感知到反馈循环，扩张仍依赖某几个老员工的经验。',
    symptoms: [
      '异常出现后自动派人、限时处理、结果回看',
      '人机分工写得清楚，多大金额升级到谁',
      '每月用经营结果复盘运价与成本政策',
      '扩线路、开分公司时，管理方式可以复制'
    ],
    value: [
      '智能预测接进计划与运力筹备',
      '预警自动派成审批与待办，跟到关闭',
      '货源大厅与运力大厅补运力缺口',
      '开放平台与 MCP，让客户系统和你自己的 AI 读到同一套数据'
    ]
  }
];

const CHECK_TABLE = [
  {
    name: '信息化',
    band: 'L1–L2',
    action: '核心单据上线，流程进系统',
    illusion: '系统买了不少，Excel 仍是真相',
    standard: '核心业务在系统里执行，关键节点可追溯、可追责'
  },
  {
    name: '数字化',
    band: 'L3–L4',
    action: '打通数据、统一口径、算清成本',
    illusion: '大屏做了几块，开会还是拍脑袋',
    standard: '数据改变了报价与线路决策，经营状态随时看得见'
  },
  {
    name: '智能化',
    band: 'L5–L6',
    action: '预测、推荐、预警、自动校验',
    illusion: '演示效果好，上线后没人用',
    standard: '嵌进真实流程，效果能量化，错了能发现能纠正'
  },
  {
    name: '数智化',
    band: 'L7–L8',
    action: '智能结果进入决策与执行闭环',
    illusion: '项目很多，却没有感知到反馈的循环',
    standard: '人机协同成为机制，经营结果持续复盘并驱动迭代'
  }
];

const PITFALLS = [
  {
    title: '把买软件当成完成转型',
    desc: '系统上线只是第一层的成果。只有当数据开始改变报价、排班和线路决策，才算真的走到第二层。'
  },
  {
    title: '把大屏当成数字化管理',
    desc: '大屏只提高了可见性。没有责任机制、任务机制和复盘机制，看见了也不会有人动。'
  },
  {
    title: '把接入大模型当成智能化',
    desc: '能聊天不等于能干活。要看它是否稳定解决具体业务问题，比如把录单时间从两小时压到十分钟。'
  },
  {
    title: '业务不上线就先买 AI',
    desc: '回单还在群里发、派车还在打电话，模型只能生成看起来合理、但没法验证的结论。先把业务跑进系统，AI 才有燃料。'
  }
];

const ASKS = [
  {
    title: '我们在哪',
    desc: '按业务域分别看：卡在系统承载、数据贯通、智能应用，还是经营闭环？'
  },
  {
    title: '缺什么',
    desc: '以最弱的一环决定补齐顺序：业务还没在线，就先别堆 AI。'
  },
  {
    title: '下一件事是什么',
    desc: '选一个 90 天内能验证、且能改善明确经营指标的动作。'
  }
];
</script>

<style scoped lang="scss">
/* --------------------------------------------------------------- hero */

.intro-title {
  font-size: clamp(30px, 3.8vw, 48px);
  margin: 18px 0 20px;
}

.intro-lede {
  max-width: none;
  margin-bottom: 36px;
}

/* 本页导语吃满栏宽；全局 .sec-head 仍锁 720，不改全站默认 */
.sec-head--wide {
  max-width: none;
}

/* --------------------------------------------------------------- 演进路径 */

.sec-head--tight {
  margin-bottom: 28px;
}

.sec-head--flush {
  margin-bottom: 0;
}

.path-title {
  margin-top: 12px;
  font-size: clamp(24px, 2.4vw, 28px);
}

.path {
  background: var(--paper);
  border-radius: var(--r-lg);
  overflow: hidden;
}

.path-stack {
  display: none;
}

.path-rail {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  margin: 0;
  padding: 28px 8px 22px;
  list-style: none;

  li {
    position: relative;
    padding: 0 20px 16px;
  }

  /* 节点之间的轨道：从本列圆点接到下一列圆点 */
  li:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 4px;
    left: 32px;
    width: calc(100% - 12px);
    height: 1px;
    background: var(--line);
  }
}

.path-dot {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-bottom: 14px;
  background: var(--tier-1);
  box-shadow: 0 0 0 4px var(--paper);
}

[data-tier='2'] > .path-dot {
  background: var(--tier-2);
}

[data-tier='3'] > .path-dot {
  background: var(--tier-3);
}

[data-tier='4'] > .path-dot {
  background: var(--tier-4);
}

.path-band {
  display: block;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  font-variant-numeric: tabular-nums;
  color: var(--ink-3);
  line-height: 1;
}

.path-rail b,
.path-stack header b {
  display: block;
  margin: 8px 0 6px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.path-rail em,
.path-stack header em {
  display: block;
  font-size: 13px;
  font-style: normal;
  font-weight: 600;
  color: var(--brand);
}

.path-rail li {
  border-bottom: 2px solid var(--tier-1);
}

.path-rail li[data-tier='2'] {
  border-bottom-color: var(--tier-2);
}

.path-rail li[data-tier='3'] {
  border-bottom-color: var(--tier-3);
}

.path-rail li[data-tier='4'] {
  border-bottom-color: var(--tier-4);
}

.path-dim {
  padding: 18px 8px 8px;
}

.path-dim[data-kind='pitfall'] {
  background: var(--bg);
}

.path-dim + .path-dim {
  box-shadow: inset 0 1px 0 var(--line-soft);
}

.path-kicker {
  padding: 0 20px 10px;
  font-size: 12px;
  color: var(--ink-3);
}

.path-cells {
  display: grid;
  grid-template-columns: repeat(4, 1fr);

  p {
    padding: 0 20px 16px;
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.7;
  }
}

.path-dim[data-kind='pitfall'] .path-cells p {
  color: var(--ink-2);
}

.path-row {
  span {
    display: block;
    font-size: 12px;
    color: var(--ink-3);
    margin-bottom: 6px;
  }

  p {
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.7;
  }
}

/* --------------------------------------------------------------- 先在线，再智能 */

.fuel-logic {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 28px;

  li {
    display: grid;
    gap: 8px;
    align-content: start;
  }

  .num {
    font-size: 13px;
    color: var(--brand);
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

.fuel-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.fuel-pane {
  border-radius: var(--r-lg);
  padding: 24px 26px 22px;
  background: var(--bg);

  &[data-tone='on'] {
    background: var(--surface-tint);
  }

  h3 {
    font-size: 18px;
    margin-bottom: 14px;
    letter-spacing: -0.015em;
  }

  ul {
    display: grid;
    gap: 10px;
  }

  li {
    position: relative;
    padding-left: 14px;
    font-size: 14px;
    color: var(--ink-2);
    line-height: 1.6;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 9px;
      width: 5px;
      height: 1px;
      background: var(--ink-3);
    }
  }

  &[data-tone='on'] li::before {
    background: var(--brand);
  }
}

.pane-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  margin-bottom: 10px;

  &::before {
    content: '';
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
  }
}

.fuel-pane[data-tone='off'] .pane-label {
  color: var(--ink-3);
}

.fuel-pane[data-tone='on'] .pane-label {
  color: var(--brand);
}

.fuel-thesis {
  margin-top: 28px;
  padding: 20px 24px;
  border-radius: var(--r-lg);
  background: var(--ink-0);
  color: var(--ink-inv);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 20px;
  align-items: center;

  p {
    font-size: 16px;
    line-height: 1.7;
    color: rgba(244, 247, 252, 0.88);
  }

  b {
    color: #fff;
    font-weight: 700;
  }

  .btn {
    white-space: nowrap;
  }
}

/* --------------------------------------------------------------- 四层幻灯 */

.tier-title {
  font-size: 28px;
  letter-spacing: -0.025em;
  margin: 8px 0;
}

.tier-one {
  font-size: 16px;
  color: var(--ink-2);
  max-width: none;
  line-height: 1.65;
  margin-bottom: 22px;
}

.tier-cost {
  margin: 0 0 24px;
  padding: 16px 20px;
  border-radius: var(--r);
  background: var(--surface-tint);
  font-size: 16px;
  line-height: 1.65;

  b {
    color: var(--brand);
  }
}

.tier-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;

  h4 {
    font-size: 14px;
    margin-bottom: 12px;
  }
}

.tier-list {
  display: grid;
  gap: 9px;

  li {
    position: relative;
    padding-left: 16px;
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.65;

    &::before {
      content: '';
      position: absolute;
      left: 2px;
      top: 11px;
      width: 5px;
      height: 1px;
      background: var(--ink-3);
    }
  }
}

.tier-value {
  background: var(--bg);
  border-radius: var(--r);
  padding: 18px 20px;

  h4 {
    color: var(--brand);
  }
}

/* --------------------------------------------------------------- 速查表 */

.check-head :deep(.h-sec) {
  white-space: nowrap;
}

.col-layer {
  width: 110px;
}

table.ctable-mid td {
  vertical-align: middle;
}

/* --------------------------------------------------------------- 闭环 */

.loop-grid {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 52px;
  align-items: center;
}

.loop-title {
  margin: 14px 0 18px;
}

.loop-more {
  margin-top: 16px;
}

.loop-actions {
  margin-top: 26px;
}

.loop {
  width: 100%;
  height: auto;

  text {
    font-family: var(--font);
  }
}

/* --------------------------------------------------------------- 三问 */

.asks-title {
  margin: 16px 0;
}

.asks {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--line-dark);
  border: 1px solid var(--line-dark);
  border-radius: var(--r-lg);
  overflow: hidden;
  margin-top: 40px;
}

.ask {
  padding: 28px 26px;

  .num {
    font-size: 12px;
    color: var(--brand-on-dark);
    letter-spacing: 0.1em;
  }

  h3 {
    font-size: 20px;
    margin: 10px 0;
    color: #fff;
  }

  p {
    font-size: 15px;
    color: rgba(244, 247, 252, 0.68);
  }
}

.asks-actions {
  margin-top: 36px;
}

/* --------------------------------------------------------------- 响应式 */

@media (max-width: 1024px) {
  .path-rail,
  .path-dim {
    padding-left: 4px;
    padding-right: 4px;
  }

  .path-rail li,
  .path-kicker,
  .path-cells p {
    padding-left: 14px;
    padding-right: 14px;
  }

  .path-rail li:not(:last-child)::after {
    left: 26px;
  }

  .loop-grid,
  .fuel-compare,
  .tier-body {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .check-head :deep(.h-sec) {
    white-space: normal;
  }

  .fuel-thesis {
    grid-template-columns: 1fr;
    gap: 16px;
    align-items: start;
  }

  .asks {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .fuel-logic {
    grid-template-columns: 1fr;
  }

  .path {
    display: none;
  }

  .path-stack {
    display: grid;
    gap: 12px;
  }

  .path-stack article {
    background: var(--paper);
    border-radius: var(--r-lg);
    padding: 22px 22px 20px;
    border-bottom: 2px solid var(--tier-1);
  }

  .path-stack article[data-tier='2'] {
    border-bottom-color: var(--tier-2);
  }

  .path-stack article[data-tier='3'] {
    border-bottom-color: var(--tier-3);
  }

  .path-stack article[data-tier='4'] {
    border-bottom-color: var(--tier-4);
  }

  .path-stack header {
    margin-bottom: 16px;
  }

  .path-stack .path-row + .path-row {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--line-soft);
  }
}
</style>
