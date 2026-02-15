declare function __VLS_template(): {
    header?(_: {
        close: () => void;
        titleId: string;
        titleClass: string;
    }): any;
    footer?(_: {}): any;
    maxIcon?(_: {
        fullscreen: boolean;
    }): any;
    closeIcon?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    modalProps: import('vue').PropType<Partial<Omit<import('../ele-app/plus').EleModalProps, "modelValue">>>;
    height: StringConstructor;
    src: StringConstructor;
    imageType: {
        type: StringConstructor;
        default: string;
    };
    accept: {
        type: StringConstructor;
        default: string;
    };
    tools: {
        type: StringConstructor;
        default: string;
    };
    preview: {
        type: BooleanConstructor;
        default: boolean;
    };
    previewWidth: {
        type: NumberConstructor;
        default: number;
    };
    toBlob: BooleanConstructor;
    options: import('vue').PropType<import('../ele-cropper/types').CropperOptions>;
    croppedOptions: import('vue').PropType<import('../ele-cropper/types').CroppedOptions>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    beforeUploadClick: import('vue').PropType<import('../ele-cropper/types').BeforeUploadClick>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: import('vue').PropType<Partial<import('../ele-cropper/types').CropperLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    done: (_result: string | Blob | null) => void;
    "update:modelValue": (_value: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    modalProps: import('vue').PropType<Partial<Omit<import('../ele-app/plus').EleModalProps, "modelValue">>>;
    height: StringConstructor;
    src: StringConstructor;
    imageType: {
        type: StringConstructor;
        default: string;
    };
    accept: {
        type: StringConstructor;
        default: string;
    };
    tools: {
        type: StringConstructor;
        default: string;
    };
    preview: {
        type: BooleanConstructor;
        default: boolean;
    };
    previewWidth: {
        type: NumberConstructor;
        default: number;
    };
    toBlob: BooleanConstructor;
    options: import('vue').PropType<import('../ele-cropper/types').CropperOptions>;
    croppedOptions: import('vue').PropType<import('../ele-cropper/types').CroppedOptions>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    beforeUploadClick: import('vue').PropType<import('../ele-cropper/types').BeforeUploadClick>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: import('vue').PropType<Partial<import('../ele-cropper/types').CropperLocale>>;
}>> & Readonly<{
    onDone?: ((_result: string | Blob | null) => any) | undefined;
    "onUpdate:modelValue"?: ((_value: boolean) => any) | undefined;
}>, {
    modelValue: boolean;
    tooltip: boolean;
    responsive: boolean;
    preview: boolean;
    tools: string;
    accept: string;
    imageType: string;
    previewWidth: number;
    toBlob: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
