import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElIconProps } from '../ele-app/el';
import { TextType, TextSize, TextIcon } from './types';

/**
 * 属性
 */
export declare const textProps: {
    /** 渲染标签 */
    tag: StringConstructor;
    /** 类型 */
    type: PropType<TextType>;
    /** 文字大小 */
    size: PropType<TextSize>;
    /** 文字删除线 */
    deleted: BooleanConstructor;
    /** 文字下划线 */
    underline: BooleanConstructor;
    /** 是否加粗 */
    strong: BooleanConstructor;
    /** 是否斜体 */
    italic: BooleanConstructor;
    /** 图标 */
    icon: PropType<TextIcon>;
    /** 图标属性 */
    iconProps: PropType<ElIconProps>;
    /** 图标样式 */
    iconStyle: PropType<StyleValue>;
};
export type TextProps = ExtractPropTypes<typeof textProps>;
export type TextPropKeys = Array<keyof typeof textProps>;
/**
 * 属性名
 */
export declare const textPropKeys: TextPropKeys;
