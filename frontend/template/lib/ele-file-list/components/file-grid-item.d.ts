import { PropType } from 'vue';
import { IconItem, FileItem, SelectionType, ContextOpenOption } from '../types';

declare function __VLS_template(): {
    icon?(_: {
        icon: string | undefined;
        item: FileItem;
    }): any;
    title?(_: {
        item: FileItem;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 数据 */
    item: {
        type: PropType<FileItem>;
        required: true;
    };
    /** 选择框类型 */
    selectionType: PropType<SelectionType>;
    /** 多选选中数据 */
    selections: PropType<FileItem[]>;
    /** 单选选中数据 */
    current: PropType<FileItem>;
    /** 后缀对应的图标 */
    icons: PropType<IconItem[]>;
    /** 右键下拉菜单是否显示 */
    ctxMenuDropdownVisible: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    click: (_item: FileItem) => void;
    checkChange: (_item: FileItem) => void;
    contextOpen: (_option: ContextOpenOption) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 数据 */
    item: {
        type: PropType<FileItem>;
        required: true;
    };
    /** 选择框类型 */
    selectionType: PropType<SelectionType>;
    /** 多选选中数据 */
    selections: PropType<FileItem[]>;
    /** 单选选中数据 */
    current: PropType<FileItem>;
    /** 后缀对应的图标 */
    icons: PropType<IconItem[]>;
    /** 右键下拉菜单是否显示 */
    ctxMenuDropdownVisible: BooleanConstructor;
}>> & Readonly<{
    onClick?: ((_item: FileItem) => any) | undefined;
    onCheckChange?: ((_item: FileItem) => any) | undefined;
    onContextOpen?: ((_option: ContextOpenOption) => any) | undefined;
}>, {
    ctxMenuDropdownVisible: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
