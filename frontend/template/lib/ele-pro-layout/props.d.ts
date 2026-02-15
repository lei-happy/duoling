import { PropType, ExtractPropTypes, InjectionKey } from 'vue';
import { EleMenusProps } from '../ele-app/plus';
import { BreadcrumbSeparator as Separator } from '../ele-breadcrumb/types';
import { MenuItem, TabItem, MenuItemTrigger, MenuI18n, BeforeClick, TabItemEventOption, BodySizeChangeOption, ProLayoutProvide } from './types';

type TextEllipsisTooltip = EleMenusProps['textEllipsisTooltip'];
type ProLayoutKey = InjectionKey<ProLayoutProvide>;
/**
 * 属性
 */
export declare const proLayoutProps: {
    /** 高度 */
    height: {
        type: (NumberConstructor | StringConstructor)[];
        default: null;
    };
    /** 菜单数据 */
    menus: PropType<MenuItem[] | null>;
    /** 页签数据 */
    tabs: PropType<TabItem[] | null>;
    /** 刷新路由地址 */
    redirectPath: {
        type: StringConstructor;
        default: string;
    };
    /** 内容区是否撑满 */
    fluid: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 返回键退出内容区最大化 */
    compressOnEsc: BooleanConstructor;
    /** 固定主体时切换路由自动滚到顶部 */
    autoScrollTop: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 顶栏菜单触发模式 */
    navTrigger: PropType<MenuItemTrigger>;
    /** 双侧栏一级菜单触发模式 */
    boxTrigger: PropType<MenuItemTrigger>;
    /** 侧栏菜单触发模式 */
    itemTrigger: PropType<MenuItemTrigger>;
    /** hover模式的菜单切换超时 */
    menuHoverTimeout: {
        type: NumberConstructor;
        default: number;
    };
    /** 菜单点击事件前钩子 */
    beforeClick: PropType<BeforeClick>;
    /** 是否支持内嵌缓存 */
    keepAlive: BooleanConstructor;
    /** 内嵌切换动画 */
    transitionName: StringConstructor;
    /** 内嵌进入动画延迟时间 */
    transitionDelay: {
        type: NumberConstructor;
        default: number;
    };
    /** 是否开启响应式 */
    responsive: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 国际化语言 */
    locale: StringConstructor;
    /** 菜单标题国际化方法 */
    i18n: PropType<MenuI18n>;
    /** 顶栏菜单是否省略多余的子项 */
    ellipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 顶栏菜单省略项的属性 */
    ellipsisProps: PropType<EleMenusProps["ellipsisProps"]>;
    /** 顶栏子菜单触发方式 */
    menuTrigger: PropType<EleMenusProps["menuTrigger"]>;
    /** 侧栏默认展开的菜单 */
    sidebarOpeneds: PropType<string[]>;
    /** 侧栏是否只保持一个子菜单展开 */
    uniqueOpened: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 侧栏菜单是否彩色图标 */
    colorfulIcon: BooleanConstructor;
    /** 菜单 tooltip 主题 */
    tooltipEffect: PropType<EleMenusProps["popperEffect"]>;
    /** 是否开启菜单文本溢出提示 */
    menuTextEllipsisTooltip: PropType<TextEllipsisTooltip>;
    /** 内容区最大时不带页签栏 */
    expanded: BooleanConstructor;
    /** 面包屑导航分隔符 */
    breadcrumbSeparator: PropType<Separator>;
    /** 返回顶部可见的滚动高度 */
    backTopVisibilityHeight: NumberConstructor;
    /** 返回顶部的右边距 */
    backTopRight: NumberConstructor;
    /** 返回顶部的下边距 */
    backTopBottom: NumberConstructor;
    /** 返回顶部的目标选择器 */
    backTopTarget: StringConstructor;
    collapse: BooleanConstructor;
    layout: PropType<import('./types').Layout>;
    compact: BooleanConstructor;
    maximized: PropType<import('../ele-admin-layout/types').Maximized>;
    tabBar: {
        type: PropType<import('./types').TabBar>;
        default: boolean;
    };
    breadcrumb: {
        type: PropType<boolean | import('../ele-app/plus').EleBreadcrumbProps>;
        default: boolean;
    };
    backTop: {
        type: PropType<boolean | import('../ele-app/plus').EleBacktopProps>;
        default: boolean;
    };
    headerMenuProps: PropType<EleMenusProps>;
    sidebarMenuProps: PropType<EleMenusProps>;
    sideboxMenuProps: PropType<EleMenusProps>;
    sidebarLayout: PropType<import('./types').SidebarLayout>;
    headerStyle: PropType<import('./types').HeaderStyle>;
    sidebarStyle: {
        type: PropType<import('./types').SidebarStyle>;
        default: string;
    };
    mixSidebarStyle: PropType<import('./types').SidebarStyle>;
    tabStyle: {
        type: PropType<import('./types').TabStyle>;
        default: string;
    };
    fixedHeader: {
        type: BooleanConstructor;
        default: boolean;
    };
    fixedSidebar: {
        type: BooleanConstructor;
        default: boolean;
    };
    fixedBody: {
        type: BooleanConstructor;
        default: boolean;
    };
    logoInHeader: BooleanConstructor;
    fixedHome: {
        type: BooleanConstructor;
        default: boolean;
    };
    homePath: StringConstructor;
    tabContextMenu: PropType<boolean | import('../ele-app/plus').EleDropdownProps>;
    tabContextMenus: PropType<import('../ele-tabs/types').ContextMenus>;
    tabSortable: BooleanConstructor;
    headerTitleSlot: {
        type: StringConstructor;
        default: string;
    };
    headerIconSlot: {
        type: StringConstructor;
        default: string;
    };
    sidebarTitleSlot: {
        type: StringConstructor;
        default: string;
    };
    sidebarIconSlot: {
        type: StringConstructor;
        default: string;
    };
    sideboxTitleSlot: {
        type: StringConstructor;
        default: string;
    };
    sideboxIconSlot: {
        type: StringConstructor;
        default: string;
    };
    headerCustomStyle: PropType<import('../ele-app/types').StyleValue | null>;
    sidebarCustomStyle: PropType<import('../ele-app/types').StyleValue | null>;
    sideboxCustomStyle: PropType<import('../ele-app/types').StyleValue | null>;
    sideCustomStyle: PropType<import('../ele-app/types').StyleValue | null>;
    tabsCustomStyle: PropType<import('../ele-app/types').StyleValue | null>;
    contentCustomStyle: PropType<import('../ele-app/types').StyleValue | null>;
    logoStyle: PropType<import('../ele-app/types').StyleValue | null>;
    logoTitleStyle: PropType<import('../ele-app/types').StyleValue | null>;
    headerMenusStyle: PropType<import('../ele-app/types').StyleValue | null>;
    sidebarMenusStyle: PropType<import('../ele-app/types').StyleValue | null>;
    sideboxMenusStyle: PropType<import('../ele-app/types').StyleValue | null>;
    logoSrc: StringConstructor;
    logoTitle: StringConstructor;
    menuScrollToActive: {
        type: BooleanConstructor;
        default: boolean;
    };
};
export type ProLayoutProps = ExtractPropTypes<typeof proLayoutProps>;
/**
 * 事件
 */
export declare const proLayoutEmits: {
    'update:collapse': (_collapse: boolean) => boolean;
    'update:maximized': (_maximized: boolean) => boolean;
    tabAdd: (_data: TabItem) => boolean;
    tabClick: (_option: TabItemEventOption) => boolean;
    tabRemove: (_option: TabItemEventOption) => boolean;
    tabContextMenu: (_option: TabItemEventOption) => boolean;
    tabSortChange: (_data: TabItem[]) => boolean;
    logoClick: (_isHome: boolean, _e: MouseEvent) => boolean;
    headMenuOpen: (_index: string, _indexPath: string[]) => boolean;
    headMenuClose: (_index: string, _indexPath: string[]) => boolean;
    sideMenuOpen: (_index: string, _indexPath: string[]) => boolean;
    sideMenuClose: (_index: string, _indexPath: string[]) => boolean;
    bodySizeChange: (_option: BodySizeChangeOption) => boolean;
};
/**
 * 共享数据key
 */
export declare const PRO_LAYOUT_KEY: ProLayoutKey;
export {};
