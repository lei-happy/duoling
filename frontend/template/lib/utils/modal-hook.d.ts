import { MessageOptions } from './message';
import { MessageBoxOptions } from './message-box';

export interface UseModalOptions {
    message: MessageOptions;
    messageBox?: MessageBoxOptions;
}
/**
 * 弹窗, 抽屉, 消息, 弹出框, 消息通知等组件操作
 */
export declare function useModal(options?: UseModalOptions): {
    message: import('./message').Message;
    messageBox: import('./message-box').MessageBox;
    notification: (import('element-plus').Notify & import('vue').Plugin) & {
        _context: import('vue').AppContext | null;
    };
    ModalHolder: import('vue').DefineComponent<{}, () => any[], {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{}> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
    modalProps: import('vue').Ref<import('../ele-app/plus').EleDrawerPropsAndEmits | import('../ele-app/plus').EleModalPropsAndEmits, import('../ele-app/plus').EleDrawerPropsAndEmits | import('../ele-app/plus').EleModalPropsAndEmits> | undefined;
    openModal: (option: import('../ele-modal-render/types').ModalItem) => import('../ele-modal-render/types').ModalItemId;
    closeAllModal: (current?: boolean) => void;
    closeModal: (modalId?: import('../ele-modal-render/types').ModalItemId) => void;
    setModalProps: (modalId?: import('../ele-modal-render/types').ModalItemId | Record<string, any>, options?: Record<string, any>) => void;
};
