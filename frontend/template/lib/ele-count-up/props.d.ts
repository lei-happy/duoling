import { PropType, ExtractPropTypes } from 'vue';
import { CountUpOptions, CountUp } from 'countup.js';

/**
 * 属性
 */
export declare const countUpProps: {
    /** 首次动画延迟时间 */
    delay: {
        type: NumberConstructor;
        default: number;
    };
    /** 结束值 */
    endVal: {
        type: NumberConstructor;
        required: boolean;
    };
    /** 参数配置 */
    options: PropType<CountUpOptions>;
};
export type CountUpProps = ExtractPropTypes<typeof countUpProps>;
/**
 * 事件
 */
export declare const countUpEmits: {
    /** 渲染完成事件 */
    ready: (_instance?: CountUp | null) => boolean;
};
