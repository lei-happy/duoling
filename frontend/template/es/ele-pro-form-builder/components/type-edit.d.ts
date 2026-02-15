import { ProFormItemProps } from '../../ele-pro-form/types';
import { ComponentGroup } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项数据 */
    formItem?: ProFormItemProps;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    openComponentPicker: (item: ProFormItemProps) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项数据 */
    formItem?: ProFormItemProps;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
}>>> & Readonly<{
    onOpenComponentPicker?: ((item: ProFormItemProps) => any) | undefined;
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
