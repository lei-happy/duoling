import { UserComponent } from '../../ele-app/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 数据 */
    modelValue?: string;
    /** 弹窗标题 */
    title?: string;
    /** 顶部提示内容 */
    codeTips?: string;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (data?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 数据 */
    modelValue?: string;
    /** 弹窗标题 */
    title?: string;
    /** 顶部提示内容 */
    codeTips?: string;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
}>>> & Readonly<{
    "onUpdate:modelValue"?: ((data?: string | undefined) => any) | undefined;
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
