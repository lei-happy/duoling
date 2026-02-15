import { EleTooltipInstance } from '../ele-app/plus';

declare function __VLS_template(): {
    reference?(_: {}): any;
    body?(_: {}): any;
    title?(_: {}): any;
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    transition: {
        type: StringConstructor;
        default: string;
    };
    bodyClass: StringConstructor;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    contentStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    title: StringConstructor;
    content: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    width: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    offset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
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
        readonly default: "light";
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
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
    disabled: BooleanConstructor;
    tabindex: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    persistent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
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
        readonly default: true;
    };
    enterable: {
        readonly default: true;
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    popperStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    zIndex: NumberConstructor;
    ariaLabel: StringConstructor;
    bg: StringConstructor;
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: import('vue').PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
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
    className: StringConstructor;
    gpuAcceleration: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    arrowBg: StringConstructor;
}>, {
    tooltipRef: import('vue').Ref<EleTooltipInstance, EleTooltipInstance>;
    hide: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:visible": (value: boolean) => void;
    "before-enter": () => void;
    "before-leave": () => void;
    "after-enter": () => void;
    "after-leave": () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    transition: {
        type: StringConstructor;
        default: string;
    };
    bodyClass: StringConstructor;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    contentStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    title: StringConstructor;
    content: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    width: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    offset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
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
        readonly default: "light";
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
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
    disabled: BooleanConstructor;
    tabindex: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    persistent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
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
        readonly default: true;
    };
    enterable: {
        readonly default: true;
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    popperStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    zIndex: NumberConstructor;
    ariaLabel: StringConstructor;
    bg: StringConstructor;
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: import('vue').PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
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
    className: StringConstructor;
    gpuAcceleration: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    arrowBg: StringConstructor;
}>> & Readonly<{
    "onUpdate:visible"?: ((value: boolean) => any) | undefined;
    "onBefore-enter"?: (() => any) | undefined;
    "onBefore-leave"?: (() => any) | undefined;
    "onAfter-enter"?: (() => any) | undefined;
    "onAfter-leave"?: (() => any) | undefined;
}>, {
    content: string;
    width: string | number;
    offset: number;
    transition: string;
    showAfter: number;
    hideAfter: number;
    autoClose: number;
    effect: import('element-plus').PopperEffect;
    placement: import('element-plus').Placement;
    teleported: boolean;
    disabled: boolean;
    tabindex: string | number;
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
    gpuAcceleration: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
