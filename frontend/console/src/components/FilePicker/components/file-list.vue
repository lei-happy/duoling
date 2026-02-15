<template>
  <div class="ele-file-picker-main">
    <div class="ele-file-picker-body">
      <div class="ele-file-picker-toolbar">
        <ElUpload
          action=""
          :accept="accept"
          :showFileList="false"
          :beforeUpload="handleUpload"
        >
          <BtnItems :items="[{ preset: 'upload' }]" />
        </ElUpload>
        <div class="ele-file-picker-search">
          <ElInput
            :clearable="true"
            v-model="searchKeyword"
            :placeholder="lang.searchPlaceholder"
            @clear="handleSearch"
            @change="handleSearch"
          />
          <ElButton
            type="primary"
            :icon="SearchOutlined"
            class="ele-btn-icon"
            @click="handleSearch"
          />
        </div>
        <EleSegmented
          v-model="isGridMode"
          :items="modeSegmentedItems"
          :validateEvent="false"
        />
      </div>
      <template v-if="fileData.length">
        <div class="ele-file-picker-file-list" @scroll="handleFileListScroll">
          <EleFileList
            :boxChoose="true"
            :icons="localIcons"
            :smallIcons="localSmallIcons"
            :contextMenuProps="contextMenuProps"
            v-bind="fileListProps || {}"
            :data="fileData"
            :grid="isGridMode === 1"
            :selectionType="limit === 1 ? 'radio' : 'checkbox'"
            :selections="fileSelections"
            v-model:current="fileCurrent"
            :contextMenus="fileContextMenus"
            :class="[{ 'is-ping-top': isPingTop }]"
            @itemClick="handleFileItemClick"
            @itemContextMenu="handleFileCtxMenuClick"
            @update:selections="updateSelections"
            @itemContextOpen="handleFileCtxMenuOpen"
          />
        </div>
        <ElePagination
          size="small"
          :teleported="false"
          :pageSizes="[18, 24, 30, 36, 42]"
          layout="total,prev,pager,next,sizes"
          v-bind="paginationProps || {}"
          :currentPage="currentPage"
          :pageSize="pageSize"
          :total="total"
          @update:currentPage="handleCurrentPageChange"
          @update:pageSize="handlePageSizeChange"
        />
      </template>
      <ElEmpty v-else :imageSize="80" v-bind="emptyProps || {}" />
    </div>
    <FileSelections
      ref="fileSelectionsRef"
      :fileSelections="
        limit === 1 ? (fileCurrent ? [fileCurrent] : []) : fileSelections
      "
      :limit="limit"
      :selectionListProps="selectionListProps"
      :baseIndex="baseIndex"
      :lang="lang"
      @clearSelections="clearSelections"
      @removeItem="removeItem"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, markRaw } from 'vue';
  import type { ElEmptyProps } from 'ele-admin-plus/es/ele-app/el';
  import type {
    EleFileListProps,
    EleUploadListProps,
    EleDropdownProps,
    ElePaginationProps
  } from 'ele-admin-plus/es/ele-app/plus';
  import type { DropdownItem } from 'ele-admin-plus/es/ele-dropdown/types';
  import type {
    FileItem,
    ItemContextMenuOption
  } from 'ele-admin-plus/es/ele-file-list/types';
  import {
    localIcons,
    localSmallIcons
  } from 'ele-admin-plus/es/ele-file-list/icons';
  import {
    SearchOutlined,
    MenuOutlined,
    AppstoreOutlined,
    EditOutlined,
    DragOutlined,
    DeleteOutlined
  } from '@/components/icons';
  import { isImageUrl } from '@/utils/common';
  import BtnItems from '@/components/BtnItems/index.vue';
  import type { FilePickerLocale, UserFile } from '../types';
  import { listFileApi, uploadFileApi } from '../config';
  import FileSelections from './file-selections.vue';

  const props = defineProps<{
    /** 最大选择数量 */
    limit?: number;
    /** 文件大小限制, 单位MB */
    fileLimit?: number;
    /** 接受上传的文件类型 */
    accept?: string;
    /** 接口查询参数 */
    params?: Record<string, any>;
    /** 文件列表自定义属性 */
    fileListProps?: EleFileListProps;
    /** 已选列表自定义属性 */
    selectionListProps?: EleUploadListProps;
    /** 空组件属性 */
    emptyProps?: ElEmptyProps;
    /** 分页组件属性 */
    paginationProps?: ElePaginationProps;
    /** 统一设置层级 */
    baseIndex?: number;
    /** 消息提示组件 */
    messageIns?: any;
    /** 组件文案 */
    lang: FilePickerLocale;
  }>();

  const emit = defineEmits<{
    (e: 'queryStart'): void;
    (e: 'queryDone'): void;
    (e: 'renameFile', item: UserFile, isFile?: boolean): void;
    (e: 'moveFile', item: UserFile, isFile?: boolean): void;
    (e: 'removeFile', item: UserFile, isFile?: boolean): void;
    (e: 'fileItemContextOpen'): void;
  }>();

  /** 查询方法参数 */
  interface QueryDataParams {
    /** 页码 */
    page?: number;
    /** 分组id */
    parentId?: number;
    /** 文件名 */
    name?: string;
  }

  /** 当前分组id */
  const fileParentId = ref<number>();

  /** 文件数据 */
  const fileData = ref<FileItem[]>([]);

  /** 选中的文件数据 */
  const fileSelections = ref<FileItem[]>([]);

  /** 单选选中的文件数据 */
  const fileCurrent = ref<FileItem>();

  /** 是否网格模式 */
  const isGridMode = ref(1);

  /** 搜索关键字 */
  const searchKeyword = ref('');

  /** 当前页码 */
  const currentPage = ref(1);

  /** 每页显示数量 */
  const pageSize = ref(24);

  /** 总数量 */
  const total = ref(0);

  /** 文件列表是否固定表头 */
  const isPingTop = ref(false);

  /** 视图模式分段器数据 */
  const modeSegmentedItems = [
    { icon: MenuOutlined, value: 0, iconStyle: { transform: 'scale(0.9)' } },
    { icon: AppstoreOutlined, value: 1 }
  ];

  /** 已选择列表组件 */
  const fileSelectionsRef = ref<InstanceType<typeof FileSelections>>();

  /** 文件列表右键菜单属性 */
  const contextMenuProps = reactive<EleDropdownProps>({
    menuStyle: { minWidth: '120px' },
    iconProps: { size: 15 },
    popperOptions: { strategy: 'fixed' },
    zIndex: props.baseIndex
  });

  /** 校验最大选择数量 */
  const checkLimit = (selections: FileItem[], isAdd?: boolean) => {
    if (
      props.limit &&
      props.limit > 1 &&
      (isAdd
        ? selections.length >= props.limit
        : selections.length > props.limit)
    ) {
      props.messageIns?.error?.(
        props.lang.limitMessage.replace(/\{\s*limit\s*\}/g, String(props.limit))
      );
      return false;
    }
  };

  /** 更新选中数据 */
  const updateSelections = (selections: FileItem[]) => {
    if (checkLimit(selections) !== false) {
      fileSelections.value = selections;
      return;
    }
    if (props.limit && props.limit > 1) {
      fileSelections.value = selections.slice(0, props.limit);
    }
  };

  /** 清空选中 */
  const clearSelections = () => {
    fileSelections.value = [];
    fileCurrent.value = void 0;
  };

  /** 获取选中数据 */
  const getSelections = () => {
    if (fileSelectionsRef.value) {
      const selections = fileSelectionsRef.value.getSelections() || [];
      return selections.map((d) => d.userFile as UserFile);
    }
    return [];
  };

  /** 移除选中 */
  const removeItem = (item: FileItem) => {
    if (props.limit === 1) {
      clearSelections();
      return;
    }
    const index = fileSelections.value.findIndex((d) => d.key === item.key);
    if (index !== -1) {
      fileSelections.value.splice(index, 1);
    }
  };

  /** 搜索 */
  const handleSearch = () => {
    queryData({ page: 1 });
  };

  /** 切换当前页码 */
  const handleCurrentPageChange = (page: number) => {
    if (currentPage.value !== page) {
      currentPage.value = page;
      queryData();
    }
  };

  /** 切换每页显示数量 */
  const handlePageSizeChange = (limit: number) => {
    if (pageSize.value !== limit) {
      currentPage.value = 1;
      pageSize.value = limit;
      const maxPage = Math.ceil(total.value / limit);
      if (maxPage && currentPage.value > maxPage) {
        currentPage.value = maxPage;
      }
      queryData();
    }
  };

  /** 文件列表点击事件 */
  const handleFileItemClick = (item: FileItem) => {
    if (props.limit === 1) {
      fileCurrent.value = item;
      return;
    }
    const index = fileSelections.value.findIndex((d) => d.key === item.key);
    if (index !== -1) {
      fileSelections.value.splice(index, 1);
      return;
    }
    if (checkLimit(fileSelections.value, true) !== false) {
      fileSelections.value.push(item);
    }
  };

  /** 文件列表右键菜单点击事件 */
  const handleFileCtxMenuClick = (option: ItemContextMenuOption) => {
    const { key, item } = option;
    const userFileItem = item.userFile as UserFile;
    if (key === 'preview') {
      if (!item.thumbnail) {
        window.open(item.url);
        return;
      }
      const data = fileData.value.filter((d) => !!d.thumbnail);
      const urls = data.map((d) => d.url) as string[];
      const index = data.indexOf(item);
      if (index !== -1) {
        fileSelectionsRef.value &&
          fileSelectionsRef.value.openImagePreview(urls, index);
      }
    } else if (key === 'rename') {
      emit('renameFile', userFileItem, true);
    } else if (key === 'move') {
      emit('moveFile', userFileItem, true);
    } else if (key === 'remove') {
      emit('removeFile', userFileItem, true);
    }
  };

  /** 文件列表右键菜单数据 */
  const fileContextMenus = (item: FileItem) => {
    const menus: DropdownItem[] = [
      {
        title: props.lang.renameTitle,
        command: 'rename',
        icon: markRaw(EditOutlined)
      },
      {
        title: props.lang.moveTitle,
        command: 'move',
        icon: markRaw(DragOutlined)
      },
      {
        title: props.lang.delete,
        command: 'remove',
        icon: markRaw(DeleteOutlined),
        divided: true,
        danger: true
      }
    ];
    if (item.thumbnail) {
      menus[0].divided = true;
      menus.unshift({ title: props.lang.preview, command: 'preview' });
    } else {
      menus[0].divided = true;
      menus.unshift({ title: props.lang.open, command: 'preview' });
    }
    return menus;
  };

  /** 文件列表右键菜单打开事件 */
  const handleFileCtxMenuOpen = () => {
    emit('fileItemContextOpen');
  };

  /** 校验选择的文件 */
  const checkFile = (file?: File) => {
    if (!file) {
      return;
    }
    if (props.accept === 'image/*') {
      if (!file.type.startsWith('image')) {
        props.messageIns?.error?.(props.lang.imageMessage);
        return;
      }
    } else if (props.accept === '.xls,.xlsx') {
      if (
        ![
          'application/vnd.ms-excel',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ].includes(file.type)
      ) {
        props.messageIns?.error?.(props.lang.excelMessage);
        return;
      }
    }
    if (props.fileLimit && file.size / 1024 / 1024 > props.fileLimit) {
      props.messageIns?.error?.(
        props.lang.sizeLimitMessage.replace(
          /\{\s*limit\s*\}/g,
          String(props.fileLimit)
        )
      );
      return;
    }
    return true;
  };

  /** 文件上传事件 */
  const handleUpload = (file: File) => {
    if (checkFile(file)) {
      const loading = props.messageIns?.loading?.({
        message: props.lang.uploadLoading,
        plain: true,
        mask: true
      });
      uploadFileApi(file)
        .then((msg) => {
          loading?.close?.();
          props.messageIns?.success?.(msg);
          queryData();
        })
        .catch((e) => {
          loading?.close?.();
          props.messageIns?.error?.(e.message);
        });
    }
    return false;
  };

  /** 文件列表滚动事件 */
  const handleFileListScroll = (e: MouseEvent) => {
    const wrapEl = e.currentTarget as any;
    const scrollTop = wrapEl.scrollTop;
    isPingTop.value = scrollTop > 1;
  };

  /** 触发文件数据请求完成 */
  const handleQueryDone = () => {
    emit('queryDone');
  };

  /** 判断是否是图片文件 */
  const isImageFile = (item: UserFile) => {
    if (!item.url) {
      return false;
    }
    if (
      typeof item.contentType === 'string' &&
      item.contentType.startsWith('image/')
    ) {
      return true;
    }
    return isImageUrl(item.url);
  };

  /** 格式化文件大小 */
  const formatLength = (length?: number) => {
    if (length == null) {
      return '-';
    }
    if (length < 1024) {
      return length + 'B';
    } else if (length < 1024 * 1024) {
      return (length / 1024).toFixed(1) + 'KB';
    } else if (length < 1024 * 1024 * 1024) {
      return (length / 1024 / 1024).toFixed(1) + 'M';
    } else {
      return (length / 1024 / 1024 / 1024).toFixed(1) + 'G';
    }
  };

  /** 查询文件数据 */
  const queryData = (params?: QueryDataParams) => {
    emit('queryStart');
    if (params) {
      if (params.page != null) {
        currentPage.value = params.page;
      }
      if (params.parentId != null) {
        fileParentId.value = params.parentId;
      }
      if (params.name != null) {
        searchKeyword.value = params.name;
      }
    }
    const parentId = fileParentId.value;
    listFileApi({
      page: currentPage.value,
      limit: pageSize.value,
      parentId: parentId === -1 ? void 0 : parentId,
      name: searchKeyword.value,
      isDirectory: 0,
      ...(props.params || {})
    })
      .then((result) => {
        if (!result?.list?.length && result?.count) {
          const maxPage = Math.ceil(result.count / pageSize.value);
          if (maxPage && currentPage.value > maxPage) {
            queryData({ page: maxPage });
            return;
          }
        }
        total.value = result?.count || 0;
        fileData.value =
          result?.list?.map?.((d) => {
            return {
              key: d.id as number,
              name: d.name as string,
              url: d.url,
              thumbnail: isImageFile(d) ? d.thumbnail || d.url : void 0,
              length: formatLength(d.length),
              updateTime: d.updateTime,
              isDirectory: d.isDirectory === 1,
              userFile: d
            };
          }) || [];
        handleQueryDone();
      })
      .catch((e) => {
        fileData.value = [];
        props.messageIns?.error?.(e.message);
        handleQueryDone();
      });
  };

  watch(
    () => props.limit,
    () => {
      clearSelections();
    }
  );

  watch(
    () => props.baseIndex,
    (baseIndex) => {
      contextMenuProps.zIndex = baseIndex;
    }
  );

  defineExpose({ queryData, clearSelections, getSelections });
</script>
