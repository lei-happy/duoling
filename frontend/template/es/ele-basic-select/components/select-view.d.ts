import { ElInputInstance } from '../../ele-app/el';
import { SelectedItem } from '../types';

declare function __VLS_template(): {
    default?(_: {}): any;
    select?(_: {
        visible: boolean;
        value: import('../types').SelectValue;
        selectedLabel: string | undefined;
        selected: SelectedItem[] | undefined;
        currentTags: SelectedItem[];
        omittedTags: SelectedItem[];
        omittedSize: number;
        openPopper: () => void;
        closePopper: () => void;
        removeItem: (item: SelectedItem) => void;
        clear: () => void;
    }): any;
    prefix?(_: {}): any;
    clearIcon?(_: {}): any;
    suffixIcon?(_: {
        visible: boolean;
    }): any;
    maxTagPlaceholder?(_: {
        omittedValues: SelectedItem[];
        omittedSize: number;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    value: {
        type: import('vue').PropType<import('../types').SelectValue>;
        default: () => null;
    };
    selectedLabel: StringConstructor;
    selected: import('vue').PropType<SelectedItem[]>;
    visible: BooleanConstructor;
    multiple: BooleanConstructor;
    disabled: BooleanConstructor;
    size: import('vue').PropType<import('../../ele-app/el').ElInputProps["size"]>;
    clearable: BooleanConstructor;
    placeholder: StringConstructor;
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    tagType: {
        type: import('vue').PropType<import('../../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    automaticDropdown: BooleanConstructor;
    filterable: BooleanConstructor;
    selectClass: StringConstructor;
    selectStyle: import('vue').PropType<import('../../ele-app/types').StyleValue | string>;
    inputStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
    selectTagsStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    popperWidth: (StringConstructor | NumberConstructor)[];
    popperHeight: (StringConstructor | NumberConstructor)[];
    popperType: import('vue').PropType<import('../types').PopperType>;
    popperProps: import('vue').PropType<import('../types').PopperProps>;
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
        type: import('vue').PropType<import('../../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    transition: {
        type: StringConstructor;
        default: string;
    };
    popperOptions: import('vue').PropType<import('../../ele-app/plus').EleTooltipProps["popperOptions"]>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
}>, {
    inputRef: import('vue').Ref<ElInputInstance, ElInputInstance>;
    searchRef: import('vue').Ref<ElInputInstance, ElInputInstance>;
    focusSearchInput: () => void;
    updateSearchValue: (modelValue: string) => void;
    updateInputValue: (modelValue: string) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    clear: () => void;
    focus: (_e: FocusEvent) => void;
    blur: (_e: FocusEvent) => void;
    "update:visible": (_visible: boolean) => void;
    filterChange: (_value: string) => void;
    removeTag: (_item: SelectedItem) => void;
    inputClick: (_e: MouseEvent) => void;
    wrapClick: (_isCustom?: boolean | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    value: {
        type: import('vue').PropType<import('../types').SelectValue>;
        default: () => null;
    };
    selectedLabel: StringConstructor;
    selected: import('vue').PropType<SelectedItem[]>;
    visible: BooleanConstructor;
    multiple: BooleanConstructor;
    disabled: BooleanConstructor;
    size: import('vue').PropType<import('../../ele-app/el').ElInputProps["size"]>;
    clearable: BooleanConstructor;
    placeholder: StringConstructor;
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    tagType: {
        type: import('vue').PropType<import('../../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    automaticDropdown: BooleanConstructor;
    filterable: BooleanConstructor;
    selectClass: StringConstructor;
    selectStyle: import('vue').PropType<import('../../ele-app/types').StyleValue | string>;
    inputStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
    selectTagsStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
    popperClass: StringConstructor;
    popperWidth: (StringConstructor | NumberConstructor)[];
    popperHeight: (StringConstructor | NumberConstructor)[];
    popperType: import('vue').PropType<import('../types').PopperType>;
    popperProps: import('vue').PropType<import('../types').PopperProps>;
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
        type: import('vue').PropType<import('../../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    transition: {
        type: StringConstructor;
        default: string;
    };
    popperOptions: import('vue').PropType<import('../../ele-app/plus').EleTooltipProps["popperOptions"]>;
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
    onInputClick?: ((_e: MouseEvent) => any) | undefined;
    onWrapClick?: ((_isCustom?: boolean | undefined) => any) | undefined;
}>, {
    value: import('../types').SelectValue;
    placement: import('element-plus').Placement | undefined;
    teleported: boolean;
    disabled: boolean;
    clearable: boolean;
    filterable: boolean;
    tagType: ("primary" | "success" | "warning" | "info" | "danger") | undefined;
    persistent: boolean;
    transition: string;
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
