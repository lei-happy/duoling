import { PropType } from 'vue';
import { CronPanelLocale } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** minute */
    modelValue: StringConstructor;
    /** 国际化 */
    lang: {
        type: PropType<CronPanelLocale>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_minute?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** minute */
    modelValue: StringConstructor;
    /** 国际化 */
    lang: {
        type: PropType<CronPanelLocale>;
        required: true;
    };
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_minute?: string | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
