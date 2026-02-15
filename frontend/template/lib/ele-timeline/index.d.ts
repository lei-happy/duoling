import { TimelineItem } from './types';

declare function __VLS_template(): {
    itemIcon?(_: {
        item: TimelineItem;
    }): any;
    itemTitle?(_: {
        item: TimelineItem;
    }): any;
    itemDescription?(_: {
        item: TimelineItem;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    data: import('vue').PropType<TimelineItem[]>;
    itemWidth: {
        type: NumberConstructor;
        default: number;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_item: TimelineItem, _e?: MouseEvent | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    data: import('vue').PropType<TimelineItem[]>;
    itemWidth: {
        type: NumberConstructor;
        default: number;
    };
}>> & Readonly<{
    onItemClick?: ((_item: TimelineItem, _e?: MouseEvent | undefined) => any) | undefined;
}>, {
    itemWidth: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
