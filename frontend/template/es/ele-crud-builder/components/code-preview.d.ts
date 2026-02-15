import { UserComponent } from '../../ele-app/types';
import { EleCrudProps } from '../../ele-app/plusx';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 弹窗是否打开 */
    modelValue?: boolean;
    /** 表单配置数据 */
    config?: EleCrudProps;
    /** 代码查看器组件 */
    codeViewerComponent?: UserComponent;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (visible?: boolean | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 弹窗是否打开 */
    modelValue?: boolean;
    /** 表单配置数据 */
    config?: EleCrudProps;
    /** 代码查看器组件 */
    codeViewerComponent?: UserComponent;
}>>> & Readonly<{
    "onUpdate:modelValue"?: ((visible?: boolean | undefined) => any) | undefined;
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
