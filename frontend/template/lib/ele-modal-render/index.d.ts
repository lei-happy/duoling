import { PropType } from 'vue';
import { ModalItem, ModalItemId } from './types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modals: PropType<ModalItem[]>;
}>, () => any[], {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    removeItem: (_modalId?: ModalItemId) => true;
    updateItemVisible: (_modalId?: ModalItemId, _visible?: boolean) => true;
    updateItemProps: (_modalId?: ModalItemId, _opt?: Record<string, any>) => true;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modals: PropType<ModalItem[]>;
}>> & Readonly<{
    onRemoveItem?: ((_modalId?: ModalItemId | undefined) => any) | undefined;
    onUpdateItemVisible?: ((_modalId?: ModalItemId | undefined, _visible?: boolean | undefined) => any) | undefined;
    onUpdateItemProps?: ((_modalId?: ModalItemId | undefined, _opt?: Record<string, any> | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
