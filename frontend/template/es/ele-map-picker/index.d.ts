import { EleMapPickerViewInstance } from '../ele-app/plusx';
import { PoiItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    modalProps: import('vue').PropType<Omit<import('../ele-app/plus').EleModalProps, "modelValue">>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: import('vue').PropType<Partial<import('./types').MapLocale>>;
    keywordMode: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    height: {
        type: StringConstructor;
        default: string;
    };
    center: import('vue').PropType<number[]>;
    zoom: {
        type: NumberConstructor;
        default: number;
    };
    selectedZoom: {
        type: NumberConstructor;
        default: number;
    };
    poiLimit: {
        type: NumberConstructor;
        default: number;
    };
    poiType: {
        type: StringConstructor;
        default: string;
    };
    poiKeywords: {
        type: StringConstructor;
        default: string;
    };
    poiRadius: {
        type: NumberConstructor;
        default: number;
    };
    returnRegions: BooleanConstructor;
    required: {
        type: BooleanConstructor;
        default: boolean;
    };
    message: StringConstructor;
    suggestionCity: {
        type: StringConstructor;
        default: string;
    };
    searchPlaceholder: StringConstructor;
    markerSrc: {
        type: StringConstructor;
        default: string;
    };
    mapKey: StringConstructor;
    mapVersion: {
        type: StringConstructor;
        default: string;
    };
    mapStyle: StringConstructor;
    darkMode: BooleanConstructor;
    okText: StringConstructor;
    emptyProps: import('vue').PropType<import('../ele-app/el').ElEmptyProps>;
    searchStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    mode: {
        type: import('vue').PropType<import('./types').SelectMode>;
        default: string;
    };
    filterable: {
        type: BooleanConstructor;
        default: boolean;
    };
    clickMessage: StringConstructor;
    selected: import('vue').PropType<PoiItem>;
    sideStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
}>, {
    mapRef: import('vue').Ref<EleMapPickerViewInstance, EleMapPickerViewInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    done: (_result: PoiItem) => void;
    open: () => void;
    "update:modelValue": (_value: boolean) => void;
    closed: () => void;
    mapDone: (_ins: any) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    modalProps: import('vue').PropType<Omit<import('../ele-app/plus').EleModalProps, "modelValue">>;
    responsive: {
        type: BooleanConstructor;
        default: null;
    };
    locale: import('vue').PropType<Partial<import('./types').MapLocale>>;
    keywordMode: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    height: {
        type: StringConstructor;
        default: string;
    };
    center: import('vue').PropType<number[]>;
    zoom: {
        type: NumberConstructor;
        default: number;
    };
    selectedZoom: {
        type: NumberConstructor;
        default: number;
    };
    poiLimit: {
        type: NumberConstructor;
        default: number;
    };
    poiType: {
        type: StringConstructor;
        default: string;
    };
    poiKeywords: {
        type: StringConstructor;
        default: string;
    };
    poiRadius: {
        type: NumberConstructor;
        default: number;
    };
    returnRegions: BooleanConstructor;
    required: {
        type: BooleanConstructor;
        default: boolean;
    };
    message: StringConstructor;
    suggestionCity: {
        type: StringConstructor;
        default: string;
    };
    searchPlaceholder: StringConstructor;
    markerSrc: {
        type: StringConstructor;
        default: string;
    };
    mapKey: StringConstructor;
    mapVersion: {
        type: StringConstructor;
        default: string;
    };
    mapStyle: StringConstructor;
    darkMode: BooleanConstructor;
    okText: StringConstructor;
    emptyProps: import('vue').PropType<import('../ele-app/el').ElEmptyProps>;
    searchStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    mode: {
        type: import('vue').PropType<import('./types').SelectMode>;
        default: string;
    };
    filterable: {
        type: BooleanConstructor;
        default: boolean;
    };
    clickMessage: StringConstructor;
    selected: import('vue').PropType<PoiItem>;
    sideStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
}>> & Readonly<{
    onDone?: ((_result: PoiItem) => any) | undefined;
    onOpen?: (() => any) | undefined;
    "onUpdate:modelValue"?: ((_value: boolean) => any) | undefined;
    onClosed?: (() => any) | undefined;
    onMapDone?: ((_ins: any) => any) | undefined;
}>, {
    height: string;
    zoom: number;
    required: boolean;
    modelValue: boolean;
    filterable: boolean;
    mode: import('./types').SelectMode;
    responsive: boolean;
    keywordMode: boolean;
    selectedZoom: number;
    poiLimit: number;
    poiType: string;
    poiKeywords: string;
    poiRadius: number;
    returnRegions: boolean;
    suggestionCity: string;
    markerSrc: string;
    mapVersion: string;
    darkMode: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
