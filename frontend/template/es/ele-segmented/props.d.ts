import { PropType, ExtractPropTypes } from 'vue';
import { SegmentedSize, SegmentedItem } from './types';

/**
 * 属性
 */
export declare const segmentedProps: {
    /** 选中的值 */
    modelValue: (NumberConstructor | StringConstructor)[];
    /** 将宽度调整为父元素宽度 */
    block: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 数据 */
    items: {
        type: PropType<SegmentedItem[]>;
        required: boolean;
    };
    /** 尺寸 */
    size: PropType<SegmentedSize>;
    /** 是否触发表单验证 */
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
};
export type SegmentedProps = ExtractPropTypes<typeof segmentedProps>;
/**
 * 事件
 */
export declare const segmentedEmits: {
    /** 更新绑定值 */
    'update:modelValue': (_value: string | number) => boolean;
    /** 选中改变的事件 */
    change: (_active: string | number) => boolean;
};
