import { PropType } from 'vue';
import { StyleValue } from '../../ele-app/types';
import { WatermarkFont } from '../../ele-watermark/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 宽度 */
    width: {
        type: NumberConstructor;
        default: number;
    };
    /** 高度 */
    height: {
        type: NumberConstructor;
        default: number;
    };
    /** 旋转角度 */
    rotate: {
        type: NumberConstructor;
        default: number;
    };
    /** 水平间距 */
    gapX: {
        type: NumberConstructor;
        default: number;
    };
    /** 垂直间距 */
    gapY: {
        type: NumberConstructor;
        default: number;
    };
    /** 多行文字的行间距 */
    lineGap: {
        type: NumberConstructor;
        default: number;
    };
    /** 文字样式 */
    font: {
        type: PropType<Required<WatermarkFont>>;
        required: true;
    };
    /** 文字内容 */
    contents: {
        type: PropType<string[]>;
        required: true;
    };
    /** 图片源 */
    image: StringConstructor;
    /** 水平偏移量 */
    offsetX: {
        type: NumberConstructor;
        default: number;
    };
    /** 垂直偏移量 */
    offsetY: {
        type: NumberConstructor;
        default: number;
    };
    /** 公共样式 */
    commonStyle: PropType<StyleValue>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 宽度 */
    width: {
        type: NumberConstructor;
        default: number;
    };
    /** 高度 */
    height: {
        type: NumberConstructor;
        default: number;
    };
    /** 旋转角度 */
    rotate: {
        type: NumberConstructor;
        default: number;
    };
    /** 水平间距 */
    gapX: {
        type: NumberConstructor;
        default: number;
    };
    /** 垂直间距 */
    gapY: {
        type: NumberConstructor;
        default: number;
    };
    /** 多行文字的行间距 */
    lineGap: {
        type: NumberConstructor;
        default: number;
    };
    /** 文字样式 */
    font: {
        type: PropType<Required<WatermarkFont>>;
        required: true;
    };
    /** 文字内容 */
    contents: {
        type: PropType<string[]>;
        required: true;
    };
    /** 图片源 */
    image: StringConstructor;
    /** 水平偏移量 */
    offsetX: {
        type: NumberConstructor;
        default: number;
    };
    /** 垂直偏移量 */
    offsetY: {
        type: NumberConstructor;
        default: number;
    };
    /** 公共样式 */
    commonStyle: PropType<StyleValue>;
}>> & Readonly<{}>, {
    height: number;
    rotate: number;
    width: number;
    gapX: number;
    gapY: number;
    lineGap: number;
    offsetX: number;
    offsetY: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
