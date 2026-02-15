import { EleBasicSelectViewInstance, EleTooltipInstance, EleModalInstance, EleDrawerInstance } from '../ele-app/plus';
import { SelectedItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    value: {
        type: import('vue').PropType<import('./types').SelectValue>;
        default: () => null;
    };
    selectedLabel: StringConstructor;
    selected: import('vue').PropType<SelectedItem[]>;
    visible: BooleanConstructor;
    multiple: BooleanConstructor;
    disabled: BooleanConstructor;
    size: import('vue').PropType<import('../ele-app/el').ElInputProps["size"]>;
    clearable: BooleanConstructor;
    placeholder: StringConstructor;
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    tagType: {
        type: import('vue').PropType<import('../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    automaticDropdown: BooleanConstructor;
    filterable: BooleanConstructor;
    selectClass: StringConstructor;
    selectStyle: import('vue').PropType<import('../ele-app/types').StyleValue | string>;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    selectTagsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    popperWidth: (NumberConstructor | StringConstructor)[];
    popperHeight: (NumberConstructor | StringConstructor)[];
    popperType: import('vue').PropType<import('./types').PopperType>;
    popperProps: import('vue').PropType<import('./types').PopperProps>;
    popperSlots: import('vue').PropType<Record<string, string>>;
    popperTitle: StringConstructor;
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
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>, {
    selectViewRef: import('vue').Ref<EleBasicSelectViewInstance, EleBasicSelectViewInstance>;
    tooltipRef: import('vue').Ref<EleTooltipInstance, EleTooltipInstance>;
    modalRef: import('vue').Ref<EleModalInstance, EleModalInstance>;
    drawerRef: import('vue').Ref<EleDrawerInstance, EleDrawerInstance>;
    updatePopper: () => void;
    focusSearchInput: (e?: MouseEvent) => void;
    updateVisible: (visible: boolean) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    clear: () => void;
    focus: (_e: FocusEvent) => void;
    blur: (_e: FocusEvent) => void;
    "update:visible": (_visible: boolean) => void;
    filterChange: (_value: string) => void;
    removeTag: (_item: SelectedItem) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    value: {
        type: import('vue').PropType<import('./types').SelectValue>;
        default: () => null;
    };
    selectedLabel: StringConstructor;
    selected: import('vue').PropType<SelectedItem[]>;
    visible: BooleanConstructor;
    multiple: BooleanConstructor;
    disabled: BooleanConstructor;
    size: import('vue').PropType<import('../ele-app/el').ElInputProps["size"]>;
    clearable: BooleanConstructor;
    placeholder: StringConstructor;
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    tagType: {
        type: import('vue').PropType<import('../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    automaticDropdown: BooleanConstructor;
    filterable: BooleanConstructor;
    selectClass: StringConstructor;
    selectStyle: import('vue').PropType<import('../ele-app/types').StyleValue | string>;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    selectTagsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    popperWidth: (NumberConstructor | StringConstructor)[];
    popperHeight: (NumberConstructor | StringConstructor)[];
    popperType: import('vue').PropType<import('./types').PopperType>;
    popperProps: import('vue').PropType<import('./types').PopperProps>;
    popperSlots: import('vue').PropType<Record<string, string>>;
    popperTitle: StringConstructor;
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
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>> & Readonly<{
    onClear?: (() => any) | undefined;
    onFocus?: ((_e: FocusEvent) => any) | undefined;
    onBlur?: ((_e: FocusEvent) => any) | undefined;
    "onUpdate:visible"?: ((_visible: boolean) => any) | undefined;
    onFilterChange?: ((_value: string) => any) | undefined;
    onRemoveTag?: ((_item: SelectedItem) => any) | undefined;
}>, {
    transition: string;
    placement: import('element-plus').Placement | undefined;
    teleported: boolean;
    disabled: boolean;
    clearable: boolean;
    value: import('./types').SelectValue;
    filterable: boolean;
    tagType: ("primary" | "success" | "warning" | "info" | "danger") | undefined;
    persistent: boolean;
    visible: boolean;
    automaticDropdown: boolean;
    multiple: boolean;
    responsive: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
