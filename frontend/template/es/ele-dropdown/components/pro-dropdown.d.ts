import { PropType } from 'vue';
import { EleTooltipInstance } from '../../ele-app/plus';
import { DropdownItem } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    default?(_: {
        active: (string | number | Record<string, any>) | undefined;
        selected: DropdownItem | null | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 当前选中菜单项 */
    selected: PropType<DropdownItem | null>;
    transition: {
        type: StringConstructor;
        default: string;
    };
    items: PropType<DropdownItem[]>;
    modelValue: PropType<DropdownItem["command"]>;
    menuStyle: PropType<import('../../ele-app/types').StyleValue>;
    iconProps: PropType<import('../../ele-app/el').ElIconProps>;
    iconSize: PropType<"small" | "default">;
    componentType: PropType<"pro">;
    preventContextmenu: BooleanConstructor;
    splitButtonProps: PropType<import('../../ele-app/el').ElButtonProps>;
    caretButtonProps: PropType<import('../../ele-app/el').ElButtonProps>;
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    id: StringConstructor;
    maxHeight: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    type: {
        readonly type: PropType<"" | "text" | "default" | "primary" | "success" | "warning" | "info" | "danger">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    effect: {
        readonly default: "light";
        readonly type: PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    placement: {
        readonly type: PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "bottom";
    };
    popperClass: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    teleported: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    disabled: BooleanConstructor;
    tabindex: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    persistent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    triggerKeys: {
        readonly type: PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => string[];
    };
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperOptions: {
        readonly type: PropType<Partial<import('element-plus').Options>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    splitButton: BooleanConstructor;
    hideOnClick: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    loop: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showArrow: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    hideTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    role: {
        readonly type: PropType<"dialog" | "menu" | "grid" | "listbox" | "tooltip" | "tree" | "group" | "navigation">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "menu";
    };
    buttonProps: {
        readonly type: PropType<Partial<import('element-plus').ButtonProps>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    size: PropType<import('../../ele-app/el').ElButtonProps["size"]>;
    zIndex: NumberConstructor;
    offset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    popperStyle: PropType<import('../../ele-app/types').StyleValue>;
    appendTo: {
        readonly type: PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    bg: StringConstructor;
    visible: {
        readonly type: PropType<boolean | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: null;
    };
    trigger: {
        readonly type: PropType<import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    enterable: {
        readonly default: true;
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    arrowOffset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 5;
    };
    focusOnTarget: BooleanConstructor;
    className: StringConstructor;
    gpuAcceleration: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    arrowBg: StringConstructor;
}>, {
    tooltipRef: import('vue').Ref<EleTooltipInstance, EleTooltipInstance>;
    hidePopper: () => void;
    updatePopper: () => void;
    handleOpen: () => void;
    handleClose: () => void;
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
    /** 当前选中菜单项 */
    selected: PropType<DropdownItem | null>;
    transition: {
        type: StringConstructor;
        default: string;
    };
    items: PropType<DropdownItem[]>;
    modelValue: PropType<DropdownItem["command"]>;
    menuStyle: PropType<import('../../ele-app/types').StyleValue>;
    iconProps: PropType<import('../../ele-app/el').ElIconProps>;
    iconSize: PropType<"small" | "default">;
    componentType: PropType<"pro">;
    preventContextmenu: BooleanConstructor;
    splitButtonProps: PropType<import('../../ele-app/el').ElButtonProps>;
    caretButtonProps: PropType<import('../../ele-app/el').ElButtonProps>;
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    id: StringConstructor;
    maxHeight: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    type: {
        readonly type: PropType<"" | "text" | "default" | "primary" | "success" | "warning" | "info" | "danger">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    effect: {
        readonly default: "light";
        readonly type: PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    placement: {
        readonly type: PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "bottom";
    };
    popperClass: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    teleported: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    disabled: BooleanConstructor;
    tabindex: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    persistent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    triggerKeys: {
        readonly type: PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => string[];
    };
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperOptions: {
        readonly type: PropType<Partial<import('element-plus').Options>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    splitButton: BooleanConstructor;
    hideOnClick: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    loop: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showArrow: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    showTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    hideTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    role: {
        readonly type: PropType<"dialog" | "menu" | "grid" | "listbox" | "tooltip" | "tree" | "group" | "navigation">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "menu";
    };
    buttonProps: {
        readonly type: PropType<Partial<import('element-plus').ButtonProps>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    size: PropType<import('../../ele-app/el').ElButtonProps["size"]>;
    zIndex: NumberConstructor;
    offset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    popperStyle: PropType<import('../../ele-app/types').StyleValue>;
    appendTo: {
        readonly type: PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    bg: StringConstructor;
    visible: {
        readonly type: PropType<boolean | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: null;
    };
    trigger: {
        readonly type: PropType<import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    enterable: {
        readonly default: true;
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    arrowOffset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 5;
    };
    focusOnTarget: BooleanConstructor;
    className: StringConstructor;
    gpuAcceleration: {
        readonly type: PropType<boolean>;
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
    maxHeight: string | number;
    offset: number;
    transition: string;
    effect: import('element-plus').PopperEffect;
    placement: import('element-plus').Placement;
    popperClass: string;
    teleported: boolean;
    disabled: boolean;
    tabindex: string | number;
    validateEvent: boolean;
    persistent: boolean;
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
