import { CropperOptions } from './types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
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
    options: import('vue').PropType<CropperOptions>;
    croppedOptions: import('vue').PropType<import('./types').CroppedOptions>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    beforeUploadClick: import('vue').PropType<import('./types').BeforeUploadClick>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: import('vue').PropType<Partial<import('./types').CropperLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    done: (_result?: string | Blob | null | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
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
    options: import('vue').PropType<CropperOptions>;
    croppedOptions: import('vue').PropType<import('./types').CroppedOptions>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    beforeUploadClick: import('vue').PropType<import('./types').BeforeUploadClick>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: import('vue').PropType<Partial<import('./types').CropperLocale>>;
}>> & Readonly<{
    onDone?: ((_result?: string | Blob | null | undefined) => any) | undefined;
}>, {
    tooltip: boolean;
    responsive: boolean;
    tools: string;
    preview: boolean;
    accept: string;
    imageType: string;
    previewWidth: number;
    toBlob: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
