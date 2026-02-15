import { PropType, ExtractPropTypes, EmitsToProps } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElPopconfirmProps, ElIconProps, ElButtonProps } from '../ele-app/el';
import { ElePopoverProps } from '../ele-app/plus';

/**
 * 属性
 */
export declare const popconfirmProps: {
    trigger: {
        type: PropType<ElePopoverProps["trigger"]>;
        default: string;
    };
    /** 确认按钮文字 */
    confirmButtonText: StringConstructor;
    /** 取消按钮文字 */
    cancelButtonText: StringConstructor;
    /** 确认按钮类型 */
    confirmButtonType: {
        type: PropType<ElPopconfirmProps["confirmButtonType"]>;
        default: string;
    };
    /** 取消按钮类型 */
    cancelButtonType: {
        type: PropType<ElPopconfirmProps["cancelButtonType"]>;
        default: string;
    };
    /** 自定义图标 */
    icon: PropType<ElPopconfirmProps["icon"]>;
    /** 图标颜色 */
    iconColor: {
        type: StringConstructor;
        default: string;
    };
    /** 是否隐藏图标 */
    hideIcon: BooleanConstructor;
    /** 是否隐藏确认按钮 */
    hideConfirmButton: BooleanConstructor;
    /** 是否隐藏取消按钮 */
    hideCancelButton: BooleanConstructor;
    /** 图标样式 */
    iconStyle: PropType<StyleValue>;
    /** 图标组件属性 */
    iconProps: PropType<ElIconProps>;
    /** 确认按钮组件属性 */
    confirmButtonProps: PropType<ElButtonProps>;
    /** 取消按钮组件属性 */
    cancelButtonProps: PropType<ElButtonProps>;
    /** 底栏样式 */
    footerStyle: PropType<StyleValue>;
    transition: {
        type: StringConstructor;
        default: string;
    };
    bodyClass: StringConstructor;
    bodyStyle: PropType<StyleValue>;
    titleStyle: PropType<StyleValue>;
    contentStyle: PropType<StyleValue>;
    showAfter: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    hideAfter: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 200;
    };
    autoClose: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    title: StringConstructor;
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
    teleported: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    appendTo: {
        readonly type: PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
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
    offset: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    persistent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    width: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 150;
    };
    visible: {
        readonly type: PropType<boolean | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: null;
    };
    triggerKeys: {
        readonly type: PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => string[];
    };
    popperOptions: {
        readonly type: PropType<Partial<import('element-plus').Options>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    showArrow: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    content: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    enterable: {
        readonly default: true;
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        readonly __epPropKey: true;
    };
    popperStyle: PropType<StyleValue>;
    popperClass: StringConstructor;
    ariaLabel: StringConstructor;
    bg: StringConstructor;
    zIndex: NumberConstructor;
    virtualTriggering: BooleanConstructor;
    virtualRef: {
        readonly type: PropType<import('element-plus').Measurable>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
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
export type PopconfirmProps = ExtractPropTypes<typeof popconfirmProps>;
/**
 * 事件
 */
export declare const popconfirmEmits: {
    confirm: (_e: MouseEvent) => boolean;
    cancel: (_e: MouseEvent) => boolean;
    "update:visible": (value: boolean) => boolean;
    "before-enter": () => boolean;
    "before-leave": () => boolean;
    "after-enter": () => boolean;
    "after-leave": () => boolean;
};
export type PopconfirmEmitsProps = EmitsToProps<typeof popconfirmEmits>;
export type PopconfirmPropsAndEmits = PopconfirmProps & PopconfirmEmitsProps;
