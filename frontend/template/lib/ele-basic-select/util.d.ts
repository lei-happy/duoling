import { InjectionKey } from 'vue';
import { SelectValue, SelectDataProvider } from './types';

/**
 * 下拉组件数据注入键名
 */
export declare const SELECT_DATA_KEY: InjectionKey<SelectDataProvider>;
/**
 * 判断是否是空值
 * @param value 值
 * @param multiple 值是否是数组
 */
export declare function isEmptyValue(value?: SelectValue, multiple?: boolean): boolean;
/**
 * 判断值是否有变化
 * @param value1 新值
 * @param value2 当前值
 * @param multiple 是否多选
 */
export declare function valueIsChanged(value1: SelectValue, value2: SelectValue, multiple?: boolean): boolean;
/**
 * 触发表单验证
 */
export declare function useFormValidate(): {
    validateChange: () => void;
};
