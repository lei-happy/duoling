import { PropType, ExtractPropTypes, EmitsToProps } from 'vue';
import { dialogProps } from 'element-plus';
import { StyleValue } from '../ele-app/types';
import { EleLoadingProps } from '../ele-app/plus';
import { Resizable, MoveOut, Position } from './types';

/**
 * 属性
 */
export declare const modalProps: {
    appendToBody: {
        type: BooleanConstructor;
        default: boolean;
    };
    draggable: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 弹窗高度 */
    height: (NumberConstructor | StringConstructor)[];
    /** 弹窗最大高度 */
    maxHeight: (NumberConstructor | StringConstructor)[];
    /** 是否可以拖出边界 */
    moveOut: PropType<MoveOut>;
    /** 是否可以拉伸 */
    resizable: PropType<Resizable>;
    /** 初始位置 */
    position: PropType<Position>;
    /** 是否在弹窗关闭后重置位置和大小 */
    resetOnClose: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否显示最大化切换按钮 */
    maxable: BooleanConstructor;
    /** 是否支持打开多个 */
    multiple: BooleanConstructor;
    /** 是否限制在主体内部 */
    inner: BooleanConstructor;
    /** 最小拉伸宽度 */
    minWidth: {
        type: NumberConstructor;
        default: number;
    };
    /** 最小拉伸高度 */
    minHeight: {
        type: NumberConstructor;
        default: number;
    };
    /** 标题栏样式 */
    headerStyle: PropType<StyleValue>;
    /** 标题样式 */
    titleStyle: PropType<StyleValue>;
    /** 主体样式 */
    bodyStyle: PropType<StyleValue>;
    /** 底栏样式 */
    footerStyle: PropType<StyleValue>;
    /** 自定义关闭按钮样式 */
    closeBtnStyle: PropType<StyleValue>;
    /** 自定义全屏按钮样式 */
    fullscreenBtnStyle: PropType<StyleValue>;
    /** 拉伸图标样式 */
    resizeIconStyle: PropType<StyleValue>;
    /** 主体类名 */
    modalBodyClass: StringConstructor;
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
    /** 是否是表单弹窗 */
    form: BooleanConstructor;
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
    headerAriaLevel: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "2";
    };
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
export type ModalProps = ExtractPropTypes<typeof modalProps>;
/**
 * 事件
 */
export declare const modalEmits: {
    /** 更新全屏状态 */
    'update:fullscreen': (_fullscreen: boolean) => boolean;
    open: () => boolean;
    opened: () => boolean;
    close: () => boolean;
    closed: () => boolean;
    "update:modelValue": (value: boolean) => boolean;
    openAutoFocus: () => boolean;
    closeAutoFocus: () => boolean;
};
export type ModalEmitsProps = EmitsToProps<typeof modalEmits>;
export type ModalPropsAndEmits = ModalProps & ModalEmitsProps;
/**
 * 弹窗组件属性名
 */
export type DialogPropKeys = (keyof typeof dialogProps)[];
export declare const dialogPropKeys: DialogPropKeys;
