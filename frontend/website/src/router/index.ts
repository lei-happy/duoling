import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { title: '首页' }
    },
    {
      path: '/features',
      name: 'Features',
      component: () => import('@/views/Features.vue'),
      meta: { title: '产品功能' }
    },
    {
      path: '/pricing',
      name: 'Pricing',
      component: () => import('@/views/Pricing.vue'),
      meta: { title: '价格方案' }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { title: '企业注册', fullPage: true }
    },
    {
      path: '/about',
      name: 'About',
      component: () => import('@/views/About.vue'),
      meta: { title: '关于我们' }
    }
  ],
  scrollBehavior() {
    return { top: 0 };
  }
});

router.beforeEach((to) => {
  document.title = `智途·轿运物流AI操作系统`;
});

export default router;
