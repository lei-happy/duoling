import { ExtractPropTypes, PropType } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElRowProps } from '../ele-app/el';
import { CheckedValue, CheckCardItem, CheckCardItemsFunction } from './types';

/**
 * 属性
 */
export declare const checkCardProps: {
    /** 选中值 */
    modelValue: {
        type: PropType<CheckedValue>;
        default: () => null;
    };
    /** 数据 */
    items: PropType<CheckCardItem[] | CheckCardItemsFunction>;
    /** 是否多选 */
    multiple: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否显示边框 */
    bordered: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否需要选中箭头 */
    arrow: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 选中箭头样式 */
    arrowStyle: PropType<StyleValue>;
    /** 自定义卡片类名 */
    itemClass: StringConstructor;
    /** 自定义卡片样式 */
    itemStyle: PropType<StyleValue>;
    /** 是否使用栅格布局 */
    row: PropType<boolean | ElRowProps>;
    /** 单选时允许取消选中 */
    allowUncheck: BooleanConstructor;
};
export type CheckCardProps = ExtractPropTypes<typeof checkCardProps>;
/**
 * 事件
 */
export declare const checkCardEmits: {
    /** 更新选中值 */
    'update:modelValue': (_value: CheckedValue) => boolean;
    /** 选中改变事件 */
    change: (_value: CheckedValue) => boolean;
};
