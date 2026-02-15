import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { Level, ImageSettings, QrCodeTag } from './types';

/**
 * 属性
 */
export declare const qrCodeProps: {
    /** 绑定值 */
    value: StringConstructor;
    /** 尺寸 */
    size: {
        type: NumberConstructor;
        default: number;
    };
    /** 容错等级 */
    level: {
        type: PropType<Level>;
        default: string;
    };
    /** 背景色 */
    bgColor: {
        type: StringConstructor;
        default: string;
    };
    /** 颜色 */
    fgColor: {
        type: StringConstructor;
        default: string;
    };
    /** 外间距 */
    margin: {
        type: NumberConstructor;
        default: number;
    };
    /** 自定义图片 */
    imageSettings: PropType<ImageSettings>;
    /** 自定义样式 */
    customStyle: PropType<StyleValue>;
    /** 渲染标签 */
    tag: PropType<QrCodeTag>;
};
export type QrCodeProps = ExtractPropTypes<typeof qrCodeProps>;
/**
 * 事件
 */
export declare const qrCodeEmits: {
    /** 渲染完成事件 */
    done: () => boolean;
};
