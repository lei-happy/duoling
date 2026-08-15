<template>
  <footer class="foot">
    <div class="wrap">
      <div class="foot-top">
        <div>
          <div class="brand">
            <span class="brand-mark">{{ BRAND.mark }}</span>
            <span>{{ BRAND.product }}</span>
          </div>
          <p class="foot-slogan">{{ BRAND.slogan }}</p>
        </div>

        <div v-for="group in GROUPS" :key="group.title">
          <h4>{{ group.title }}</h4>
          <ul>
            <li v-for="link in group.links" :key="link.label">
              <RouterLink v-if="link.to" :to="link.to">
                {{ link.label }}
              </RouterLink>
              <a v-else-if="link.href" :href="link.href">{{ link.label }}</a>
              <span v-else class="foot-plain">{{ link.label }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="foot-btm">
        <span>© {{ BRAND.copyrightYear }} {{ BRAND.legalEntity }}</span>
        <span class="pending">{{ PENDING_INFO.icp }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { BRAND, PENDING_INFO } from '@/config/brand';

interface FootLink {
  label: string;
  /** 站内路由 */
  to?: string;
  /** 站外链接或 tel: */
  href?: string;
}

const GROUPS: { title: string; links: FootLink[] }[] = [
  {
    title: '产品',
    links: [
      { label: BRAND.product, to: '/features' },
      { label: BRAND.driverProduct, to: '/features#roles' },
      { label: '价格方案', to: '/pricing' },
      { label: '更新记录', to: '/changelog' }
    ]
  },
  {
    title: '了解数智化',
    links: [
      { label: '四阶段辨析', to: '/transformation' },
      { label: '企业水位快测', to: '/assessment' },
      { label: '完整转型报告', to: '/assessment#lead' }
    ]
  },
  {
    title: '联系我们',
    links: [
      { label: '预约演示', to: '/assessment#lead' },
      { label: PENDING_INFO.hotline, href: `tel:${PENDING_INFO.hotline}` },
      { label: `北京 · ${BRAND.company}`, to: '/about' }
    ]
  }
];
</script>

<style scoped lang="scss">
.foot {
  background: var(--ink-0);
  color: rgba(244, 247, 252, 0.66);
  padding: 56px 0 28px;
  font-size: 14px;
}

.foot-top {
  display: grid;
  grid-template-columns: 1.4fr repeat(3, 1fr);
  gap: 32px;
  padding-bottom: 36px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #fff;
}

.brand-mark {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--brand);
  color: #fff;
  display: grid;
  place-items: center;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
}

.foot-slogan {
  margin-top: 12px;
  max-width: 300px;
  line-height: 1.7;
}

h4 {
  color: #fff;
  font-size: 14px;
  margin-bottom: 14px;
}

li {
  margin-bottom: 9px;
}

a {
  transition: color var(--dur-hover) var(--ease);
}

.foot-btm {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  justify-content: space-between;
  padding-top: 22px;
  font-size: 13px;
  color: rgba(244, 247, 252, 0.42);
}

@media (hover: hover) and (pointer: fine) {
  a:hover {
    color: #fff;
  }
}

@media (max-width: 1024px) {
  .foot-top {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .foot-top {
    grid-template-columns: 1fr;
    gap: 26px;
  }
}
</style>
