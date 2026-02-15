declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 对应的表单项类型 */
    itemType?: string;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    delete: (event: MouseEvent) => void;
    copy: (event: MouseEvent) => void;
    add: (event: MouseEvent) => void;
    addTableRow: (event: MouseEvent) => void;
    addTableCol: (event: MouseEvent) => void;
    openTableTool: (event: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 对应的表单项类型 */
    itemType?: string;
}>>> & Readonly<{
    onDelete?: ((event: MouseEvent) => any) | undefined;
    onAdd?: ((event: MouseEvent) => any) | undefined;
    onCopy?: ((event: MouseEvent) => any) | undefined;
    onAddTableRow?: ((event: MouseEvent) => any) | undefined;
    onAddTableCol?: ((event: MouseEvent) => any) | undefined;
    onOpenTableTool?: ((event: MouseEvent) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
type __VLS_NonUndefinedable<T> = T extends undefined ? never : T;
type __VLS_TypePropsToRuntimeProps<T> = {
    [K in keyof T]-?: {} extends Pick<T, K> ? {
        type: import('vue').PropType<__VLS_NonUndefinedable<T[K]>>;
    } : {
        type: import('vue').PropType<T[K]>;
        required: true;
    };
};
