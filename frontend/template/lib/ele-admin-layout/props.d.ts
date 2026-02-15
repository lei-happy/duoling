import { PropType, ExtractPropTypes, InjectionKey } from 'vue';
import { StyleValue } from '../ele-app/types';
import { EleMenusProps, EleBreadcrumbProps, EleBacktopProps, EleDropdownProps } from '../ele-app/plus';
import { MenuItem, MenuItemClickType } from '../ele-menus/types';
import { BreadcrumbItem } from '../ele-breadcrumb/types';
import { TabPaneItem, TabEventOption, ContextMenus } from '../ele-tabs/types';
import { Layout, SidebarLayout, HeaderStyle, SidebarStyle, TabStyle, TabBar, Maximized, LayoutProvide } from './types';

/**
 * 属性
 */
export declare const adminLayoutProps: {
    /** 高度 */
    height: {
        type: (NumberConstructor | StringConstructor)[];
        default: string;
    };
    /** 顶栏菜单数据 */
    headerMenus: PropType<MenuItem[]>;
    /** 顶栏菜单选中 */
    headerActive: StringConstructor;
    /** 侧栏菜单数据 */
    sidebarMenus: PropType<MenuItem[]>;
    /** 侧栏菜单选中 */
    sidebarActive: StringConstructor;
    /** 双侧栏一级菜单数据 */
    sideboxMenus: PropType<MenuItem[]>;
    /** 双侧栏一级菜单选中 */
    sideboxActive: StringConstructor;
    /** 页签数据 */
    tabs: PropType<TabPaneItem[]>;
    /** 页签选中 */
    tabActive: StringConstructor;
    /** 面包屑导航数据 */
    levels: PropType<BreadcrumbItem[]>;
    /** 是否折叠侧栏 */
    collapse: BooleanConstructor;
    /** 双侧栏一级是否紧凑风格 */
    compact: BooleanConstructor;
    /** 内容区是否最大化 */
    maximized: PropType<Maximized>;
    /** 是否需要页签栏 */
    tabBar: {
        type: PropType<TabBar>;
        default: boolean;
    };
    /** 是否需要面包屑导航 */
    breadcrumb: {
        type: PropType<boolean | EleBreadcrumbProps>;
        default: boolean;
    };
    /** 是否需要返回顶部 */
    backTop: {
        type: PropType<boolean | EleBacktopProps>;
        default: boolean;
    };
    /** 顶栏菜单属性 */
    headerMenuProps: PropType<EleMenusProps>;
    /** 侧栏菜单属性 */
    sidebarMenuProps: PropType<EleMenusProps>;
    /** 双侧栏一级菜单属性 */
    sideboxMenuProps: PropType<EleMenusProps>;
    /** 布局类型 */
    layout: PropType<Layout>;
    /** 侧栏布局类型 */
    sidebarLayout: PropType<SidebarLayout>;
    /** 顶栏风格 */
    headerStyle: PropType<HeaderStyle>;
    /** 侧栏风格 */
    sidebarStyle: {
        type: PropType<SidebarStyle>;
        default: string;
    };
    /** 双侧栏时二级侧栏风格 */
    mixSidebarStyle: PropType<SidebarStyle>;
    /** 页签风格 */
    tabStyle: {
        type: PropType<TabStyle>;
        default: string;
    };
    /** 是否固定顶栏 */
    fixedHeader: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否固定侧栏 */
    fixedSidebar: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否固定内容区 */
    fixedBody: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** logo是否置于顶栏 */
    logoInHeader: BooleanConstructor;
    /** 是否需要固定的主页页签 */
    fixedHome: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 主页路由地址 */
    homePath: StringConstructor;
    /** 是否选中固定的主页页签 */
    isHome: BooleanConstructor;
    /** 是否支持页签右键菜单 */
    tabContextMenu: PropType<boolean | EleDropdownProps>;
    /** 页签右键菜单数据 */
    tabContextMenus: PropType<ContextMenus>;
    /** 是否支持页签拖动排序 */
    tabSortable: BooleanConstructor;
    /** 顶栏菜单标题插槽名称 */
    headerTitleSlot: {
        type: StringConstructor;
        default: string;
    };
    /** 顶栏菜单图标插槽名称 */
    headerIconSlot: {
        type: StringConstructor;
        default: string;
    };
    /** 侧栏菜单标题插槽名称 */
    sidebarTitleSlot: {
        type: StringConstructor;
        default: string;
    };
    /** 侧栏菜单图标插槽名称 */
    sidebarIconSlot: {
        type: StringConstructor;
        default: string;
    };
    /** 双侧栏一级菜单标题插槽名称 */
    sideboxTitleSlot: {
        type: StringConstructor;
        default: string;
    };
    /** 双侧栏一级菜单图标插槽名称 */
    sideboxIconSlot: {
        type: StringConstructor;
        default: string;
    };
    /** 顶栏样式 */
    headerCustomStyle: PropType<StyleValue | null>;
    /** 侧栏样式 */
    sidebarCustomStyle: PropType<StyleValue | null>;
    /** 双侧栏一级样式 */
    sideboxCustomStyle: PropType<StyleValue | null>;
    /** 侧栏容器样式 */
    sideCustomStyle: PropType<StyleValue | null>;
    /** 页签栏样式 */
    tabsCustomStyle: PropType<StyleValue | null>;
    /** 内容区样式 */
    contentCustomStyle: PropType<StyleValue | null>;
    /** logo样式 */
    logoStyle: PropType<StyleValue | null>;
    /** logo文字样式 */
    logoTitleStyle: PropType<StyleValue | null>;
    /** 顶栏菜单样式 */
    headerMenusStyle: PropType<StyleValue | null>;
    /** 侧栏菜单样式 */
    sidebarMenusStyle: PropType<StyleValue | null>;
    /** 双侧栏一级菜单样式 */
    sideboxMenusStyle: PropType<StyleValue | null>;
    /** logo图片地址 */
    logoSrc: StringConstructor;
    /** logo文字 */
    logoTitle: StringConstructor;
    /** 菜单是否自动滚动到选中位置 */
    menuScrollToActive: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否是移动端风格 */
    mobile: BooleanConstructor;
};
export type AdminLayoutProps = ExtractPropTypes<typeof adminLayoutProps>;
/**
 * 事件
 */
