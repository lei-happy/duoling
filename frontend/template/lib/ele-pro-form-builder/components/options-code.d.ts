import { UserComponent } from '../../ele-app/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 选项数据代码 */
    data?: Array<any> | string;
    /** 默认提示示例代码 */
    codePlaceholder?: string;
    /** 代码字符串前缀 */
    codePrefix: string;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
}>>, {
    getResult: () => string | undefined;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 选项数据代码 */
    data?: Array<any> | string;
    /** 默认提示示例代码 */
    codePlaceholder?: string;
    /** 代码字符串前缀 */
    codePrefix: string;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
}>>> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
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
