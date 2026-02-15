import { EleProTableInstance } from '../ele-app/plus';
import { DataItem } from '../ele-data-table/types';
import { CrudField, DeleteApi, TreeListApi } from './types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    fields: import('vue').PropType<CrudField[]>;
    listConfig: import('vue').PropType<import('./types').ListConfig>;
    searchConfig: {
        type: import('vue').PropType<import('./types').SearchConfig | boolean>;
        default: () => null;
    };
    addConfig: {
        type: import('vue').PropType<import('./types').EditConfig | boolean>;
        default: () => null;
    };
    editConfig: {
        type: import('vue').PropType<import('./types').EditConfig | boolean>;
        default: () => null;
    };
    pageConfig: import('vue').PropType<import('./types').PageConfig>;
    proFormComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    listApi: import('vue').PropType<import('../ele-pro-table/types').Datasource | string>;
    deleteApi: import('vue').PropType<DeleteApi | string>;
    addApi: import('vue').PropType<import('./types').EditApi | string>;
    editApi: import('vue').PropType<import('./types').EditApi | string>;
    treeListApi: import('vue').PropType<Array<Record<string, any>> | TreeListApi | string>;
    messageOptions: import('vue').PropType<import('../ele-app/plus').EleMessageOptions>;
    itemTypeData: import('vue').PropType<import('../ele-pro-form/types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    screenSize: import('vue').PropType<import('../ele-pro-form/types').ScreenSize>;
    locale: import('vue').PropType<Partial<import('./types').CrudLocale>>;
}>, {
    tableRef: import('vue').Ref<EleProTableInstance, EleProTableInstance>;
    getTableSelections: () => {
        [x: string]: any;
        [x: number]: any;
        [x: symbol]: any;
        _isMock?: boolean | undefined;
    }[];
    reloadTree: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    tableSelectionsChange: (_selections: DataItem[]) => boolean;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    fields: import('vue').PropType<CrudField[]>;
    listConfig: import('vue').PropType<import('./types').ListConfig>;
    searchConfig: {
        type: import('vue').PropType<import('./types').SearchConfig | boolean>;
        default: () => null;
    };
    addConfig: {
        type: import('vue').PropType<import('./types').EditConfig | boolean>;
        default: () => null;
    };
    editConfig: {
        type: import('vue').PropType<import('./types').EditConfig | boolean>;
        default: () => null;
    };
    pageConfig: import('vue').PropType<import('./types').PageConfig>;
    proFormComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    listApi: import('vue').PropType<import('../ele-pro-table/types').Datasource | string>;
    deleteApi: import('vue').PropType<DeleteApi | string>;
    addApi: import('vue').PropType<import('./types').EditApi | string>;
    editApi: import('vue').PropType<import('./types').EditApi | string>;
    treeListApi: import('vue').PropType<Array<Record<string, any>> | TreeListApi | string>;
    messageOptions: import('vue').PropType<import('../ele-app/plus').EleMessageOptions>;
    itemTypeData: import('vue').PropType<import('../ele-pro-form/types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    screenSize: import('vue').PropType<import('../ele-pro-form/types').ScreenSize>;
    locale: import('vue').PropType<Partial<import('./types').CrudLocale>>;
}>> & Readonly<{
    onTableSelectionsChange?: ((_selections: DataItem[]) => any) | undefined;
}>, {
    searchConfig: boolean | import('./types').SearchConfig;
    addConfig: boolean | import('./types').EditConfig;
    editConfig: boolean | import('./types').EditConfig;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
