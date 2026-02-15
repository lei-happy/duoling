import { EleBasicSelectInstance, EleProTableInstance } from '../ele-app/plus';
import { SelectValue, SingleValue, SelectedItem } from '../ele-basic-select/types';
import { DataItem } from '../ele-data-table/types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    popperTopExtra?(_: {}): any;
    popperBottomExtra?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    transition: {
        type: StringConstructor;
        default: string;
    };
    modelValue: {
        type: import('vue').PropType<SelectValue>;
        default: () => null;
    };
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    beforeConfirm: import('vue').PropType<import('../ele-basic-select/types').BeforeConfirm<DataItem>>;
    valueKey: {
        type: StringConstructor;
        default: string;
    };
    labelKey: {
        type: StringConstructor;
        default: string;
    };
    cacheData: import('vue').PropType<DataItem[]>;
    tableProps: import('vue').PropType<import('../ele-app/plus').EleProTableProps>;
    tableSlots: import('vue').PropType<Record<string, string>>;
    wrapperComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    wrapperComponentProps: ObjectConstructor;
    initValue: import('vue').PropType<DataItem | DataItem[]>;
    placement: {
        type: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    popperClass: StringConstructor;
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    size: import('vue').PropType<import('../ele-app/el').ElInputProps["size"]>;
    disabled: BooleanConstructor;
    placeholder: StringConstructor;
    clearable: BooleanConstructor;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    filterable: BooleanConstructor;
    tagType: {
        type: import('vue').PropType<import('../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    persistent: {
        type: BooleanConstructor;
        default: boolean;
    };
    visible: BooleanConstructor;
    popperOptions: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["popperOptions"]>;
    automaticDropdown: BooleanConstructor;
    multiple: BooleanConstructor;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    selectClass: StringConstructor;
    selectStyle: import('vue').PropType<import('../ele-app/types').StyleValue | string>;
    selectTagsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperWidth: (NumberConstructor | StringConstructor)[];
    popperHeight: (NumberConstructor | StringConstructor)[];
    popperType: import('vue').PropType<import('../ele-basic-select/types').PopperType>;
    popperProps: import('vue').PropType<import('../ele-basic-select/types').PopperProps>;
    popperSlots: import('vue').PropType<Record<string, string>>;
    popperTitle: StringConstructor;
}>, {
    clearSelectedItems: () => void;
    removeSelectedItem: (item: SelectedItem) => void;
    updateSelectedItems: (items: SelectedItem[]) => void;
    clearTempSelectedItems: () => void;
    removeTempSelectedItem: (item: SelectedItem) => void;
    updateTempSelectedItems: (items: SelectedItem[]) => void;
    selectRef: import('vue').Ref<EleBasicSelectInstance, EleBasicSelectInstance>;
    tableRef: import('vue').Ref<EleProTableInstance, EleProTableInstance>;
    updatePopover: () => void;
    updateVisible: (visible: boolean) => void;
    focusSearchInput: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    select: (_item: DataItem | DataItem[]) => void;
    clear: () => void;
    focus: (_e: FocusEvent) => void;
    blur: (_e: FocusEvent) => void;
    "update:modelValue": (_value: SelectValue) => void;
    change: (_value: SelectValue) => void;
    visibleChange: (_visible: boolean) => void;
    "update:visible": (_visible: boolean) => void;
    filterChange: (_value: string) => void;
    removeTag: (_value: SingleValue) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    transition: {
        type: StringConstructor;
        default: string;
    };
    modelValue: {
        type: import('vue').PropType<SelectValue>;
        default: () => null;
    };
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    beforeConfirm: import('vue').PropType<import('../ele-basic-select/types').BeforeConfirm<DataItem>>;
    valueKey: {
        type: StringConstructor;
        default: string;
    };
    labelKey: {
        type: StringConstructor;
        default: string;
    };
    cacheData: import('vue').PropType<DataItem[]>;
    tableProps: import('vue').PropType<import('../ele-app/plus').EleProTableProps>;
    tableSlots: import('vue').PropType<Record<string, string>>;
    wrapperComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    wrapperComponentProps: ObjectConstructor;
    initValue: import('vue').PropType<DataItem | DataItem[]>;
    placement: {
        type: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    popperClass: StringConstructor;
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    size: import('vue').PropType<import('../ele-app/el').ElInputProps["size"]>;
    disabled: BooleanConstructor;
    placeholder: StringConstructor;
    clearable: BooleanConstructor;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    filterable: BooleanConstructor;
    tagType: {
        type: import('vue').PropType<import('../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    persistent: {
        type: BooleanConstructor;
        default: boolean;
    };
    visible: BooleanConstructor;
    popperOptions: import('vue').PropType<import('../ele-app/plus').EleTooltipProps["popperOptions"]>;
    automaticDropdown: BooleanConstructor;
    multiple: BooleanConstructor;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    selectClass: StringConstructor;
    selectStyle: import('vue').PropType<import('../ele-app/types').StyleValue | string>;
    selectTagsStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    popperWidth: (NumberConstructor | StringConstructor)[];
    popperHeight: (NumberConstructor | StringConstructor)[];
    popperType: import('vue').PropType<import('../ele-basic-select/types').PopperType>;
    popperProps: import('vue').PropType<import('../ele-basic-select/types').PopperProps>;
    popperSlots: import('vue').PropType<Record<string, string>>;
    popperTitle: StringConstructor;
}>> & Readonly<{
    onSelect?: ((_item: DataItem | DataItem[]) => any) | undefined;
    onClear?: (() => any) | undefined;
    onFocus?: ((_e: FocusEvent) => any) | undefined;
    onBlur?: ((_e: FocusEvent) => any) | undefined;
    "onUpdate:modelValue"?: ((_value: SelectValue) => any) | undefined;
    onChange?: ((_value: SelectValue) => any) | undefined;
    onVisibleChange?: ((_visible: boolean) => any) | undefined;
    "onUpdate:visible"?: ((_visible: boolean) => any) | undefined;
    onFilterChange?: ((_value: string) => any) | undefined;
    onRemoveTag?: ((_value: SingleValue) => any) | undefined;
}>, {
    transition: string;
    valueKey: string;
    modelValue: SelectValue;
    placement: import('element-plus').Placement | undefined;
    teleported: boolean;
    disabled: boolean;
    clearable: boolean;
    validateEvent: boolean;
    filterable: boolean;
    tagType: ("primary" | "success" | "warning" | "info" | "danger") | undefined;
    persistent: boolean;
    visible: boolean;
    automaticDropdown: boolean;
    multiple: boolean;
    responsive: boolean;
    labelKey: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
