import { StyleValue } from '../ele-app/types';
import { AvatarItem, AvatarErrorOption } from './types';

declare function __VLS_template(): {
    item?(_: {
        item: AvatarItem;
    }): any;
    more?(_: {
        overflowCount: number;
        overflowData: AvatarItem[];
    }): any;
    overflow?(_: {
        overflowData: AvatarItem[];
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    data: {
        type: import('vue').PropType<AvatarItem[]>;
        required: boolean;
    };
    maxCount: NumberConstructor;
    shape: import('vue').PropType<import('../ele-app/el').ElAvatarProps["shape"]>;
    size: import('vue').PropType<import('../ele-app/el').ElAvatarProps["size"]>;
    itemStyle: import('vue').PropType<StyleValue>;
    avatarStyle: import('vue').PropType<StyleValue>;
    moreStyle: import('vue').PropType<StyleValue>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    overflowPopover: {
        type: BooleanConstructor;
        default: boolean;
    };
    overflowPopoverProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    hoverOpen: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    error: (_option: AvatarErrorOption) => void;
    itemClick: (_item: AvatarItem) => void;
    moreClick: () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    data: {
        type: import('vue').PropType<AvatarItem[]>;
        required: boolean;
    };
    maxCount: NumberConstructor;
    shape: import('vue').PropType<import('../ele-app/el').ElAvatarProps["shape"]>;
    size: import('vue').PropType<import('../ele-app/el').ElAvatarProps["size"]>;
    itemStyle: import('vue').PropType<StyleValue>;
    avatarStyle: import('vue').PropType<StyleValue>;
    moreStyle: import('vue').PropType<StyleValue>;
    tooltip: {
        type: BooleanConstructor;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    overflowPopover: {
        type: BooleanConstructor;
        default: boolean;
    };
    overflowPopoverProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    hoverOpen: BooleanConstructor;
}>> & Readonly<{
    onError?: ((_option: AvatarErrorOption) => any) | undefined;
    onItemClick?: ((_item: AvatarItem) => any) | undefined;
    onMoreClick?: (() => any) | undefined;
}>, {
    tooltip: boolean;
    overflowPopover: boolean;
    hoverOpen: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
