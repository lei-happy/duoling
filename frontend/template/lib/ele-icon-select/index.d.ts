import { EleBasicSelectInstance } from '../ele-app/plus';
import { IconItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    icon?(_: {
        icon: string;
        prefix: boolean;
    }): any;
    tabLeftExtra?(_: {}): any;
    tabRightExtra?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: StringConstructor;
    data: import('vue').PropType<string[] | IconItem[]>;
    disabled: BooleanConstructor;
    size: import('vue').PropType<import('../ele-app/el').ElInputProps["size"]>;
    clearable: BooleanConstructor;
    placeholder: StringConstructor;
    automaticDropdown: BooleanConstructor;
    filterable: import('vue').PropType<boolean | "popper">;
    selectStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    selectTagsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    popperWidth: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    popperHeight: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    popperType: {
        type: import('vue').PropType<import('../ele-basic-select/types').PopperType>;
        default: string;
    };
    popperProps: import('vue').PropType<import('../ele-basic-select/types').PopperProps>;
    popperSlots: import('vue').PropType<Record<string, string>>;
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    persistent: {
        type: BooleanConstructor;
        default: boolean;
    };
    placement: {
        type: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    transition: {
        type: StringConstructor;
        default: string;
    };
    popperOptions: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["popperOptions"]>;
    filterPlaceholder: StringConstructor;
    tooltip: {
        type: import('vue').PropType<import('./types').ItemTooltip>;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    emptyProps: import('vue').PropType<import('../ele-app/el').ElEmptyProps>;
    hideOnSingleTab: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    tabsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    searchStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    menusStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    gridStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>, {
    selectRef: import('vue').Ref<EleBasicSelectInstance, EleBasicSelectInstance>;
    updatePopover: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    clear: () => void;
    focus: (_e: FocusEvent) => void;
    blur: (_e: FocusEvent) => void;
    "update:modelValue": (_value?: string | null | undefined) => void;
    change: (_value?: string | null | undefined) => void;
    visibleChange: (_visible: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: StringConstructor;
    data: import('vue').PropType<string[] | IconItem[]>;
    disabled: BooleanConstructor;
    size: import('vue').PropType<import('../ele-app/el').ElInputProps["size"]>;
    clearable: BooleanConstructor;
    placeholder: StringConstructor;
    automaticDropdown: BooleanConstructor;
    filterable: import('vue').PropType<boolean | "popper">;
    selectStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    selectTagsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    popperWidth: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    popperHeight: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    popperType: {
        type: import('vue').PropType<import('../ele-basic-select/types').PopperType>;
        default: string;
    };
    popperProps: import('vue').PropType<import('../ele-basic-select/types').PopperProps>;
    popperSlots: import('vue').PropType<Record<string, string>>;
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    persistent: {
        type: BooleanConstructor;
        default: boolean;
    };
    placement: {
        type: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    transition: {
        type: StringConstructor;
        default: string;
    };
    popperOptions: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["popperOptions"]>;
    filterPlaceholder: StringConstructor;
    tooltip: {
        type: import('vue').PropType<import('./types').ItemTooltip>;
        default: boolean;
    };
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    emptyProps: import('vue').PropType<import('../ele-app/el').ElEmptyProps>;
    hideOnSingleTab: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    tabsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    searchStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    menusStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    gridStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>> & Readonly<{
    onClear?: (() => any) | undefined;
    onFocus?: ((_e: FocusEvent) => any) | undefined;
    onBlur?: ((_e: FocusEvent) => any) | undefined;
    "onUpdate:modelValue"?: ((_value?: string | null | undefined) => any) | undefined;
    onChange?: ((_value?: string | null | undefined) => any) | undefined;
    onVisibleChange?: ((_visible: boolean) => any) | undefined;
}>, {
    transition: string;
    placement: import('element-plus').Placement | undefined;
    teleported: boolean;
    disabled: boolean;
    clearable: boolean;
    persistent: boolean;
    tooltip: import('./types').ItemTooltip;
    automaticDropdown: boolean;
    responsive: boolean;
    popperWidth: string | number;
    popperHeight: string | number;
    popperType: import('../ele-basic-select/types').PopperType;
    hideOnSingleTab: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
