import { PropType, ExtractPropTypes } from 'vue';
import { EllipsisTooltip } from './types';

/**
 * 属性
 */
export declare const ellipsisProps: {
    /** 最大行数 */
    maxLine: NumberConstructor;
    /** 行高 */
    lineHeight: (NumberConstructor | StringConstructor)[];
    /** 文字提示属性 */
    tooltip: {
        type: PropType<boolean | EllipsisTooltip>;
        default: () => {
            original: boolean;
        };
    };
    tag: StringConstructor;
    type: PropType<import('../ele-text/types').TextType>;
    size: PropType<import('../ele-text/types').TextSize>;
    deleted: BooleanConstructor;
    underline: BooleanConstructor;
    strong: BooleanConstructor;
    italic: BooleanConstructor;
    icon: PropType<import('../ele-text/types').TextIcon>;
    iconProps: PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: PropType<import('../ele-app/types').StyleValue>;
};
export type EllipsisProps = ExtractPropTypes<typeof ellipsisProps>;
