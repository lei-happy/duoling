import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/login.vue'),
    meta: { title: '登录', noAuth: true }
  },
  {
    path: '/sms-login',
    name: 'SmsLogin',
    component: () => import('@/views/login/sms-login.vue'),
    meta: { title: '验证码登录', noAuth: true }
  },
  {
    path: '/tenant-select',
    name: 'TenantSelect',
    component: () => import('@/views/login/tenant-select.vue'),
    meta: { title: '选择企业', requireTokenOnly: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/profile/change-password.vue'),
    meta: { title: '修改密码' }
  },
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/home/index.vue'),
    meta: { title: '工作台', tab: 'home' }
  },
  {
    path: '/task',
    name: 'TaskList',
    component: () => import('@/views/task/task-list.vue'),
    meta: { title: '我的任务', tab: 'task' }
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: () => import('@/views/task/task-detail.vue'),
    meta: { title: '任务详情' }
  },
  {
    path: '/finance',
    name: 'FinanceList',
    component: () => import('@/views/finance/finance-list.vue'),
    meta: { title: '我的收入', tab: 'finance' }
  },
  {
    path: '/finance/:id',
    name: 'FinanceDetail',
    component: () => import('@/views/finance/finance-detail.vue'),
    meta: { title: '费用单详情' }
  },
  {
    path: '/finance/summary',
    name: 'FinanceSummary',
    component: () => import('@/views/finance/income-summary.vue'),
    meta: { title: '收入汇总' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/profile/profile.vue'),
    meta: { title: '我的', tab: 'profile' }
  },
  {
    path: '/profile/info',
    name: 'ProfileInfo',
    component: () => import('@/views/profile/profile-info.vue'),
    meta: { title: '个人信息' }
  },
  {
    path: '/profile/switch-tenant',
    name: 'SwitchTenant',
    component: () => import('@/views/profile/switch-tenant.vue'),
    meta: { title: '切换企业' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/common/not-found.vue'),
    meta: { title: '页面不存在', noAuth: true }
  }
];
