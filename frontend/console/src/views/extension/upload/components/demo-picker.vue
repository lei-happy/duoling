<template>
  <ele-card header="调用文件选择器">
    <div style="margin-bottom: 12px">
      可自定义上传按钮和修改按钮的逻辑，例如弹出文件选择弹窗进行选择。
    </div>
    <ele-upload-list
      :drag="true"
      :tools="true"
      :limit="limit"
      :multiple="true"
      v-model="images"
      :sortable="{ forceFallback: true }"
      :beforeUploadClick="beforeUploadClick"
      :beforeItemEdit="beforeItemEdit"
      @upload="handleUpload"
      @retry="(item) => handleUpload(item, true)"
      @remove="handleRemove"
    />
    <div style="display: flex; align-items: center; margin-top: 12px">
      <el-button type="primary" @click="getData" class="ele-btn-icon">
        获取数据
      </el-button>
    </div>
    <file-picker
      title="图片选择"
      :fileLimit="2"
      accept="image/*"
      :params="{ contentType: 'image/' }"
      v-model="showFilePicker"
      :limit="filePickerLimit"
      @done="handleFilePickerDone"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { UploadItem } from 'ele-admin-plus/es/ele-upload-list/types';
  import FilePicker from '@/components/FilePicker/index.vue';
  import type { UserFile } from '@/api/system/user-file/model';

  /** 已上传数据 */
  const images = ref<UploadItem[]>([
    // 回显已上传的文件数据
    {
      key: '001',
      name: 'c184eef391ae48dba87e3057e70238fb.jpg',
      url: 'https://cdn.eleadmin.com/20200609/8931360b593040238d894a542c9037bc.jpg',
      status: 'done'
    },
    {
      key: '002',
      name: 'WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg',
      url: 'https://cdn.eleadmin.com/20200609/4e60a84551fa48439bf42ecdb9673331.jpg',
      status: 'done'
    },
    {
      key: '003',
      name: 'f6bc05af944a4f738b54128717952107.jpg',
      url: 'https://cdn.eleadmin.com/20200609/d6442cfa99b64b51aabfc470055b05dc.jpg',
      status: 'done'
    }
  ]);

  /** 最大文件数量 */
  const limit = ref(8);

  /** 是否打开文件选择弹窗 */
  const showFilePicker = ref(false);

  /** 文件选择弹窗的最大选择数量 */
  const filePickerLimit = ref(1);

  /** 当前修改的文件项 */
  let currentEditItem: UploadItem | null = null;

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

  /** 删除事件 */
  const handleRemove = (item: UploadItem) => {
    images.value.splice(images.value.indexOf(item), 1);
  };

  /** 上传按钮点击打开文件选择弹窗 */
  const beforeUploadClick = () => {
    filePickerLimit.value = limit.value - images.value.length;
    showFilePicker.value = true;
    currentEditItem = null;
    return false;
  };

  /** 修改按钮点击打开文件选择弹窗 */
  const beforeItemEdit = (item: UploadItem) => {
    filePickerLimit.value = 1;
    showFilePicker.value = true;
    currentEditItem = item;
    return false;
  };

  /** 文件选择弹窗选择完成事件 */
  const handleFilePickerDone = (files: UserFile[]) => {
    showFilePicker.value = false;
    // 添加
    if (currentEditItem == null) {
      files.forEach((fileItem) => {
        images.value.push({
          key: String(Date.now()) + fileItem.id,
          name: fileItem.name,
          url: fileItem.url,
          status: 'done'
        });
      });
      return;
    }
    // 修改
    const oldItem = images.value.find((t) => t.key === currentEditItem?.key);
    if (oldItem && files.length) {
      const fileItem = files[0];
      oldItem.name = fileItem.name;
      oldItem.url = fileItem.url;
      oldItem.status = 'done';
    }
  };
</script>
