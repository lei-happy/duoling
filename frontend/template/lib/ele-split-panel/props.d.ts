import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';

/**
 * 属性
 */
export declare const splitPanelProps: {
    /** 边栏默认尺寸 */
    size: (StringConstructor | NumberConstructor)[];
    /** 最小拉伸尺寸 */
    minSize: NumberConstructor;
    /** 最大拉伸尺寸 */
    maxSize: NumberConstructor;
    /** 间距 */
    space: (StringConstructor | NumberConstructor)[];
    /** 自定义边栏样式 */
    customStyle: PropType<StyleValue>;
    /** 自定义边栏容器样式 */
    customWrapStyle: PropType<StyleValue>;
    /** 自定义内容样式 */
    bodyStyle: PropType<StyleValue>;
    /** 是否可折叠边栏 */
    allowCollapse: PropType<boolean | "both">;
    /** 折叠按钮样式 */
    collapseStyle: PropType<StyleValue>;
    /** 折叠按钮折叠时到边缘的距离 */
    collapseBtnOffset: (StringConstructor | NumberConstructor)[];
    /** 是否折叠状态 */
    collapse: PropType<boolean | "body">;
    /** 是否垂直方向 */
    vertical: BooleanConstructor;
    /** 是否反向布局 */
    reverse: BooleanConstructor;
    /** 是否可拉伸宽度 */
    resizable: BooleanConstructor;
    /** 拉伸宽度是否使用百分比 */
    percentage: BooleanConstructor;
    /** 自定义边栏顶部样式 */
    sideHeaderStyle: PropType<StyleValue>;
    /** 自定义内容顶栏样式 */
    bodyHeaderStyle: PropType<StyleValue>;
    /** 内部表格弹性布局 */
    flexTable: PropType<boolean | "auto">;
    /** 是否开启响应式 */
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
};
export type SplitPanelProps = ExtractPropTypes<typeof splitPanelProps>;
/**
 * 事件
 */
export declare const splitPanelEmits: {
    /** 更新边栏折叠状态 */
    'update:collapse': (_collapse: boolean | "body") => boolean;
    resizeStart: (_size: number) => boolean;
    resize: (_size: number | undefined, _strSize: string | null) => boolean;
    resizeEnd: (_size: number | undefined, _strSize: string | null) => boolean;
};
