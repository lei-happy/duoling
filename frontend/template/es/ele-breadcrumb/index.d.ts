import { ElBreadcrumbInstance } from '../ele-app/el';

declare function __VLS_template(): Partial<Record<string, (_: {
    item: import('./types').BreadcrumbItem;
}) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    separator: {
        type: import('vue').PropType<import('./types').BreadcrumbSeparator>;
        default: string;
    };
    items: {
        type: import('vue').PropType<import('./types').BreadcrumbItem[]>;
        required: boolean;
    };
    separatorIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
}>, {
    breadcrumbRef: import('vue').Ref<ElBreadcrumbInstance, ElBreadcrumbInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    separator: {
        type: import('vue').PropType<import('./types').BreadcrumbSeparator>;
        default: string;
    };
    items: {
        type: import('vue').PropType<import('./types').BreadcrumbItem[]>;
        required: boolean;
    };
    separatorIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
}>> & Readonly<{}>, {
    separator: import('./types').BreadcrumbSeparator;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
