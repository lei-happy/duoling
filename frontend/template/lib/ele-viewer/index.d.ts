declare function __VLS_template(): {
    default?(_: {}): any;
    markerItem?(_: {
        item: import('./types').MarkerItem;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    src: StringConstructor;
    markers: import('vue').PropType<import('./types').MarkerItem[]>;
    contentStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    imageStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    zoomStep: {
        type: NumberConstructor;
        default: number;
    };
    zoomMin: {
        type: NumberConstructor;
        default: number;
    };
    zoomMax: {
        type: NumberConstructor;
        default: number;
    };
    rotateStep: {
        type: NumberConstructor;
        default: number;
    };
}>, {
    viewerMoving: import('vue').Ref<boolean, boolean>;
    viewerTranslateX: import('vue').Ref<number, number>;
    viewerTranslateY: import('vue').Ref<number, number>;
    viewerScale: import('vue').Ref<number, number>;
    viewerFlipX: import('vue').Ref<boolean, boolean>;
    viewerFlipY: import('vue').Ref<boolean, boolean>;
    viewerRotate: import('vue').Ref<number, number>;
    zoomIn: () => void;
    zoomOut: () => void;
    flipX: () => void;
    flipY: () => void;
    rotateLeft: () => void;
    rotateRight: () => void;
    setTranslateX: (xValue: number) => void;
    setTranslateY: (yValue: number) => void;
    autoIntoView: () => void;
    autoIntoViewWidth: () => void;
    autoIntoViewHeight: () => void;
    reset: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    contentClick: (_e: MouseEvent) => void;
    contentContextmenu: (_e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    src: StringConstructor;
    markers: import('vue').PropType<import('./types').MarkerItem[]>;
    contentStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    imageStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    zoomStep: {
        type: NumberConstructor;
        default: number;
    };
    zoomMin: {
        type: NumberConstructor;
        default: number;
    };
    zoomMax: {
        type: NumberConstructor;
        default: number;
    };
    rotateStep: {
        type: NumberConstructor;
        default: number;
    };
}>> & Readonly<{
    onContentClick?: ((_e: MouseEvent) => any) | undefined;
    onContentContextmenu?: ((_e: MouseEvent) => any) | undefined;
}>, {
    zoomStep: number;
    zoomMin: number;
    zoomMax: number;
    rotateStep: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
