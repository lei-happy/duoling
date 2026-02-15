import { PropType, ExtractPropTypes } from 'vue';
import { DashboardType } from './types';

/**
 * 属性
 */
export declare const dashboardProps: {
    /** 类型 */
    type: PropType<DashboardType>;
    /** 自定义颜色 */
    color: StringConstructor;
    /** 尺寸 */
    size: (StringConstructor | NumberConstructor)[];
    /** 间距 */
    space: (StringConstructor | NumberConstructor)[];
};
export type DashboardProps = ExtractPropTypes<typeof dashboardProps>;
