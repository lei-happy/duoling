<template>
  <ele-modal
    form
    :width="560"
    :title="isUpdate ? '修改产品版本' : '添加产品版本'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent=""
    >
      <el-form-item label="版本编码" prop="versionCode">
        <el-input
          clearable
          :maxlength="50"
          v-model="form.versionCode"
          placeholder="如 free / pro / enterprise"
        />
      </el-form-item>
      <el-form-item label="版本名称" prop="versionName">
        <el-input
          clearable
          :maxlength="100"
          v-model="form.versionName"
          placeholder="请输入版本名称"
        />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          :rows="3"
          type="textarea"
          v-model="form.description"
          placeholder="请输入版本描述"
        />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="最大用户数" prop="maxUsers">
            <el-input-number
              :min="0"
              :max="999999"
              v-model="form.maxUsers"
              controls-position="right"
              class="ele-fluid"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="最大车辆数" prop="maxVehicles">
            <el-input-number
              :min="0"
              :max="999999"
              v-model="form.maxVehicles"
              controls-position="right"
              class="ele-fluid"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="价格" prop="price">
            <el-input
              clearable
              v-model="form.price"
              placeholder="如 0 / 199 / 定制"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="排序号" prop="sortOrder">
            <el-input-number
              :min="0"
              :max="9999"
              v-model="form.sortOrder"
              controls-position="right"
              class="ele-fluid"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="状态" prop="status" v-if="isUpdate">
        <el-radio-group v-model="form.status">
          <el-radio :value="1">正常</el-radio>
          <el-radio :value="0">停用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import { addVersion, updateVersion } from '@/api/product';
  import type { ProductVersion } from '@/api/product/model';

  const props = defineProps<{
    data?: ProductVersion | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);

  const loading = ref(false);

  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData<ProductVersion>({
    id: void 0,
    versionCode: '',
    versionName: '',
    description: '',
    maxUsers: 0,
    maxVehicles: 0,
    price: '',
    sortOrder: 0,
    status: 1
  });

  const rules = reactive<FormRules>({
    versionCode: [
      {
        required: true,
        message: '请输入版本编码',
        type: 'string',
        trigger: 'blur'
      }
    ],
    versionName: [
      {
        required: true,
        message: '请输入版本名称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  const handleCancel = () => {
    closeModal();
  };

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const saveOrUpdate = isUpdate.value
        ? () => updateVersion(form)
        : () =>
            addVersion({
              versionCode: form.versionCode,
              versionName: form.versionName,
              description: form.description,
              maxUsers: form.maxUsers,
              maxVehicles: form.maxVehicles,
              price: form.price,
              sortOrder: form.sortOrder ?? 0
            });
      saveOrUpdate()
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
    });
  };

  if (props.data) {
    assignFields({ ...props.data });
    isUpdate.value = true;
  }
</script>
