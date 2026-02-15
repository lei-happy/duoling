import { RouteLocationNormalizedLoaded, RouteLocationMatched } from 'vue-router';
import { EleMenuItemProps } from '../ele-app/plus';
import { LayoutProvide } from '../ele-admin-layout/types';
import { MenuItem, TabItem, LevelItem, MatchedResult, ProLayoutProvide, ResponsiveProps } from './types';

/**
 * 根据菜单地址获取菜单
 * @param path 菜单地址
 * @param menus 菜单数据
 */
export declare function findMenuByPath(path?: string, menus?: MenuItem[]): MenuItem | undefined;
/**
 * 根据路由地址获取页签
 * @param path 路由地址
 * @param tabs 页签数据
 */
export declare function findTabByPath(path?: string, tabs?: TabItem[] | null): TabItem | undefined;
/**
 * 根据页签标识获取页签
 * @param key 页签标识
 * @param tabs 页签数据
 */
export declare function findTabByKey(key?: string, tabs?: TabItem[] | null): TabItem | undefined;
/**
 * 根据菜单地址获取菜单及所有父级
 * @param path 菜单地址
 * @param menus 菜单数据
 */
export declare function getMatchedMenus(path: string, menus: MenuItem[], parents?: MenuItem[]): MenuItem[] | undefined;
/**
 * 获取路由匹配的菜单数据
 * @param route 路由信息
 * @param menus 菜单数据
 */
export declare function getRouteMatched(route: RouteLocationNormalizedLoaded, menus: MenuItem[]): MatchedResult;
/**
 * 获取面包屑导航数据
 * @param matched 匹配的菜单数据
 * @param activeOther 是否选中非本身
 * @param route 路由信息
 * @param menus 菜单数据
 * @param tabs 页签数据
 */
export declare function getMatchedLevels(matched: MenuItem[] | undefined, activeOther: boolean | undefined, route: RouteLocationNormalizedLoaded, menus: MenuItem[], tabs: TabItem[]): LevelItem[];
/**
 * 获取路由对应的组件名称
 * @param matched 路由匹配数据
 */
export declare function getMatchedComponents(matched: RouteLocationMatched[]): string[];
/**
 * 返回路由对应的页签数据
 * @param route 路由信息
 * @param tabs 当前页签数据
 * @param homePath 主页地址
 * @param routeTitle 路由对应的标题
 */
export declare function getRouteTab(route: RouteLocationNormalizedLoaded, tabs: TabItem[], homePath: string | undefined, routeTitle?: string): TabItem;
/**
 * 获取选中菜单的子级
 * @param menus 菜单数据
 * @param active 选中地址
 * @param childrenName 子级字段名称
 */
export declare function getActiveChilds(menus: MenuItem[], active?: string, childrenName?: string): MenuItem[];
/**
 * 拼接内嵌地址
 * @param routePath 路由地址含参数
 * @param iframeUrl 内嵌地址
 */
export declare function getIframeSrc(routePath?: string, iframeUrl?: string): string;
/**
 * 菜单数据转换
 * @param menus 菜单数据
 * @param link 是否使用超链接
 */
export declare function getMenuItems(menus: MenuItem[], link: boolean): EleMenuItemProps[];
/**
 * 获取布局共享数据
 */
export declare function useLayoutState(): LayoutProvide;
/**
 * 获取高级布局共享数据
 */
export declare function useProLayoutState(): ProLayoutProvide;
/**
 * 获取是否开启布局响应
 */
export declare function useResponsive(props: ResponsiveProps): import('vue').ComputedRef<boolean>;
