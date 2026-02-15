import { PropType, ExtractPropTypes } from 'vue';
import { EleTooltipProps } from '../ele-app/plus';
import { CropperOptions, CroppedOptions, BeforeUploadClick, CropperLocale } from './types';

/**
 * 属性
 */
export declare const cropperProps: {
    /** 图片高度 */
    height: StringConstructor;
    /** 图片地址 */
    src: StringConstructor;
    /** 图片地址对应的图片类型,如'image/jpeg' */
    imageType: {
        type: StringConstructor;
        default: string;
    };
    /** 允许上传的图片类型 */
    accept: {
        type: StringConstructor;
        default: string;
    };
    /** 操作按钮布局 */
    tools: {
        type: StringConstructor;
        default: string;
    };
    /** 是否需要预览组件 */
    preview: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 预览组件宽度 */
    previewWidth: {
        type: NumberConstructor;
        default: number;
    };
    /** 是否返回blob数据 */
    toBlob: BooleanConstructor;
    /** cropperjs的参数 */
    options: PropType<CropperOptions>;
    /** cropperjs裁剪方法的参数 */
    croppedOptions: PropType<CroppedOptions>;
    /** 是否需要tooltip */
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** tooltip属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 上传按钮点击前的钩子 */
    beforeUploadClick: PropType<BeforeUploadClick>;
    /** 是否开启响应式 */
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    /** 国际化 */
    locale: PropType<Partial<CropperLocale>>;
};
export type CropperProps = ExtractPropTypes<typeof cropperProps>;
/**
 * 事件
 */
export declare const cropperEmits: {
    /** 裁剪完成事件 */
    done: (_result?: Blob | string | null) => boolean;
};
