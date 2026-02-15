import { ElTreeV2Instance } from '../ele-app/el';
import { EleBasicSelectInstance } from '../ele-app/plus';
import { SelectValue, SelectedItem } from '../ele-basic-select/types';
import { DataItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    default?(_: any): any;
    empty?(_: {}): any;
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
    cacheData: import('vue').PropType<import('./types').TreeData>;
    treeProps: import('vue').PropType<import('./types').TreeProps>;
    showCheckedStrategy: import('vue').PropType<import('./types').ShowCheckedStrategy>;
    checkedValueStrategy: BooleanConstructor;
    wrapperComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    wrapperComponentProps: ObjectConstructor;
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
    selectedItems: import('vue').Ref<{
        [x: string]: any;
        label: string;
        value: import('../ele-basic-select/types').SingleValue;
        data?: any;
        hide?: boolean | undefined;
    }[], SelectedItem[] | {
        [x: string]: any;
        label: string;
        value: import('../ele-basic-select/types').SingleValue;
        data?: any;
        hide?: boolean | undefined;
    }[]>;
    selectedLabel: import('vue').ComputedRef<string>;
    clearSelectedItems: () => void;
    removeSelectedItem: (item: SelectedItem) => void;
    updateSelectedItems: (items: SelectedItem[]) => void;
    clearTempSelectedItems: () => void;
    removeTempSelectedItem: (item: SelectedItem) => void;
    updateTempSelectedItems: (items: SelectedItem[]) => void;
    selectRef: import('vue').Ref<EleBasicSelectInstance, EleBasicSelectInstance>;
    treeRef: import('vue').Ref<ElTreeV2Instance, ElTreeV2Instance>;
    updatePopover: () => void;
    updateVisible: (visible: boolean) => void;
    focusSearchInput: () => void;
    reloadOptions: (params?: any) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    select: (_item: import('element-plus/es/components/tree-v2/src/types').TreeNodeData | import('element-plus/es/components/tree-v2/src/types').TreeNodeData[]) => void;
    clear: () => void;
    focus: (_e: FocusEvent) => void;
    blur: (_e: FocusEvent) => void;
    "update:modelValue": (_value: SelectValue) => void;
    change: (_value: SelectValue) => void;
    "update:visible": (_visible: boolean) => void;
    visibleChange: (_visible: boolean) => void;
    filterChange: (_value: string) => void;
    removeTag: (_value: import('../ele-basic-select/types').SingleValue) => void;
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
    cacheData: import('vue').PropType<import('./types').TreeData>;
    treeProps: import('vue').PropType<import('./types').TreeProps>;
    showCheckedStrategy: import('vue').PropType<import('./types').ShowCheckedStrategy>;
    checkedValueStrategy: BooleanConstructor;
    wrapperComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    wrapperComponentProps: ObjectConstructor;
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
    onSelect?: ((_item: import('element-plus/es/components/tree-v2/src/types').TreeNodeData | import('element-plus/es/components/tree-v2/src/types').TreeNodeData[]) => any) | undefined;
    onClear?: (() => any) | undefined;
    onFocus?: ((_e: FocusEvent) => any) | undefined;
    onBlur?: ((_e: FocusEvent) => any) | undefined;
    "onUpdate:modelValue"?: ((_value: SelectValue) => any) | undefined;
    onChange?: ((_value: SelectValue) => any) | undefined;
    "onUpdate:visible"?: ((_visible: boolean) => any) | undefined;
    onVisibleChange?: ((_visible: boolean) => any) | undefined;
    onFilterChange?: ((_value: string) => any) | undefined;
    onRemoveTag?: ((_value: import('../ele-basic-select/types').SingleValue) => any) | undefined;
}>, {
    transition: string;
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
    checkedValueStrategy: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
