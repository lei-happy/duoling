import { PropType, ExtractPropTypes } from 'vue';

/**
 * 属性
 */
export declare const backtopProps: {
    /** 触发滚动的对象 */
    target: PropType<string | HTMLElement | null>;
    /** 滚动高度达到此参数值才出现 */
    visibilityHeight: {
        type: NumberConstructor;
        default: number;
    };
    /** 距离页面底部距离 */
    bottom: {
        type: (StringConstructor | NumberConstructor)[];
        default: number;
    };
    /** 距离页面右边距 */
    right: {
        type: (StringConstructor | NumberConstructor)[];
        default: number;
    };
    /** 过渡动画名称 */
    transitionName: {
        type: StringConstructor;
        default: string;
    };
};
export type BacktopProps = ExtractPropTypes<typeof backtopProps>;
/**
 * 事件
 */
export declare const backtopEmits: {
    click: (_e: MouseEvent) => boolean;
};
