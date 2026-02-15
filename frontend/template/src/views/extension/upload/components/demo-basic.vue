<template>
  <ele-card header="基础示例">
    <ele-upload-list
      :limit="8"
      :drag="true"
      :tools="true"
      v-model="images"
      :readonly="readonly"
      :sortable="{ forceFallback: true }"
      @upload="handleUpload"
      @retry="(item) => handleUpload(item, true)"
      @remove="handleRemove"
      @editUpload="handleEditUpload"
    />
    <div style="display: flex; align-items: center; margin-top: 12px">
      <el-button type="primary" @click="getData">获取数据</el-button>
      <div style="line-height: 22px; margin-left: 22px">只读:</div>
      <div style="flex: 1; padding-left: 12px">
        <el-radio-group v-model="readonly">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </div>
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

  /** 数据 */
  const images = ref<UploadItem[]>([
    // 回显已上传的文件数据
    {
      key: 1,
      name: 'c184eef391ae48dba87e3057e70238fb.jpg',
      url: 'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg',
      status: 'done'
    },
    {
      key: 2,
      name: 'WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg',
      url: 'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg',
      status: 'done'
    },
    {
      key: 3,
      name: 'f6bc05af944a4f738b54128717952107.jpg',
      url: 'https://cdn.eleadmin.com/20200609/2d98970a51b34b6b859339c96b240dcd.jpg',
      status: 'done'
    }
  ]);

  /** 只读 */
  const readonly = ref(false);

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
