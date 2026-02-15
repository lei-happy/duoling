import { defineComponent, ref, computed, h } from 'vue';
import { useRoute } from 'vue-router';
import type {
  RouteRecordRaw,
  _RouteRecordBase,
  RouteComponent
} from 'vue-router';
import type { MenuItem } from '../ele-pro-layout/types';
import { useProLayoutState, getIframeSrc } from '../ele-pro-layout/util';
import { findTree, isExternalLink } from './common';

/**
 * 获取路由组件方法
 */
export type GetComponent = (
  component?: string,
  menu?: MenuItem,
  name?: string
) => (() => Promise<RouteComponent>) | RouteComponent | undefined;

/**
 * 获取内嵌页面路由组件
 * @param menu 菜单数据
 * @param name 组件名称
 */
export function getIframeRouteComponent(menu: MenuItem, name: string) {
  return defineComponent({
    name,
    setup() {
      const proLayoutState = useProLayoutState();
      const route = useRoute();
      const { fullPath } = route;
      const iframeSrc = ref(getIframeSrc(fullPath, menu.component));
      const isAlive = menu.meta?.keepAlive !== false;
      const keepAlive = computed(() => !!proLayoutState.keepAlive);
      return () => {
        if (!isAlive || !keepAlive.value) {
          return h('iframe', {
            src: iframeSrc.value,
            class: 'ele-admin-iframe'
          });
        }
        return h('div', { class: 'ele-none', style: { display: 'none' } });
      };
    }
  });
}

/**
 * 中划线斜线转驼峰
 * @param str 字符串
 */
function camelCase(str: string) {
  const val = str.replace(/[-|/](\w)/g, (_, c) => (c ? c.toUpperCase() : ''));
  return val.charAt(0).toUpperCase() + val.slice(1);
}

/**
 * 判断路由地址是否已经添加
 * @param path 路由地址
 * @param data 路由数据
 */
function pathIsAdd(path: string, data: _RouteRecordBase[]): boolean {
  return findTree(data, (d) => path === d.path) != null;
}

/**
 * 路由地址去掉非法格式
 * @param path 路由地址
 */
function getRoutePath(path: string) {
  if (!path || !path.includes('?') || path.endsWith('?')) {
    return path;
  }
  return path.substring(0, path.indexOf('?'));
}

/**
 * 获取路由组件
 * @param menu 菜单数据
 * @param name 组件名称
 * @param func 加载组件的方法
 */
function getRouteComponent(menu: MenuItem, name: string, func: GetComponent) {
  if (!menu.component || !isExternalLink(menu.component)) {
    return { component: func(menu.component, menu, name) as any };
  }
  return { component: getIframeRouteComponent(menu, name), link: true };
}

/**
 * 菜单数据转为路由数据
 * @param menus 菜单数据
 * @param getComponent 加载组件的方法
 * @param added 已添加的路由
 */
export function menuToRoutes(
  menus: MenuItem[] | undefined,
  getComponent: GetComponent,
  added?: _RouteRecordBase[]
): RouteRecordRaw[] | undefined {
  if (!menus?.length) {
    return;
  }
  const routes: RouteRecordRaw[] = [];
  const addedRoutes: _RouteRecordBase[] = added ? [...added] : [];
  menus.forEach((item) => {
    const meta = { ...item.meta };
    const path = meta.routePath || getRoutePath(item.path);
    if (path && !isExternalLink(path) && !pathIsAdd(path, addedRoutes)) {
      const name = item.name || camelCase(path);
      const { component, link } = getRouteComponent(item, name, getComponent);
      if (link) {
        meta.iframe = item.component;
        meta.hideFooter = true;
      }
      addedRoutes.push({ path });
      routes.push({
        name,
        path,
        component,
        redirect: item.redirect as string,
        props: item.props,
        meta,
        children: menuToRoutes(item.children, getComponent, addedRoutes)
      });
    }
  });
  return routes;
}
