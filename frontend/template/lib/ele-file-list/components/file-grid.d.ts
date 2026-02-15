import { PropType } from 'vue';
import { IconItem, FileItem, SelectionType, ContextOpenOption } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 文件数据 */
    data: PropType<FileItem[]>;
    /** 后缀对应的图标 */
    icons: PropType<IconItem[]>;
    /** 选择框类型 */
    selectionType: PropType<SelectionType>;
    /** 已选中的数据 */
    selections: PropType<FileItem[]>;
    /** 单选选中数据 */
    current: PropType<FileItem>;
    /** 是否是全选 */
    isCheckAll: BooleanConstructor;
    /** 是否是半选 */
    isIndeterminate: BooleanConstructor;
    /** 全选按钮文字 */
    checkAllText: StringConstructor;
    /** 选中后的文字 */
    selectedText: StringConstructor;
    /** 文件右键菜单是否打开 */
    ctxMenuDropdownVisible: BooleanConstructor;
    /** 当前打开的右键菜单对应的文件数据 */
    contextMenuFileItem: PropType<FileItem | null>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_item: FileItem) => void;
    checkAllChange: () => void;
    itemCheckChange: (_item: FileItem) => void;
    itemContextOpen: (_option: ContextOpenOption) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 文件数据 */
    data: PropType<FileItem[]>;
    /** 后缀对应的图标 */
    icons: PropType<IconItem[]>;
    /** 选择框类型 */
    selectionType: PropType<SelectionType>;
    /** 已选中的数据 */
    selections: PropType<FileItem[]>;
    /** 单选选中数据 */
    current: PropType<FileItem>;
    /** 是否是全选 */
    isCheckAll: BooleanConstructor;
    /** 是否是半选 */
    isIndeterminate: BooleanConstructor;
    /** 全选按钮文字 */
    checkAllText: StringConstructor;
    /** 选中后的文字 */
    selectedText: StringConstructor;
    /** 文件右键菜单是否打开 */
    ctxMenuDropdownVisible: BooleanConstructor;
    /** 当前打开的右键菜单对应的文件数据 */
    contextMenuFileItem: PropType<FileItem | null>;
}>> & Readonly<{
    onItemClick?: ((_item: FileItem) => any) | undefined;
    onCheckAllChange?: (() => any) | undefined;
    onItemCheckChange?: ((_item: FileItem) => any) | undefined;
    onItemContextOpen?: ((_option: ContextOpenOption) => any) | undefined;
}>, {
    isCheckAll: boolean;
    isIndeterminate: boolean;
    ctxMenuDropdownVisible: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
