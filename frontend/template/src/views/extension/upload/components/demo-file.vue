<template>
  <ele-card header="附件上传">
    <div style="margin-bottom: 24px">
      不仅仅能用于图片上传的场景, 还可用于文件上传的场景
    </div>
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
      <el-form-item label="附件" prop="files">
        <file-upload ref="filesUploadRef" :limit="8" v-model="form.files" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save">提交</el-button>
        <el-button type="primary" @click="setData">回显数据</el-button>
      </el-form-item>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import FileUpload from '@/components/FileUpload/index.vue';

  interface User {
    id?: number;
    content?: string;
    files?: string;
  }

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, _resetFields, assignFields] = useFormData<User>({
    id: void 0,
    content: '',
    /** 附件 */
    files: ''
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
    files: [
      {
        required: true,
        message: '请上传现场附件',
        type: 'string',
        trigger: 'change'
      },
      {
        type: 'string',
        trigger: 'change',
        validator: (_rule: any, _value: string, callback: any) => {
          if (!filesUploadRef.value?.isDone?.()) {
            return callback(new Error('现场附件还未上传完毕'));
          }
          callback();
        }
      }
    ]
  });

  /** 现场附件上传组件 */
  const filesUploadRef = ref<InstanceType<typeof FileUpload> | null>(null);

  /** 保存编辑 */
  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      console.log(JSON.parse(JSON.stringify(form)));
      EleMessage.success({ message: '数据已打印在控制台', plain: true });
    });
  };

  /** 回显数据 */
  const setData = async () => {
    filesUploadRef.value?.clearData?.();
    await nextTick();
    const data: User = {
      id: 1,
      content: '2栋楼下的路灯已经坏了几天了都没人来维修一下',
      files:
        '[{"url":"https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg","name":"c184eef391ae48dba87e3057e70238fb.jpg"},{"url":"https://cdn.eleadmin.com/20200610/WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg","name":"WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg"},{"url":"https://cdn.eleadmin.com/20200610/20200708224450.pdf","name":"20200708224450.pdf"}]'
    };
    assignFields(data);
    formRef.value?.clearValidate?.();
  };
</script>
