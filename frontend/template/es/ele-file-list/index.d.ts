import { EleDropdownInstance } from '../ele-app/plus';
import { FileItem, SortValue, ItemContextMenuOption } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: {
    item: FileItem;
    col: import('./types').ColumnItem;
}) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    data: {
        type: import('vue').PropType<FileItem[]>;
        required: boolean;
    };
    selectionType: import('vue').PropType<import('./types').SelectionType>;
    selections: import('vue').PropType<FileItem[]>;
    current: import('vue').PropType<FileItem>;
    grid: {
        type: BooleanConstructor;
        default: boolean;
    };
    sortable: BooleanConstructor;
    sort: StringConstructor;
    order: StringConstructor;
    icons: {
        type: import('vue').PropType<import('./types').IconItem[]>;
        default: () => import('./types').IconItem[];
    };
    smallIcons: import('vue').PropType<import('./types').IconItem[]>;
    columns: import('vue').PropType<import('./types').ColumnItem[]>;
    boxChoose: BooleanConstructor;
    contextMenus: import('vue').PropType<import('./types').ContextMenus>;
    contextMenuProps: import('vue').PropType<import('../ele-app/plus').EleDropdownProps>;
    locale: import('vue').PropType<Partial<import('./types').FileListLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    sortChange: (_sorter: SortValue) => void;
    itemClick: (_item: FileItem) => void;
    "update:selections": (_selection?: FileItem[] | undefined) => void;
    "update:current": (_current?: FileItem | null | undefined) => void;
    itemContextOpen: (_dropdownRef: EleDropdownInstance, _item: FileItem) => void;
    itemContextMenu: (_option: ItemContextMenuOption) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    data: {
        type: import('vue').PropType<FileItem[]>;
        required: boolean;
    };
    selectionType: import('vue').PropType<import('./types').SelectionType>;
    selections: import('vue').PropType<FileItem[]>;
    current: import('vue').PropType<FileItem>;
    grid: {
        type: BooleanConstructor;
        default: boolean;
    };
    sortable: BooleanConstructor;
    sort: StringConstructor;
    order: StringConstructor;
    icons: {
        type: import('vue').PropType<import('./types').IconItem[]>;
        default: () => import('./types').IconItem[];
    };
    smallIcons: import('vue').PropType<import('./types').IconItem[]>;
    columns: import('vue').PropType<import('./types').ColumnItem[]>;
    boxChoose: BooleanConstructor;
    contextMenus: import('vue').PropType<import('./types').ContextMenus>;
    contextMenuProps: import('vue').PropType<import('../ele-app/plus').EleDropdownProps>;
    locale: import('vue').PropType<Partial<import('./types').FileListLocale>>;
}>> & Readonly<{
    onSortChange?: ((_sorter: SortValue) => any) | undefined;
    onItemClick?: ((_item: FileItem) => any) | undefined;
    "onUpdate:selections"?: ((_selection?: FileItem[] | undefined) => any) | undefined;
    "onUpdate:current"?: ((_current?: FileItem | null | undefined) => any) | undefined;
    onItemContextOpen?: ((_dropdownRef: EleDropdownInstance, _item: FileItem) => any) | undefined;
    onItemContextMenu?: ((_option: ItemContextMenuOption) => any) | undefined;
}>, {
    grid: boolean;
    sortable: boolean;
    icons: import('./types').IconItem[];
    boxChoose: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
