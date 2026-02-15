import { PropType, ExtractPropTypes, EmitsToProps } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElIconProps, ElButtonProps, ElDropdownInstance } from '../ele-app/el';
import { default as ProDropdown } from './components/pro-dropdown';
import { DropdownItem } from './types';

declare const normalizeDropdownProps: Omit<{
    readonly trigger: {
        readonly type: PropType<import('element-plus').TooltipTriggerType | import('element-plus').TooltipTriggerType[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    readonly triggerKeys: {
        readonly type: PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => string[];
    };
    readonly virtualTriggering: BooleanConstructor;
    readonly virtualRef: {
        readonly type: PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    readonly effect: {
        readonly default: "light";
        readonly type: PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    readonly type: {
        readonly type: PropType<"" | "primary" | "success" | "warning" | "info" | "text" | "default" | "danger">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    readonly placement: {
        readonly type: PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "bottom";
    };
    readonly popperOptions: {
        readonly type: PropType<Partial<import('element-plus').Options>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    readonly id: StringConstructor;
    readonly size: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    readonly splitButton: BooleanConstructor;
    readonly hideOnClick: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    readonly loop: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    readonly showArrow: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    readonly showTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    readonly hideTimeout: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    readonly tabindex: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    readonly maxHeight: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    readonly popperClass: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    readonly disabled: BooleanConstructor;
    readonly role: {
        readonly type: PropType<"dialog" | "menu" | "grid" | "listbox" | "tooltip" | "tree" | "group" | "navigation">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "menu";
    };
    readonly buttonProps: {
        readonly type: PropType<Partial<import('element-plus').ButtonProps>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    readonly teleported: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    readonly persistent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
}, "size" | "trigger">;
/**
 * 属性
 */
export declare const dropdownProps: {
    /** 下拉框渐变动画 */
    transition: {
        type: StringConstructor;
        default: string;
    };
    /** 下拉菜单数据 */
    items: PropType<DropdownItem[]>;
    /** 选中的菜单 */
    modelValue: PropType<DropdownItem["command"]>;
    /** 自定义下拉菜单样式 */
    menuStyle: PropType<StyleValue>;
    /** 自定义图标属性 */
    iconProps: PropType<ElIconProps>;
    /** 图标尺寸 */
    iconSize: PropType<"small" | "default">;
    /** 下拉菜单使用的组件类型 */
    componentType: PropType<"pro">;
    /** 是否阻止下拉菜单的右键事件 */
    preventContextmenu: BooleanConstructor;
    /** 内容按钮属性 */
    splitButtonProps: PropType<ElButtonProps>;
    /** 箭头按钮属性 */
    caretButtonProps: PropType<ElButtonProps>;
    /** 是否触发表单验证 */
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    type: {
        readonly type: PropType<"" | "primary" | "success" | "warning" | "info" | "text" | "default" | "danger">;
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
    id: StringConstructor;
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
    maxHeight: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
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
    size: PropType<ElButtonProps["size"]>;
    popperStyle: PropType<StyleValue>;
    appendTo: {
        readonly type: PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    ariaLabel: StringConstructor;
    offset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    bg: StringConstructor;
    zIndex: NumberConstructor;
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
};
export type DropdownProps = ExtractPropTypes<typeof dropdownProps>;
/**
 * 事件
 */
export declare const dropdownEmits: {
    /** 内容按钮点击事件 */
    click: (_e: MouseEvent) => boolean;
    /** 菜单项点击事件 */
    command: (_command: DropdownItem["command"]) => boolean;
    /** 下拉框显示状态改变事件 */
    visibleChange: (_visible: boolean) => boolean;
    /** 更新选中值 */
    'update:modelValue': (_value: DropdownItem["command"]) => boolean;
    /** 选中改变的事件 */
    change: (_active: DropdownItem["command"]) => boolean;
    "update:visible": (value: boolean) => boolean;
    "before-enter": () => boolean;
    "before-leave": () => boolean;
    "after-enter": () => boolean;
    "after-leave": () => boolean;
};
export type DropdownEmitsProps = EmitsToProps<typeof dropdownEmits>;
export type DropdownPropsAndEmits = DropdownProps & DropdownEmitsProps;
/**
 * 属性名
 */
export type ElDropdownPropKeys = Array<keyof typeof normalizeDropdownProps>;
export declare const elDropdownPropKeys: ElDropdownPropKeys;
/**
 * 下拉菜单组件实例
 */
export type ProDropdownInstance = InstanceType<typeof ProDropdown> | null;
export type DropdownInstance = ElDropdownInstance | ProDropdownInstance;
export {};
