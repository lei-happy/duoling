import { ExtractPropTypes } from 'vue';

/**
 * 属性
 */
export declare const imageViewerProps: {
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否打开 */
    modelValue: BooleanConstructor;
    /** 自定义类名 */
    customClass: StringConstructor;
    /** 自定义样式 */
    customStyle: ObjectConstructor;
    /** 过渡动画名称 */
    transitionName: {
        type: StringConstructor;
        default: string;
    };
    /** 是否失活后仍然显示 */
    keepAlive: BooleanConstructor;
    urlList: {
        readonly type: import('vue').PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [];
    };
    zIndex: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    initialIndex: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    infinite: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    hideOnClickModal: BooleanConstructor;
    closeOnPressEscape: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    zoomRate: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 1.2;
    };
    scale: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 1;
    };
    minScale: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0.2;
    };
    maxScale: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 7;
    };
    showProgress: BooleanConstructor;
    crossorigin: {
        readonly type: import('vue').PropType<"" | "anonymous" | "use-credentials">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
};
export type ImageViewerProps = ExtractPropTypes<typeof imageViewerProps>;
/**
 * 事件
 */
export declare const imageViewerEmits: {
    /** 更新打开状态 */
    'update:modelValue': (_value?: boolean) => boolean;
    /** 关闭事件 */
    close: () => boolean;
    /** 切换图像事件 */
    switch: (_index: number) => boolean;
    /** 旋转图像事件 */
    rotate: (_deg: number) => boolean;
};
