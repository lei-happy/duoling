import { PropType } from 'vue';
import { ModalItem, ModalItemId } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    item: {
        type: PropType<ModalItem>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    removeItem: (_modalId?: ModalItemId | undefined) => void;
    updateItemVisible: (_modalId?: ModalItemId | undefined, _visible?: boolean | undefined) => void;
    updateItemProps: (_modalId?: ModalItemId | undefined, _opt?: Record<string, any> | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    item: {
        type: PropType<ModalItem>;
        required: true;
    };
}>> & Readonly<{
    onRemoveItem?: ((_modalId?: ModalItemId | undefined) => any) | undefined;
    onUpdateItemVisible?: ((_modalId?: ModalItemId | undefined, _visible?: boolean | undefined) => any) | undefined;
    onUpdateItemProps?: ((_modalId?: ModalItemId | undefined, _opt?: Record<string, any> | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
