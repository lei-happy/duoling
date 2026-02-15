<template>
  <ele-card header="使用案例一">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      style="max-width: 460px"
      @submit.prevent=""
    >
      <el-form-item label="投诉内容" prop="content">
        <el-input
          :rows="4"
          type="textarea"
          v-model="form.content"
          placeholder="请输入投诉内容"
        />
      </el-form-item>
      <el-form-item label="现场照片" prop="images">
        <ele-upload-list
          :limit="3"
          :drag="true"
          :tools="true"
          v-model="form.images"
          :sortable="{ forceFallback: true }"
          @upload="handleUpload"
          @retry="(item) => handleUpload(item, true)"
          @remove="handleRemove"
          @editUpload="handleEditUpload"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save">提交</el-button>
        <el-button type="primary" @click="setData">回显数据</el-button>
      </el-form-item>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { AxiosProgressEvent } from 'axios';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    UploadItem,
    EditUploadResult
  } from 'ele-admin-plus/es/ele-upload-list/types';
  import { useFormData } from '@/utils/use-form-data';
  import { uploadFile } from '@/api/system/file';

  interface Complaint {
    id?: number;
    content?: string;
    images?: string[];
  }

  interface ComplaintForm extends Omit<Complaint, 'images'> {
    images: UploadItem[];
  }

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, _resetFields, assignFields] = useFormData<ComplaintForm>({
    id: void 0,
    content: '',
    /** 现场照片 */
    images: []
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    content: [
      {
        required: true,
        message: '请输入投诉内容',
        type: 'string',
        trigger: 'blur'
      }
    ],
    images: [
      {
        required: true,
        message: '请上传现场照片',
        type: 'array',
        trigger: 'change'
      },
      {
        type: 'array',
        trigger: 'change',
        validator: (_rule, value, callback) => {
          if (value && value.some((d: UploadItem) => d.status !== 'done')) {
            return callback(new Error('现场照片还未上传完毕'));
          }
          callback();
        }
      }
    ]
  });

  /** 保存编辑 */
  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      const data: Complaint = {
        ...form,
        // 上传组件的数据格式转为字符串
        images: form.images.map((d) => d.url as string)
      };
      console.log(JSON.parse(JSON.stringify(data))); // 实际项目用data提交到后台而不是form
      EleMessage.success({ message: '数据已打印在控制台', plain: true });
    });
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
    if (!data.file || !checkFile(data.file)) {
      return;
    }
    if (!retry) {
      form.images.push({ ...data });
    }
    const item = form.images.find((t) => t.key === data.key);
    if (!item) {
      return;
    }
    item.status = 'uploading';
    uploadFile(data.file, {
      onUploadProgress: (e: AxiosProgressEvent) => {
        if (e.total != null) {
          item.progress = (e.loaded / e.total) * 100;
        }
      }
    })
      .then((res) => {
        item.status = 'done';
        item.url = res.url;
        // 上传后清空验证
        formRef.value?.clearValidate?.(['images']);
      })
      .catch((e) => {
        item.status = 'exception';
        EleMessage.error({ message: e.message, plain: true });
        formRef.value?.validateField?.(['images']).catch(() => {});
      });
  };

  /** 修改事件 */
  const handleEditUpload = ({ item, newItem }: EditUploadResult) => {
    if (!checkFile(newItem.file)) {
      return;
    }
    const oldItem = form.images.find((t) => t.key === item.key);
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
    form.images.splice(form.images.indexOf(item), 1);
    formRef.value?.validateField?.(['images']).catch(() => {});
  };

  /** 回显数据 */
  const setData = () => {
    const data: Complaint = {
      id: 1,
      content: '2栋楼下的路灯已经坏了几天了都没人来维修一下',
      images: [
        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg',
        'https://cdn.eleadmin.com/20200610/WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg'
      ]
    };
    // 图片url转为上传组件需要的格式
    const images = data.images
      ? data.images.map((d, i) => {
          return { key: i, url: d, status: 'done' };
        })
      : [];
    assignFields({ ...data, images });
    formRef.value?.clearValidate?.();
  };
</script>
