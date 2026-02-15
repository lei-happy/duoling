import { PropType, ExtractPropTypes } from 'vue';
import { TimelineItem } from './types';

/**
 * 属性
 */
export declare const timelineProps: {
    /** 数据 */
    data: PropType<TimelineItem[]>;
    /** 每项最小宽度 */
    itemWidth: {
        type: NumberConstructor;
        default: number;
    };
};
export type TimelineProps = ExtractPropTypes<typeof timelineProps>;
/**
 * 事件
 */
export declare const timelineEmits: {
    itemClick: (_item: TimelineItem, _e?: MouseEvent) => boolean;
};
