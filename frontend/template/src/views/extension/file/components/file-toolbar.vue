<template>
  <ele-toolbar theme="plain" class="demo-file-toolbar">
    <el-upload
      action=""
      :show-file-list="false"
      :before-upload="handleUpload"
      style="display: inline-block; vertical-align: middle"
    >
      <el-button type="primary" class="ele-btn-icon" :icon="UploadOutlined">
        上传
      </el-button>
    </el-upload>
    <el-button
      class="ele-btn-icon"
      :icon="FolderAddOutlined"
      style="margin-left: 12px"
      @click="openFolderAdd"
    >
      <span>新建</span>
      <span class="hidden-sm-and-down">文件夹</span>
    </el-button>
    <el-button
      plain
      type="danger"
      :icon="DeleteOutlined"
      :disabled="!selections.length"
      class="ele-btn-icon hidden-xs-only"
      @click="removeBatch"
    >
      删除
    </el-button>
    <el-button
      class="ele-btn-icon"
      style="margin-left: 12px"
      @click="openFilePicker"
    >
      <span class="hidden-sm-and-down">打开</span>
      <span>文件选择</span>
    </el-button>
    <template #tools>
      <!-- 搜索框 -->
      <div style="max-width: 240px" class="hidden-sm-and-down">
        <el-input
          v-model="search"
          placeholder="搜索您的文件"
          :prefix-icon="SearchOutlined"
        />
      </div>
      <!-- 显示方式切换 -->
      <el-icon
        class="demo-file-tool"
        :title="grid ? '表格模式' : '网格模式'"
        @click="toggleShowType"
      >
        <TableOutlined v-if="grid" />
        <AppstoreOutlined v-else />
      </el-icon>
    </template>
  </ele-toolbar>
  <!-- 新建文件夹弹窗 -->
  <folder-edit
    v-model="folderAddVisible"
    :parent-id="parentId"
    @done="handleDone"
  />
  <!-- 文件选择弹窗 -->
  <file-picker v-model="showFilePicker" @done="handleFilePickerDone" />
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { FileItem } from 'ele-admin-plus/es/ele-file-list/types';
  import {
    UploadOutlined,
    FolderAddOutlined,
    DeleteOutlined,
    SearchOutlined,
    TableOutlined,
    AppstoreOutlined
  } from '@/components/icons';
  import { uploadFile } from '@/api/system/file';
  import { addUserFile, removeUserFiles } from '@/api/system/user-file';
  import FolderEdit from './folder-edit.vue';
  import FilePicker from '@/components/FilePicker/index.vue';
  import type { UserFile } from '@/api/system/user-file/model';

  const props = defineProps<{
    /** 是否网格展示 */
    grid: boolean;
    /** 选中数据 */
    selections: FileItem[];
    /** 父级id */
    parentId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:grid', value: boolean): void;
    (e: 'done'): void;
  }>();

  /** 搜索关键字 */
  const search = ref<string>('');

  /** 新建文件夹弹窗是否打开 */
  const folderAddVisible = ref<boolean>(false);

  /** 上传 */
  const handleUpload = (file: File) => {
    if (file.size / 1024 / 1024 > 100) {
      EleMessage.error({ message: '大小不能超过 100MB', plain: true });
      return false;
    }
    const loading = EleMessage.loading({
      message: '上传中..',
      plain: true
    });
    uploadFile(file)
      .then((data) => {
        addUserFile({
          name: data.name,
          isDirectory: 0,
          parentId: props.parentId,
          path: data.path,
          length: data.length,
          contentType: data.contentType
        })
          .then(() => {
            loading.close();
            EleMessage.success({ message: '上传成功', plain: true });
            handleDone();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
    return false;
  };

  /** 打开新建文件夹弹窗 */
  const openFolderAdd = () => {
    folderAddVisible.value = true;
  };

  /** 批量删除 */
  const removeBatch = () => {
    const rows = props.selections;
    ElMessageBox.confirm(
      `确定要删除“${rows.map((d) => d.name).join(', ')}”吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeUserFiles(rows.map((d) => d.id as number))
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

  /** 显示方式切换 */
  const toggleShowType = () => {
    emit('update:grid', !props.grid);
  };

  /** 是否打开文件选择弹窗 */
  const showFilePicker = ref(false);

  /** 打开文件选择弹窗 */
  const openFilePicker = () => {
    showFilePicker.value = true;
  };

  /** 文件选择弹窗选择完成事件 */
  const handleFilePickerDone = (files: UserFile[]) => {
    showFilePicker.value = false;
    if (files.length) {
      console.log(JSON.parse(JSON.stringify(files)));
      EleMessage.success({
        message: files.length + '条数据已打印在控制台',
        plain: true
      });
    }
  };
</script>

<style lang="scss" scoped>
  /* 图标按钮 */
  .demo-file-tool {
    font-size: 18px;
    margin-left: 16px;
    cursor: pointer;
  }
</style>
