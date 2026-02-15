import { ProFormItemProps, ProFormItemKey } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项 */
    item: ProFormItemProps;
    /** 编辑模式选中的表单项 */
    activeItemKey?: ProFormItemKey;
    /** 是否需要拖拽手柄 */
    handle?: boolean;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:activeItemKey": (activeKey?: string | number | symbol | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项 */
    item: ProFormItemProps;
    /** 编辑模式选中的表单项 */
    activeItemKey?: ProFormItemKey;
    /** 是否需要拖拽手柄 */
    handle?: boolean;
}>>> & Readonly<{
    "onUpdate:activeItemKey"?: ((activeKey?: string | number | symbol | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
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
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
