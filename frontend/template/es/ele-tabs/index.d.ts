import { TabPaneName } from 'element-plus';
import { ElTabsInstance } from '../ele-app/el';
import { EleDropdownInstance } from '../ele-app/plus';
import { TabPaneItem, TabSize, TabType } from './types';

declare function __VLS_template(): Partial<Record<NonNullable<string | number>, (_: {
    item: TabPaneItem;
}) => any>> & {
    "add-icon"?(_: {}): any;
    addIcon?(_: {}): any;
    label?(_: {
        item: TabPaneItem;
        label: string | undefined;
        active: (string | number) | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    items: {
        type: import('vue').PropType<TabPaneItem[]>;
        required: boolean;
    };
    size: import('vue').PropType<TabSize>;
    type: import('vue').PropType<TabType>;
    center: BooleanConstructor;
    contextMenu: import('vue').PropType<boolean | import('../ele-app/plus').EleDropdownProps>;
    contextMenus: import('vue').PropType<import('./types').ContextMenus>;
    sortable: BooleanConstructor;
    mousewheel: BooleanConstructor;
    handleClick: BooleanConstructor;
    flexTable: import('vue').PropType<boolean | "auto">;
    closable: BooleanConstructor;
    addable: BooleanConstructor;
    modelValue: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    editable: BooleanConstructor;
    tabPosition: {
        readonly type: import('vue').PropType<"bottom" | "left" | "right" | "top">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "top";
    };
    beforeLeave: {
        readonly type: import('vue').PropType<(newName: TabPaneName, oldName: TabPaneName) => boolean | void | Promise<boolean | void>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => true;
    };
    stretch: BooleanConstructor;
}>, {
    tabRef: import('vue').Ref<ElTabsInstance, ElTabsInstance>;
    ctxMenuDropdownRef: import('vue').Ref<EleDropdownInstance, EleDropdownInstance>;
    hideAllDropdown: () => void;
    updateActiveBar: () => void;
    scrollTabs: (direction: "prev" | "next", done?: () => void) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (name: TabPaneName) => void;
    edit: (paneName: TabPaneName | undefined, action: "add" | "remove") => void;
    tabItemClick: (_opt: import('./types').TabEventOption) => void;
    tabContextMenu: (_opt: import('./types').TabEventOption) => void;
    tabContextOpen: (_ref: EleDropdownInstance, _item?: TabPaneItem | null | undefined, _name?: string | number | null | undefined) => void;
    tabSortChange: (_data: TabPaneItem[]) => void;
    tabClick: (pane: {
        uid: number;
        getVnode: () => import('vue').VNode;
        slots: import('vue').Slots;
        props: {
            readonly label: string;
            readonly disabled: boolean;
            readonly lazy: boolean;
            readonly closable?: boolean | undefined;
            readonly name?: (string | number) | undefined;
        };
        paneName: TabPaneName | undefined;
        active: boolean;
        index: string | undefined;
        isClosable: boolean;
        isFocusInsidePane: () => boolean | undefined;
    }, ev: Event) => void;
    tabChange: (name: TabPaneName) => void;
    tabRemove: (name: TabPaneName) => void;
    tabAdd: () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    items: {
        type: import('vue').PropType<TabPaneItem[]>;
        required: boolean;
    };
    size: import('vue').PropType<TabSize>;
    type: import('vue').PropType<TabType>;
    center: BooleanConstructor;
    contextMenu: import('vue').PropType<boolean | import('../ele-app/plus').EleDropdownProps>;
    contextMenus: import('vue').PropType<import('./types').ContextMenus>;
    sortable: BooleanConstructor;
    mousewheel: BooleanConstructor;
    handleClick: BooleanConstructor;
    flexTable: import('vue').PropType<boolean | "auto">;
    closable: BooleanConstructor;
    addable: BooleanConstructor;
    modelValue: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    editable: BooleanConstructor;
    tabPosition: {
        readonly type: import('vue').PropType<"bottom" | "left" | "right" | "top">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "top";
    };
    beforeLeave: {
        readonly type: import('vue').PropType<(newName: TabPaneName, oldName: TabPaneName) => boolean | void | Promise<boolean | void>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => true;
    };
    stretch: BooleanConstructor;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((name: TabPaneName) => any) | undefined;
    onEdit?: ((paneName: TabPaneName | undefined, action: "add" | "remove") => any) | undefined;
    onTabItemClick?: ((_opt: import('./types').TabEventOption) => any) | undefined;
    onTabContextMenu?: ((_opt: import('./types').TabEventOption) => any) | undefined;
    onTabContextOpen?: ((_ref: EleDropdownInstance, _item?: TabPaneItem | null | undefined, _name?: string | number | null | undefined) => any) | undefined;
    onTabSortChange?: ((_data: TabPaneItem[]) => any) | undefined;
    onTabClick?: ((pane: {
        uid: number;
        getVnode: () => import('vue').VNode;
        slots: import('vue').Slots;
        props: {
            readonly label: string;
            readonly disabled: boolean;
            readonly lazy: boolean;
            readonly closable?: boolean | undefined;
            readonly name?: (string | number) | undefined;
        };
        paneName: TabPaneName | undefined;
        active: boolean;
        index: string | undefined;
        isClosable: boolean;
        isFocusInsidePane: () => boolean | undefined;
    }, ev: Event) => any) | undefined;
    onTabChange?: ((name: TabPaneName) => any) | undefined;
    onTabRemove?: ((name: TabPaneName) => any) | undefined;
    onTabAdd?: (() => any) | undefined;
}>, {
    closable: boolean;
    center: boolean;
    sortable: boolean;
    addable: boolean;
    editable: boolean;
    tabPosition: "bottom" | "left" | "right" | "top";
    beforeLeave: (newName: TabPaneName, oldName: TabPaneName) => boolean | void | Promise<boolean | void>;
    stretch: boolean;
    handleClick: boolean;
    mousewheel: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
