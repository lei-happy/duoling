import { UserComponent } from '../../ele-app/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 数据 */
    modelValue?: Record<string, any>;
    /** 弹窗标题 */
    title?: string;
    /** 需要排除编辑的字段 */
    excludeFields?: string[];
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (data?: Record<string, any> | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 数据 */
    modelValue?: Record<string, any>;
    /** 弹窗标题 */
    title?: string;
    /** 需要排除编辑的字段 */
    excludeFields?: string[];
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
}>>> & Readonly<{
    "onUpdate:modelValue"?: ((data?: Record<string, any> | undefined) => any) | undefined;
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
