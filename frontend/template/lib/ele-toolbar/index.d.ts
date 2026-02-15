import { Ref } from 'vue';
import { EleTooltipInstance, EleTooltipProps } from '../ele-app/plus';

declare function __VLS_template(): {
    default?(_: {}): any;
    tools?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    title: StringConstructor;
    subtitle: StringConstructor;
    theme: {
        type: import('vue').PropType<import('./types').ToolbarTheme>;
        default: string;
    };
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    toolsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleProps: import('vue').PropType<import('../ele-app/plus').EleTextProps>;
    subtitleProps: import('vue').PropType<import('../ele-app/plus').EleTextProps>;
}>, {
    tooltipRef: Ref<EleTooltipInstance, EleTooltipInstance>;
    showTooltip: (text?: string, el?: HTMLElement, options?: EleTooltipProps) => void;
    hideTooltip: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    title: StringConstructor;
    subtitle: StringConstructor;
    theme: {
        type: import('vue').PropType<import('./types').ToolbarTheme>;
        default: string;
    };
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    toolsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleProps: import('vue').PropType<import('../ele-app/plus').EleTextProps>;
    subtitleProps: import('vue').PropType<import('../ele-app/plus').EleTextProps>;
}>> & Readonly<{}>, {
    theme: import('./types').ToolbarTheme;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
