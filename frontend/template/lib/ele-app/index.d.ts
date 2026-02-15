declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<{}, {
    openModal: (option: import('../ele-modal-render/types').ModalItem) => import('../ele-modal-render/types').ModalItemId;
    closeModal: (modalId?: import('../ele-modal-render/types').ModalItemId) => void;
    closeAllModal: () => void;
    updateModalProps: (modalId?: import('../ele-modal-render/types').ModalItemId, option?: Record<string, any>) => void;
    openDropdown: (triggerEl: any, items?: import('../ele-dropdown/types').DropdownItem[], props?: import('./plus').EleDropdownPropsAndEmits) => void;
    openPopconfirm: (triggerEl: any, props?: import('./plus').ElePopconfirmPropsAndEmits) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{}> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