export declare const adminLayoutEmits: {
    'update:collapse': (_collapse: boolean) => boolean;
    logoClick: (_e: MouseEvent) => boolean;
    headMenuOpen: (_index: string, _indexPath: string[]) => boolean;
    headMenuClose: (_index: string, _indexPath: string[]) => boolean;
    headMenuItemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => boolean;
    headMenuItemMouseenter: (_item: MenuItem, _e: MouseEvent) => boolean;
    headMenuItemMouseleave: (_item: MenuItem, _e: MouseEvent) => boolean;
    headMouseenter: (_e: MouseEvent) => boolean;
    headMouseleave: (_e: MouseEvent) => boolean;
    boxMenuItemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => boolean;
    boxMenuItemMouseenter: (_item: MenuItem, _e: MouseEvent) => boolean;
    boxMenuItemMouseleave: (_item: MenuItem, _e: MouseEvent) => boolean;
    boxMouseenter: (_e: MouseEvent) => boolean;
    boxMouseleave: (_e: MouseEvent) => boolean;
    sideMenuOpen: (_index: string, _indexPath: string[]) => boolean;
    sideMenuClose: (_index: string, _indexPath: string[]) => boolean;
    sideMenuItemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => boolean;
    sideMouseenter: (_e: MouseEvent) => boolean;
    sideMouseleave: (_e: MouseEvent) => boolean;
    tabClick: (_option: TabEventOption) => boolean;
    tabRemove: (_name: string) => boolean;
    tabContextMenu: (_option: TabEventOption) => boolean;
    tabSortChange: (_data: TabPaneItem[]) => boolean;
    contentMounted: (_contentEl: HTMLElement, _modalsEl: HTMLElement) => boolean;
};
/**
 * 共享数据key
 */
export declare const LAYOUT_KEY: InjectionKey<LayoutProvide>;
