import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { TabBarItem, TabBarType } from './types';

/**
 * 属性
 */
export declare const tabBarProps: {
    /** 标签选中 */
    modelValue: (StringConstructor | NumberConstructor | BooleanConstructor | ObjectConstructor)[];
    /** 标签数据 */
    items: PropType<TabBarItem[]>;
    /** 标签项样式 */
    itemStyle: PropType<StyleValue>;
    /** 风格类型 */
    type: PropType<TabBarType>;
};
export type TabBarProps = ExtractPropTypes<typeof tabBarProps>;
/**
 * 事件
 */
export declare const tabBarEmits: {
    /** 更新标签选中 */
    'update:modelValue': (_value?: any) => boolean;
    /** 选中改变事件 */
    change: (_active?: any) => boolean;
};
