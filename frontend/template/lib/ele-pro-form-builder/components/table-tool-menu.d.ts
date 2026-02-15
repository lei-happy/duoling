import { ProFormItemProps } from '../../ele-pro-form/types';
import { ComponentGroup, UpdateItemsResult } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 全部表单项 */
    formItems?: ProFormItemProps[];
    /** 组件库数据 */
    componentData?: ComponentGroup[];
}>>, {
    openMenu: (formItemId: string, triggerEl?: HTMLElement) => void;
    hideMenu: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    updateItems: (result: UpdateItemsResult) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 全部表单项 */
    formItems?: ProFormItemProps[];
    /** 组件库数据 */
    componentData?: ComponentGroup[];
}>>> & Readonly<{
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
