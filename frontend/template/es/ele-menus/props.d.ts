import { PropType, ExtractPropTypes } from 'vue';
import { menuProps } from 'element-plus';
import { MenuItem, MenuMode, MenuTheme, PopupMenuTheme, PopupColorful, EllipsisProps, TextEllipsisTooltip, MenuItemClickType } from './types';

/**
 * 属性
 */
export declare const menusProps: {
    mode: PropType<MenuMode>;
    /** 菜单数据 */
    items: {
        type: PropType<MenuItem[]>;
        required: boolean;
    };
    /** 主题 */
    theme: PropType<MenuTheme>;
    /** 弹出菜单主题 */
    popupTheme: {
        type: PropType<PopupMenuTheme>;
        default: string;
    };
    /** 彩色菜单图标 */
    colorful: BooleanConstructor;
    /** 弹出菜单是否彩色图标 */
    popupColorful: {
        type: PropType<PopupColorful>;
        default: string;
    };
    /** 一级子菜单类名 */
    firstPopperClass: StringConstructor;
    /** 禁用 tooltip */
    tooltipDisabled: BooleanConstructor;
    /** 省略菜单的属性 */
    ellipsisProps: PropType<EllipsisProps>;
    /** 是否开启菜单文本溢出提示 */
    textEllipsisTooltip: PropType<TextEllipsisTooltip>;
    defaultActive: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    defaultOpeneds: {
        readonly type: PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [];
    };
    uniqueOpened: BooleanConstructor;
    router: BooleanConstructor;
    menuTrigger: {
        readonly type: PropType<"hover" | "click">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    collapse: BooleanConstructor;
    backgroundColor: StringConstructor;
    textColor: StringConstructor;
    activeTextColor: StringConstructor;
    closeOnClickOutside: BooleanConstructor;
    collapseTransition: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    ellipsis: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    popperOffset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 6;
    };
    ellipsisIcon: {
        readonly type: PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    popperEffect: {
        readonly type: PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "dark";
    };
    popperClass: StringConstructor;
    showTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 300;
    };
    hideTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 300;
    };
    persistent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
};
export type MenusProps = ExtractPropTypes<typeof menusProps>;
export type MenuPropKeys = Array<keyof typeof menuProps>;
/**
 * 菜单组件属性名
 */
export declare const menuPropKeys: MenuPropKeys;
/**
 * 事件
 */
export declare const menusEmits: {
    /** 子菜单项点击事件 */
    itemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => boolean;
    /** 子菜单项鼠标进入事件 */
    itemMouseenter: (_item: MenuItem, _e: MouseEvent) => boolean;
    /** 子菜单项鼠标离开事件 */
    itemMouseleave: (_item: MenuItem, _e: MouseEvent) => boolean;
    /** 父级菜单项鼠标进入事件 */
    parentMouseenter: (_item: MenuItem, _e: MouseEvent) => boolean;
    /** 父级菜单项鼠标离开事件 */
    parentMouseleave: (_item: MenuItem, _e: MouseEvent) => boolean;
    close: (index: string, indexPath: string[]) => boolean;
    open: (index: string, indexPath: string[]) => boolean;
    select: (index: string, indexPath: string[], item: import('element-plus').MenuItemClicked, routerResult?: Promise<void | import('vue-router').NavigationFailure>) => boolean;
};
