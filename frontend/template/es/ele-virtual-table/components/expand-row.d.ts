import { PropType } from 'vue';
import { DataItem, Column } from '../../ele-data-table/types';

declare function __VLS_template(): Partial<Record<string, (_: {
    row: DataItem | undefined;
    column: Column;
    $index: number | undefined;
}) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 列配置(原始配置) */
    column: PropType<Column>;
    /** 行索引 */
    rowIndex: NumberConstructor;
    /** 行数据(原始数据) */
    rowData: PropType<DataItem>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 列配置(原始配置) */
    column: PropType<Column>;
    /** 行索引 */
    rowIndex: NumberConstructor;
    /** 行数据(原始数据) */
    rowData: PropType<DataItem>;
}>> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
