import { Ref } from 'vue';
import { DropdownItem } from './types';
import { DropdownInstance } from './props';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: {
    item: DropdownItem;
}) => any>> & {
    default?(_: {
        active: (string | number | Record<string, any>) | undefined;
        selected: DropdownItem | null | undefined;
    }): any;
    dropdown?(_: {}): any;
    dropdownMenu?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    transition: {
        type: StringConstructor;
        default: string;
    };
    items: import('vue').PropType<DropdownItem[]>;
    modelValue: import('vue').PropType<DropdownItem["command"]>;
    menuStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconSize: import('vue').PropType<"small" | "default">;
    componentType: import('vue').PropType<"pro">;
    preventContextmenu: BooleanConstructor;
    splitButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    caretButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    type: {
        readonly type: import('vue').PropType<"" | "primary" | "success" | "warning" | "info" | "text" | "default" | "danger">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
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
    popperClass: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    id: StringConstructor;
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
    splitButton: BooleanConstructor;
    hideOnClick: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    loop: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showArrow: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    hideTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    maxHeight: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    role: {
        readonly type: import('vue').PropType<"dialog" | "menu" | "grid" | "listbox" | "tooltip" | "tree" | "group" | "navigation">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "menu";
    };
    buttonProps: {
        readonly type: import('vue').PropType<Partial<import('element-plus').ButtonProps>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    size: import('vue').PropType<import('../ele-app/el').ElButtonProps["size"]>;
    popperStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    appendTo: {
        readonly type: import('vue').PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    offset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    bg: StringConstructor;
    zIndex: NumberConstructor;
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
    enterable: {
        readonly default: true;
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
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
    dropdownRef: Ref<DropdownInstance, DropdownInstance>;
    handleOpen: () => void;
    handleClose: () => void;
    updatePopper: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    click: (_e: MouseEvent) => void;
    command: (_command: (string | number | Record<string, any>) | undefined) => void;
    "update:modelValue": (_value: (string | number | Record<string, any>) | undefined) => void;
    change: (_active: (string | number | Record<string, any>) | undefined) => void;
    visibleChange: (_visible: boolean) => void;
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
    items: import('vue').PropType<DropdownItem[]>;
    modelValue: import('vue').PropType<DropdownItem["command"]>;
    menuStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconSize: import('vue').PropType<"small" | "default">;
    componentType: import('vue').PropType<"pro">;
    preventContextmenu: BooleanConstructor;
    splitButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    caretButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    type: {
        readonly type: import('vue').PropType<"" | "primary" | "success" | "warning" | "info" | "text" | "default" | "danger">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
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
    popperClass: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    id: StringConstructor;
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
    splitButton: BooleanConstructor;
    hideOnClick: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    loop: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showArrow: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    hideTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    maxHeight: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    role: {
        readonly type: import('vue').PropType<"dialog" | "menu" | "grid" | "listbox" | "tooltip" | "tree" | "group" | "navigation">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "menu";
    };
    buttonProps: {
        readonly type: import('vue').PropType<Partial<import('element-plus').ButtonProps>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    size: import('vue').PropType<import('../ele-app/el').ElButtonProps["size"]>;
    popperStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    appendTo: {
        readonly type: import('vue').PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    offset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    bg: StringConstructor;
    zIndex: NumberConstructor;
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
    enterable: {
        readonly default: true;
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
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
    onClick?: ((_e: MouseEvent) => any) | undefined;
    onCommand?: ((_command: (string | number | Record<string, any>) | undefined) => any) | undefined;
    "onUpdate:modelValue"?: ((_value: (string | number | Record<string, any>) | undefined) => any) | undefined;
    onChange?: ((_active: (string | number | Record<string, any>) | undefined) => any) | undefined;
    onVisibleChange?: ((_visible: boolean) => any) | undefined;
    "onUpdate:visible"?: ((value: boolean) => any) | undefined;
    "onBefore-enter"?: (() => any) | undefined;
    "onBefore-leave"?: (() => any) | undefined;
    "onAfter-enter"?: (() => any) | undefined;
    "onAfter-leave"?: (() => any) | undefined;
}>, {
    effect: import('element-plus').PopperEffect;
    placement: import('element-plus').Placement;
    popperClass: string;
    teleported: boolean;
    disabled: boolean;
    tabindex: string | number;
    validateEvent: boolean;
    offset: number;
    persistent: boolean;
    transition: string;
    visible: boolean | null;
    trigger: import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[];
    triggerKeys: string[];
    virtualTriggering: boolean;
    popperOptions: Partial<import('element-plus').Options>;
    splitButton: boolean;
    hideOnClick: boolean;
    loop: boolean;
    showArrow: boolean;
    showTimeout: number;
    hideTimeout: number;
    maxHeight: string | number;
    role: "dialog" | "menu" | "grid" | "listbox" | "tooltip" | "tree" | "group" | "navigation";
    enterable: boolean;
    arrowOffset: number;
    focusOnTarget: boolean;
    gpuAcceleration: boolean;
    preventContextmenu: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
