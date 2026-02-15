import { ProFormItemKey, ProFormItemProps, ProFormItemTypeData } from '../../ele-pro-form/types';
import { AddChildrenItemAction, ComponentGroup } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项 */
    items: ProFormItemProps[];
    /** 选中的表单项 */
    currentFormItemId?: ProFormItemKey;
    /** 折叠的表单项 */
    collapseItemIds?: ProFormItemKey[];
    /** 父级数据 */
    parent?: ProFormItemProps;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentFormItemId": (formItemId?: string | number | symbol | undefined) => void;
    toggleItemCollapse: (formItemId: string | number | symbol) => void;
    deleteItem: (formItemId: string | number | symbol) => void;
    copyItem: (formItemId: string | number | symbol) => void;
    addChildren: (triggerItem: ProFormItemProps, action?: AddChildrenItemAction | undefined) => void;
    updateItemChildren: (children: ProFormItemProps[], parentKey?: string | number | symbol | undefined) => void;
    openTableTool: (item: ProFormItemProps, event: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项 */
    items: ProFormItemProps[];
    /** 选中的表单项 */
    currentFormItemId?: ProFormItemKey;
    /** 折叠的表单项 */
    collapseItemIds?: ProFormItemKey[];
    /** 父级数据 */
    parent?: ProFormItemProps;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
}>>> & Readonly<{
    onToggleItemCollapse?: ((formItemId: string | number | symbol) => any) | undefined;
    onDeleteItem?: ((formItemId: string | number | symbol) => any) | undefined;
    onCopyItem?: ((formItemId: string | number | symbol) => any) | undefined;
    onAddChildren?: ((triggerItem: ProFormItemProps, action?: AddChildrenItemAction | undefined) => any) | undefined;
    onUpdateItemChildren?: ((children: ProFormItemProps[], parentKey?: string | number | symbol | undefined) => any) | undefined;
    "onUpdate:currentFormItemId"?: ((formItemId?: string | number | symbol | undefined) => any) | undefined;
    onOpenTableTool?: ((item: ProFormItemProps, event: MouseEvent) => any) | undefined;
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
