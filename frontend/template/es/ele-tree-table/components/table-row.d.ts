declare function __VLS_template(): {
    cells?(_: {}): any;
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 行索引 */
    rowIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 是否有子级 */
    hasChildren: BooleanConstructor;
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
    /** 行索引 */
    rowIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 是否有子级 */
    hasChildren: BooleanConstructor;
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
}>> & Readonly<{}>, {
    hasChildren: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
