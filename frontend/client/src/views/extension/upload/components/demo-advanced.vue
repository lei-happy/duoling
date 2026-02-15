<template>
  <ele-card header="手动上传">
    <ele-upload-list
      :drag="true"
      :tools="true"
      v-model="images"
      :readonly="loading"
      :disabled="disabled"
      :sortable="{ forceFallback: true }"
      @upload="handleUpload"
      @retry="uploadItem"
      @remove="handleRemove"
      @editUpload="handleEditUpload"
    />
    <div style="display: flex; align-items: center; margin-top: 12px">
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        提交
      </el-button>
      <div style="line-height: 22px; margin-left: 22px">禁用:</div>
      <div style="flex: 1; padding-left: 12px">
        <el-radio-group v-model="disabled">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </div>
    </div>
    <div style="margin-top: 20px">
      默认选择文件后就会调用请求后端上传的方法，也可以改为在点击提交按钮后才上传
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    UploadItem,
    EditUploadResult
  } from 'ele-admin-plus/es/ele-upload-list/types';

  /** 数据 */
  const images = ref<UploadItem[]>([
    // 回显已上传的文件数据
    {
      key: 1,
      url: 'https://cdn.eleadmin.com/20200609/b6a811873e704db49db994053a5019b2.jpg',
      status: 'done'
    },
    {
      key: 2,
      url: 'https://cdn.eleadmin.com/20200609/fe9196dd091e438fba115205c1003ee7.jpg',
      status: 'done'
    },
    {
      key: 3,
      url: 'https://cdn.eleadmin.com/20200609/0bfaa58e801b47fb9f56dcb128206d94.jpg',
      status: 'done'
    }
  ]);

  /** 是否禁用 */
  const disabled = ref(false);

  /** 上传状态 */
  const loading = ref(false);

  /** 校验选择的文件 */
  const checkFile = (file?: File) => {
    if (!file) {
      return;
    }
    if (!file.type.startsWith('image')) {
      EleMessage.error({ message: '只能选择图片', plain: true });
      return;
    }
    if (file.size / 1024 / 1024 > 2) {
      EleMessage.error({ message: '大小不能超过 2MB', plain: true });
      return;
    }
    return true;
  };

  /** 上传事件, 只添加, 不请求后台 */
  const handleUpload = (item: UploadItem) => {
    if (!checkFile(item.file)) {
      return;
    }
    images.value.push({ ...item });
  };

  /** 修改事件, 只修改, 不请求后台 */
  const handleEditUpload = ({ item, newItem }: EditUploadResult) => {
    if (!checkFile(newItem.file)) {
      return;
    }
    const oldItem = images.value.find((t) => t.key === item.key);
    if (oldItem) {
      oldItem.url = void 0; // 已上传回显的文件清空地址
      oldItem.name = newItem.name;
      oldItem.file = newItem.file;
      oldItem.status = void 0; // 已上传回显的文件重置上传状态
      oldItem.progress = 0;
    }
  };

  /** 删除事件 */
  const handleRemove = (item: UploadItem) => {
    ElMessageBox.confirm('确定要删除吗?', '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        images.value.splice(images.value.indexOf(item), 1);
      })
      .catch(() => {});
  };

  /** 手动上传 */
  const handleSubmit = () => {
    if (checkDone()) {
      submitForm();
      return;
    }
    loading.value = true;
    images.value.forEach((item) => {
      if (item.status == null || item.status === 'exception') {
        uploadItem(item);
      }
    });
  };

  /** 请求后台上传 */
  const uploadItem = (item: UploadItem) => {
    // 模拟上传
    item.status = 'uploading';
    if (item.progress == null) {
      item.progress = 20;
    }
    const timer = setInterval(
      () => {
        if (Math.round(Math.random() * 10) < 3) {
          item.status = 'exception';
          EleMessage.error({
            message: '上传失败, 服务器繁忙，请重试',
            plain: true
          });
          clearInterval(timer);
          return;
        }
        if (item.progress == null) {
          item.progress = 20;
        } else {
          item.progress += 20;
        }
        if (item.progress === 100) {
          item.status = 'done';
          clearInterval(timer);
          // 每个图片上传完成后都检查是否全部上传完成
          if (checkDone()) {
            submitForm();
          }
        }
      },
      Math.round(Math.random() * 2500) + 500
    );
  };

  /** 检查是否全部上传完毕 */
  const checkDone = () => {
    return !images.value.some((d) => d.status !== 'done');
  };

  /** 全部上传完毕后与其它表单数据一起提交 */
  const submitForm = () => {
    EleMessage.success({ message: '已全部上传完毕', plain: true });
    console.log(JSON.parse(JSON.stringify(images.value)));
    loading.value = false;
  };
</script>
