import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElAvatarProps } from '../ele-app/el';
import { EleTooltipProps } from '../ele-app/plus';
import { AvatarItem, AvatarErrorOption } from './types';

/**
 * 属性
 */
export declare const avatarGroupProps: {
    /** 数据 */
    data: {
        type: PropType<AvatarItem[]>;
        required: boolean;
    };
    /** 最大显示个数 */
    maxCount: NumberConstructor;
    /** 形状 */
    shape: PropType<ElAvatarProps["shape"]>;
    /** 大小 */
    size: PropType<ElAvatarProps["size"]>;
    /** 自定义样式 */
    itemStyle: PropType<StyleValue>;
    /** 自定义头像样式 */
    avatarStyle: PropType<StyleValue>;
    /** 自定义溢出样式 */
    moreStyle: PropType<StyleValue>;
    /** 是否显示提示 */
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 提示属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 是否显示溢出气泡 */
    overflowPopover: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 溢出气泡属性 */
    overflowPopoverProps: PropType<EleTooltipProps>;
    /** 是否鼠标移入展开 */
    hoverOpen: BooleanConstructor;
};
export type AvatarGroupProps = ExtractPropTypes<typeof avatarGroupProps>;
/**
 * 事件
 */
export declare const avatarGroupEmits: {
    /** item 点击事件 */
    itemClick: (_item: AvatarItem) => boolean;
    /** 更多点击事件 */
    moreClick: () => boolean;
    /** 图片加载失败事件 */
    error: (_option: AvatarErrorOption) => boolean;
};
