import { EleTooltipProps } from '../ele-app/plus';

declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    title: StringConstructor;
    placement: {
        type: import('vue').PropType<EleTooltipProps["placement"]>;
        default: string;
    };
    disabled: BooleanConstructor;
    clickHideTooltip: BooleanConstructor;
}>, {
    showTooltip: (text?: string, el?: HTMLElement, options?: EleTooltipProps) => void;
    hideTooltip: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    click: (_e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    title: StringConstructor;
    placement: {
        type: import('vue').PropType<EleTooltipProps["placement"]>;
        default: string;
    };
    disabled: BooleanConstructor;
    clickHideTooltip: BooleanConstructor;
}>> & Readonly<{
    onClick?: ((_e: MouseEvent) => any) | undefined;
}>, {
    placement: import('element-plus').Placement | undefined;
    disabled: boolean;
    clickHideTooltip: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
