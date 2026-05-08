import type { RouteRecordRaw } from 'vue-router';
import { menuToRoutes, eachTree } from 'ele-admin-plus';
import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
import {
  LOGIN_PATH,
  HOME_PATH,
  LAYOUT_PATH,
  REDIRECT_PATH,
  WHITE_LIST
} from '@/config/setting';
import Layout from '@/layout/index.vue';
import RedirectLayout from '@/components/RedirectLayout/index.vue';
const modules = import.meta.glob('/src/views/**/index.vue');

/** 已在布局 childRoutes 中静态注册的路径，供 menuToRoutes 去重，避免与后端菜单重复生成 */
const STATIC_LAYOUT_MENU_PATHS = [
  { path: '/enterprise/manage' },
  { path: '/user/profile' },
  { path: '/user/message' }
] as const;

/**
 * 静态路由
 */
export const routes: RouteRecordRaw[] = [
  {
    path: LOGIN_PATH,
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
  // 承运商邀请着陆页（白名单免登录，路径 B 激活入口）
  {
    path: '/invite-landing/:code',
    component: () => import('@/views/invite-landing/index.vue'),
    meta: { title: '承运商邀请激活', layout: false }
  },
  // 升级方案对比页（不依赖后端菜单，已登录用户也可直接访问）
  {
    path: '/upgrade-plans',
    component: () => import('@/views/upgrade-plans/index.vue'),
    meta: { title: '升级方案', layout: false }
  },
  // 404
  {
    path: '/:path(.*)*',
    component: () => import('@/views/exception/404/index.vue')
  }
];

/**
 * 根据菜单生成动态路由
 * @param menus 菜单数据
 * @param homePath 主页地址
 */
export function getMenuRoutes(menus?: MenuItem[], homePath?: string) {
  const childRoutes: RouteRecordRaw[] = [
    // 用于刷新的路由
    {
      path: REDIRECT_PATH + '/:path(.*)',
      component: RedirectLayout,
      meta: { hideFooter: true }
    },
    // 企业管理（静态路由，不依赖后端菜单）
    {
      path: '/enterprise/manage',
      component: () => import('@/views/enterprise/manage.vue'),
      meta: { title: '企业管理' }
    },
    // 个人中心（静态路由，不依赖后端菜单；与运营端入口一致）
    {
      path: '/user/profile',
      component: () => import('@/views/user/profile/index.vue'),
      meta: { title: '个人中心' }
    },
    // 消息中心（静态路由，不依赖后端菜单；与顶栏通知「查看更多」等入口一致）
    {
      path: '/user/message',
      component: () => import('@/views/user/message/index.vue'),
      meta: { title: '消息中心' }
    }
  ];
  const layoutRoutes: RouteRecordRaw[] = [
    {
      path: LAYOUT_PATH,
      component: Layout,
      redirect: HOME_PATH ?? homePath,
      children: childRoutes
    }
  ];
  // 路由铺平处理
  eachTree(
    menuToRoutes(menus, getComponent, [
      ...routes,
      ...STATIC_LAYOUT_MENU_PATHS
    ]),
    (route) => {
    const temp: RouteRecordRaw = Object.assign({}, route, { children: void 0 });
    if (!temp.component && !temp.redirect) {
      // 后端菜单已勾选但前端工程暂未实现对应页面时，统一回退到「功能开发中」占位页，
      // 避免给用户呈现刺眼的 404；真正未注册的非法路径仍由 routes 兜底的 404 处理。
      temp.component = () =>
        import('@/views/exception/placeholder/index.vue');
    }
    if (temp.meta?.layout === false) {
      layoutRoutes.push(temp); // 不需要外层布局的路由
    } else {
      childRoutes.push(temp); // 需要外层布局的路由
    }
  });
  return layoutRoutes;
}

/**
 * 判断是否是白名单路由
 * @param path 路由地址
 */
export function isWhiteList(path: string) {
  if (!path) {
    return false;
  }
  return WHITE_LIST.some((whitePath) => {
    if (whitePath === path) {
      return true;
    }
    if (whitePath.endsWith('*') && path.startsWith(whitePath.slice(0, -1))) {
      return true;
    }
    return false;
  });
}

/**
 * 解析路由组件
 * @param component 组件名称
 */
function getComponent(component?: string) {
  if (component) {
    const normalized = component.startsWith('/') ? component : `/${component}`;
    const module = modules[`/src/views${normalized}.vue`];
    if (!module) {
      return modules[`/src/views${normalized}/index.vue`];
    }
    return module;
  }
}
