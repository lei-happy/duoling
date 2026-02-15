import { PropType, ExtractPropTypes } from 'vue';
import { TabSize, TabType } from '../ele-tabs/types';

/**
 * 属性
 */
export declare const tabWrapProps: {
    /** 尺寸 */
    size: PropType<TabSize>;
    /** 风格类型 */
    type: PropType<TabType>;
};
export type TabWrapProps = ExtractPropTypes<typeof tabWrapProps>;
