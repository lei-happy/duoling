import { PropType } from 'vue';
import { SideConfig, CrudLocale } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 侧栏配置 */
    sideConfig: PropType<SideConfig>;
    /** 数据 */
    data: PropType<Record<string, any>[]>;
    /** 加载状态 */
    loading: BooleanConstructor;
    /** 加载错误信息 */
    errorMessage: StringConstructor;
    /** 选中值 */
    selectedValue: PropType<any>;
    /** 侧栏树搜索关键字 */
    keywords: StringConstructor;
    /** 国际化 */
    lang: {
        type: PropType<Partial<CrudLocale>>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    treeNodeClick: (_nodeValue?: any) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 侧栏配置 */
    sideConfig: PropType<SideConfig>;
    /** 数据 */
    data: PropType<Record<string, any>[]>;
    /** 加载状态 */
    loading: BooleanConstructor;
    /** 加载错误信息 */
    errorMessage: StringConstructor;
    /** 选中值 */
    selectedValue: PropType<any>;
    /** 侧栏树搜索关键字 */
    keywords: StringConstructor;
    /** 国际化 */
    lang: {
        type: PropType<Partial<CrudLocale>>;
        required: true;
    };
}>> & Readonly<{
    onTreeNodeClick?: ((_nodeValue?: any) => any) | undefined;
}>, {
    loading: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
