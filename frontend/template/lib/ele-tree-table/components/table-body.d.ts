import { PropType } from 'vue';
import { TreeTableDataItem, TreeTableColumn } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    bodyCell?(_: {
        row: TreeTableDataItem;
        rowIndex: number;
        column: TreeTableColumn;
        treeLevel: number;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 数据 */
    data: {
        type: PropType<TreeTableDataItem[]>;
        required: true;
    };
    /** 列配置 */
    columns: {
        type: PropType<TreeTableColumn[]>;
        required: true;
    };
    /** 序号列宽度 */
    indexColWidth: {
        type: NumberConstructor;
        required: true;
    };
    /** 所处深度 */
    level: {
        type: NumberConstructor;
        required: true;
    };
    /** 最大深度 */
    depth: {
        type: NumberConstructor;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 数据 */
    data: {
        type: PropType<TreeTableDataItem[]>;
        required: true;
    };
    /** 列配置 */
    columns: {
        type: PropType<TreeTableColumn[]>;
        required: true;
    };
    /** 序号列宽度 */
    indexColWidth: {
        type: NumberConstructor;
        required: true;
    };
    /** 所处深度 */
    level: {
        type: NumberConstructor;
        required: true;
    };
    /** 最大深度 */
    depth: {
        type: NumberConstructor;
        required: true;
    };
}>> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
