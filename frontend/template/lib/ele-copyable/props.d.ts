import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElIconProps } from '../ele-app/el';
import { EleTooltipProps } from '../ele-app/plus';
import { CopyableIcon, CopyableLocale } from './types';

/**
 * 属性
 */
export declare const copyableProps: {
    /** 重新定义拷贝到剪切板里的文本 */
    text: StringConstructor;
    /** 自定义内容样式 */
    innerStyle: PropType<StyleValue>;
    /** 自定义拷贝按钮样式 */
    customStyle: PropType<StyleValue>;
    /** 自定义拷贝图标 */
    icon: PropType<CopyableIcon>;
    /** 自定义拷贝图标属性 */
    iconProps: PropType<ElIconProps>;
    /** 自定义拷贝图标样式 */
    iconStyle: PropType<StyleValue>;
    /** 自定义拷贝后图标 */
    copiedIcon: PropType<CopyableIcon>;
    /** 自定义拷贝后图标属性 */
    copiedIconProps: PropType<ElIconProps>;
    /** 自定义拷贝后图标样式 */
    copiedIconStyle: PropType<StyleValue>;
    /** 文字提示属性 */
    tooltip: {
        type: PropType<boolean | EleTooltipProps>;
        default: boolean;
    };
    /** 拷贝成功状态重置时间 */
    resetAfter: {
        type: NumberConstructor;
        default: number;
    };
    /** 国际化 */
    locale: PropType<Partial<CopyableLocale>>;
};
export type CopyableProps = ExtractPropTypes<typeof copyableProps>;
/**
 * 事件
 */
export declare const copyableEmits: {
    copy: (_error?: any) => boolean;
};
