import { PropType, ExtractPropTypes } from 'vue';
import { UserComponent } from '../ele-app/types';
import { EleMessageOptions } from '../ele-app/plus';
import { DataItem } from '../ele-data-table/types';
import { Datasource } from '../ele-pro-table/types';
import { ProFormItemTypeData, ScreenSize } from '../ele-pro-form/types';
import { CrudField, ListConfig, SearchConfig, EditConfig, PageConfig, DeleteApi, EditApi, TreeListApi, CrudLocale } from './types';

/**
 * 属性
 */
export declare const crudProps: {
    /** 字段数据 */
    fields: PropType<CrudField[]>;
    /** 列表配置 */
    listConfig: PropType<ListConfig>;
    /** 搜索栏配置 */
    searchConfig: {
        type: PropType<SearchConfig | boolean>;
        default: () => null;
    };
    /** 添加配置 */
    addConfig: {
        type: PropType<EditConfig | boolean>;
        default: () => null;
    };
    /** 修改配置 */
    editConfig: {
        type: PropType<EditConfig | boolean>;
        default: () => null;
    };
    /** 页面配置 */
    pageConfig: PropType<PageConfig>;
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 表格数据接口 */
    listApi: PropType<Datasource | string>;
    /** 删除数据接口 */
    deleteApi: PropType<DeleteApi | string>;
    /** 添加数据接口 */
    addApi: PropType<EditApi | string>;
    /** 修改数据接口 */
    editApi: PropType<EditApi | string>;
    /** 侧栏树组件数据接口 */
    treeListApi: PropType<Array<Record<string, any>> | TreeListApi | string>;
    /** 消息提示组件属性 */
    messageOptions: PropType<EleMessageOptions>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    /** 屏幕尺寸 */
    screenSize: PropType<ScreenSize>;
    /** 国际化 */
    locale: PropType<Partial<CrudLocale>>;
};
export type CrudProps = ExtractPropTypes<typeof crudProps>;
/**
 * 事件
 */
export declare const crudEmits: {
    /** 表格多选数据改变事件 */
    tableSelectionsChange: (_selections: DataItem[]) => boolean;
};
