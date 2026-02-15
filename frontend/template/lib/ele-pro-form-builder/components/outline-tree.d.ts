import { ProFormItemKey, ProFormItemProps, ProFormItemTypeData } from '../../ele-pro-form/types';
import { ComponentGroup, UpdateItemsResult } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 全部表单项 */
    formItems?: ProFormItemProps[];
    /** 选中的表单项 */
    currentFormItemId?: ProFormItemKey;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentFormItemId": (formItemId?: string | number | symbol | undefined) => void;
    updateItems: (result: UpdateItemsResult) => void;
    updateItemChildren: (children: ProFormItemProps[], parentKey?: string | number | symbol | undefined) => void;
    openTableTool: (formItemId: string, el: HTMLElement) => void;
    openComponentPicker: (formItemId: string) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 全部表单项 */
    formItems?: ProFormItemProps[];
    /** 选中的表单项 */
    currentFormItemId?: ProFormItemKey;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
}>>> & Readonly<{
    onUpdateItems?: ((result: UpdateItemsResult) => any) | undefined;
    onUpdateItemChildren?: ((children: ProFormItemProps[], parentKey?: string | number | symbol | undefined) => any) | undefined;
    onOpenTableTool?: ((formItemId: string, el: HTMLElement) => any) | undefined;
    "onUpdate:currentFormItemId"?: ((formItemId?: string | number | symbol | undefined) => any) | undefined;
    onOpenComponentPicker?: ((formItemId: string) => any) | undefined;
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
