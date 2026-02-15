import { CrudField } from '../../ele-crud/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 字段 */
    items: CrudField[];
    /** 折叠的字段 */
    collapseItemIds?: string[];
    /** 父级数据 */
    parent?: CrudField;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    toggleItemCollapse: (key: string) => void;
    deleteItem: (key: string) => void;
    copyItem: (key: string) => void;
    editItem: (item: CrudField) => void;
    addChildren: (parentKey: string) => void;
    updateItemChildren: (data: CrudField[], parentKey?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 字段 */
    items: CrudField[];
    /** 折叠的字段 */
    collapseItemIds?: string[];
    /** 父级数据 */
    parent?: CrudField;
}>>> & Readonly<{
    onToggleItemCollapse?: ((key: string) => any) | undefined;
    onDeleteItem?: ((key: string) => any) | undefined;
    onCopyItem?: ((key: string) => any) | undefined;
    onEditItem?: ((item: CrudField) => any) | undefined;
    onAddChildren?: ((parentKey: string) => any) | undefined;
    onUpdateItemChildren?: ((data: CrudField[], parentKey?: string | undefined) => any) | undefined;
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
