import { PropType, ExtractPropTypes, EmitsToProps } from 'vue';
import { drawerProps as elDrawerProps } from 'element-plus';
import { EleLoadingProps } from '../ele-app/plus';
import { StyleValue } from '../ele-app/types';

/**
 * 属性
 */
export declare const drawerProps: {
    appendToBody: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否限制在主体内部 */
    inner: BooleanConstructor;
    /** 自定义标题样式 */
    headerStyle: PropType<StyleValue>;
    /** 标题样式 */
    titleStyle: PropType<StyleValue>;
    /** 自定义主体样式 */
    bodyStyle: PropType<StyleValue>;
    /** 自定义底部样式 */
    footerStyle: PropType<StyleValue>;
    /** 自定义关闭按钮样式 */
    closeBtnStyle: PropType<StyleValue>;
    /** 主体类名 */
    drawerBodyClass: StringConstructor;
    /** 是否是失活状态 */
    isDeactivated: BooleanConstructor;
    /** 异步内容组件时加载状态 */
    compLoading: BooleanConstructor;
    /** 加载状态 */
    loading: BooleanConstructor;
    /** 加载组件属性 */
    loadingProps: PropType<EleLoadingProps>;
    /** 是否开启响应式 */
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    /** 内部表格弹性布局 */
    flexTable: PropType<boolean | "auto">;
    /** 是否是在内容区添加自定义底栏 */
    customFooter: BooleanConstructor;
    /** 是否是表单抽屉 */
    form: BooleanConstructor;
    direction: {
        readonly type: PropType<"ltr" | "rtl" | "ttb" | "btt">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "rtl";
    };
    resizable: BooleanConstructor;
    size: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "30%";
    };
    withHeader: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    modalFade: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    headerAriaLevel: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "2";
    };
    appendTo: {
        readonly type: PropType<string | HTMLElement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "body";
    };
    beforeClose: {
        readonly type: PropType<import('element-plus').DialogBeforeCloseFn>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    destroyOnClose: BooleanConstructor;
    closeOnClickModal: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    closeOnPressEscape: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    lockScroll: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    modal: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    modalPenetrable: BooleanConstructor;
    openDelay: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    closeDelay: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    top: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    modelValue: BooleanConstructor;
    modalClass: StringConstructor;
    headerClass: StringConstructor;
    bodyClass: StringConstructor;
    footerClass: StringConstructor;
    width: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    zIndex: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    trapFocus: BooleanConstructor;
    transition: {
        readonly type: PropType<import('element-plus').DialogTransition>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    center: BooleanConstructor;
    alignCenter: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    closeIcon: {
        readonly type: PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    draggable: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    overflow: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    fullscreen: BooleanConstructor;
    showClose: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    title: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    ariaLevel: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "2";
    };
};
export type DrawerProps = ExtractPropTypes<typeof drawerProps>;
/**
 * 事件
 */
export declare const drawerEmits: {
    open: () => boolean;
    opened: () => boolean;
    close: () => boolean;
    closed: () => boolean;
    "update:modelValue": (value: boolean) => boolean;
    openAutoFocus: () => boolean;
    closeAutoFocus: () => boolean;
};
export type DrawerEmitsProps = EmitsToProps<typeof drawerEmits>;
export type DrawerPropsAndEmits = DrawerProps & DrawerEmitsProps;
/**
 * 抽屉组件属性名
 */
export type ElDrawerPropKeys = Array<keyof typeof elDrawerProps>;
export declare const elDrawerPropKeys: ElDrawerPropKeys;
