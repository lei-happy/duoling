import { PropType, ExtractPropTypes } from 'vue';
import { EleDropdownProps, EleDropdownInstance } from '../ele-app/plus';
import { default as FileGridItem } from './components/file-grid-item';
import { default as FileTableItem } from './components/file-table-item';
import { IconItem, FileItem, SortValue, ItemContextMenuOption, ColumnItem, SelectionType, ContextMenus, FileListLocale } from './types';

/**
 * 属性
 */
export declare const fileListProps: {
    /** 数据 */
    data: {
        type: PropType<FileItem[]>;
        required: boolean;
    };
    /** 选择框类型 */
    selectionType: PropType<SelectionType>;
    /** 多选选中数据 */
    selections: PropType<FileItem[]>;
    /** 单选选中数据 */
    current: PropType<FileItem>;
    /** 是否网格展示 */
    grid: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 表格模式默认的列是否可以排序 */
    sortable: BooleanConstructor;
    /** 排序字段 */
    sort: StringConstructor;
    /** 排序方式 */
    order: StringConstructor;
    /** 网格模式后缀对应图标 */
    icons: {
        type: PropType<IconItem[]>;
        default: () => IconItem[];
    };
    /** 表格模式后缀对应图标 */
    smallIcons: PropType<IconItem[]>;
    /** 表格模式自定义列配置 */
    columns: PropType<ColumnItem[]>;
    /** 多选时是否支持鼠标框选 */
    boxChoose: BooleanConstructor;
    /** 右键菜单 */
    contextMenus: PropType<ContextMenus>;
    /** 右键菜单属性 */
    contextMenuProps: PropType<EleDropdownProps>;
    /** 国际化 */
    locale: PropType<Partial<FileListLocale>>;
};
export type FileListProps = ExtractPropTypes<typeof fileListProps>;
/**
 * 事件
 */
export declare const fileListEmits: {
    /** item 点击事件 */
    itemClick: (_item: FileItem) => boolean;
    /** 排序方式改变事件 */
    sortChange: (_sorter: SortValue) => boolean;
    /** 更新多选选中数据 */
    'update:selections': (_selection?: FileItem[]) => boolean;
    /** 更新单选选中数据 */
    'update:current': (_current?: FileItem | null) => boolean;
    /** item 右键菜单项点击事件 */
    itemContextMenu: (_option: ItemContextMenuOption) => boolean;
    /** item 右键菜单打开事件 */
    itemContextOpen: (_dropdownRef: EleDropdownInstance, _item: FileItem) => boolean;
};
/**
 * 网格 item 实例
 */
export type GridItemInstance = InstanceType<typeof FileGridItem> | null;
/**
 * 表格 item 实例
 */
export type TableItemInstance = InstanceType<typeof FileTableItem> | null;
