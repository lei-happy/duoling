import { UserComponent } from '../../ele-app/types';
import { TreeTableColumn } from '../../ele-tree-table/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 选项数据 */
    modelValue?: Array<any> | string;
    /** 弹窗标题 */
    title?: string;
    /** 是否是树形结构数据 */
    isTreeData?: boolean | {
        maxDepth?: number;
    };
    /** 自定义列 */
    columns?: TreeTableColumn[] | "tableData" | "tableColumns" | "stringArray";
    /** 是否支持远程数据 */
    codeOptions?: boolean;
    /** 顶部提示内容 */
    codeTips?: string;
    /** 默认提示示例代码 */
    codePlaceholder?: string;
    /** 代码字符串前缀 */
    codePrefix?: string;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (data: string | any[]) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 选项数据 */
    modelValue?: Array<any> | string;
    /** 弹窗标题 */
    title?: string;
    /** 是否是树形结构数据 */
    isTreeData?: boolean | {
        maxDepth?: number;
    };
    /** 自定义列 */
    columns?: TreeTableColumn[] | "tableData" | "tableColumns" | "stringArray";
    /** 是否支持远程数据 */
    codeOptions?: boolean;
    /** 顶部提示内容 */
    codeTips?: string;
    /** 默认提示示例代码 */
    codePlaceholder?: string;
    /** 代码字符串前缀 */
    codePrefix?: string;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
}>>> & Readonly<{
    "onUpdate:modelValue"?: ((data: string | any[]) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
type __VLS_NonUndefinedable<T> = T extends undefined ? never : T;
type __VLS_TypePropsToRuntimeProps<T> = {
    [K in keyof T]-?: {} extends Pick<T, K> ? {
        type: import('vue').PropType<__VLS_NonUndefinedable<T[K]>>;
    } : {
        type: import('vue').PropType<T[K]>;
        required: true;
    };
};
