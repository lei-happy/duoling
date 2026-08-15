<template>
  <div>
    <!-- Hero -->
    <section class="band band-tight band-paper">
      <div class="wrap">
        <div class="sec-head sec-head--wide hero-head">
          <span class="eyebrow">产品能力</span>
          <h1 class="h-hero hero-title">
            接单、派车、算钱、收钱，<br /><span class="hl">在一套系统里跑完</span>
          </h1>
          <p class="lede">
            {{ BRAND.product }}面向轿运行业（汽车物流），按商品车运输企业的真实动线设计：业务从计划中心进来，经配载、调度、在途、回单，落到能源成本与财务结算，再回到经营分析。带
            <span class="tag tag-pro">旗舰版</span>
            标记的能力属于旗舰版，其余在基础版即可使用。
          </p>
        </div>
      </div>
    </section>

    <!-- 角色视角 -->
    <section id="roles" class="band band-soft band-line">
      <div class="wrap">
        <div class="role-head">
          <div class="sec-head sec-head--flush reveal">
            <span class="eyebrow">五个角色</span>
            <h2 class="h-sec role-title">你的人，每天在系统里做什么</h2>
          </div>
          <div class="reveal">
            <UiTabs
              v-model="role"
              :items="ROLE_TABS"
              aria-label="切换角色"
              panel-id="role-panel"
            />
          </div>
        </div>

        <div id="role-panel" class="role-panel reveal" role="tabpanel">
          <div>
            <span class="tag tag-brand">{{ activeRole.tag }}</span>
            <h3>{{ activeRole.title }}</h3>
            <p class="lede role-lede">{{ activeRole.lede }}</p>
            <ul class="role-list">
              <li v-for="item in activeRole.items" :key="item.text">
                <span class="num">{{ item.when }}</span>
                <span>
                  {{ item.text }}
                  <span v-if="item.pro" class="tag tag-pro">旗舰版</span>
                </span>
              </li>
            </ul>
          </div>

          <!-- 界面示意，纯装饰，对读屏隐藏 -->
          <div class="mock" aria-hidden="true">
            <div class="mock-bar">
              <i /><i /><i /><b>{{ activeRole.mock.title }}</b>
            </div>
            <div class="mock-body">
              <div v-if="activeRole.mock.flow" class="mock-flow">
                <span
                  v-for="node in activeRole.mock.flow"
                  :key="node.text"
                  class="mock-node"
                  :class="node.state && `is-${node.state}`"
                >
                  {{ node.text }}
                </span>
              </div>

              <div v-if="activeRole.mock.kpis" class="mock-kpis">
                <div v-for="k in activeRole.mock.kpis" :key="k.label" class="mock-kpi">
                  <span>{{ k.label }}</span>
                  <b :class="k.tone">{{ k.value }}</b>
                </div>
              </div>

              <div v-if="activeRole.mock.bars" class="mock-bars">
                <i
                  v-for="(h, i) in activeRole.mock.bars"
                  :key="i"
                  :class="{ 'is-hi': i === activeRole.mock.bars.length - 1 }"
                  :style="{ height: `${h}%` }"
                />
              </div>

              <MockRows v-if="activeRole.mock.rows" :rows="activeRole.mock.rows" />

              <div v-if="activeRole.mock.kpisTail" class="mock-kpis">
                <div
                  v-for="k in activeRole.mock.kpisTail"
                  :key="k.label"
                  class="mock-kpi"
                >
                  <span>{{ k.label }}</span>
                  <b :class="k.tone">{{ k.value }}</b>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 四条主线 -->
    <section class="band band-paper">
      <div class="wrap">
        <article
          v-for="(p, i) in PILLARS"
          :id="p.anchor"
          :key="p.step"
          class="pillar reveal"
          :class="{ 'pillar-alt': i % 2 === 1 }"
        >
          <div>
            <span class="pillar-step">{{ p.step }}</span>
            <h2>{{ p.title }}</h2>
            <p class="lede">{{ p.lede }}</p>
            <ul class="pillar-points">
              <li v-for="pt in p.points" :key="pt.name">
                <span class="pt-ico" v-html="pt.icon" />
                <span>
                  <b>{{ pt.name }}</b>：{{ pt.text }}
                  <span v-if="pt.pro" class="tag tag-pro">{{ pt.pro }}</span>
                </span>
              </li>
            </ul>
            <RouterLink v-if="p.link" class="btn btn-text" :to="p.link.to">
              {{ p.link.text }} <span class="arrow">→</span>
            </RouterLink>
            <p v-if="p.note" class="muted">{{ p.note }}</p>
          </div>

          <div class="mock" aria-hidden="true">
            <div class="mock-bar"><i /><i /><i /><b>{{ p.mock.title }}</b></div>
            <div class="mock-body">
              <div v-if="p.mock.flow" class="mock-flow">
                <span
                  v-for="node in p.mock.flow"
                  :key="node.text"
                  class="mock-node"
                  :class="node.state && `is-${node.state}`"
                >
                  {{ node.text }}
                </span>
              </div>

              <MockRows v-if="p.mock.rows" :rows="p.mock.rows" />
              <MockRows v-if="p.mock.rows2" :rows="p.mock.rows2" />

              <div v-if="p.mock.kpis" class="mock-kpis">
                <div v-for="k in p.mock.kpis" :key="k.label" class="mock-kpi">
                  <span>{{ k.label }}</span>
                  <b :class="k.tone">{{ k.value }}</b>
                </div>
              </div>

              <div v-if="p.mock.flowTail" class="mock-flow">
                <span
                  v-for="node in p.mock.flowTail"
                  :key="node.text"
                  class="mock-node"
                  :class="node.state && `is-${node.state}`"
                >
                  {{ node.text }}
                </span>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- 模块全景 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="经营链路" title="模块按经营链路收在一起">
          不按菜单平铺。先选一条链路，看它解决什么经营问题，再看对应模块。带标记的属于旗舰版。
        </SectionHead>

        <div class="reveal">
          <UiTabs
            v-model="chain"
            :items="CHAIN_TABS"
            aria-label="切换经营链路"
            panel-id="chain-panel"
          />
        </div>

        <div id="chain-panel" class="reveal" role="tabpanel">
          <p class="map-why">{{ activeChain.why }}</p>
          <div class="map-mods">
            <div
              v-for="(mod, i) in activeChain.mods"
              :key="mod.name"
              class="mod card-lift"
            >
              <div class="mod-head">
                <h3>{{ mod.name }}</h3>
                <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
              </div>
              <p>{{ mod.desc }}</p>
              <div class="tag-list">
                <span
                  v-for="t in mod.tags"
                  :key="t.text"
                  class="tag"
                  :class="{ 'tag-pro': t.pro }"
                >
                  {{ t.text }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="band band-tight band-deep">
      <div class="wrap cta">
        <div>
          <h2 class="h-sec cta-title">想看这些模块在你企业怎么跑？</h2>
          <p class="lede cta-lede">用你自己的线路和运价，我们做一遍演示。</p>
        </div>
        <div class="btn-row">
          <RouterLink class="btn btn-primary btn-lg" to="/assessment#lead">
            预约 30 分钟演示<span class="arrow">→</span>
          </RouterLink>
          <RouterLink class="btn btn-line btn-lg" to="/pricing">
            看价格方案
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { BRAND } from '@/config/brand';
import { useReveal } from '@/composables/useReveal';
import SectionHead from '@/components/ui/SectionHead.vue';
import UiTabs from '@/components/ui/UiTabs.vue';
import MockRows from '@/components/ui/MockRows.vue';
import type { MockPanel } from '@/components/ui/mock';

useReveal();

/* ------------------------------------------------------------- 角色视角 */

type RoleKey = 'boss' | 'dispatch' | 'captain' | 'finance' | 'driver';

interface RoleView {
  tag: string;
  title: string;
  lede: string;
  items: { when: string; text: string; pro?: boolean }[];
  mock: MockPanel;
}

const ROLE_TABS = [
  { key: 'boss', label: '老板' },
  { key: 'dispatch', label: '调度员' },
  { key: 'captain', label: '车队长' },
  { key: 'finance', label: '财务' },
  { key: 'driver', label: '驾驶员' }
];

const ROLES: Record<RoleKey, RoleView> = {
  boss: {
    tag: '老板 / 总经理',
    title: '不用等月报，也不用问人',
    lede: '进系统第一眼就是经营驾驶舱：这个月赚了多少、哪条线在亏、哪个客户的报价该谈了。',
    items: [
      { when: '每天', text: '看驾驶舱：收入、单车日均利润、亏损线路、在途异常。' },
      {
        when: '每周',
        text: '看运营看板与线路盈利排名，定下周要调的价和要停的线。',
        pro: true
      },
      {
        when: '随时',
        text: '问 AI 数据分析员：上月哪个客户毛利最低，为什么。',
        pro: true
      },
      { when: '按需', text: '审大额费用与例外申请，手机上就能批。' }
    ],
    mock: {
      title: '经营驾驶舱 / 利润总览',
      kpis: [
        { label: '本月毛利', value: '86.4万', tone: 'up' },
        { label: '毛利率', value: '17.8%' },
        { label: '待回款', value: '212万', tone: 'down' }
      ],
      bars: [38, 52, 44, 66, 58, 72, 88],
      rows: [
        { head: true, cells: ['客户', '趟次', '毛利率', '建议'] },
        {
          cells: ['某主机厂华东', '126', '21.4%'],
          nums: [1, 2],
          tag: { text: '保持', kind: 'brand' }
        },
        {
          cells: ['某经销商集团', '48', '6.2%'],
          nums: [1, 2],
          tag: { text: '重谈价', kind: 'pro' }
        }
      ]
    }
  },
  dispatch: {
    tag: '调度员',
    title: '从计划池到派车，不用来回打电话',
    lede: '客户的车辆清单进来就在计划池里，按线路和车型配载成任务单，直接派给自有车或承运商。',
    items: [
      { when: '接单', text: '计划中心接客户需求，支持批量导入与 AI 识别录入。' },
      {
        when: '配载',
        text: '手动配载或让系统推荐板位组合，空板先降下来。',
        pro: true
      },
      { when: '派车', text: '调度工作台看车辆在哪、谁有空，一键派给司机或承运商。' },
      { when: '跟车', text: '在途监控看节点是否超期，异常直接派成待办。' }
    ],
    mock: {
      title: '调度工作台 / 今日待派 18 车',
      rows: [
        { head: true, cells: ['线路', '台数', '可用运力', '状态'] },
        {
          cells: ['上海 → 郑州', '8', '自有 3 车'],
          nums: [1],
          tag: { text: '可配', kind: 'brand' }
        },
        {
          cells: ['宁波 → 合肥', '6', '承运商 2 车'],
          nums: [1],
          tag: { text: '待确认' }
        },
        {
          cells: ['南京 → 武汉', '4', '缺 1 车'],
          nums: [1],
          tag: { text: '去运力大厅', kind: 'pro' }
        }
      ],
      flow: [
        { text: '计划池', state: 'done' },
        { text: '配载中', state: 'live' },
        { text: '待派车' },
        { text: '在途' }
      ]
    }
  },
  captain: {
    tag: '车队长',
    title: '车、人、证照，不再记在本子上',
    lede: '自有车、挂车、驾驶员集中建档，证照和维保到期系统提前提醒，出车审批在线走。',
    items: [
      { when: '管车', text: '车辆、挂车、分组、变更记录全部在册，谁在开哪台车清楚。' },
      { when: '合规', text: '行驶证、营运证、驾驶证、押运资质到期自动预警。' },
      {
        when: '维保',
        text: '维保计划与费用台账，避免临期抛锚耽误交车。',
        pro: true
      },
      { when: '能源', text: '能源卡绑车绑人，加油加气充电流水能追到车与任务。' }
    ],
    mock: {
      title: '证照监控 / 30 天内到期',
      kpis: [
        { label: '在册板车', value: '42' },
        { label: '7 天内到期', value: '3', tone: 'down' },
        { label: '待维保', value: '5' }
      ],
      rows: [
        { head: true, cells: ['车牌 / 人员', '证件', '到期', '状态'] },
        {
          cells: ['苏A·9F21 挂', '营运证', '08-19'],
          nums: [2],
          tag: { text: '5 天', kind: 'pro' }
        },
        {
          cells: ['李师傅', '押运资质', '09-02'],
          nums: [2],
          tag: { text: '19 天' }
        }
      ]
    }
  },
  finance: {
    tag: '财务',
    title: '对账、开票、打款，不再各拉一张表',
    lede: '运费按合同生成，成本按政策归集；客户应收、承运商应付、司机工资与能源账户在同一条资金链上闭环。',
    items: [
      {
        when: '应收',
        text: '客户对账 → 结算 → 开票 → 收款核销，账龄一眼看清。',
        pro: true
      },
      { when: '应付', text: '任务费用、承运商对账结算、自有司机工资单一处处理。' },
      {
        when: '出纳',
        text: '银行账户、打款批次与到账认领，钱在哪看得见。',
        pro: true
      },
      {
        when: '核算',
        text: '经营核算按已确认收入与已审批成本算毛利。',
        pro: true
      }
    ],
    mock: {
      title: '出纳工作台 / 待付款与待认领',
      kpis: [
        { label: '待付款', value: '6 笔', tone: 'down' },
        { label: '待认领到账', value: '3' },
        { label: '本月开票', value: '78万' }
      ],
      rows: [
        { head: true, cells: ['对象', '类型', '金额', '状态'] },
        {
          cells: ['某承运商', '应付结算', '￥18.6万'],
          nums: [2],
          tag: { text: '待打款', kind: 'pro' }
        },
        {
          cells: ['某主机厂', '应收结算', '￥84.2万'],
          nums: [2],
          tag: { text: '待收款', kind: 'brand' }
        },
        {
          cells: ['自有司机 · 7 月', '工资单', '￥9.4万'],
          nums: [2],
          tag: { text: '待审批' }
        }
      ]
    }
  },
  driver: {
    tag: '驾驶员',
    title: '手机上接任务、交回单、看收入',
    lede: '不用回场补录，装车、到货、签收当场拍完就传上去，跑了多少、该拿多少自己看得见。',
    items: [
      { when: '接单', text: '手机收到任务，车辆清单、线路、收货门店都在里面。' },
      { when: '执行', text: '装车、到货、签收逐节点上报，拍照即上传。' },
      { when: '异常', text: '划伤、延误、改配当场提报，调度立刻看到。' },
      { when: '收入', text: '我的收入与账户明细自己查，少扯皮。' }
    ],
    mock: {
      title: `${BRAND.driverProduct} / 我的任务`,
      flow: [
        { text: '接受', state: 'done' },
        { text: '装车', state: 'done' },
        { text: '在途', state: 'live' },
        { text: '到货' },
        { text: '签收' }
      ],
      rows: [
        { head: true, cells: ['任务', '台数', '里程', '回单'] },
        {
          cells: ['上海 → 郑州', '8', '862km'],
          nums: [1, 2],
          tag: { text: '待上传' }
        },
        {
          cells: ['郑州 → 西安', '6', '505km'],
          nums: [1, 2],
          tag: { text: '已完成', kind: 'brand' }
        }
      ],
      kpisTail: [
        { label: '本月趟次', value: '11' },
        { label: '本月里程', value: '7,420' },
        { label: '预计收入', value: '￥13,860', tone: 'up' }
      ]
    }
  }
};

const role = ref<RoleKey>('boss');
const activeRole = computed(() => ROLES[role.value]);

/* ------------------------------------------------------------- 四条主线 */

const ICON = {
  list: '<svg viewBox="0 0 24 24"><path d="M5 7h14M5 12h14M5 17h9"/></svg>',
  deck: '<svg viewBox="0 0 24 24"><rect x="4" y="6" width="16" height="12" rx="2"/><path d="M8 6v12M14 6v12"/></svg>',
  clock: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="M5 12l4 4 10-10"/></svg>',
  doc: '<svg viewBox="0 0 24 24"><path d="M6 4h9l3 3v13H6z"/><path d="M9 12h6M9 16h4"/></svg>',
  chart:
    '<svg viewBox="0 0 24 24"><path d="M4 19V5M4 19h16"/><path d="M8 15V9M12 15v-4M16 15V7"/></svg>',
  flow: '<svg viewBox="0 0 24 24"><path d="M4 8h16M4 16h16"/><circle cx="9" cy="8" r="2"/><circle cx="15" cy="16" r="2"/></svg>',
  card: '<svg viewBox="0 0 24 24"><rect x="4" y="6" width="16" height="12" rx="2"/><path d="M8 10h8M8 14h5"/></svg>',
  board:
    '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 15v-3M12 15V9M16 15v-5"/></svg>',
  spark:
    '<svg viewBox="0 0 24 24"><path d="M12 4l1.7 4L18 9.7l-4.3 1.7L12 16l-1.7-4.6L6 9.7 10.3 8z"/></svg>',
  search:
    '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M15.5 15.5L20 20"/></svg>',
  bell: '<svg viewBox="0 0 24 24"><path d="M12 4a6 6 0 016 6c0 4-2 5-2 7H8c0-2-2-3-2-7a6 6 0 016-6z"/><path d="M10 20h4"/></svg>',
  link: '<svg viewBox="0 0 24 24"><path d="M9 7H7a5 5 0 000 10h2M15 7h2a5 5 0 010 10h-2"/><path d="M8 12h8"/></svg>',
  catalog:
    '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="2"/><path d="M8 10h8M8 14h5"/></svg>',
  shield:
    '<svg viewBox="0 0 24 24"><path d="M12 3l7 3v6c0 4.2-2.9 7.6-7 9-4.1-1.4-7-4.8-7-9V6z"/><path d="M9.5 12l1.8 1.8L15 10"/></svg>'
};

interface Pillar {
  step: string;
  /** 锚点 id，供首页等处深链到具体某条主线 */
  anchor?: string;
  title: string;
  lede: string;
  points: { icon: string; name: string; text: string; pro?: string }[];
  link?: { to: string; text: string };
  note?: string;
  mock: MockPanel;
}

const PILLARS: Pillar[] = [
  {
    step: '主线 01 / 接单到派车',
    title: '单据从进门那一刻就在线',
    lede: '客户发来的车辆清单，无论是 Excel、系统对接还是运单照片，进来就是计划。配载成任务单、派给车和人，在途和回单都跟到底。',
    points: [
      {
        icon: ICON.list,
        name: '计划中心',
        text: '接单、批量导入、拆分与合并，需求不再散落在群里。'
      },
      {
        icon: ICON.deck,
        name: '配载建单',
        text: '按车型与板位组合，手动配载或智能推荐。'
      },
      {
        icon: ICON.clock,
        name: '调度工作台与在途监控',
        text: '谁有空、车在哪、哪个节点超期。'
      },
      {
        icon: ICON.check,
        name: '回单签收',
        text: '司机现场上传，齐不齐一眼看得见。'
      }
    ],
    link: { to: '/assessment#lead', text: '看这条主线的演示' },
    mock: {
      title: '计划中心 / 待配载 34 台',
      rows: [
        { head: true, cells: ['品牌车型', '台数', '提车地', '交车门店'] },
        { cells: ['某品牌 SUV', '6', '上海港', '郑州中原店'], nums: [1] },
        { cells: ['某品牌轿车', '9', '上海仓', '洛阳建业店'], nums: [1] },
        { cells: ['某品牌 MPV', '4', '宁波港', '合肥政务店'], nums: [1] }
      ],
      flowTail: [
        { text: '配载建单', state: 'live' },
        { text: '任务单' },
        { text: '派车' },
        { text: '在途' },
        { text: '签收' }
      ]
    }
  },
  {
    step: '主线 02 / 算钱到收钱',
    title: '运费、能源、结算，在同一条资金链上',
    lede: '报价有合同、成本有政策；油 / 气 / 电进能源账户，客户应收与承运商应付进财务结算。对账、结算、开票、打款与经营核算接在一起，不再各拉一张表。',
    points: [
      {
        icon: ICON.doc,
        name: '运价合同与成本政策',
        text: '报价自动取价；油、路桥、人工、外协按规则摊到每一趟。',
        pro: '成本政策 · 旗舰版'
      },
      {
        icon: ICON.chart,
        name: '能源中心',
        text: '供应商账户、能源卡、充值与消费一本账；异常加注可追。',
        pro: '消费对账分析 · 旗舰版'
      },
      {
        icon: ICON.flow,
        name: '应付路径',
        text: '任务费用工作台、承运商对账结算、自有司机工资单。'
      },
      {
        icon: ICON.card,
        name: '应收 · 出纳 · 发票 · 核算',
        text: '客户对账到回款，银行打款与进销项票，经营核算看毛利。',
        pro: '旗舰版'
      }
    ],
    link: { to: '/pricing', text: '看版本差异' },
    mock: {
      title: '财务结算 / 客户对账 → 结算 → 收款',
      flow: [
        { text: '对账', state: 'done' },
        { text: '结算', state: 'done' },
        { text: '开票', state: 'live' },
        { text: '收款' },
        { text: '核算' }
      ],
      rows: [
        { head: true, cells: ['成本项', '金额', '占比', '口径'] },
        {
          cells: ['司机人工', '￥3,240', '31%'],
          nums: [1, 2],
          tag: { text: '工资单' }
        },
        {
          cells: ['能源费', '￥2,860', '27%'],
          nums: [1, 2],
          tag: { text: '账户扣减' }
        },
        {
          cells: ['路桥', '￥1,910', '18%'],
          nums: [1, 2],
          tag: { text: '按线路' }
        },
        {
          cells: ['外协运费', '￥1,480', '14%'],
          nums: [1, 2],
          tag: { text: '承运商结算' }
        }
      ],
      kpis: [
        { label: '单趟收入', value: '￥13,200' },
        { label: '单趟成本', value: '￥10,490' },
        { label: '单趟毛利', value: '￥2,710', tone: 'up' }
      ]
    }
  },
  {
    step: '主线 03 / 看数与 AI',
    title: '该提醒的事不靠人记，该算的数不靠人拉',
    lede: '经营驾驶舱把结果摆在明面上；AI 数字员工承担录单和取数这类重复活；预警和预测让问题在发生之前被看见。',
    points: [
      {
        icon: ICON.board,
        name: '经营驾驶舱与运营看板',
        text: '收入、成本、利润、履约一屏看完。'
      },
      {
        icon: ICON.spark,
        name: 'AI 录单员',
        text: '读 Excel 与运单照片，直接生成计划。',
        pro: '旗舰版'
      },
      {
        icon: ICON.search,
        name: 'AI 数据分析员',
        text: '用一句话问出线路排名与客户毛利。',
        pro: '旗舰版'
      },
      {
        icon: ICON.bell,
        name: '预警与智能预测',
        text: '证照、运费、回单异常主动提醒；旺季前预判缺车。',
        pro: '旗舰版'
      }
    ],
    link: { to: '/assessment', text: '测测我该先补哪一层' },
    mock: {
      title: 'AI 数字员工 / 数据分析员',
      rows: [
        { head: true, cells: ['你问'] },
        { cells: ['上个月哪条线亏得最多，主要亏在哪？'], full: true },
        { head: true, cells: ['它答'] },
        {
          cells: [
            '成都 → 西安，17 趟合计亏 5,270 元。主要是返程空驶率 61%，且外协单价高于合同均价 8%。'
          ],
          full: true
        }
      ],
      rows2: [
        { head: true, cells: ['它顺手给的动作'] },
        {
          cells: ['建议：在货源大厅挂返程需求；对该线路承运商重新议价。'],
          full: true
        }
      ]
    }
  },
  {
    step: '主线 04 / 对外连接',
    anchor: 'open-platform',
    title: '让 AI 和别的系统，都能接上这套数据',
    lede: '一份能力目录，两个通道：给系统用的标准 REST 接口，给 AI 用的远程 MCP 服务。都在「接入应用」里创建、授权和审计，不用另开一套账号体系。',
    points: [
      {
        icon: ICON.link,
        name: 'MCP 连接器',
        text: '生成配置粘进支持远程 MCP 的 AI 工具，你的 AI 就能读到系统数据。'
      },
      {
        icon: ICON.catalog,
        name: '能力目录',
        text: '每项能力的通道、入参与示例都列出来，当前 MCP 侧开放连接自检与客户、车辆、运单查询。'
      },
      {
        icon: ICON.shield,
        name: '授权与安全',
        text: '按连接勾选能力、Token 仅展示一次、敏感字段自动脱敏、按凭证限流。'
      },
      {
        icon: ICON.clock,
        name: '调用记录',
        text: '时间、能力、通道、状态、耗时、来源 IP 与请求编号全程可查。'
      }
    ],
    note: '当前开放的 MCP 能力均为只读查询；写入类能力在规划中。',
    mock: {
      title: '开放平台 / MCP 连接与调用记录',
      flow: [
        { text: '建应用', state: 'done' },
        { text: '新建连接', state: 'done' },
        { text: '勾选能力', state: 'done' },
        { text: '复制配置', state: 'live' },
        { text: 'AI 里粘贴' }
      ],
      rows: [
        { head: true, cells: ['时间', '能力', '通道', '结果'] },
        {
          cells: ['14:02:11', '查询运单', 'MCP'],
          nums: [0],
          tag: { text: '成功 82ms', kind: 'brand' }
        },
        {
          cells: ['14:02:36', '查询车辆', 'MCP'],
          nums: [0],
          tag: { text: '成功 64ms', kind: 'brand' }
        },
        {
          cells: ['14:05:09', '查询客户', 'MCP'],
          nums: [0],
          tag: { text: '未授权', kind: 'pro' }
        },
        {
          cells: ['14:11:47', '运输指令接收', 'API'],
          nums: [0],
          tag: { text: '成功 131ms', kind: 'brand' }
        }
      ],
      kpis: [
        { label: '已授权能力', value: '4' },
        { label: '本月调用', value: '1,286' },
        { label: '失败率', value: '0.3%', tone: 'up' }
      ]
    }
  }
];

/* ------------------------------------------------------------- 模块全景 */

const CHAIN_TABS = [
  { key: 'ops', label: '接单到交车' },
  { key: 'fleet', label: '运力与能源' },
  { key: 'money', label: '计费到资金' },
  { key: 'intel', label: '智能与连接' },
  { key: 'org', label: '组织底座' }
];

/** 把标签串按「基础版 | 旗舰版」拆成两组，避免逐个手写对象 */
function tags(base: string, pro = '') {
  return [
    ...base.split(' ').filter(Boolean).map((text) => ({ text, pro: false })),
    ...pro.split(' ').filter(Boolean).map((text) => ({ text, pro: true }))
  ];
}

type ChainKey = 'ops' | 'fleet' | 'money' | 'intel' | 'org';

interface ChainView {
  why: string;
  mods: {
    name: string;
    desc: string;
    tags: { text: string; pro: boolean }[];
  }[];
}

const CHAINS: Record<ChainKey, ChainView> = {
  ops: {
    why: '客户需求进来，到配载、派车、在途、回单签收，单据不落地、节点能倒查。',
    mods: [
      {
        name: '运营调度',
        desc: '从接单到签收的主流程。',
        tags: tags('计划中心 配载建单 调度工作台 在途监控 回单签收 任务单台账', '智能配载')
      },
      {
        name: '客商中心',
        desc: '客户、承运商与交车门店档案。',
        tags: tags('客户管理 承运商管理 供应商 互联客户 经销商门店')
      },
      {
        name: '服务平台',
        desc: '缺车找车，空板找货。',
        tags: tags('货源大厅 运力大厅 我的合作 企业名片', '主动联系同行')
      }
    ]
  },
  fleet: {
    why: '车、人、证照和油电气收在一本账里，出车前知道能不能走，跑完知道钱花在哪。',
    mods: [
      {
        name: '运力中心',
        desc: '自有车、外协车、社会运力一起管。',
        tags: tags('自有运力 驾驶员 车辆与挂车 承运商运力 社会运力池 证照监控', '车辆维保')
      },
      {
        name: '能源中心',
        desc: '油、气、电一本账，钱在哪、花在哪看得见。',
        tags: tags(
          '能源账户 能源卡 充值管理 供应商与站点 能源设置',
          '能源消费 数据接入 能源对账 异常中心 成本分析'
        )
      }
    ]
  },
  money: {
    why: '报价有合同、成本有政策；客户应收与承运商应付对上，开票打款能闭环。',
    mods: [
      {
        name: '计费中心',
        desc: '价格与成本的规则都在这里。',
        tags: tags('运价合同 路线管理', '成本政策 承运商合同 费用模板')
      },
      {
        name: '财务结算',
        desc: '从费用确认到收付款与利润核算。',
        tags: tags(
          '费用工作台 费用单台账 承运商对账 承运商结算 司机工资单',
          '对账工作台 出纳工作台 客户对账结算 进销项发票 应收账龄 经营核算'
        )
      }
    ]
  },
  intel: {
    why: '经营结果摆在明面上；重复活交给数字员工；你自己的 AI 也能连进同一套数据。',
    mods: [
      {
        name: '数据洞察',
        desc: '把结果和原因摆出来。',
        tags: tags('经营驾驶舱', '运营看板 数据报表 智能预测')
      },
      {
        name: 'AI 数字员工',
        desc: '承担录单、取数这类重复活。',
        tags: tags('', 'AI录单员 AI数据分析员 对话工作台')
      },
      {
        name: '开放平台',
        desc: '对接客户系统，也给 AI 留了入口。',
        tags: tags('接入应用 MCP连接器 能力目录 接口文档 调用记录')
      }
    ]
  },
  org: {
    why: '谁能看、谁能批、谁改过什么，写清楚，扩张时管理半径不失控。',
    mods: [
      {
        name: '审批中心',
        desc: '该谁批就谁批，留痕可查。',
        tags: tags('我的待办 我的申请 审批记录 审批配置')
      },
      {
        name: '企业配置',
        desc: '组织、权限与基础数据。',
        tags: tags('组织架构 经营主体 员工管理 角色权限 数据管理 系统设置')
      },
      {
        name: '日志中心',
        desc: '谁做了什么，什么时候做的。',
        tags: tags('操作记录 登录记录')
      }
    ]
  }
};

const chain = ref<ChainKey>('ops');
const activeChain = computed(() => CHAINS[chain.value]);
</script>

<style scoped lang="scss">
/* --------------------------------------------------------------- hero */

.hero-head {
  max-width: none;
  margin-bottom: 0;
}

.hero-title {
  font-size: clamp(30px, 3.6vw, 46px);
  margin: 16px 0 18px;
}

/* --------------------------------------------------------------- 角色视角 */

.role-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 30px;
}

