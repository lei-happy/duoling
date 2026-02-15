import { PropType } from 'vue';
import { Columns } from '../../ele-data-table/types';
import { TableTool, TableLocale } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: {}) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 工具按钮布局 */
    tools: {
        type: PropType<TableTool[]>;
        required: true;
    };
    /** 表格尺寸 */
    size: StringConstructor;
    /** 表格列数据 */
    columns: PropType<Columns>;
    /** 是否开启列拖拽排序 */
    columnSortable: BooleanConstructor;
    /** 是否开启开关固定列 */
    columnFixed: BooleanConstructor;
    /** 是否最大化 */
    maximized: BooleanConstructor;
    /** 本地缓存的名称 */
    cacheKey: StringConstructor;
    /** 国际化 */
    lang: {
        type: PropType<TableLocale>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    reload: () => void;
    "update:size": (_size: "" | "small" | "default" | "large" | undefined) => void;
    "update:columns": (_columns: Columns, _tableColumns: Columns, _isReset: boolean) => void;
    "update:maximized": (_maximized: boolean) => void;
    openExportModal: () => void;
    openPrintModal: () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 工具按钮布局 */
    tools: {
        type: PropType<TableTool[]>;
        required: true;
    };
    /** 表格尺寸 */
    size: StringConstructor;
    /** 表格列数据 */
    columns: PropType<Columns>;
    /** 是否开启列拖拽排序 */
    columnSortable: BooleanConstructor;
    /** 是否开启开关固定列 */
    columnFixed: BooleanConstructor;
    /** 是否最大化 */
    maximized: BooleanConstructor;
    /** 本地缓存的名称 */
    cacheKey: StringConstructor;
    /** 国际化 */
    lang: {
        type: PropType<TableLocale>;
        required: true;
    };
}>> & Readonly<{
    onReload?: (() => any) | undefined;
    "onUpdate:size"?: ((_size: "" | "small" | "default" | "large" | undefined) => any) | undefined;
    "onUpdate:columns"?: ((_columns: Columns, _tableColumns: Columns, _isReset: boolean) => any) | undefined;
    "onUpdate:maximized"?: ((_maximized: boolean) => any) | undefined;
    onOpenExportModal?: (() => any) | undefined;
    onOpenPrintModal?: (() => any) | undefined;
}>, {
    maximized: boolean;
    columnSortable: boolean;
    columnFixed: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
