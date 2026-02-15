import { CSSProperties, PropType } from 'vue';
import { ElFormItemProps, ElButtonProps, ElLinkProps } from '../../ele-app/el';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    footer?(_: {
        submitForm: () => void;
        resetForm: () => void;
    }): any;
    footerExtra?(_: {
        submitForm: () => void;
        resetForm: () => void;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 底栏 ElFormItem 属性 */
    footerProps: PropType<ElFormItemProps>;
    /** 底栏 ElFormItem 插槽 */
    footerSlots: PropType<Record<string, string>>;
    /** 自动计算底栏栅格份数 */
    autoFooterCol: BooleanConstructor;
    /** 底栏样式 */
    footerStyle: PropType<CSSProperties>;
    /** 提交按钮文本 */
    submitText: StringConstructor;
    /** 重置按钮文本 */
    resetText: StringConstructor;
    /** 提交按钮属性 */
    submitButtonProps: PropType<ElButtonProps>;
    /** 重置按钮属性 */
    resetButtonProps: PropType<ElButtonProps>;
    /** 是否在底栏显示表单展开收起按钮 */
    showSearchExpand: BooleanConstructor;
    /** 搜索表单展开状态 */
    searchExpand: BooleanConstructor;
    /** 展开和收起按钮属性 */
    searchExpandButtonProps: PropType<ElLinkProps>;
    /** 展开按钮的文字 */
    searchExpandText: StringConstructor;
    /** 收起按钮的文字 */
    searchShrinkText: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    reset: () => void;
    submit: () => void;
    updateSearchExpand: (_expand: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 底栏 ElFormItem 属性 */
    footerProps: PropType<ElFormItemProps>;
    /** 底栏 ElFormItem 插槽 */
    footerSlots: PropType<Record<string, string>>;
    /** 自动计算底栏栅格份数 */
    autoFooterCol: BooleanConstructor;
    /** 底栏样式 */
    footerStyle: PropType<CSSProperties>;
    /** 提交按钮文本 */
    submitText: StringConstructor;
    /** 重置按钮文本 */
    resetText: StringConstructor;
    /** 提交按钮属性 */
    submitButtonProps: PropType<ElButtonProps>;
    /** 重置按钮属性 */
    resetButtonProps: PropType<ElButtonProps>;
    /** 是否在底栏显示表单展开收起按钮 */
    showSearchExpand: BooleanConstructor;
    /** 搜索表单展开状态 */
    searchExpand: BooleanConstructor;
    /** 展开和收起按钮属性 */
    searchExpandButtonProps: PropType<ElLinkProps>;
    /** 展开按钮的文字 */
    searchExpandText: StringConstructor;
    /** 收起按钮的文字 */
    searchShrinkText: StringConstructor;
}>> & Readonly<{
    onReset?: (() => any) | undefined;
    onSubmit?: (() => any) | undefined;
    onUpdateSearchExpand?: ((_expand: boolean) => any) | undefined;
}>, {
    autoFooterCol: boolean;
    showSearchExpand: boolean;
    searchExpand: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
