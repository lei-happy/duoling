import { RouteRecordRaw, _RouteRecordBase, RouteComponent } from 'vue-router';
import { MenuItem } from '../ele-pro-layout/types';

/**
 * 获取路由组件方法
 */
export type GetComponent = (component?: string, menu?: MenuItem, name?: string) => (() => Promise<RouteComponent>) | RouteComponent | undefined;
/**
 * 获取内嵌页面路由组件
 * @param menu 菜单数据
 * @param name 组件名称
 */
export declare function getIframeRouteComponent(menu: MenuItem, name: string): import('vue').DefineComponent<{}, () => import('vue').VNode<import('vue').RendererNode, import('vue').RendererElement, {
    [key: string]: any;
}>, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{}> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
/**
 * 菜单数据转为路由数据
 * @param menus 菜单数据
 * @param getComponent 加载组件的方法
 * @param added 已添加的路由
 */
export declare function menuToRoutes(menus: MenuItem[] | undefined, getComponent: GetComponent, added?: _RouteRecordBase[]): RouteRecordRaw[] | undefined;
