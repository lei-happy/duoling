import { ProFormItemProps } from '../../ele-pro-form/types';
import { ComponentGroup } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 添加按钮文本 */
    addBtnText?: string;
    /** 表单项数据 */
    formItem: ProFormItemProps;
    /** 组件库数据 */
    componentData: ComponentGroup[];
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentFormItemId": (formItemId?: string | undefined) => void;
    updateChildLabel: (label: string, child: ProFormItemProps, field: string) => void;
    sortChildren: (children: ProFormItemProps[]) => void;
    deleteChildren: (child: ProFormItemProps) => void;
    addChildren: (parent: ProFormItemProps) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 添加按钮文本 */
    addBtnText?: string;
    /** 表单项数据 */
    formItem: ProFormItemProps;
    /** 组件库数据 */
    componentData: ComponentGroup[];
}>>> & Readonly<{
    onAddChildren?: ((parent: ProFormItemProps) => any) | undefined;
    "onUpdate:currentFormItemId"?: ((formItemId?: string | undefined) => any) | undefined;
    onUpdateChildLabel?: ((label: string, child: ProFormItemProps, field: string) => any) | undefined;
    onSortChildren?: ((children: ProFormItemProps[]) => any) | undefined;
    onDeleteChildren?: ((child: ProFormItemProps) => any) | undefined;
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
