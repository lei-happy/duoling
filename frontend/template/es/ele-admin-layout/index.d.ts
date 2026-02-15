import { EleMenusInstance } from '../ele-app/plus';
import { MenuItem, MenuItemClickType } from '../ele-menus/types';
import { TabPaneItem, TabEventOption } from '../ele-tabs/types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    logo?(_: {}): any;
    logoTitle?(_: {}): any;
    left?(_: {}): any;
    breadcrumb?(_: {}): any;
    center?(_: {}): any;
    right?(_: {}): any;
    boxTop?(_: {}): any;
    boxBottom?(_: {}): any;
    top?(_: {}): any;
    bottom?(_: {}): any;
    default?(_: {}): any;
    body?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    height: {
        type: (StringConstructor | NumberConstructor)[];
        default: string;
    };
    headerMenus: import('vue').PropType<MenuItem[]>;
    headerActive: StringConstructor;
    sidebarMenus: import('vue').PropType<MenuItem[]>;
    sidebarActive: StringConstructor;
    sideboxMenus: import('vue').PropType<MenuItem[]>;
    sideboxActive: StringConstructor;
    tabs: import('vue').PropType<TabPaneItem[]>;
    tabActive: StringConstructor;
    levels: import('vue').PropType<import('../ele-breadcrumb/types').BreadcrumbItem[]>;
    collapse: BooleanConstructor;
    compact: BooleanConstructor;
    maximized: import('vue').PropType<import('./types').Maximized>;
    tabBar: {
        type: import('vue').PropType<import('./types').TabBar>;
        default: boolean;
    };
    breadcrumb: {
        type: import('vue').PropType<boolean | import('../ele-app/plus').EleBreadcrumbProps>;
        default: boolean;
    };
    backTop: {
        type: import('vue').PropType<boolean | import('../ele-app/plus').EleBacktopProps>;
        default: boolean;
    };
    headerMenuProps: import('vue').PropType<import('../ele-app/plus').EleMenusProps>;
    sidebarMenuProps: import('vue').PropType<import('../ele-app/plus').EleMenusProps>;
    sideboxMenuProps: import('vue').PropType<import('../ele-app/plus').EleMenusProps>;
    layout: import('vue').PropType<import('./types').Layout>;
    sidebarLayout: import('vue').PropType<import('./types').SidebarLayout>;
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
    isHome: BooleanConstructor;
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
    mobile: BooleanConstructor;
}>, {
    sidebarMenuRef: import('vue').ShallowRef<EleMenusInstance, EleMenusInstance>;
    sideboxMenuRef: import('vue').ShallowRef<EleMenusInstance, EleMenusInstance>;
    getContentEl: () => HTMLElement | null;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    tabContextMenu: (_option: TabEventOption) => void;
    tabSortChange: (_data: TabPaneItem[]) => void;
    tabClick: (_option: TabEventOption) => void;
    tabRemove: (_name: string) => void;
    "update:collapse": (_collapse: boolean) => void;
    logoClick: (_e: MouseEvent) => void;
    headMenuOpen: (_index: string, _indexPath: string[]) => void;
    headMenuClose: (_index: string, _indexPath: string[]) => void;
    headMenuItemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => void;
    headMenuItemMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    headMenuItemMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
    headMouseenter: (_e: MouseEvent) => void;
    headMouseleave: (_e: MouseEvent) => void;
    boxMenuItemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => void;
    boxMenuItemMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    boxMenuItemMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
    boxMouseenter: (_e: MouseEvent) => void;
    boxMouseleave: (_e: MouseEvent) => void;
    sideMenuOpen: (_index: string, _indexPath: string[]) => void;
    sideMenuClose: (_index: string, _indexPath: string[]) => void;
    sideMenuItemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => void;
    sideMouseenter: (_e: MouseEvent) => void;
    sideMouseleave: (_e: MouseEvent) => void;
    contentMounted: (_contentEl: HTMLElement, _modalsEl: HTMLElement) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    height: {
        type: (StringConstructor | NumberConstructor)[];
        default: string;
    };
    headerMenus: import('vue').PropType<MenuItem[]>;
    headerActive: StringConstructor;
    sidebarMenus: import('vue').PropType<MenuItem[]>;
    sidebarActive: StringConstructor;
    sideboxMenus: import('vue').PropType<MenuItem[]>;
    sideboxActive: StringConstructor;
    tabs: import('vue').PropType<TabPaneItem[]>;
    tabActive: StringConstructor;
    levels: import('vue').PropType<import('../ele-breadcrumb/types').BreadcrumbItem[]>;
    collapse: BooleanConstructor;
    compact: BooleanConstructor;
    maximized: import('vue').PropType<import('./types').Maximized>;
    tabBar: {
        type: import('vue').PropType<import('./types').TabBar>;
        default: boolean;
    };
    breadcrumb: {
        type: import('vue').PropType<boolean | import('../ele-app/plus').EleBreadcrumbProps>;
        default: boolean;
    };
    backTop: {
        type: import('vue').PropType<boolean | import('../ele-app/plus').EleBacktopProps>;
        default: boolean;
    };
    headerMenuProps: import('vue').PropType<import('../ele-app/plus').EleMenusProps>;
    sidebarMenuProps: import('vue').PropType<import('../ele-app/plus').EleMenusProps>;
    sideboxMenuProps: import('vue').PropType<import('../ele-app/plus').EleMenusProps>;
    layout: import('vue').PropType<import('./types').Layout>;
    sidebarLayout: import('vue').PropType<import('./types').SidebarLayout>;
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
    isHome: BooleanConstructor;
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
    mobile: BooleanConstructor;
}>> & Readonly<{
    onTabContextMenu?: ((_option: TabEventOption) => any) | undefined;
    onTabSortChange?: ((_data: TabPaneItem[]) => any) | undefined;
    onTabClick?: ((_option: TabEventOption) => any) | undefined;
    onTabRemove?: ((_name: string) => any) | undefined;
    "onUpdate:collapse"?: ((_collapse: boolean) => any) | undefined;
    onLogoClick?: ((_e: MouseEvent) => any) | undefined;
    onHeadMenuOpen?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onHeadMenuClose?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onHeadMenuItemClick?: ((_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => any) | undefined;
    onHeadMenuItemMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onHeadMenuItemMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onHeadMouseenter?: ((_e: MouseEvent) => any) | undefined;
    onHeadMouseleave?: ((_e: MouseEvent) => any) | undefined;
    onBoxMenuItemClick?: ((_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => any) | undefined;
    onBoxMenuItemMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onBoxMenuItemMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onBoxMouseenter?: ((_e: MouseEvent) => any) | undefined;
    onBoxMouseleave?: ((_e: MouseEvent) => any) | undefined;
    onSideMenuOpen?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onSideMenuClose?: ((_index: string, _indexPath: string[]) => any) | undefined;
    onSideMenuItemClick?: ((_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => any) | undefined;
    onSideMouseenter?: ((_e: MouseEvent) => any) | undefined;
    onSideMouseleave?: ((_e: MouseEvent) => any) | undefined;
    onContentMounted?: ((_contentEl: HTMLElement, _modalsEl: HTMLElement) => any) | undefined;
}>, {
    height: string | number;
    mobile: boolean;
    collapse: boolean;
    compact: boolean;
    breadcrumb: boolean | import('../ele-app/plus').EleBreadcrumbProps;
    tabBar: import('./types').TabBar;
    backTop: boolean | import('../ele-app/plus').EleBacktopProps;
    sidebarStyle: import('./types').SidebarStyle;
    tabStyle: import('./types').TabStyle;
    fixedHeader: boolean;
    fixedSidebar: boolean;
    fixedBody: boolean;
    logoInHeader: boolean;
    fixedHome: boolean;
    isHome: boolean;
    tabSortable: boolean;
    headerTitleSlot: string;
    headerIconSlot: string;
    sidebarTitleSlot: string;
    sidebarIconSlot: string;
    sideboxTitleSlot: string;
    sideboxIconSlot: string;
    menuScrollToActive: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
