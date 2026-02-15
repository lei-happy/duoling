import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElTagProps } from '../ele-app/el';
import { EleTooltipProps } from '../ele-app/plus';
import { Validator, BeforeRemove } from './types';

/**
 * 属性
 */
export declare const editTagProps: {
    /** 标签数据 */
    modelValue: PropType<string[]>;
    /** 类型 */
    type: PropType<ElTagProps["type"]>;
    /** 是否有边框描边 */
    hit: BooleanConstructor;
    /** 颜色 */
    color: StringConstructor;
    /** 尺寸 */
    size: PropType<ElTagProps["size"]>;
    /** 主题 */
    effect: PropType<ElTagProps["effect"]>;
    /** 是否为圆形 */
    round: BooleanConstructor;
    /** 提示文本 */
    placeholder: StringConstructor;
    /** 输入框样式 */
    inputStyle: PropType<StyleValue>;
    /** 输入框外层标签样式 */
    inputTagStyle: PropType<StyleValue>;
    /** 添加按钮样式 */
    buttonStyle: PropType<StyleValue>;
    /** 标签样式 */
    itemStyle: PropType<StyleValue>;
    /** 添加校验方法 */
    validator: PropType<Validator>;
    /** 移除校验方法 */
    beforeRemove: PropType<BeforeRemove>;
    /** 提示属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 是否只读 */
    readonly: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
};
export type EditTagProps = ExtractPropTypes<typeof editTagProps>;
/**
 * 事件
 */
export declare const editTagEmits: {
    /** 更新数据 */
    'update:modelValue': (_value?: string[]) => boolean;
    /** 数据改变事件 */
    change: (_value?: string[]) => boolean;
    /** 标签点击事件 */
    itemClick: (_index: number, _value: string) => boolean;
};
