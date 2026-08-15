<template>
  <div>
    <!-- Hero：定位 + 行业判断 + 愿景，同一屏说完我们是谁、看见什么、要去哪 -->
    <section class="band band-paper">
      <div class="wrap">
        <div class="sec-head sec-head--wide hero-head">
          <span class="eyebrow">关于我们</span>
          <h1 class="h-hero hero-title">
            我们只做一件事：<br /><span class="hl">让轿运企业的每一公里都算得清</span>
          </h1>
          <p class="lede">
            {{ BRAND.legalEntity }}面向轿运行业（汽车物流）。我们不做通用
            TMS，也不做大而全的物流平台——只服务商品车整车运输企业，把计划到结算这条主线做深。
          </p>
        </div>

        <div class="stance">
          <article>
            <span class="stance-kicker">行业判断</span>
            <h2>轿运不缺软件，缺一条跑得完的经营闭环</h2>
            <p>
              系统买了、大屏上了、模型也接了，业务却还在微信和 Excel
              里转——钱往往花在了错的一层。行业下一步不是再上一个平台，而是先让计划、派车、回单、结算在线上跑起来，数据和
              AI 才有燃料。
            </p>
          </article>
          <article class="stance-vision">
            <span class="stance-kicker">我们的愿景</span>
            <h2>让每一公里都不白跑</h2>
            <p>
              把{{ BRAND.product }}做成轿运企业真正用得起来的综合操作系统：流程在线、账算得清、智能用在真业务上。办公室里管经营的人，和路上跑车的司机，用的是同一套事实。
            </p>
          </article>
        </div>
      </div>
    </section>

    <!-- 我们相信 -->
    <section class="band band-soft band-line">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="我们相信" title="业务先在线，AI 才值钱">
          这不是一句口号，而是产品的建设顺序：先把计划、派车、回单、结算跑进系统，再叠加数据和智能。跳过前面两层直接买
          AI，钱多半花在演示上。
        </SectionHead>

        <div class="grid g-2">
          <div
            v-for="(item, i) in BELIEFS"
            :key="item.title"
            class="card reveal"
            :data-stagger="i"
          >
            <h3 class="h-card">{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 产品线 -->
    <section class="band band-paper">
      <div class="wrap">
        <SectionHead class="sec-head--wide" eyebrow="品牌与产品" title="一个母品牌，两条产品线">
          「朵灵」是母品牌，下面两条产品线各自面向不同的人：办公室里管经营的，和路上跑车的。
        </SectionHead>

        <div class="grid g-2">
          <div class="line-card reveal">
            <span class="tag tag-brand">租户端</span>
            <h3>{{ BRAND.product }}</h3>
            <p>
              {{ BRAND.tagline }}。计划中心、配载调度、运力与能源、计费与财务结算、数据洞察与
              AI 数字员工，收在同一套系统里。
            </p>
            <RouterLink class="btn btn-text" to="/features">
              看产品能力 <span class="arrow">→</span>
            </RouterLink>
          </div>

          <div class="line-card reveal" data-stagger="1">
            <span class="tag">司机端</span>
            <h3>{{ BRAND.driverProduct }}</h3>
            <p>
              司机在手机上接任务、逐节点上报、拍照传回单、查自己的收入。不用回场补录，调度那头当场就能看到。
            </p>
            <p class="muted">随{{ BRAND.product }}一起开通，不单独售卖。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 联系 -->
    <section class="band band-tight band-deep">
      <div class="wrap contact">
        <div>
          <h2 class="h-sec contact-title">想聊聊你的场景？</h2>
          <p class="lede contact-lede">
            留一个联系方式，顾问会带着你的行业情况来找你，不群发资料。
          </p>
          <dl class="contact-list">
            <div>
              <dt>公司主体</dt>
              <dd>{{ BRAND.legalEntity }}</dd>
            </div>
            <div>
              <dt>所在城市</dt>
              <dd>北京</dd>
            </div>
            <div>
              <dt>服务热线</dt>
              <dd class="num pending">{{ PENDING_INFO.hotline }}</dd>
            </div>
          </dl>
        </div>
        <div class="btn-row">
          <RouterLink class="btn btn-primary btn-lg" to="/assessment#lead">
            预约演示<span class="arrow">→</span>
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
import { RouterLink } from 'vue-router';
import { BRAND, PENDING_INFO } from '@/config/brand';
import { useReveal } from '@/composables/useReveal';
import SectionHead from '@/components/ui/SectionHead.vue';

useReveal();

const BELIEFS = [
  {
    title: '只服务一个行业',
    desc: '商品车整车运输有自己的规矩：板位怎么配、门店怎么交车、回单怎么算齐。通用物流软件里没有这些概念，硬套只会让一线绕路。'
  },
  {
    title: '功能要能被验证',
    desc: '每上一个模块，都要能回答「它改善了哪个经营指标、多久能验证」。答不出来的功能，我们宁可不做。'
  },
  {
    title: '不按席位收钱',
    desc: '版本只按管理深度区分，不设账号数和车辆数门槛。预算应该花在真正要用起来的模块上，而不是先买一堆用不上的席位。'
  },
  {
    title: '数据是你的',
    desc: '按租户隔离、按角色分权，关键操作全部留痕。需要时可以导出完整业务数据，我们不做数据锁定。'
  }
];
</script>

<style scoped lang="scss">
.hero-head {
  max-width: none;
  margin-bottom: 40px;
}

.hero-title {
  font-size: clamp(28px, 3.4vw, 44px);
  margin: 16px 0 18px;
}

.stance {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--line);
  border-radius: var(--r-lg);
  overflow: hidden;
}

.stance article {
  padding: 28px 32px 30px;
  background: var(--bg);
}

.stance-vision {
  background: var(--surface-tint);
}

.stance-kicker {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--brand);
  margin-bottom: 12px;
}

.stance h2 {
  font-size: clamp(20px, 2vw, 24px);
  letter-spacing: -0.025em;
  margin-bottom: 12px;
  line-height: 1.35;
}

.stance p {
  font-size: 15px;
  color: var(--ink-2);
  line-height: 1.75;
}

.line-card {
  background: var(--surface-tint);
  border-radius: var(--r-lg);
  padding: 28px;

  h3 {
    font-size: 22px;
    margin: 12px 0 10px;
  }

  p {
    font-size: 15px;
    color: var(--ink-2);
    margin-bottom: 12px;
  }
}

.contact {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  align-items: center;
  justify-content: space-between;
}

.contact-title {
  font-size: 26px;
}

.contact-lede {
  margin-top: 10px;
}

.contact-list {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin: 22px 0 0;

  dt {
    font-size: 12px;
    color: rgba(244, 247, 252, 0.55);
    margin-bottom: 4px;
  }

  dd {
    margin: 0;
    font-size: 15px;
    font-weight: 600;
  }
}

@media (max-width: 768px) {
  .stance {
    grid-template-columns: 1fr;
  }
}
</style>
