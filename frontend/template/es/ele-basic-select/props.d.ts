import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElInputProps, ElTagProps } from '../ele-app/el';
import { EleTooltipProps } from '../ele-app/plus';
import { SelectValue, SelectedItem, PopperType, PopperProps } from './types';

/**
 * 属性
 */
export declare const basicSelectProps: {
    /** 选中值 */
    value: {
        type: PropType<SelectValue>;
        default: () => null;
    };
    /** 单选选中展示文本 */
    selectedLabel: StringConstructor;
    /** 多选选中数据 */
    selected: PropType<SelectedItem[]>;
    /** 下拉组件是否显示 */
    visible: BooleanConstructor;
    /** 是否多选 */
    multiple: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 尺寸 */
    size: PropType<ElInputProps["size"]>;
    /** 是否支持清除 */
    clearable: BooleanConstructor;
    /** 无选中时提示文本 */
    placeholder: StringConstructor;
    /** 多选标签最大显示数量 */
    maxTagCount: NumberConstructor;
    /** 多选标签最大显示文本长度 */
    maxTagTextLength: NumberConstructor;
    /** 多选标签类型 */
    tagType: {
        type: PropType<ElTagProps["type"]>;
        default: string;
    };
    /** 是否在输入框获得焦点后自动弹出选项菜单 */
    automaticDropdown: BooleanConstructor;
    /** 是否可以筛选 */
    filterable: BooleanConstructor;
    /** 自定义类名 */
    selectClass: StringConstructor;
    /** 自定义样式 */
    selectStyle: PropType<StyleValue | string>;
    /** 自定义输入框样式 */
    inputStyle: PropType<StyleValue>;
    /** 自定义多选标签容器样式 */
    selectTagsStyle: PropType<StyleValue>;
    /** 下拉组件类名 */
    popperClass: StringConstructor;
    /** 下拉组件宽度 */
    popperWidth: (NumberConstructor | StringConstructor)[];
    /** 下拉组件高度 */
    popperHeight: (NumberConstructor | StringConstructor)[];
    /** 下拉组件类型 */
    popperType: PropType<PopperType>;
    /** 下拉组件属性 */
    popperProps: PropType<PopperProps>;
    /** 下拉组件插槽对应名称 */
    popperSlots: PropType<Record<string, string>>;
    /** 下拉组件标题 */
    popperTitle: StringConstructor;
    /** 是否将下拉组件插入 body */
    teleported: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 始终渲染下拉组件 */
    persistent: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 下拉框位置 */
    placement: {
        type: PropType<EleTooltipProps["placement"]>;
        default: string;
    };
    /** 下拉框渐变动画 */
    transition: {
        type: StringConstructor;
        default: string;
    };
    /** popper.js 参数 */
    popperOptions: PropType<EleTooltipProps["popperOptions"]>;
    /** 是否开启响应式 */
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
};
export type BasicSelectProps = ExtractPropTypes<typeof basicSelectProps>;
/**
 * 事件
 */
export declare const basicSelectEmits: {
    /** 更新下拉框显示状态 */
    'update:visible': (_visible: boolean) => boolean;
    /** 多选标签移除事件 */
    removeTag: (_item: SelectedItem) => boolean;
    /** 清空事件 */
    clear: () => boolean;
    /** 获取焦点事件 */
    focus: (_e: FocusEvent) => boolean;
    /** 失去焦点事件 */
    blur: (_e: FocusEvent) => boolean;
    /** 筛选输入框值改变事件 */
    filterChange: (_value: string) => boolean;
};