.sec-head--flush {
  margin-bottom: 0;
}

.role-title {
  margin-top: 12px;
}

.role-panel {
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  gap: 44px;
  align-items: center;
  background: var(--paper);
  border-radius: var(--r-lg);
  padding: 34px;

  h3 {
    font-size: 22px;
    margin: 10px 0 12px;
  }
}

.role-lede {
  font-size: 15px;
}

.role-list {
  display: grid;
  gap: 12px;
  margin-top: 20px;

  li {
    display: grid;
    grid-template-columns: 62px 1fr;
    gap: 14px;
    align-items: baseline;
    font-size: 15px;
    color: var(--ink-2);
    padding-bottom: 12px;
    border-bottom: 1px solid var(--line-soft);

    &:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }
  }

  .num {
    font-size: 11px;
    color: var(--brand);
    letter-spacing: 0.04em;
  }
}

/* --------------------------------------------------------------- 主线 */

.pillar {
  display: grid;
  grid-template-columns: 1fr 1.08fr;
  gap: 56px;
  align-items: center;

  & + .pillar {
    margin-top: 88px;
    padding-top: 88px;
    border-top: 1px solid var(--line);
  }

  h2 {
    font-size: clamp(24px, 2.4vw, 32px);
    letter-spacing: -0.025em;
    margin: 12px 0 16px;
  }
}

