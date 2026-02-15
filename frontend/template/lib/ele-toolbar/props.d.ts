import { PropType, ExtractPropTypes, InjectionKey } from 'vue';
import { StyleValue } from '../ele-app/types';
import { EleTextProps } from '../ele-app/plus';
import { ToolbarTheme, ToolbarProvide } from './types';

/**
 * 属性
 */
export declare const toolbarProps: {
    /** 标题 */
    title: StringConstructor;
    /** 二级标题 */
    subtitle: StringConstructor;
    /** 主题风格 */
    theme: {
        type: PropType<ToolbarTheme>;
        default: string;
    };
    /** 标题区样式 */
    titleStyle: PropType<StyleValue>;
    /** 内容区样式 */
    bodyStyle: PropType<StyleValue>;
    /** 按钮区样式 */
    toolsStyle: PropType<StyleValue>;
    /** 标题组件属性 */
    titleProps: PropType<EleTextProps>;
    /** 二级标题组件属性 */
    subtitleProps: PropType<EleTextProps>;
};
export type ToolbarProps = ExtractPropTypes<typeof toolbarProps>;
/**
 * 共享数据key
 */
export declare const TOOLBAR_KEY: InjectionKey<ToolbarProvide>;
