<template>
  <ele-card header="支持多选">
    <div style="margin-bottom: 12px">
      点击上传按钮后可以一次选多个文件添加。
    </div>
    <ele-upload-list
      :limit="8"
      :drag="true"
      :tools="true"
      :multiple="true"
      v-model="images"
      :listType="listType"
      :sortable="{ forceFallback: true }"
      :style="{ maxWidth: listType === 'file' ? '460px' : void 0 }"
      @upload="handleUpload"
      @retry="(item) => handleUpload(item, true)"
      @remove="handleRemove"
      @editUpload="handleEditUpload"
    />
    <div style="display: flex; align-items: center; margin-top: 12px">
      <el-button type="primary" @click="getData" class="ele-btn-icon">
        获取数据
      </el-button>
      <div style="line-height: 22px; margin-left: 18px">显示模式:</div>
      <div style="flex: 1; padding-left: 8px">
        <el-radio-group v-model="listType">
          <el-radio value="image" label="相册" />
          <el-radio value="file" label="列表" />
        </el-radio-group>
      </div>
    </div>
    <div style="margin-top: 12px">
      用于文件上传的场景可以将显示模式改为列表模式更友好。
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    UploadItem,
    EditUploadResult
  } from 'ele-admin-plus/es/ele-upload-list/types';

  /** 已上传数据 */
  const images = ref<UploadItem[]>([
    // 回显已上传的文件数据
    {
      key: 1,
      name: 'c184eef391ae48dba87e3057e70238fb.jpg',
      url: 'https://cdn.eleadmin.com/20200609/e36594e7423147748b2592ccb720ae9e.jpg',
      status: 'done'
    },
    {
      key: 2,
      name: 'WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg',
      url: 'https://cdn.eleadmin.com/20200609/be7dc0c24fc342fda44e12a2c2a2b7bb.jpg',
      status: 'done'
    },
    {
      key: 3,
      name: 'f6bc05af944a4f738b54128717952107.jpg',
      url: 'https://cdn.eleadmin.com/20200609/66e6f6c60cfa44b288d6343027b544d0.jpg',
      status: 'done'
    }
  ]);

  /** 显示模式 */
  const listType = ref<'image' | 'file'>('image');

  /** 获取当前数据 */
  const getData = () => {
    console.log(JSON.parse(JSON.stringify(images.value)));
    EleMessage.success({ message: '数据已打印在控制台', plain: true });
  };

  /** 校验选择的文件 */
  const checkFile = (file?: File) => {
    if (!file) {
      return;
    }
    if (file.size / 1024 / 1024 > 20) {
      EleMessage.error({ message: '大小不能超过 20MB', plain: true });
      return;
    }
    return true;
  };

  /** 上传事件 */
  const handleUpload = (data: UploadItem, retry?: boolean) => {
    if (!checkFile(data.file)) {
      return;
    }
    if (!retry) {
      images.value.push({ ...data }); // 上传时添加数据, 失败重试时不添加
    }
    const item = images.value.find((t) => t.key === data.key);
    console.log(JSON.parse(JSON.stringify(item)));
    if (!item) {
      return;
    }
    // 模拟上传
    item.status = 'uploading';
    if (item.progress == null) {
      item.progress = 20;
    }
    const timer = setInterval(() => {
      if (Math.round(Math.random() * 10) < 3) {
        item.status = 'exception';
        EleMessage.error({ message: '上传失败, 服务器繁忙', plain: true });
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
      }
    }, 1000);
  };

  /** 修改事件 */
  const handleEditUpload = ({ item, newItem }: EditUploadResult) => {
    if (!checkFile(newItem.file)) {
      return;
    }
    const oldItem = images.value.find((t) => t.key === item.key);
    if (oldItem) {
      oldItem.url = void 0;
      oldItem.name = newItem.name;
      oldItem.file = newItem.file;
      oldItem.progress = 0;
      handleUpload(oldItem, true);
    }
  };

  /** 删除事件 */
  const handleRemove = (item: UploadItem) => {
    images.value.splice(images.value.indexOf(item), 1);
  };
</script>
