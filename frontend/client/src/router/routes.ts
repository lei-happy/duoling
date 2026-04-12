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

/**
 * 静态路由
 */
export const routes: RouteRecordRaw[] = [
  {
    path: LOGIN_PATH,
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
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
  eachTree(menuToRoutes(menus, getComponent, routes), (route) => {
    const temp: RouteRecordRaw = Object.assign({}, route, { children: void 0 });
    if (!temp.component && !temp.redirect) {
      // 没有对应组件的路由页面使用 404 组件
      temp.component = () => import('@/views/exception/404/index.vue');
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
