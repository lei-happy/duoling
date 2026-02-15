import { ElImageViewerInstance } from '../ele-app/el';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    modelValue: BooleanConstructor;
    customClass: StringConstructor;
    customStyle: ObjectConstructor;
    transitionName: {
        type: StringConstructor;
        default: string;
    };
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
}>, {
    imageViewerRef: import('vue').Ref<ElImageViewerInstance, ElImageViewerInstance>;
    setActiveItem: (index: number) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    rotate: (_deg: number) => void;
    close: () => void;
    "update:modelValue": (_value?: boolean | undefined) => void;
    switch: (_index: number) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    modelValue: BooleanConstructor;
    customClass: StringConstructor;
    customStyle: ObjectConstructor;
    transitionName: {
        type: StringConstructor;
        default: string;
    };
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
}>> & Readonly<{
    onRotate?: ((_deg: number) => any) | undefined;
    onClose?: (() => any) | undefined;
    "onUpdate:modelValue"?: ((_value?: boolean | undefined) => any) | undefined;
    onSwitch?: ((_index: number) => any) | undefined;
}>, {
    scale: number;
    modelValue: boolean;
    teleported: boolean;
    closeOnPressEscape: boolean;
    hideOnClickModal: boolean;
    initialIndex: number;
    infinite: boolean;
    zoomRate: number;
    minScale: number;
    maxScale: number;
    showProgress: boolean;
    urlList: string[];
    transitionName: string;
    keepAlive: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
