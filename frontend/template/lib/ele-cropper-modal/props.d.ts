import { PropType, ExtractPropTypes } from 'vue';
import { EleModalProps } from '../ele-app/plus';

/**
 * 属性
 */
export declare const cropperModalProps: {
    /** 弹窗是否显示 */
    modelValue: BooleanConstructor;
    /** 弹窗参数 */
    modalProps: PropType<Partial<Omit<EleModalProps, "modelValue">>>;
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
    options: PropType<import('../ele-cropper/types').CropperOptions>;
    croppedOptions: PropType<import('../ele-cropper/types').CroppedOptions>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: PropType<import('../ele-app/plus').EleTooltipProps>;
    beforeUploadClick: PropType<import('../ele-cropper/types').BeforeUploadClick>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: PropType<Partial<import('../ele-cropper/types').CropperLocale>>;
};
export type CropperModalProps = ExtractPropTypes<typeof cropperModalProps>;
/**
 * 事件
 */
export declare const cropperModalEmits: {
    /** 裁剪完成事件 */
    done: (_result: Blob | string | null) => boolean;
    /** 更新弹窗显示状态 */
    'update:modelValue': (_value: boolean) => boolean;
};
