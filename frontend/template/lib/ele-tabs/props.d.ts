import { PropType, ExtractPropTypes, InjectionKey } from 'vue';
import { tabsProps as elTabsProps } from 'element-plus';
import { EleDropdownProps, EleDropdownInstance } from '../ele-app/plus';
import { TabPaneItem, TabSize, TabType, ContextMenus, TabEventOption, TabWrapProvide } from './types';

/**
 * 属性
 */
export declare const tabsProps: {
    /** 标签页数据 */
    items: {
        type: PropType<TabPaneItem[]>;
        required: boolean;
    };
    /** 尺寸 */
    size: PropType<TabSize>;
    /** 风格类型 */
    type: PropType<TabType>;
    /** 标签是否居中显示 */
    center: BooleanConstructor;
    /** 是否支持右键菜单 */
    contextMenu: PropType<boolean | EleDropdownProps>;
    /** 右键菜单 */
    contextMenus: PropType<ContextMenus>;
    /** 是否支持拖动排序 */
    sortable: BooleanConstructor;
    /** 是否支持鼠标滚轮滑动 */
    mousewheel: BooleanConstructor;
    /** 是否自己处理页签点击事件 */
    handleClick: BooleanConstructor;
    /** 内部表格是否弹性布局 */
    flexTable: PropType<boolean | "auto">;
    closable: BooleanConstructor;
    addable: BooleanConstructor;
    modelValue: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    editable: BooleanConstructor;
    tabPosition: {
        readonly type: PropType<"bottom" | "left" | "right" | "top">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "top";
    };
    beforeLeave: {
        readonly type: PropType<(newName: import('element-plus').TabPaneName, oldName: import('element-plus').TabPaneName) => boolean | void | Promise<boolean | void>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => true;
    };
    stretch: BooleanConstructor;
};
export type TabsProps = ExtractPropTypes<typeof tabsProps>;
/**
 * 事件
 */
export declare const tabsEmits: {
    /** 页签点击事件 */
    tabItemClick: (_opt: TabEventOption) => boolean;
    /** 页签右键菜单项点击事件 */
    tabContextMenu: (_opt: TabEventOption) => boolean;
    /** 页签右键菜单打开事件 */
    tabContextOpen: (_ref: EleDropdownInstance, _item?: TabPaneItem | null, _name?: string | number | null) => boolean;
    /** 拖动排序改变事件 */
    tabSortChange: (_data: TabPaneItem[]) => boolean;
    "update:modelValue": (name: import('element-plus').TabPaneName) => name is string | number;
    tabClick: (pane: import('element-plus').TabsPaneContext, ev: Event) => boolean;
    tabChange: (name: import('element-plus').TabPaneName) => name is string | number;
    edit: (paneName: import('element-plus').TabPaneName | undefined, action: "remove" | "add") => boolean;
    tabRemove: (name: import('element-plus').TabPaneName) => name is string | number;
    tabAdd: () => boolean;
};
/**
 * 标签页组件属性名
 */
export type TabPropKeys = Array<keyof typeof elTabsProps>;
export declare const tabPropKeys: TabPropKeys;
/**
 * 标签页容器依赖注入key
 */
export declare const TAB_WRAP_KEY: InjectionKey<TabWrapProvide>;
