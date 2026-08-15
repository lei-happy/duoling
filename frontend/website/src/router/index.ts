import { createRouter, createWebHistory } from 'vue-router';
import { BRAND } from '@/config/brand';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { title: BRAND.tagline }
    },
    {
      path: '/transformation',
      name: 'Transformation',
      component: () => import('@/views/Transformation.vue'),
      meta: { title: '企业数智化转型的四层能力' }
    },
    {
      path: '/features',
      name: 'Features',
      component: () => import('@/views/Features.vue'),
      meta: { title: '产品能力' }
    },
    {
      path: '/assessment',
      name: 'Assessment',
      component: () => import('@/views/Assessment.vue'),
      meta: { title: '企业数智化水位快测' }
    },
    {
      path: '/pricing',
      name: 'Pricing',
      component: () => import('@/views/Pricing.vue'),
      meta: { title: '价格方案' }
    },
    {
      path: '/about',
      name: 'About',
      component: () => import('@/views/About.vue'),
      meta: { title: '关于我们' }
    },
    {
      path: '/changelog',
      name: 'Changelog',
      component: () => import('@/views/Changelog.vue'),
      meta: { title: '更新记录' }
    },
    // 自助注册已下线，旧链接与外部书签统一收到自测页的留资区
    {
      path: '/register',
      redirect: { path: '/assessment', hash: '#lead' }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
  scrollBehavior(to, _from, savedPosition) {
    if (to.hash) {
      return { el: to.hash, top: 88, behavior: 'smooth' };
    }
    return savedPosition ?? { top: 0 };
  }
});

router.afterEach((to) => {
  const title = to.meta.title as string | undefined;
  document.title = title ? `${title} · ${BRAND.product}` : BRAND.product;
});

export default router;
