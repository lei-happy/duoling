import { PropType, ExtractPropTypes } from 'vue';
import { UserComponent } from '../ele-app/types';
import { EleProTableProps } from '../ele-app/plus';
import { DataItem } from '../ele-data-table/types';
import { SelectValue, SingleValue, BeforeConfirm } from '../ele-basic-select/types';

/**
 * 属性
 */
export declare const tableSelectProps: {
    transition: {
        type: StringConstructor;
        default: string;
    };
    /** 选中值 */
    modelValue: {
        type: PropType<SelectValue>;
        default: () => null;
    };
    /** 是否触发表单验证 */
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 确认事件钩子 */
    beforeConfirm: PropType<BeforeConfirm<DataItem>>;
    /** 数据值的键名 */
    valueKey: {
        type: StringConstructor;
        default: string;
    };
    /** 显示文本的键名 */
    labelKey: {
        type: StringConstructor;
        default: string;
    };
    /** 缓存的数据 */
    cacheData: PropType<DataItem[]>;
    /** 表格配置 */
    tableProps: PropType<EleProTableProps>;
    /** 表格组件插槽对应名称 */
    tableSlots: PropType<Record<string, string>>;
    /** 内容容器组件 */
    wrapperComponent: PropType<UserComponent>;
    /** 内容容器组件属性 */
    wrapperComponentProps: ObjectConstructor;
    /** 初始选中值(已废弃) */
    initValue: PropType<DataItem | DataItem[]>;
    placement: {
        type: PropType<import('../ele-app/plus').EleTooltipProps["placement"]>;
        default: string;
    };
    popperClass: StringConstructor;
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    size: PropType<import('../ele-app/el').ElInputProps["size"]>;
    disabled: BooleanConstructor;
    placeholder: StringConstructor;
    clearable: BooleanConstructor;
    inputStyle: PropType<import('../ele-app/types').StyleValue>;
    filterable: BooleanConstructor;
    tagType: {
        type: PropType<import('../ele-app/el').ElTagProps["type"]>;
        default: string;
    };
    persistent: {
        type: BooleanConstructor;
        default: boolean;
    };
    visible: BooleanConstructor;
    popperOptions: PropType<import('../ele-app/plus').EleTooltipProps["popperOptions"]>;
    automaticDropdown: BooleanConstructor;
    multiple: BooleanConstructor;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    maxTagCount: NumberConstructor;
    maxTagTextLength: NumberConstructor;
    selectClass: StringConstructor;
    selectStyle: PropType<import('../ele-app/types').StyleValue | string>;
    selectTagsStyle: PropType<import('../ele-app/types').StyleValue>;
    popperWidth: (NumberConstructor | StringConstructor)[];
    popperHeight: (NumberConstructor | StringConstructor)[];
    popperType: PropType<import('../ele-basic-select/types').PopperType>;
    popperProps: PropType<import('../ele-basic-select/types').PopperProps>;
    popperSlots: PropType<Record<string, string>>;
    popperTitle: StringConstructor;
};
export type TableSelectProps = ExtractPropTypes<typeof tableSelectProps>;
/**
 * 事件
 */
export declare const tableSelectEmits: {
    /** 多选标签移除事件 */
    removeTag: (_value: SingleValue) => boolean;
    /** 更新选中值 */
    'update:modelValue': (_value: SelectValue) => boolean;
    /** 选中值改变事件 */
    change: (_value: SelectValue) => boolean;
    /** 下拉框展开状态改变事件 */
    visibleChange: (_visible: boolean) => boolean;
    /** 表格行选中事件 */
    select: (_item: DataItem | DataItem[]) => boolean;
    'update:visible': (_visible: boolean) => boolean;
    clear: () => boolean;
    focus: (_e: FocusEvent) => boolean;
    blur: (_e: FocusEvent) => boolean;
    filterChange: (_value: string) => boolean;
};
