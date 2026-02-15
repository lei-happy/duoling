<!-- 文件展示列表 -->
<template>
  <div class="demo-file-list">
    <ele-file-list
      :data="data"
      :grid="grid"
      :sort="sort"
      :order="order"
      :sortable="true"
      :box-choose="true"
      selection-type="checkbox"
      :selections="selections"
      :context-menus="contextMenus"
      :context-menu-props="{
        menuStyle: { minWidth: '120px' },
        iconProps: { size: 15 },
        popperOptions: { strategy: 'fixed' }
      }"
      :icons="localIcons"
      :small-icons="localSmallIcons"
      :style="{ minHeight: '400px', minWidth: grid ? 'auto' : '456px' }"
      @item-click="handleItemClick"
      @sort-change="handleSortChange"
      @update:selections="updateSelections"
      @item-context-menu="handleCtxMenuClick"
    />
    <div v-if="!data.length" class="demo-file-list-empty">
      <el-empty description="无数据" :image-size="80" />
    </div>
  </div>
  <!-- 图片预览 -->
  <ele-image-viewer
    v-model="showImageViewer"
    :urlList="viewerImages"
    :initialIndex="viewerIndex"
    :infinite="false"
    :hide-on-click-modal="true"
  />
  <!-- 文件重命名弹窗 -->
  <name-edit
    v-model="nameEditVisible"
    :data="nameEditData"
    @done="handleDone"
  />
  <!-- 文件移动弹窗 -->
  <file-move
    v-model="fileMoveVisible"
    :data="fileMoveData"
    @done="handleDone"
  />
</template>

<script lang="ts" setup>
  import { ref, markRaw } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { DropdownItem } from 'ele-admin-plus/es/ele-dropdown/types';
  import {
    localIcons,
    localSmallIcons
  } from 'ele-admin-plus/es/ele-file-list/icons';
  import type {
    FileItem,
    SortValue,
    ItemContextMenuOption
  } from 'ele-admin-plus/es/ele-file-list/types';
  import {
    DownloadOutlined,
    EditOutlined,
    DragOutlined,
    DeleteOutlined
  } from '@/components/icons';
  import { removeUserFile } from '@/api/system/user-file';
  import type { UserFile } from '@/api/system/user-file/model';
  import NameEdit from './name-edit.vue';
  import FileMove from './file-move.vue';

  const props = defineProps<{
    /** 父级id */
    parentId?: number;
    /** 文件列表数据 */
    data: FileItem[];
    /** 排序字段 */
    sort?: string;
    /** 排序方式 */
    order?: string;
    /** 选中数据 */
    selections: FileItem[];
    /** 是否网格展示 */
    grid: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'sort-change', value: SortValue): void;
    (e: 'update:selections', value: FileItem[]): void;
    (e: 'go-directory', value: UserFile): void;
    (e: 'done'): void;
  }>();

  /** 文件重命名弹窗是否打开 */
  const nameEditVisible = ref<boolean>(false);

  /** 文件重命名的数据 */
  const nameEditData = ref<UserFile>();

  /** 文件移动弹窗是否打开 */
  const fileMoveVisible = ref<boolean>(false);

  /** 文件移动的数据 */
  const fileMoveData = ref<UserFile>();

  /** 是否打开图片预览 */
  const showImageViewer = ref(false);

  /** 图片预览数据 */
  const viewerImages = ref<string[]>([]);

  /** 图片预览初始位置 */
  const viewerIndex = ref(0);

  /** 文件列表排序方式改变 */
  const handleSortChange = (option: SortValue) => {
    emit('sort-change', option);
  };

  /** 更新选中数据 */
  const updateSelections = (value: FileItem[]) => {
    emit('update:selections', value);
  };

  /** item 点击事件 */
  const handleItemClick = (item: FileItem) => {
    console.log('onItemClick:', JSON.parse(JSON.stringify(item)));
    if (item.isDirectory) {
      // 进入文件夹
      emit('go-directory', item as unknown as UserFile);
    } else if (isImageFile(item)) {
      // 预览图片文件
      previewItemImage(item);
    } else {
      // 选中或取消选中文件
      updateSelections(
        props.selections.includes(item)
          ? props.selections.filter((d) => d !== item)
          : [...props.selections, item]
      );
    }
  };

  /** 右键菜单点击事件 */
  const handleCtxMenuClick = (option: ItemContextMenuOption) => {
    const { key, item } = option;
    if (key === 'open') {
      // 打开文件
      if (item.isDirectory || isImageFile(item)) {
        handleItemClick(item);
      } else {
        window.open(item.url);
      }
    } else if (key === 'download') {
      // 下载文件
      if (typeof item.downloadUrl === 'string') {
        window.open(item.downloadUrl);
      }
    } else if (key === 'edit') {
      // 重命名
      nameEditData.value = item as unknown as UserFile;
      nameEditVisible.value = true;
    } else if (key === 'remove') {
      // 删除文件
      removeItem(item);
    } else if (key === 'move') {
      // 移动
      fileMoveData.value = item as unknown as UserFile;
      fileMoveVisible.value = true;
    }
  };

  /** 删除 */
  const removeItem = (item: FileItem) => {
    ElMessageBox.confirm(`确定要删除“${item.name}”吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeUserFile(item.id as number)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            handleDone();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  /** 完成刷新列表数据 */
  const handleDone = () => {
    emit('done');
  };

  /** 判断是否是图片文件 */
  const isImageFile = (item: FileItem) => {
    return (
      typeof item.contentType === 'string' &&
      item.contentType.startsWith('image/') &&
      item.url
    );
  };

  /** 预览图片文件 */
  const previewItemImage = (item: FileItem) => {
    const temp = props.data.filter((d) => isImageFile(d));
    const index = temp.indexOf(item);
    if (index !== -1) {
      viewerImages.value = temp.map((d) => d.url as string);
      viewerIndex.value = index;
      showImageViewer.value = true;
    }
  };

  /** 右键菜单 */
  const contextMenus = (item?: FileItem) => {
    if (!item) {
      return [];
    }
    const menus: DropdownItem[] = [
      {
        title: '重命名',
        command: 'edit',
        icon: markRaw(EditOutlined),
        divided: true
      },
      {
        title: '移动到',
        command: 'move',
        icon: markRaw(DragOutlined)
      },
      {
        title: '删除',
        command: 'remove',
        icon: markRaw(DeleteOutlined),
        divided: true,
        danger: true
      }
    ];
    if (item.isDirectory) {
      menus.unshift({ title: '打开', command: 'open' });
    } else if (
      isImageFile(item) ||
      (typeof item.contentType === 'string' &&
        (item.contentType.startsWith('video/') ||
          item.contentType.startsWith('text/') ||
          item.contentType.startsWith('application/pdf') ||
          item.contentType.startsWith('application/json') ||
          item.contentType.startsWith('application/javascript')))
    ) {
      menus[0].divided = false;
      menus.unshift({
        title: '下载',
        command: 'download',
        icon: markRaw(DownloadOutlined),
        divided: true
      });
      menus.unshift({ title: '预览', command: 'open' });
    } else {
      menus.unshift({
        title: '下载',
        command: 'download',
        icon: markRaw(DownloadOutlined)
      });
    }
    return menus;
  };
</script>

<style lang="scss" scoped>
  .demo-file-list {
    position: relative;
    overflow-x: auto;

    .demo-file-list-empty {
      position: absolute;
      top: 100px;
      left: 50%;
      transform: translateX(-50%);
    }
  }
</style>
