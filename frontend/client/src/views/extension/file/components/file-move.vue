<template>
  <ele-modal :width="460" title="移动到" v-model="visible" @open="handleOpen">
    <div class="demo-file-move-tree">
      <el-tree
        :data="folderData"
        nodeKey="id"
        :props="{ label: 'name' }"
        :expand-on-click-node="false"
        :default-expand-all="true"
        @node-click="handleFolderSelect"
      >
        <template #default="scope">
          <img
            src="/ele-file-list/ic_file_folder.png"
            style="width: 18px; height: 18px; margin-right: 6px"
          />
          <span
            :class="[
              'el-tree-node__label',
              { 'is-active': scope.data.id === selectedId }
            ]"
          >
            {{ scope.data.name }}
          </span>
          <el-radio :value="true" :model-value="scope.data.id === selectedId" />
        </template>
      </el-tree>
    </div>
    <ele-loading
      v-if="folderLoading"
      :loading="folderLoading"
      :style="{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        borderRadius: 'var(--el-border-radius-base)',
        overflow: 'hidden'
      }"
    />
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="save">
        保存
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, toTree, mapTree } from 'ele-admin-plus';
  import { updateUserFile, listUserFiles } from '@/api/system/user-file';
  import type { UserFile } from '@/api/system/user-file/model';

  const props = defineProps<{
    /** 文件数据 */
    data?: UserFile;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  /** 弹窗是否打开 */
  const visible = defineModel({ type: Boolean });

  /** 提交状态 */
  const loading = ref(false);

  /** 选中的id */
  const selectedId = ref<number>();

  /** 文件夹数据 */
  const folderData = ref<UserFile[]>([]);

  /** 文件夹请求状态 */
  const folderLoading = ref(false);

  /** 文件夹选中事件 */
  const handleFolderSelect = (item: UserFile) => {
    selectedId.value = item.id;
  };

  /** 关闭弹窗 */
  const handleCancel = () => {
    visible.value = false;
  };

  /** 保存编辑 */
  const save = () => {
    const parentId = selectedId.value;
    if (parentId == null) {
      EleMessage.error({ message: '请选择分组', plain: true });
      return;
    }
    loading.value = true;
    updateUserFile({ id: props.data?.id, parentId })
      .then((msg) => {
        loading.value = false;
        EleMessage.success({ message: msg, plain: true });
        handleCancel();
        emit('done');
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 查询文件夹数据 */
  const queryFolder = () => {
    folderLoading.value = true;
    listUserFiles({ isDirectory: 1 })
      .then((list) => {
        const result = [
          { id: 0, name: '未分组' },
          ...mapTree(
            toTree({
              data: list,
              idField: 'id',
              parentIdField: 'parentId'
            }),
            (d) => (d.id === props.data?.id ? void 0 : d)
          )
        ];
        folderData.value = result;
        folderLoading.value = false;
      })
      .catch((e) => {
        folderData.value = [];
        EleMessage.error({ message: e.message, plain: true });
        folderLoading.value = false;
      });
  };

  /** 弹窗打开事件 */
  const handleOpen = () => {
    queryFolder();
    if (props.data) {
      selectedId.value = props.data.parentId;
    }
  };
</script>

<style lang="scss" scoped>
  .demo-file-move-tree {
    border: 1px solid var(--el-border-color-light);
    border-radius: var(--el-border-radius-base);

    :deep(.el-tree) {
      padding-top: 8px;
      padding-bottom: 8px;
      padding-left: calc(var(--ele-tree-item-radius) * 2);
      padding-right: calc(var(--ele-tree-item-radius) * 2);
      box-sizing: border-box;
      overflow-x: hidden;
      overflow-y: auto;
      user-select: none;
      --ele-tree-item-height: 36px;

      .el-tree-node__content {
        position: relative;
        z-index: 1;

        & > .el-tree-node__label.is-active {
          color: var(--el-color-primary);
          font-weight: bold;

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            background: var(--el-color-primary-light-9);
            border-radius: var(--ele-tree-item-radius);
          }
        }

        & > .el-radio {
          margin: 0 -12px 0 0;
        }
      }
    }
  }
</style>
