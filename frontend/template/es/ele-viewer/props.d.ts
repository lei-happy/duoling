import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { MarkerItem } from './types';

/**
 * 属性
 */
export declare const viewerProps: {
    /** 图片地址 */
    src: StringConstructor;
    /** 标记数据 */
    markers: PropType<MarkerItem[]>;
    /** 自定义内容样式 */
    contentStyle: PropType<StyleValue>;
    /** 自定义内容图片样式 */
    imageStyle: PropType<StyleValue>;
    /** 缩放速率 */
    zoomStep: {
        type: NumberConstructor;
        default: number;
    };
    /** 缩放最小百分比 */
    zoomMin: {
        type: NumberConstructor;
        default: number;
    };
    /** 缩放最大百分比 */
    zoomMax: {
        type: NumberConstructor;
        default: number;
    };
    /** 每次旋转角度 */
    rotateStep: {
        type: NumberConstructor;
        default: number;
    };
};
export type ViewerProps = ExtractPropTypes<typeof viewerProps>;
/**
 * 事件
 */
export declare const viewerEmits: {
    contentClick: (_e: MouseEvent) => boolean;
    contentContextmenu: (_e: MouseEvent) => boolean;
};
