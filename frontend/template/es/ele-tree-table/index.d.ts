declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    headerCell?(_: {
        column: import('./types').TreeTableColumn;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    data: import('vue').PropType<import('./types').TreeTableDataItem[]>;
    columns: import('vue').PropType<import('./types').TreeTableColumn[]>;
    height: StringConstructor;
    tableStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    indexColWidth: {
        type: NumberConstructor;
        default: number;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    data: import('vue').PropType<import('./types').TreeTableDataItem[]>;
    columns: import('vue').PropType<import('./types').TreeTableColumn[]>;
    height: StringConstructor;
    tableStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    indexColWidth: {
        type: NumberConstructor;
        default: number;
    };
}>> & Readonly<{}>, {
    indexColWidth: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
