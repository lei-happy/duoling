import { EleAdminLayoutInstance, EleBreadcrumbProps, EleBacktopProps, EleMenusProps } from '../ele-app/plus';
import { MenuItem, TabItem, LevelItem, TabItemEventOption } from './types';
import { Layout, SidebarLayout, TabBar, Maximized } from '../ele-admin-layout/types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    default?(_: {}): any;
    footer?(_: {}): any;
    logo?(_: {
        collapse: boolean;
        sidebar: boolean;
    }): any;
    logoTitle?(_: {
        collapse: boolean;
        sidebar: boolean;
    }): any;
    breadcrumb?(_: {
        levels: LevelItem[];
        isHome: boolean;
        homePath: string | undefined;
        sidebar: boolean;
    }): any;
    left?(_: {
        sidebar: boolean;
    }): any;
    center?(_: {
        sidebar: boolean;
    }): any;
    right?(_: {
        sidebar: boolean;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    height: {
        type: (NumberConstructor | StringConstructor)[];
        default: null;
    };
    menus: import('vue').PropType<MenuItem[] | null>;
    tabs: import('vue').PropType<TabItem[] | null>;
    redirectPath: {
        type: StringConstructor;
        default: string;
    };
    fluid: {
        type: BooleanConstructor;
        default: boolean;
    };
    compressOnEsc: BooleanConstructor;
    autoScrollTop: {
        type: BooleanConstructor;
        default: boolean;
    };
    navTrigger: import('vue').PropType<import('./types').MenuItemTrigger>;
    boxTrigger: import('vue').PropType<import('./types').MenuItemTrigger>;
    itemTrigger: import('vue').PropType<import('./types').MenuItemTrigger>;
    menuHoverTimeout: {
        type: NumberConstructor;
        default: number;
    };
    beforeClick: import('vue').PropType<import('./types').BeforeClick>;
    keepAlive: BooleanConstructor;
    transitionName: StringConstructor;
    transitionDelay: {
        type: NumberConstructor;
        default: number;
    };
    responsive: {
        type: BooleanConstructor;
        default: boolean;
    };
    locale: StringConstructor;
    i18n: import('vue').PropType<import('./types').MenuI18n>;
    ellipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    ellipsisProps: import('vue').PropType<EleMenusProps["ellipsisProps"]>;
    menuTrigger: import('vue').PropType<EleMenusProps["menuTrigger"]>;
    sidebarOpeneds: import('vue').PropType<string[]>;
    uniqueOpened: {
        type: BooleanConstructor;
        default: boolean;
    };
    colorfulIcon: BooleanConstructor;
    tooltipEffect: import('vue').PropType<EleMenusProps["popperEffect"]>;
    menuTextEllipsisTooltip: import('vue').PropType<import('../ele-menus/types').TextEllipsisTooltip | undefined>;
    expanded: BooleanConstructor;
    breadcrumbSeparator: import('vue').PropType<import('../ele-breadcrumb/types').BreadcrumbSeparator>;
    backTopVisibilityHeight: NumberConstructor;
    backTopRight: NumberConstructor;
    backTopBottom: NumberConstructor;
    backTopTarget: StringConstructor;
    collapse: BooleanConstructor;
    layout: import('vue').PropType<Layout>;
    compact: BooleanConstructor;
    maximized: import('vue').PropType<Maximized>;
    tabBar: {
        type: import('vue').PropType<TabBar>;
        default: boolean;
    };
    breadcrumb: {
        type: import('vue').PropType<boolean | EleBreadcrumbProps>;
        default: boolean;
    };
    backTop: {
        type: import('vue').PropType<boolean | EleBacktopProps>;
        default: boolean;
    };
    headerMenuProps: import('vue').PropType<EleMenusProps>;
    sidebarMenuProps: import('vue').PropType<EleMenusProps>;
    sideboxMenuProps: import('vue').PropType<EleMenusProps>;
    sidebarLayout: import('vue').PropType<SidebarLayout>;
    headerStyle: import('vue').PropType<import('./types').HeaderStyle>;
    sidebarStyle: {
        type: import('vue').PropType<import('./types').SidebarStyle>;
        default: string;
    };
    mixSidebarStyle: import('vue').PropType<import('./types').SidebarStyle>;
    tabStyle: {
        type: import('vue').PropType<import('./types').TabStyle>;
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
    tabContextMenu: import('vue').PropType<boolean | import('../ele-app/plus').EleDropdownProps>;
    tabContextMenus: import('vue').PropType<import('../ele-tabs/types').ContextMenus>;
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
    headerCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sidebarCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sideboxCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sideCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    tabsCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    contentCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    logoStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    logoTitleStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    headerMenusStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sidebarMenusStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sideboxMenusStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    logoSrc: StringConstructor;
    logoTitle: StringConstructor;
    menuScrollToActive: {
        type: BooleanConstructor;
        default: boolean;
    };
}>, {
    layoutRef: import('vue').Ref<EleAdminLayoutInstance, EleAdminLayoutInstance>;
    openModal: (option: import('../ele-modal-render/types').ModalItem) => import('../ele-modal-render/types').ModalItemId;
    closeModal: (modalId?: import('../ele-modal-render/types').ModalItemId) => void;
    closeAllModal: () => void;
    updateModalProps: (modalId?: import('../ele-modal-render/types').ModalItemId, option?: Record<string, any>) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    tabContextMenu: (_option: TabItemEventOption) => void;
    "update:maximized": (_maximized: boolean) => void;
    tabSortChange: (_data: TabItem[]) => void;
    tabClick: (_option: TabItemEventOption) => void;
    tabRemove: (_option: TabItemEventOption) => void;
    tabAdd: (_data: TabItem) => void;
    "update:collapse": (_collapse: boolean) => void;
    logoClick: (_isHome: boolean, _e: MouseEvent) => void;
    headMenuOpen: (_index: string, _indexPath: string[]) => void;
    headMenuClose: (_index: string, _indexPath: string[]) => void;
    sideMenuOpen: (_index: string, _indexPath: string[]) => void;
    sideMenuClose: (_index: string, _indexPath: string[]) => void;
    bodySizeChange: (_option: import('./types').BodySizeChangeOption) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    height: {
        type: (NumberConstructor | StringConstructor)[];
        default: null;
    };
    menus: import('vue').PropType<MenuItem[] | null>;
    tabs: import('vue').PropType<TabItem[] | null>;
    redirectPath: {
        type: StringConstructor;
        default: string;
    };
    fluid: {
        type: BooleanConstructor;
        default: boolean;
    };
    compressOnEsc: BooleanConstructor;
    autoScrollTop: {
        type: BooleanConstructor;
        default: boolean;
    };
    navTrigger: import('vue').PropType<import('./types').MenuItemTrigger>;
    boxTrigger: import('vue').PropType<import('./types').MenuItemTrigger>;
    itemTrigger: import('vue').PropType<import('./types').MenuItemTrigger>;
    menuHoverTimeout: {
        type: NumberConstructor;
        default: number;
    };
    beforeClick: import('vue').PropType<import('./types').BeforeClick>;
    keepAlive: BooleanConstructor;
    transitionName: StringConstructor;
    transitionDelay: {
        type: NumberConstructor;
        default: number;
    };
    responsive: {
        type: BooleanConstructor;
        default: boolean;
    };
    locale: StringConstructor;
    i18n: import('vue').PropType<import('./types').MenuI18n>;
    ellipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    ellipsisProps: import('vue').PropType<EleMenusProps["ellipsisProps"]>;
    menuTrigger: import('vue').PropType<EleMenusProps["menuTrigger"]>;
    sidebarOpeneds: import('vue').PropType<string[]>;
    uniqueOpened: {
        type: BooleanConstructor;
        default: boolean;
    };
    colorfulIcon: BooleanConstructor;
    tooltipEffect: import('vue').PropType<EleMenusProps["popperEffect"]>;
    menuTextEllipsisTooltip: import('vue').PropType<import('../ele-menus/types').TextEllipsisTooltip | undefined>;
    expanded: BooleanConstructor;
    breadcrumbSeparator: import('vue').PropType<import('../ele-breadcrumb/types').BreadcrumbSeparator>;
    backTopVisibilityHeight: NumberConstructor;
    backTopRight: NumberConstructor;
    backTopBottom: NumberConstructor;
    backTopTarget: StringConstructor;
    collapse: BooleanConstructor;
    layout: import('vue').PropType<Layout>;
    compact: BooleanConstructor;
    maximized: import('vue').PropType<Maximized>;
    tabBar: {
        type: import('vue').PropType<TabBar>;
        default: boolean;
    };
    breadcrumb: {
        type: import('vue').PropType<boolean | EleBreadcrumbProps>;
        default: boolean;
    };
    backTop: {
        type: import('vue').PropType<boolean | EleBacktopProps>;
        default: boolean;
    };
    headerMenuProps: import('vue').PropType<EleMenusProps>;
    sidebarMenuProps: import('vue').PropType<EleMenusProps>;
    sideboxMenuProps: import('vue').PropType<EleMenusProps>;
    sidebarLayout: import('vue').PropType<SidebarLayout>;
    headerStyle: import('vue').PropType<import('./types').HeaderStyle>;
    sidebarStyle: {
        type: import('vue').PropType<import('./types').SidebarStyle>;
        default: string;
    };
    mixSidebarStyle: import('vue').PropType<import('./types').SidebarStyle>;
    tabStyle: {
        type: import('vue').PropType<import('./types').TabStyle>;
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
    tabContextMenu: import('vue').PropType<boolean | import('../ele-app/plus').EleDropdownProps>;
    tabContextMenus: import('vue').PropType<import('../ele-tabs/types').ContextMenus>;
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
    headerCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sidebarCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sideboxCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sideCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    tabsCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    contentCustomStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    logoStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    logoTitleStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    headerMenusStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sidebarMenusStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    sideboxMenusStyle: import('vue').PropType<import('../ele-app/types').StyleValue | null>;
    logoSrc: StringConstructor;
    logoTitle: StringConstructor;
    menuScrollToActive: {
        type: BooleanConstructor;
        default: boolean;
    };
}>> & Readonly<{
    onTabContextMenu?: ((_option: TabItemEventOption) => any) | undefined;
    "onUpdate:maximized"?: ((_maximized: boolean) => any) | undefined;
    onTabSortChange?: ((_data: TabItem[]) => any) | undefined;
    onTabClick?: ((_option: TabItemEventOption) => any) | undefined;
    onTabRemove?: ((_option: TabItemEventOption) => any) | undefined;
    onTabAdd?: ((_data: TabItem) => any) | undefined;
    "onUpdate:collapse"?: ((_collapse: boolean) => any) | undefined;
    onLogoClick?: ((_isHome: boolean, _e: MouseEvent) => any) | undefined;
    onHeadMenuOpen?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onHeadMenuClose?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onSideMenuOpen?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onSideMenuClose?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onBodySizeChange?: ((_option: import('./types').BodySizeChangeOption) => any) | undefined;
}>, {
    height: string | number;
    transitionDelay: number;
    expanded: boolean;
    uniqueOpened: boolean;
    collapse: boolean;
    ellipsis: boolean;
    compact: boolean;
    tabBar: TabBar;
    breadcrumb: boolean | EleBreadcrumbProps;
    backTop: boolean | EleBacktopProps;
    sidebarStyle: import('./types').SidebarStyle;
    tabStyle: import('./types').TabStyle;
    fixedHeader: boolean;
    fixedSidebar: boolean;
    fixedBody: boolean;
    logoInHeader: boolean;
    fixedHome: boolean;
    tabSortable: boolean;
    headerTitleSlot: string;
    headerIconSlot: string;
    sidebarTitleSlot: string;
    sidebarIconSlot: string;
    sideboxTitleSlot: string;
    sideboxIconSlot: string;
    menuScrollToActive: boolean;
    keepAlive: boolean;
    responsive: boolean;
    redirectPath: string;
    fluid: boolean;
    compressOnEsc: boolean;
    autoScrollTop: boolean;
    menuHoverTimeout: number;
    colorfulIcon: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
