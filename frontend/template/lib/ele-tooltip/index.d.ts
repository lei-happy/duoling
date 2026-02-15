import { StyleValue } from '../ele-app/types';
import { ElTooltipInstance, ElPopperInstance, ElTooltipContentInstance } from '../ele-app/el';

declare function __VLS_template(): {
    default?(_: {}): any;
    body?(_: {}): any;
    content?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    bodyStyle: import('vue').PropType<StyleValue>;
    bg: StringConstructor;
    arrowBg: StringConstructor;
    width: (NumberConstructor | StringConstructor)[];
    isPopover: BooleanConstructor;
    content: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    zIndex: NumberConstructor;
    offset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 12;
    };
    transition: StringConstructor;
    showAfter: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    hideAfter: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 200;
    };
    autoClose: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    effect: {
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "dark";
    };
    placement: {
        readonly type: import('vue').PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "bottom";
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    appendTo: {
        readonly type: import('vue').PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    disabled: BooleanConstructor;
    persistent: BooleanConstructor;
    visible: {
        readonly type: import('vue').PropType<boolean | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: null;
    };
    trigger: {
        readonly type: import('vue').PropType<import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    triggerKeys: {
        readonly type: import('vue').PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => string[];
    };
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: import('vue').PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperOptions: {
        readonly type: import('vue').PropType<Partial<import('element-plus').Options>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    showArrow: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    enterable: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    arrowOffset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 5;
    };
    focusOnTarget: BooleanConstructor;
    rawContent: BooleanConstructor;
    gpuAcceleration: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    className: StringConstructor;
    popperClass: StringConstructor;
    popperStyle: import('vue').PropType<StyleValue>;
}>, {
    tooltipRef: import('vue').Ref<ElTooltipInstance | undefined, ElTooltipInstance | undefined>;
    popperRef: import('vue').ComputedRef<ElPopperInstance>;
    contentRef: import('vue').ComputedRef<ElTooltipContentInstance>;
    isFocusInsideContent: () => void;
    updatePopper: () => void;
    handleOpen: (opt?: Event) => void;
    handleClose: (opt?: Event) => void;
    onOpen: (opt?: Event) => void;
    onClose: (opt?: Event) => void;
    hide: (opt?: Event) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    close: (e: any) => void;
    hide: (e: Event) => void;
    open: (e: any) => void;
    "update:visible": (visible: boolean) => void;
    "before-show": (e: Event) => void;
    "before-hide": (e: Event) => void;
    show: (e: Event) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    bodyStyle: import('vue').PropType<StyleValue>;
    bg: StringConstructor;
    arrowBg: StringConstructor;
    width: (NumberConstructor | StringConstructor)[];
    isPopover: BooleanConstructor;
    content: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    zIndex: NumberConstructor;
    offset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 12;
    };
    transition: StringConstructor;
    showAfter: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    hideAfter: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 200;
    };
    autoClose: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    effect: {
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "dark";
    };
    placement: {
        readonly type: import('vue').PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "bottom";
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    appendTo: {
        readonly type: import('vue').PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    disabled: BooleanConstructor;
    persistent: BooleanConstructor;
    visible: {
        readonly type: import('vue').PropType<boolean | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: null;
    };
    trigger: {
        readonly type: import('vue').PropType<import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    triggerKeys: {
        readonly type: import('vue').PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => string[];
    };
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: import('vue').PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperOptions: {
        readonly type: import('vue').PropType<Partial<import('element-plus').Options>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    showArrow: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    enterable: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    arrowOffset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 5;
    };
    focusOnTarget: BooleanConstructor;
    rawContent: BooleanConstructor;
    gpuAcceleration: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    className: StringConstructor;
    popperClass: StringConstructor;
    popperStyle: import('vue').PropType<StyleValue>;
}>> & Readonly<{
    onClose?: ((e: any) => any) | undefined;
    onHide?: ((e: Event) => any) | undefined;
    onOpen?: ((e: any) => any) | undefined;
    "onUpdate:visible"?: ((visible: boolean) => any) | undefined;
    "onBefore-show"?: ((e: Event) => any) | undefined;
    "onBefore-hide"?: ((e: Event) => any) | undefined;
    onShow?: ((e: Event) => any) | undefined;
}>, {
    content: string;
    offset: number;
    showAfter: number;
    hideAfter: number;
    autoClose: number;
    effect: import('element-plus').PopperEffect;
    placement: import('element-plus').Placement;
    teleported: boolean;
    disabled: boolean;
    persistent: boolean;
    visible: boolean | null;
    trigger: import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[];
    triggerKeys: string[];
    virtualTriggering: boolean;
    popperOptions: Partial<import('element-plus').Options>;
    showArrow: boolean;
    enterable: boolean;
    arrowOffset: number;
    focusOnTarget: boolean;
    rawContent: boolean;
    gpuAcceleration: boolean;
    isPopover: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
