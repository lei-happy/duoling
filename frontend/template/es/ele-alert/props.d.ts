import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElAlertProps, ElIconProps } from '../ele-app/el';

/**
 * 属性
 */
export declare const alertProps: {
    /** 标题 */
    title: StringConstructor;
    /** 类型 */
    type: PropType<ElAlertProps["type"]>;
    /** 描述 */
    description: {
        type: (BooleanConstructor | StringConstructor)[];
        default: string;
    };
    /** 是否可关闭 */
    closable: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否居中 */
    center: BooleanConstructor;
    /** 自定义关闭按钮文字 */
    closeText: StringConstructor;
    /** 是否显示图标 */
    showIcon: BooleanConstructor;
    /** 主题 */
    effect: PropType<ElAlertProps["effect"]>;
    /** 图标样式 */
    iconStyle: PropType<StyleValue>;
    /** 图标组件属性 */
    iconProps: PropType<ElIconProps>;
    /** 关闭图标样式 */
    closeIconStyle: PropType<StyleValue>;
    /** 关闭图标组件属性 */
    closeIconProps: PropType<ElIconProps>;
    /** 内容区样式 */
    bodyStyle: PropType<StyleValue>;
    /** 标题样式 */
    titleStyle: PropType<StyleValue>;
    /** 描述样式 */
    descriptionStyle: PropType<StyleValue>;
    /** 过渡动画名称 */
    transitionName: {
        type: StringConstructor;
        default: string;
    };
};
export type AlertProps = ExtractPropTypes<typeof alertProps>;
/**
 * 事件
 */
export declare const alertEmits: {
    /** 关闭的事件 */
    close: (_e: MouseEvent) => boolean;
};
