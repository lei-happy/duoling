import { ElAutocompleteInstance } from '../../ele-app/el';
import { PoiItem } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
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
    emptyProps: import('vue').PropType<import('../../ele-app/el').ElEmptyProps>;
    searchStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
    mode: {
        type: import('vue').PropType<import('../types').SelectMode>;
        default: string;
    };
    filterable: {
        type: BooleanConstructor;
        default: boolean;
    };
    clickMessage: StringConstructor;
    selected: import('vue').PropType<PoiItem>;
    sideStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
}>, {
    autocompleteRef: import('vue').Ref<ElAutocompleteInstance, ElAutocompleteInstance>;
    getMapIns: () => any;
    showInitSelected: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    done: (_result: PoiItem) => void;
    select: (_selected: PoiItem | null) => void;
    mapDone: (_ins: any) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
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
    emptyProps: import('vue').PropType<import('../../ele-app/el').ElEmptyProps>;
    searchStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
    mode: {
        type: import('vue').PropType<import('../types').SelectMode>;
        default: string;
    };
    filterable: {
        type: BooleanConstructor;
        default: boolean;
    };
    clickMessage: StringConstructor;
    selected: import('vue').PropType<PoiItem>;
    sideStyle: import('vue').PropType<import('../../ele-app/types').StyleValue>;
}>> & Readonly<{
    onDone?: ((_result: PoiItem) => any) | undefined;
    onSelect?: ((_selected: PoiItem | null) => any) | undefined;
    onMapDone?: ((_ins: any) => any) | undefined;
}>, {
    required: boolean;
    filterable: boolean;
    mode: import('../types').SelectMode;
    height: string;
    zoom: number;
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
export default _default;
