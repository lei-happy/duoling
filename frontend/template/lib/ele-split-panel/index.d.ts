import { StyleValue } from '../ele-app/types';

declare function __VLS_template(): {
    sideHeader?(_: {}): any;
    default?(_: {}): any;
    collapse?(_: {
        collapse: boolean | "body";
    }): any;
    maximized?(_: {
        collapse: boolean | "body";
    }): any;
    bodyHeader?(_: {}): any;
    body?(_: {
        collapse: boolean | "body";
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    size: (StringConstructor | NumberConstructor)[];
    minSize: NumberConstructor;
    maxSize: NumberConstructor;
    space: (StringConstructor | NumberConstructor)[];
    customStyle: import('vue').PropType<StyleValue>;
    customWrapStyle: import('vue').PropType<StyleValue>;
    bodyStyle: import('vue').PropType<StyleValue>;
    allowCollapse: import('vue').PropType<boolean | "both">;
    collapseStyle: import('vue').PropType<StyleValue>;
    collapseBtnOffset: (StringConstructor | NumberConstructor)[];
    collapse: import('vue').PropType<boolean | "body">;
    vertical: BooleanConstructor;
    reverse: BooleanConstructor;
    resizable: BooleanConstructor;
    percentage: BooleanConstructor;
    sideHeaderStyle: import('vue').PropType<StyleValue>;
    bodyHeaderStyle: import('vue').PropType<StyleValue>;
    flexTable: import('vue').PropType<boolean | "auto">;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>, {
    toggleCollapse: (collapse?: boolean | "body") => void;
    resetSize: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    resize: (_size: number | undefined, _strSize: string | null) => void;
    "update:collapse": (_collapse: boolean | "body") => void;
    resizeStart: (_size: number) => void;
    resizeEnd: (_size: number | undefined, _strSize: string | null) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    size: (StringConstructor | NumberConstructor)[];
    minSize: NumberConstructor;
    maxSize: NumberConstructor;
    space: (StringConstructor | NumberConstructor)[];
    customStyle: import('vue').PropType<StyleValue>;
    customWrapStyle: import('vue').PropType<StyleValue>;
    bodyStyle: import('vue').PropType<StyleValue>;
    allowCollapse: import('vue').PropType<boolean | "both">;
    collapseStyle: import('vue').PropType<StyleValue>;
    collapseBtnOffset: (StringConstructor | NumberConstructor)[];
    collapse: import('vue').PropType<boolean | "body">;
    vertical: BooleanConstructor;
    reverse: BooleanConstructor;
    resizable: BooleanConstructor;
    percentage: BooleanConstructor;
    sideHeaderStyle: import('vue').PropType<StyleValue>;
    bodyHeaderStyle: import('vue').PropType<StyleValue>;
    flexTable: import('vue').PropType<boolean | "auto">;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>> & Readonly<{
    onResize?: ((_size: number | undefined, _strSize: string | null) => any) | undefined;
    "onUpdate:collapse"?: ((_collapse: boolean | "body") => any) | undefined;
    onResizeStart?: ((_size: number) => any) | undefined;
    onResizeEnd?: ((_size: number | undefined, _strSize: string | null) => any) | undefined;
}>, {
    reverse: boolean;
    vertical: boolean;
    resizable: boolean;
    percentage: boolean;
    responsive: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
