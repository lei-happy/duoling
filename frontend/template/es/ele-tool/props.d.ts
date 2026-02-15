import { PropType, ExtractPropTypes } from 'vue';
import { EleTooltipProps } from '../ele-app/plus';

/**
 * 属性
 */
export declare const toolProps: {
    /** 提示文字 */
    title: StringConstructor;
    /** 提示方向 */
    placement: {
        type: PropType<EleTooltipProps["placement"]>;
        default: string;
    };
    /** 是否禁用提示 */
    disabled: BooleanConstructor;
    /** 是否点击时关闭提示 */
    clickHideTooltip: BooleanConstructor;
};
export type ToolProps = ExtractPropTypes<typeof toolProps>;
/**
 * 事件
 */
export declare const toolEmits: {
    /** 点击事件 */
    click: (_e: MouseEvent) => boolean;
};
