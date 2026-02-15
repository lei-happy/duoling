import { VNode } from 'vue';
import { get as getValue, set as setValue, merge as mergeValue, cloneDeep } from 'lodash-es';
import { FormItemRule } from 'element-plus';
import { ProFormItemKey, ProFormItemProps, ProFormItemTypeData, ProFormItemRenderSlots } from '../types';
import { RenderProFormItemProps, RenderProFormContentProps } from '../props';

export { setValue, getValue, mergeValue, cloneDeep };
/**
 * 获取表单项的类型名称
 * @param item 表单项
 */
export declare function getItemTypeName(item: ProFormItemProps): string | undefined;
/**
 * 获取表单项类型数据
 * @param item 表单项
 * @param itemTypeData 组件类型数据
 */
export declare function getItemTypeData(item: ProFormItemProps, itemTypeData?: ProFormItemTypeData[]): ProFormItemTypeData | undefined;
/**
 * 生成兼容旧版本的组件默认属性
 * @param item 表单项
 */
export declare function getComponentLegacyProps(item: ProFormItemProps): Record<string, any>;
/**
 * 获取验证规则提示文本
 * @param label 表单项标题
 * @param requiredMessage 必填校验信息
 * @param placeholder 组件占位文本
 * @param requiredLang 默认的必填提示文本
 */
export declare function getRuleMessage(label?: string, requiredMessage?: string, placeholder?: string, requiredLang?: string): string;
/**
 * 获取组件引用名称
 * @param item 表单项
 */
export declare function getComponentRefName(item: ProFormItemProps): string;
/**
 * 渲染表单项组件
 * @param props 属性
 */
export declare function renderProFormItem(props: RenderProFormItemProps): string | VNode | Array<string | VNode> | undefined;
/**
 * 渲染表单项
 * @param props 属性
 */
export declare function renderProFormContent(props: RenderProFormContentProps): string | VNode | Array<VNode | string> | undefined;
/**
 * 表单项数据渲染组件
 */
export declare const ChildrenRender: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    contentExtraColProps: import('vue').PropType<import('../../ele-app/el').ElColProps>;
    autoContentExtraCol: {
        type: BooleanConstructor;
        required: boolean;
    };
    parentItem: import('vue').PropType<ProFormItemProps>;
    formItems: import('vue').PropType<ProFormItemProps[]>;
    searchExpand: BooleanConstructor;
    sortDisabled: BooleanConstructor;
    containerSelectable: BooleanConstructor;
    slots: import('vue').PropType<ProFormItemRenderSlots>;
    getProFormRefs: import('vue').PropType<() => Record<string, any>>;
    getAndCacheCode: import('vue').PropType<(code: string, codeResult: any) => any>;
    updateItemValue: import('vue').PropType<(prop: string, value: any) => void>;
    updateItemsData: import('vue').PropType<(items: ProFormItemProps[], parentItem?: ProFormItemProps) => void>;
    updateActiveItemKey: import('vue').PropType<(activeKey?: ProFormItemKey) => void>;
    requiredLang: StringConstructor;
    item: import('vue').PropType<ProFormItemProps>;
    grid: import('vue').PropType<boolean | import('../../ele-app/el').ElColProps>;
    model: ObjectConstructor;
    rules: {
        readonly type: import('vue').PropType<Partial<Record<string, FormItemRule | FormItemRule[]>>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    rowProps: import('vue').PropType<import('../../ele-app/el').ElRowProps>;
    editable: BooleanConstructor;
    items: import('vue').PropType<ProFormItemProps[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    screenSize: import('vue').PropType<import('../types').ScreenSize>;
    activeItemKey: import('vue').PropType<ProFormItemKey>;
    itemTypeData: import('vue').PropType<ProFormItemTypeData[]>;
}>, () => string | VNode<import('vue').RendererNode, import('vue').RendererElement, {
    [key: string]: any;
}> | (string | VNode<import('vue').RendererNode, import('vue').RendererElement, {
    [key: string]: any;
}>)[] | undefined, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    updateItemValue: (_prop: string, _value: any) => true;
    updateItemsData: (_items: ProFormItemProps[], _parentItem?: ProFormItemProps) => true;
    'update:activeItemKey': (_activeKey?: ProFormItemKey) => true;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    contentExtraColProps: import('vue').PropType<import('../../ele-app/el').ElColProps>;
    autoContentExtraCol: {
        type: BooleanConstructor;
        required: boolean;
    };
    parentItem: import('vue').PropType<ProFormItemProps>;
    formItems: import('vue').PropType<ProFormItemProps[]>;
    searchExpand: BooleanConstructor;
    sortDisabled: BooleanConstructor;
    containerSelectable: BooleanConstructor;
    slots: import('vue').PropType<ProFormItemRenderSlots>;
    getProFormRefs: import('vue').PropType<() => Record<string, any>>;
    getAndCacheCode: import('vue').PropType<(code: string, codeResult: any) => any>;
    updateItemValue: import('vue').PropType<(prop: string, value: any) => void>;
    updateItemsData: import('vue').PropType<(items: ProFormItemProps[], parentItem?: ProFormItemProps) => void>;
    updateActiveItemKey: import('vue').PropType<(activeKey?: ProFormItemKey) => void>;
    requiredLang: StringConstructor;
    item: import('vue').PropType<ProFormItemProps>;
    grid: import('vue').PropType<boolean | import('../../ele-app/el').ElColProps>;
    model: ObjectConstructor;
    rules: {
        readonly type: import('vue').PropType<Partial<Record<string, FormItemRule | FormItemRule[]>>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    rowProps: import('vue').PropType<import('../../ele-app/el').ElRowProps>;
    editable: BooleanConstructor;
    items: import('vue').PropType<ProFormItemProps[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    screenSize: import('vue').PropType<import('../types').ScreenSize>;
    activeItemKey: import('vue').PropType<ProFormItemKey>;
    itemTypeData: import('vue').PropType<ProFormItemTypeData[]>;
}>> & Readonly<{
    onUpdateItemValue?: ((_prop: string, _value: any) => any) | undefined;
    onUpdateItemsData?: ((_items: ProFormItemProps[], _parentItem?: ProFormItemProps | undefined) => any) | undefined;
    "onUpdate:activeItemKey"?: ((_activeKey?: string | number | symbol | undefined) => any) | undefined;
}>, {
    editable: boolean;
    searchExpand: boolean;
    autoContentExtraCol: boolean;
    sortDisabled: boolean;
    containerSelectable: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export type ChildrenRenderInstance = InstanceType<typeof ChildrenRender> | null;
