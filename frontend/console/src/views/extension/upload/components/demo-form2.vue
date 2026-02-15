<template>
  <ele-card header="使用案例二">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      style="max-width: 380px"
      @submit.prevent=""
    >
      <el-form-item label="真实姓名" prop="realName">
        <el-input
          clearable
          :maxlength="20"
          v-model="form.realName"
          placeholder="请输入真实姓名"
        />
      </el-form-item>
      <el-form-item label="身份证号" prop="idCard">
        <el-input
          clearable
          :maxlength="20"
          v-model="form.idCard"
          placeholder="请输入身份证号"
        />
      </el-form-item>
      <el-form-item label="身份证正面" prop="idCardImg1">
        <ele-upload-list
          :limit="1"
          :drag="true"
          :tools="true"
          :sortable="false"
          v-model="form.idCardImg1"
          :item-style="{
            width: '260px',
            height: '163px',
            background: 'var(--el-fill-color-lighter)',
            '--ele-upload-list-padding': 0
          }"
          :button-style="{ width: '260px', height: '163px' }"
          @upload="(item) => handleUpload(0, item)"
          @retry="(item) => handleUpload(0, item, true)"
          @remove="(item) => handleRemove(0, item)"
          @editUpload="(data) => handleEditUpload(0, data)"
        />
      </el-form-item>
      <el-form-item label="身份证反面" prop="idCardImg2">
        <ele-upload-list
          :limit="1"
          :drag="true"
          :tools="true"
          :sortable="false"
          v-model="form.idCardImg2"
          :item-style="{
            width: '260px',
            height: '163px',
            background: 'var(--el-fill-color-lighter)',
            '--ele-upload-list-padding': 0
          }"
          :button-style="{ width: '260px', height: '163px' }"
          @upload="(item) => handleUpload(1, item)"
          @retry="(item) => handleUpload(1, item, true)"
          @remove="(item) => handleRemove(1, item)"
          @editUpload="(data) => handleEditUpload(1, data)"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save">提交</el-button>
        <el-button type="primary" @click="setData">回显数据</el-button>
      </el-form-item>
    </el-form>
    <div style="padding-top: 8px">
      可以很方便的修改宽高等样式，单选的时候使用也非常的方便
    </div>
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

  interface User {
    id?: number;
    realName?: string;
    idCard?: string;
    idCardImg1?: string;
    idCardImg2?: string;
  }

  interface UserForm extends Omit<User, 'idCardImg1' | 'idCardImg2'> {
    idCardImg1: UploadItem[];
    idCardImg2: UploadItem[];
  }

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, _resetFields, assignFields] = useFormData<UserForm>({
    id: void 0,
    realName: '',
    idCard: '',
    /** 身份证正面 */
    idCardImg1: [],
    /** 身份证反面 */
    idCardImg2: []
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    realName: [
      {
        required: true,
        message: '请输入真实姓名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    idCard: [
      {
        required: true,
        message: '请输入身份证号',
        type: 'string',
        trigger: 'blur'
      }
    ],
    idCardImg1: [
      {
        required: true,
        message: '请上传身份证正面',
        type: 'array',
        trigger: 'change'
      },
      {
        type: 'array',
        trigger: 'change',
        validator: (_rule, value, callback) => {
          if (value && value.some((d: UploadItem) => d.status !== 'done')) {
            return callback(new Error('身份证正面还未上传完毕'));
          }
          callback();
        }
      }
    ],
    idCardImg2: [
      {
        required: true,
        message: '请上传身份证反面',
        type: 'array',
        trigger: 'change'
      },
      {
        type: 'array',
        trigger: 'change',
        validator: (_rule, value, callback) => {
          if (value && value.some((d: UploadItem) => d.status !== 'done')) {
            return callback(new Error('身份证反面还未上传完毕'));
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
      const data: User = {
        ...form,
        // 上传组件的数据格式转为字符串
        idCardImg1: form.idCardImg1.map((d) => d.url).join(),
        idCardImg2: form.idCardImg2.map((d) => d.url).join()
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
  const handleUpload = (type: number, data: UploadItem, retry?: boolean) => {
    if (!data.file || !checkFile(data.file)) {
      return;
    }
    if (!retry) {
      (type === 1 ? form.idCardImg2 : form.idCardImg1).push({ ...data }); // 上传时添加数据, 失败重试时不添加
    }
    const item = (type === 1 ? form.idCardImg2 : form.idCardImg1).find(
      (t) => t.key === data.key
    );
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
        formRef.value?.clearValidate?.([
          type === 1 ? 'idCardImg2' : 'idCardImg1'
        ]);
      })
      .catch((e) => {
        item.status = 'exception';
        EleMessage.error({ message: e.message, plain: true });
        formRef.value
          ?.validateField?.([type === 1 ? 'idCardImg2' : 'idCardImg1'])
          .catch(() => {});
      });
  };

  /** 修改事件 */
  const handleEditUpload = (
    type: number,
    { item, newItem }: EditUploadResult
  ) => {
    if (!checkFile(newItem.file)) {
      return;
    }
    const oldItem = (type === 1 ? form.idCardImg2 : form.idCardImg1).find(
      (t) => t.key === item.key
    );
    if (oldItem) {
      oldItem.url = void 0;
      oldItem.name = newItem.name;
      oldItem.file = newItem.file;
      oldItem.progress = 0;
      handleUpload(type, oldItem, true);
    }
  };

  /** 删除事件 */
  const handleRemove = (type: number, item: UploadItem) => {
    const temp = type === 1 ? form.idCardImg2 : form.idCardImg1;
    temp.splice(temp.indexOf(item), 1);
    formRef.value
      ?.validateField?.([type === 1 ? 'idCardImg2' : 'idCardImg1'])
      .catch(() => {});
  };

  /** 回显数据 */
  const setData = () => {
    const data: User = {
      id: 1,
      realName: '张三',
      idCard: '420111200001013807',
      idCardImg1:
        'https://cdn.eleadmin.com/20200610/CyrCNmTJfv7D6GFAg39bjT3eRkkRm5dI.jpg',
      idCardImg2:
        'https://cdn.eleadmin.com/20200610/ttkIjNPlVDuv4lUTvRX8GIlM2QqSe0jg.jpg'
    };
    // 图片url转为上传组件需要的格式
    const idCardImg1 = data.idCardImg1
      ? [{ key: 1, url: data.idCardImg1, status: 'done' }]
      : [];
    const idCardImg2 = data.idCardImg2
      ? [{ key: 1, url: data.idCardImg2, status: 'done' }]
      : [];
    assignFields({
      ...data,
      idCardImg1,
      idCardImg2
    });
    formRef.value?.clearValidate?.();
  };
</script>
