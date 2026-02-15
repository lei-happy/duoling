import { PropType } from 'vue';
import { ElMessageOptions } from '../el';

declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 内容 */
    message: StringConstructor;
    /** 类型 */
    type: PropType<ElMessageOptions["type"]>;
    /** 图标 */
    icon: PropType<ElMessageOptions["icon"]>;
    /** 是否显示关闭按钮 */
    showClose: BooleanConstructor;
    /** 内容是否是富文本 */
    dangerouslyUseHTMLString: BooleanConstructor;
    /** 是否是加载框 */
    loading: PropType<boolean | null>;
    /** 标识id */
    messageId: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    close: () => void;
    messageDestroy: (_messageId?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 内容 */
    message: StringConstructor;
    /** 类型 */
    type: PropType<ElMessageOptions["type"]>;
    /** 图标 */
    icon: PropType<ElMessageOptions["icon"]>;
    /** 是否显示关闭按钮 */
    showClose: BooleanConstructor;
    /** 内容是否是富文本 */
    dangerouslyUseHTMLString: BooleanConstructor;
    /** 是否是加载框 */
    loading: PropType<boolean | null>;
    /** 标识id */
    messageId: StringConstructor;
}>> & Readonly<{
    onClose?: (() => any) | undefined;
    onMessageDestroy?: ((_messageId?: string | undefined) => any) | undefined;
}>, {
    showClose: boolean;
    dangerouslyUseHTMLString: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
