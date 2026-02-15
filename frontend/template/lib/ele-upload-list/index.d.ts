import { UploadItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    icon?(_: {}): any;
    extra?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<UploadItem[]>;
    readonly: BooleanConstructor;
    disabled: BooleanConstructor;
    preview: {
        type: BooleanConstructor;
        default: boolean;
    };
    limit: NumberConstructor;
    multiple: BooleanConstructor;
    drag: BooleanConstructor;
    accept: {
        type: StringConstructor;
        default: string;
    };
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue | false>;
    buttonStyle: {
        type: import('vue').PropType<import('../ele-app/types').StyleValue | false>;
        default: null;
    };
    sortable: {
        type: import('vue').PropType<boolean | Record<keyof any, any>>;
        default: boolean;
    };
    imageProps: import('vue').PropType<import('../ele-app/el').ElImageProps>;
    progressProps: import('vue').PropType<import('../ele-app/el').ElProgressProps>;
    previewProps: import('vue').PropType<import('../ele-app/plus').EleImageViewerProps>;
    tools: BooleanConstructor;
    listType: import('vue').PropType<import('./types').ListType>;
    beforeUploadClick: import('vue').PropType<import('./types').BeforeUploadClick>;
    beforeItemEdit: import('vue').PropType<import('./types').BeforeItemEdit>;
    beforePreview: import('vue').PropType<import('./types').BeforePreview>;
    locale: import('vue').PropType<Partial<import('./types').UploadLocale>>;
}>, {
    openImagePreview: (urls: string[], index: number) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value: UploadItem[]) => void;
    remove: (_item: UploadItem) => void;
    itemClick: (_item: UploadItem) => void;
    upload: (_item: UploadItem) => void;
    preview: (_item: UploadItem) => void;
    retry: (_item: UploadItem) => void;
    editUpload: (_result: import('./types').EditUploadResult) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<UploadItem[]>;
    readonly: BooleanConstructor;
    disabled: BooleanConstructor;
    preview: {
        type: BooleanConstructor;
        default: boolean;
    };
    limit: NumberConstructor;
    multiple: BooleanConstructor;
    drag: BooleanConstructor;
    accept: {
        type: StringConstructor;
        default: string;
    };
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue | false>;
    buttonStyle: {
        type: import('vue').PropType<import('../ele-app/types').StyleValue | false>;
        default: null;
    };
    sortable: {
        type: import('vue').PropType<boolean | Record<keyof any, any>>;
        default: boolean;
    };
    imageProps: import('vue').PropType<import('../ele-app/el').ElImageProps>;
    progressProps: import('vue').PropType<import('../ele-app/el').ElProgressProps>;
    previewProps: import('vue').PropType<import('../ele-app/plus').EleImageViewerProps>;
    tools: BooleanConstructor;
    listType: import('vue').PropType<import('./types').ListType>;
    beforeUploadClick: import('vue').PropType<import('./types').BeforeUploadClick>;
    beforeItemEdit: import('vue').PropType<import('./types').BeforeItemEdit>;
    beforePreview: import('vue').PropType<import('./types').BeforePreview>;
    locale: import('vue').PropType<Partial<import('./types').UploadLocale>>;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value: UploadItem[]) => any) | undefined;
    onRemove?: ((_item: UploadItem) => any) | undefined;
    onItemClick?: ((_item: UploadItem) => any) | undefined;
    onUpload?: ((_item: UploadItem) => any) | undefined;
    onPreview?: ((_item: UploadItem) => any) | undefined;
    onRetry?: ((_item: UploadItem) => any) | undefined;
    onEditUpload?: ((_result: import('./types').EditUploadResult) => any) | undefined;
}>, {
    disabled: boolean;
    readonly: boolean;
    multiple: boolean;
    sortable: boolean | Record<string | number | symbol, any>;
    drag: boolean;
    preview: boolean;
    tools: boolean;
    accept: string;
    buttonStyle: false | Partial<import('vue').CSSProperties>;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
