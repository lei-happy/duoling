import { PropType, ExtractPropTypes } from 'vue';
import { DotType } from './types';

/**
 * 属性
 */
export declare const dotProps: {
    /** 类型 */
    type: PropType<DotType>;
    /** 自定义颜色 */
    color: StringConstructor;
    /** 是否显示水波动画 */
    ripple: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 文本 */
    text: StringConstructor;
    /** 尺寸 */
    size: {
        type: StringConstructor;
        default: string;
    };
};
export type DotProps = ExtractPropTypes<typeof dotProps>;