/* 偶数条主线左右对调，长页面读起来有节奏；1024 以下还原为单列 */
.pillar-alt > *:first-child {
  order: 2;
}

.pillar-step {
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--ink-3);
}

.pillar-points {
  display: grid;
  gap: 14px;
  margin: 24px 0 20px;

  li {
    display: grid;
    grid-template-columns: 20px 1fr;
    gap: 12px;
    font-size: 15px;
    color: var(--ink-2);
  }

  b {
    color: var(--ink-1);
    font-weight: 600;
  }
}

.pt-ico :deep(svg) {
  width: 17px;
  height: 17px;
  margin-top: 4px;
  stroke: var(--brand);
  stroke-width: 1.8;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* --------------------------------------------------------------- 模块全景 */

.map-why {
  font-size: 16px;
  color: var(--ink-2);
  margin: 22px 0 24px;
  max-width: 640px;
}

.map-mods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.mod {
  background: var(--paper);
  border-radius: var(--r-lg);
  padding: 22px 24px;

  p {
    font-size: 14px;
    color: var(--ink-3);
    margin-bottom: 14px;
  }
}

.mod-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 12px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--line-soft);

  h3 {
    font-size: 17px;
  }

  .num {
    font-size: 11px;
    color: var(--ink-3);
  }
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
  .role-panel,
  .pillar {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .pillar-alt > *:first-child {
    order: 0;
  }

  .pillar + .pillar {
    margin-top: 56px;
    padding-top: 56px;
  }

  .map-mods {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .role-panel {
    padding: 24px 20px;
  }
}
</style>
