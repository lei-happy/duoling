import { ProFormItemKey, ProFormItemProps, ProFormItemTypeData } from '../../ele-pro-form/types';
import { ComponentGroup, UpdateItemsResult } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 全部表单项 */
    formItems?: ProFormItemProps[];
    /** 要添加子级的父级表单项 id */
    parentFormItemId?: ProFormItemKey;
    /** 是否可拖拽 */
    draggable?: boolean;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 选中的组件类型 */
    selectedType?: string;
    /** 选中的表单项 id */
    selectedFormItemId?: ProFormItemKey;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    updateItems: (result: UpdateItemsResult) => void;
    itemClick: (componentType: string) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 全部表单项 */
    formItems?: ProFormItemProps[];
    /** 要添加子级的父级表单项 id */
    parentFormItemId?: ProFormItemKey;
    /** 是否可拖拽 */
    draggable?: boolean;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 选中的组件类型 */
    selectedType?: string;
    /** 选中的表单项 id */
    selectedFormItemId?: ProFormItemKey;
}>>> & Readonly<{
    onItemClick?: ((componentType: string) => any) | undefined;
    onUpdateItems?: ((result: UpdateItemsResult) => any) | undefined;
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
