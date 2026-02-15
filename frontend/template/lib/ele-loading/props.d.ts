import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { LoadingType, LoadingSize } from './types';

/**
 * 属性
 */
export declare const loadingProps: {
    /** 是否显示动画 */
    loading: BooleanConstructor;
    /** 显示在加载图标下方的加载文案 */
    text: StringConstructor;
    /** 背景模糊效果 */
    blur: BooleanConstructor;
    /** 加载器尺寸 */
    size: PropType<LoadingSize>;
    /** 自定义加载器样式 */
    spinnerStyle: PropType<StyleValue>;
    /** 自定义文本样式 */
    textStyle: PropType<StyleValue>;
    /** 是否是纯加载器模式 */
    plain: BooleanConstructor;
    /** 加载器类型 */
    type: {
        type: PropType<LoadingType>;
        default: string;
    };
    /** 背景遮罩的颜色 */
    background: StringConstructor;
    /** 自定义加载图标 */
    spinner: StringConstructor;
    /** 自定义加载图标svg的view-box */
    svgViewBox: StringConstructor;
};
export type LoadingProps = ExtractPropTypes<typeof loadingProps>;
