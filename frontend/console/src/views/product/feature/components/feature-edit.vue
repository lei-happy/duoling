<template>
  <ele-modal
    form
    :width="600"
    :title="isUpdate ? '修改功能模块' : '添加功能模块'"
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
      <el-form-item label="功能编码" prop="featureCode">
        <el-input
          clearable
          :maxlength="50"
          v-model="form.featureCode"
          :disabled="isUpdate"
          placeholder="如 resource_fuel_card"
        />
      </el-form-item>
      <el-form-item label="功能名称" prop="featureName">
        <el-input
          clearable
          :maxlength="100"
          v-model="form.featureName"
          placeholder="请输入功能名称"
        />
      </el-form-item>
      <el-form-item label="所属模块" prop="module">
        <el-select
          v-model="form.module"
          placeholder="请选择所属模块"
          clearable
          filterable
          allow-create
          class="ele-fluid"
        >
          <el-option
            v-for="item in moduleDicts"
            :key="item.dictDataCode"
            :label="item.dictDataName"
            :value="item.dictDataCode"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="功能描述" prop="description">
        <el-input
          :rows="3"
          type="textarea"
          v-model="form.description"
          placeholder="请输入功能描述"
        />
      </el-form-item>
      <el-form-item label="关联数据表" prop="requiredTables">
        <el-select
          v-model="form.requiredTables"
          placeholder="输入表名后回车添加"
          clearable
          filterable
          allow-create
          multiple
          default-first-option
          class="ele-fluid"
          :reserve-keyword="false"
        >
        </el-select>
      </el-form-item>
      <el-row :gutter="16">
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
        <el-col :span="12">
          <el-form-item label="状态" prop="status" v-if="isUpdate">
            <el-radio-group v-model="form.status">
              <el-radio :value="1">正常</el-radio>
              <el-radio :value="0">停用</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>
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
  import { addFeature, updateFeature } from '@/api/product';
  import { useDictData } from '@/utils/use-dict-data';
  import { DICT_CODE_PRODUCT_MODULE } from '@/api/product/model';
  import type { ProductFeature } from '@/api/product/model';

  const [moduleDicts] = useDictData([DICT_CODE_PRODUCT_MODULE]);

  const props = defineProps<{
    data?: ProductFeature | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData<ProductFeature>({
    id: void 0,
    featureCode: '',
    featureName: '',
    module: void 0,
    description: '',
    requiredTables: [],
    sortOrder: 0,
    status: 1
  });

  const rules = reactive<FormRules>({
    featureCode: [
      {
        required: true,
        message: '请输入功能编码',
        type: 'string',
        trigger: 'blur'
      }
    ],
    featureName: [
      {
        required: true,
        message: '请输入功能名称',
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
        ? () => updateFeature(form)
        : () =>
            addFeature({
              featureCode: form.featureCode,
              featureName: form.featureName,
              module: form.module,
              description: form.description,
              requiredTables: form.requiredTables,
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
