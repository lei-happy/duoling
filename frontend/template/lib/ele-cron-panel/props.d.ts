import { PropType, ExtractPropTypes } from 'vue';
import { CronPanelLocale } from './types';

/**
 * 属性
 */
export declare const cronPanelProps: {
    /** 绑定值 */
    modelValue: StringConstructor;
    /** 国际化 */
    locale: PropType<Partial<CronPanelLocale>>;
};
export type CronPanelProps = ExtractPropTypes<typeof cronPanelProps>;
/**
 * 事件
 */
export declare const cronPanelEmits: {
    /** 更新绑定值 */
    'update:modelValue': (_value?: string) => boolean;
};
