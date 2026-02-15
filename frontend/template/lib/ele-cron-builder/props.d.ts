import { PropType, ExtractPropTypes } from 'vue';
import { EleModalProps } from '../ele-app/plus';
import { CronBuilderLocale } from './types';

/**
 * 属性
 */
export declare const cronBuilderProps: {
    /** 弹窗是否显示 */
    modelValue: BooleanConstructor;
    /** 绑定值 */
    cron: StringConstructor;
    /** 标题 */
    title: StringConstructor;
    /** 弹窗属性 */
    modalProps: PropType<EleModalProps>;
    /** 国际化 */
    locale: PropType<Partial<CronBuilderLocale>>;
};
export type CronBuilderProps = ExtractPropTypes<typeof cronBuilderProps>;
/**
 * 事件
 */
export declare const cronBuilderEmits: {
    /** 更新弹窗显示状态 */
    'update:modelValue': (_value?: boolean) => boolean;
    /** 更新绑定值 */
    'update:cron': (_cron?: string) => boolean;
    /** 确定按钮点击事件 */
    done: (_cron?: string) => boolean;
};
