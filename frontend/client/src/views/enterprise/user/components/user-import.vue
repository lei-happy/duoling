<!-- 用户导入弹窗 -->
<template>
  <ele-modal
    :width="460"
    title="导入用户"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-upload
      drag
      action=""
      accept=".xls,.xlsx"
      :show-file-list="false"
      :before-upload="doUpload"
      class="user-import-upload"
    >
      <ele-text
        type="primary"
        :icon="CloudUploadOutlined"
        :icon-props="{ size: 52 }"
        :icon-style="{ strokeWidth: 3 }"
        style="margin-bottom: 10px"
      />
      <ele-text type="placeholder">将文件拖到此处, 或点击上传</ele-text>
    </el-upload>
    <div style="display: flex; align-items: center; justify-content: center">
      <span style="padding-right: 8px">只能上传 xls、xlsx 文件,</span>
      <el-link
        type="primary"
        underline="never"
        href="https://cdn.eleadmin.com/20200610/用户导入模板.xlsx"
        download="用户导入模板.xlsx"
      >
        下载模板
      </el-link>
    </div>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { CloudUploadOutlined } from '@/components/icons';
  import { importUsers } from '@/api/system/user';

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  /** 导入请求状态 */
  const loading = ref(false);

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 上传 */
  const doUpload = (file: File) => {
    if (
      ![
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ].includes(file.type)
    ) {
      EleMessage.error({ message: '只能选择 excel 文件', plain: true });
      return false;
    }
    if (file.size / 1024 / 1024 > 10) {
      EleMessage.error({ message: '大小不能超过 10MB', plain: true });
      return false;
    }
    loading.value = true;
    importUsers(file)
      .then((msg) => {
        loading.value = false;
        EleMessage.success({ message: msg, plain: true });
        emit('done');
        handleCancel();
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
    return false;
  };
</script>

<style lang="scss" scoped>
  .user-import-upload {
    margin-bottom: 12px;

    :deep(.el-upload-dragger) {
      padding: 0;
      height: 180px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      transition: (border-color 0.2s, background-color 0.2s);

      &:not(.is-dragover) {
        background: var(--el-fill-color-light);
      }

      &.is-dragover {
        border-width: 1px;
      }
    }
  }
</style>
