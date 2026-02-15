import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElEmptyProps } from '../ele-app/el';
import { EleModalProps } from '../ele-app/plus';
import { SelectMode, PoiItem, MapLocale } from './types';

/**
 * 属性
 */
export declare const mapProps: {
    /** 地图的高度 */
    height: {
        type: StringConstructor;
        default: string;
    };
    /** 地图默认中心点 */
    center: PropType<number[]>;
    /** 地图初始缩放级别 */
    zoom: {
        type: NumberConstructor;
        default: number;
    };
    /** 地图选中后缩放级别 */
    selectedZoom: {
        type: NumberConstructor;
        default: number;
    };
    /** POI检索最大数量 */
    poiLimit: {
        type: NumberConstructor;
        default: number;
    };
    /** POI检索兴趣点类别 */
    poiType: {
        type: StringConstructor;
        default: string;
    };
    /** POI检索关键字 */
    poiKeywords: {
        type: StringConstructor;
        default: string;
    };
    /** POI检索半径 */
    poiRadius: {
        type: NumberConstructor;
        default: number;
    };
    /** 是否返回行政区 */
    returnRegions: BooleanConstructor;
    /** 是否强制选择 */
    required: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 强制选择提示文本 */
    message: StringConstructor;
    /** 输入建议的城市范围 */
    suggestionCity: {
        type: StringConstructor;
        default: string;
    };
    /** 搜索框提示文本 */
    searchPlaceholder: StringConstructor;
    /** 地图中心图标地址 */
    markerSrc: {
        type: StringConstructor;
        default: string;
    };
    /** 高德地图密钥 */
    mapKey: StringConstructor;
    /** 高德地图版本号 */
    mapVersion: {
        type: StringConstructor;
        default: string;
    };
    /** 地图风格 */
    mapStyle: StringConstructor;
    /** 是否暗黑主题 */
    darkMode: BooleanConstructor;
    /** 完成按钮文字 */
    okText: StringConstructor;
    /** 空组件属性 */
    emptyProps: PropType<ElEmptyProps>;
    /** 自定义搜索栏样式 */
    searchStyle: PropType<StyleValue>;
    /** 位置选择模式 */
    mode: {
        type: PropType<SelectMode>;
        default: string;
    };
    /** 非关键字模式是否显示搜索框 */
    filterable: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 强制选择点击地图提示文本 */
    clickMessage: StringConstructor;
    /** 回显选中的位置 */
    selected: PropType<PoiItem>;
    /** 侧栏容器样式 */
    sideStyle: PropType<StyleValue>;
};
export declare const mapPickerProps: {
    /** 弹窗是否显示 */
    modelValue: BooleanConstructor;
    /** 弹窗参数 */
    modalProps: PropType<Omit<EleModalProps, "modelValue">>;
    /** 是否开启响应式 */
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    /** 国际化 */
    locale: PropType<Partial<MapLocale>>;
    /** 是否使用关键字检索模式, 默认POI检索模式 */
    keywordMode: BooleanConstructor;
    /** 自定义header样式 */
    headerStyle: PropType<StyleValue>;
    /** 地图的高度 */
    height: {
        type: StringConstructor;
        default: string;
    };
    /** 地图默认中心点 */
    center: PropType<number[]>;
    /** 地图初始缩放级别 */
    zoom: {
        type: NumberConstructor;
        default: number;
    };
    /** 地图选中后缩放级别 */
    selectedZoom: {
        type: NumberConstructor;
        default: number;
    };
    /** POI检索最大数量 */
    poiLimit: {
        type: NumberConstructor;
        default: number;
    };
    /** POI检索兴趣点类别 */
    poiType: {
        type: StringConstructor;
        default: string;
    };
    /** POI检索关键字 */
    poiKeywords: {
        type: StringConstructor;
        default: string;
    };
    /** POI检索半径 */
    poiRadius: {
        type: NumberConstructor;
        default: number;
    };
    /** 是否返回行政区 */
    returnRegions: BooleanConstructor;
    /** 是否强制选择 */
    required: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 强制选择提示文本 */
    message: StringConstructor;
    /** 输入建议的城市范围 */
    suggestionCity: {
        type: StringConstructor;
        default: string;
    };
    /** 搜索框提示文本 */
    searchPlaceholder: StringConstructor;
    /** 地图中心图标地址 */
    markerSrc: {
        type: StringConstructor;
        default: string;
    };
    /** 高德地图密钥 */
    mapKey: StringConstructor;
    /** 高德地图版本号 */
    mapVersion: {
        type: StringConstructor;
        default: string;
    };
    /** 地图风格 */
    mapStyle: StringConstructor;
    /** 是否暗黑主题 */
    darkMode: BooleanConstructor;
    /** 完成按钮文字 */
    okText: StringConstructor;
    /** 空组件属性 */
    emptyProps: PropType<ElEmptyProps>;
    /** 自定义搜索栏样式 */
    searchStyle: PropType<StyleValue>;
    /** 位置选择模式 */
    mode: {
        type: PropType<SelectMode>;
        default: string;
    };
    /** 非关键字模式是否显示搜索框 */
    filterable: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 强制选择点击地图提示文本 */
    clickMessage: StringConstructor;
    /** 回显选中的位置 */
    selected: PropType<PoiItem>;
    /** 侧栏容器样式 */
    sideStyle: PropType<StyleValue>;
};
export type MapPickerProps = ExtractPropTypes<typeof mapPickerProps>;
export type MapProps = ExtractPropTypes<typeof mapProps>;
/**
 * 事件
 */
export declare const mapPickerEmits: {
    /** 选择完成事件 */
    done: (_result: PoiItem) => boolean;
    /** 地图渲染完成事件 */
    mapDone: (_ins: any) => boolean;
    /** 弹窗打开事件 */
    open: () => boolean;
    /** 弹窗关闭事件 */
    closed: () => boolean;
    /** 更新弹窗打开状态 */
    'update:modelValue': (_value: boolean) => boolean;
};
export type MapPropKeys = Array<keyof typeof mapProps>;
/**
 * 地图组件属性名
 */
export declare const mapPropKeys: MapPropKeys;
