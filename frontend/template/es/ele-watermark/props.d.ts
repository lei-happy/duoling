import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { WatermarkGap, WatermarkOffset, WatermarkFont } from './types';

export declare const watermarkProps: {
    /** 宽度 */
    width: NumberConstructor;
    /** 高度 */
    height: NumberConstructor;
    /** 旋转角度 */
    rotate: NumberConstructor;
    /** 层级 */
    zIndex: NumberConstructor;
    /** 图片源 */
    image: StringConstructor;
    /** 文字内容 */
    content: PropType<string | string[]>;
    /** 文字样式 */
    font: PropType<WatermarkFont>;
    /** 间距 */
    gap: PropType<WatermarkGap>;
    /** 距离左上角的偏移量 */
    offset: PropType<WatermarkOffset>;
    /** 多行文字的行间距 */
    lineGap: NumberConstructor;
    /** 自定义样式 */
    customStyle: PropType<Exclude<StyleValue, string>>;
    /** 是否使用 svg 渲染 */
    svgRender: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否使用固定定位 */
    fixed: BooleanConstructor;
    /** 是否为容器添加定位样式 */
    wrapPosition: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 容器高度 */
    wrapHeight: (NumberConstructor | StringConstructor)[];
};
export type WatermarkProps = ExtractPropTypes<typeof watermarkProps>;
