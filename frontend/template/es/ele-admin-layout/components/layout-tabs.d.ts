import { PropType } from 'vue';
import { EleDropdownProps } from '../../ele-app/plus';
import { TabPaneItem, TabEventOption, ContextMenus } from '../../ele-tabs/types';
import { TabStyle } from '../types';

declare function __VLS_template(): {
    tabHome?(_: {
        active: string | undefined;
    }): any;
    tabTitle?(_: {
        item: TabPaneItem;
        label: string | undefined;
        active: (string | number) | undefined;
    }): any;
    tabExtra?(_: {
        active: string | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 页签数据 */
    tabs: PropType<TabPaneItem[]>;
    /** 页签选中 */
    active: StringConstructor;
    /** 是否需要固定的主页页签 */
    fixedHome: BooleanConstructor;
    /** 主页路由地址 */
    homePath: StringConstructor;
    /** 当前路由是否是主页 */
    isHome: BooleanConstructor;
    /** 页签风格 */
    tabStyle: PropType<TabStyle>;
    /** 是否支持右键菜单 */
    tabContextMenu: PropType<boolean | EleDropdownProps>;
    /** 右键菜单 */
    tabContextMenus: PropType<ContextMenus>;
    /** 是否支持拖动排序 */
    tabSortable: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    tabContextMenu: (_option: TabEventOption) => void;
    tabSortChange: (_data: TabPaneItem[]) => void;
    tabClick: (_option: TabEventOption) => void;
    tabRemove: (_name: string) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 页签数据 */
    tabs: PropType<TabPaneItem[]>;
    /** 页签选中 */
    active: StringConstructor;
    /** 是否需要固定的主页页签 */
    fixedHome: BooleanConstructor;
    /** 主页路由地址 */
    homePath: StringConstructor;
    /** 当前路由是否是主页 */
    isHome: BooleanConstructor;
    /** 页签风格 */
    tabStyle: PropType<TabStyle>;
    /** 是否支持右键菜单 */
    tabContextMenu: PropType<boolean | EleDropdownProps>;
    /** 右键菜单 */
    tabContextMenus: PropType<ContextMenus>;
    /** 是否支持拖动排序 */
    tabSortable: BooleanConstructor;
}>> & Readonly<{
    onTabContextMenu?: ((_option: TabEventOption) => any) | undefined;
    onTabSortChange?: ((_data: TabPaneItem[]) => any) | undefined;
    onTabClick?: ((_option: TabEventOption) => any) | undefined;
    onTabRemove?: ((_name: string) => any) | undefined;
}>, {
    fixedHome: boolean;
    isHome: boolean;
    tabSortable: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
