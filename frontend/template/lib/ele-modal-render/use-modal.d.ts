import { ModalItem, ModalItemId } from './types';

export declare function useModal(): {
    ModalHolder: import('vue').DefineComponent<{}, () => any[], {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{}> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
    modalProps: import('vue').Ref<import('../ele-app/plus').EleDrawerPropsAndEmits | import('../ele-app/plus').EleModalPropsAndEmits, import('../ele-app/plus').EleDrawerPropsAndEmits | import('../ele-app/plus').EleModalPropsAndEmits> | undefined;
    openModal: (option: ModalItem) => ModalItemId;
    closeAllModal: (current?: boolean) => void;
    closeModal: (modalId?: ModalItemId) => void;
    setModalProps: (modalId?: ModalItemId | Record<string, any>, options?: Record<string, any>) => void;
};
