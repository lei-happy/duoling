import { PropType, ExtractPropTypes } from 'vue';
import { TourStep, TourLocale } from './types';

/**
 * 属性
 */
export declare const tourProps: {
    /** 当前处于第几步 */
    modelValue: NumberConstructor;
    /** 步骤 */
    steps: {
        type: PropType<TourStep[]>;
        required: boolean;
    };
    /** 是否开启遮罩层 */
    mask: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 高亮区内间距 */
    padding: {
        type: NumberConstructor;
        default: number;
    };
    /** 层级 */
    zIndex: NumberConstructor;
    /** 国际化 */
    locale: PropType<Partial<TourLocale>>;
};
export type TourProps = ExtractPropTypes<typeof tourProps>;
/**
 * 事件
 */
export declare const tourEmits: {
    'update:modelValue': (_value?: number | null) => boolean;
};
