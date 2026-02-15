import { PropType, CSSProperties, ExtractPropTypes } from 'vue';
import { ElRowProps, ElColProps, ElFormItemProps, ElButtonProps, ElLinkProps } from '../ele-app/el';
import { ProFormItemKey, ProFormItemProps, ProFormItemTypeData, ProFormItemRenderSlots, ScreenSize, ProFormLocale } from './types';

/**
 * 属性
 */
export declare const proFormProps: {
    /** 标签宽度 */
    labelWidth: {
        type: (NumberConstructor | StringConstructor)[];
        default: string;
    };
    /** 表单项 */
    items: PropType<ProFormItemProps[]>;
    /** 是否栅格布局 */
    grid: PropType<boolean | ElColProps>;
    /** 栅格布局时更多 ElRow 属性 */
    rowProps: PropType<ElRowProps>;
    /** 是否需要底栏 */
    footer: BooleanConstructor;
    /** 底栏 ElFormItem 属性 */
    footerProps: PropType<ElFormItemProps>;
    /** 底栏 ElFormItem 插槽 */
    footerSlots: ObjectConstructor;
    /** 栅格布局时底栏 ElCol 属性 */
    footerColProps: PropType<ElColProps>;
    /** 自动计算底栏栅格份数 */
    autoFooterCol: BooleanConstructor;
    /** 底栏样式 */
    footerStyle: PropType<CSSProperties>;
    /** 提交按钮文本 */
    submitText: StringConstructor;
    /** 重置按钮文本 */
    resetText: StringConstructor;
    /** 提交按钮属性 */
    submitButtonProps: PropType<ElButtonProps>;
    /** 重置按钮属性 */
    resetButtonProps: PropType<ElButtonProps>;
    /** 是否在底栏显示表单展开收起按钮 */
    showSearchExpand: BooleanConstructor;
    /** 展开和收起按钮属性 */
    searchExpandButtonProps: PropType<ElLinkProps>;
    /** 展开按钮的文字 */
    searchExpandText: StringConstructor;
    /** 收起按钮的文字 */
    searchShrinkText: StringConstructor;
    /** 搜索表单展开状态 */
    searchExpand: BooleanConstructor;
    /** 阻止表单原生的表单提交事件 */
    preventFormSubmit: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 编辑模式 */
    editable: BooleanConstructor;
    /** 屏幕尺寸 */
    screenSize: PropType<ScreenSize>;
    /** 编辑模式选中的表单项 */
    activeItemKey: PropType<ProFormItemKey>;
    /** 组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    /** 国际化 */
    locale: PropType<Partial<ProFormLocale>>;
    model: ObjectConstructor;
    rules: {
        readonly type: PropType<Partial<Record<string, import('element-plus').FormItemRule | import('element-plus').FormItemRule[]>>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    labelPosition: {
        readonly type: PropType<"top" | "left" | "right">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "right";
    };
    requireAsteriskPosition: {
        readonly type: PropType<"left" | "right">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "left";
    };
    labelSuffix: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    inline: BooleanConstructor;
    inlineMessage: BooleanConstructor;
    statusIcon: BooleanConstructor;
    showMessage: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    validateOnRuleChange: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    hideRequiredAsterisk: BooleanConstructor;
    scrollToError: BooleanConstructor;
    scrollIntoViewOptions: {
        readonly type: PropType<boolean | ScrollIntoViewOptions>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    size: {
        readonly type: PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    disabled: BooleanConstructor;
};
export type ProFormProps = ExtractPropTypes<typeof proFormProps>;
/**
 * 事件
 */
export declare const proFormEmits: {
    'update:searchExpand': (_expand: boolean) => boolean;
    updateValue: (_prop: string, _value: unknown) => boolean;
    'update:items': (_items: ProFormItemProps[]) => boolean;
    'update:activeItemKey': (_activeKey: ProFormItemKey) => boolean;
    submit: (_model: Record<string, any>) => boolean;
    reset: () => boolean;
    validate: (prop: import('element-plus').FormItemProp, isValid: boolean, message: string) => boolean;
};
/**
 * 表单项数据渲染组件属性
 */
export declare const childrenRenderProps: {
    /** 额外的 ElCol 属性 */
    contentExtraColProps: PropType<ElColProps>;
    /** 自动计算额外的 ElCol 份数 */
    autoContentExtraCol: {
        type: BooleanConstructor;
        required: boolean;
    };
    /** 父级表单项 */
    parentItem: PropType<ProFormItemProps>;
    /** 全部的表单项 */
    formItems: PropType<ProFormItemProps[]>;
    /** 搜索表单展开状态 */
    searchExpand: BooleanConstructor;
    /** 编辑模式禁用子级排序 */
    sortDisabled: BooleanConstructor;
    /** 编辑模式父级拖拽容器是否可点击选中 */
    containerSelectable: BooleanConstructor;
    /** 直接传递插槽数据 */
    slots: PropType<ProFormItemRenderSlots>;
    /** 获取表单组件的组件引用数据方法 */
    getProFormRefs: PropType<() => Record<string, any>>;
    /** 获取并缓存代码解析结果方法 */
    getAndCacheCode: PropType<(code: string, codeResult: any) => any>;
    /** 更新表单数据属性值方法 */
    updateItemValue: PropType<(prop: string, value: any) => void>;
    /** 编辑模式更新表单项数据方法 */
    updateItemsData: PropType<(items: ProFormItemProps[], parentItem?: ProFormItemProps) => void>;
    /** 更新编辑模式选中项方法 */
    updateActiveItemKey: PropType<(activeKey?: ProFormItemKey) => void>;
    /** 默认的必填提示文本 */
    requiredLang: StringConstructor;
    /** 兼容旧版 */
    item: PropType<ProFormItemProps>;
    grid: PropType<boolean | ElColProps>;
    model: ObjectConstructor;
    rules: {
        readonly type: PropType<Partial<Record<string, import('element-plus').FormItemRule | import('element-plus').FormItemRule[]>>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    rowProps: PropType<ElRowProps>;
    editable: BooleanConstructor;
    items: PropType<ProFormItemProps[]>;
    screenSize: PropType<ScreenSize>;
    activeItemKey: PropType<ProFormItemKey>;
    itemTypeData: PropType<ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
};
export type ChildrenRenderProps = ExtractPropTypes<typeof childrenRenderProps>;
/**
 * 渲染表单项数据方法参数
 */
export type RenderProFormContentProps = Partial<Omit<ChildrenRenderProps, 'item'>>;
/**
 * 渲染表单项组件方法参数
 */
export interface RenderProFormItemProps extends Pick<RenderProFormContentProps, 'model' | 'rules' | 'formItems' | 'searchExpand' | 'editable' | 'screenSize' | 'activeItemKey' | 'updateItemValue' | 'updateItemsData' | 'updateActiveItemKey' | 'getProFormRefs' | 'getAndCacheCode' | 'itemTypeData' | 'httpRequest' | 'slots' | 'requiredLang'> {
    /** 循环的 key */
    key?: ProFormItemKey;
    /** 表单项 */
    item: ProFormItemProps;
}
/**
 * 渲染表单项组件时的插槽额外参数
 */
export type RenderSlotProFormParam = Partial<Omit<ChildrenRenderProps, 'items' | 'contentExtraColProps' | 'sortDisabled' | 'containerSelectable'>>;
