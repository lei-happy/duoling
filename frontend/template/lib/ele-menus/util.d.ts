import { MenuItem, MenuTheme, PopupMenuTheme, PopupColorful, MenuResult, MenuEllipsisOption } from './types';

/**
 * 生成气泡菜单的类名
 * @param customerClass 自定义的类名
 * @param theme 主题
 * @param popTheme 气泡菜单主题
 * @param colorful 是否彩色图标
 * @param popupColorful 气泡菜单是否彩色图标
 * @param firstPopClass 第一级气泡菜单类名
 * @param first 是否是第一级菜单
 * @param webkit 是否是webkit内核
 */
export declare function getPopperClass(customerClass?: string, theme?: MenuTheme, popTheme?: PopupMenuTheme, colorful?: boolean, popupColorful?: PopupColorful, firstPopClass?: string, first?: boolean, webkit?: boolean): string;
/**
 * 生成菜单数据
 * @param items 菜单数据
 * @param index 省略位置
 * @param horizontal 是否是水平菜单
 */
export declare function getMenuItems(menus?: MenuItem[], index?: number, horizontal?: boolean): MenuResult;
/**
 * 获取菜单节点宽度
 * @param el 菜单节点
 */
export declare function getMenuWidth(el?: HTMLElement | null): number | undefined;
/**
 * 获取菜单项节点宽度
 * @param el 菜单项节点
 */
export declare function getItemWidth(el?: HTMLElement | null): number | undefined;
/**
 * 获取菜单子级节点
 * @param el 菜单节点
 */
export declare function getMenuChilds(el: HTMLElement): HTMLElement[];
/**
 * 菜单溢出省略
 */
export declare function useMenuEllipsis(option: MenuEllipsisOption): {
    observe: () => void;
    unobserve: () => void;
    computedEllipsis: () => void;
};
