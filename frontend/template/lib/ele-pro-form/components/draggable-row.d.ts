import { ElRowProps, ElColProps } from '../../ele-app/el';
import { ProFormItemProps, ScreenSize } from '../types';

declare function __VLS_template(): {
    item?(_: {
        element: any;
    }): any;
    footer?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项数据 */
    itemsData?: ProFormItemProps[];
    /** 组件属性 */
    componentData?: ElRowProps;
    /** 屏幕尺寸 */
    screenSize?: ScreenSize;
    /** 栅格布局属性 */
    gridColProps?: ElColProps;
    /** 表单数据 */
    formData?: Record<string, any>;
    /** 全部的表单项 */
    formItems?: ProFormItemProps[];
    /** 搜索表单展开状态 */
    searchExpand?: boolean;
    /** 远程数据源请求工具 */
    httpRequest?: any;
    /** 获取表单组件的组件引用数据方法 */
    getProFormRefs?: () => Record<string, any>;
    /** 获取并缓存代码解析结果方法 */
    getAndCacheCode?: (code: string, codeResult: any) => any;
    /** 自动计算额外的 ElCol 份数 */
    autoContentExtraCol?: boolean;
    /** 额外的 ElCol 属性 */
    contentExtraColProps?: ElColProps;
    /** 编辑模式 */
    editable?: boolean;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    updateItems: (data?: ProFormItemProps[] | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单项数据 */
    itemsData?: ProFormItemProps[];
    /** 组件属性 */
    componentData?: ElRowProps;
    /** 屏幕尺寸 */
    screenSize?: ScreenSize;
    /** 栅格布局属性 */
    gridColProps?: ElColProps;
    /** 表单数据 */
    formData?: Record<string, any>;
    /** 全部的表单项 */
    formItems?: ProFormItemProps[];
    /** 搜索表单展开状态 */
    searchExpand?: boolean;
    /** 远程数据源请求工具 */
    httpRequest?: any;
    /** 获取表单组件的组件引用数据方法 */
    getProFormRefs?: () => Record<string, any>;
    /** 获取并缓存代码解析结果方法 */
    getAndCacheCode?: (code: string, codeResult: any) => any;
    /** 自动计算额外的 ElCol 份数 */
    autoContentExtraCol?: boolean;
    /** 额外的 ElCol 属性 */
    contentExtraColProps?: ElColProps;
    /** 编辑模式 */
    editable?: boolean;
}>>> & Readonly<{
    onUpdateItems?: ((data?: ProFormItemProps[] | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
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
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
