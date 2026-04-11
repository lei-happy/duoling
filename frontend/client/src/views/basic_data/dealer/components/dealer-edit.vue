<template>
  <ele-modal
    form
    :width="520"
    :title="isUpdate ? '修改经销商' : '添加经销商'"
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
      <el-form-item label="名称" prop="dealerName">
        <el-input v-model.trim="form.dealerName" maxlength="100" clearable />
      </el-form-item>
      <el-form-item label="类型" prop="dealerType">
        <el-input v-model.trim="form.dealerType" maxlength="50" clearable />
      </el-form-item>
      <el-form-item label="主营品牌" prop="mainBrand">
        <el-input v-model.trim="form.mainBrand" maxlength="100" clearable />
      </el-form-item>
      <el-form-item label="省" prop="province">
        <el-input v-model.trim="form.province" maxlength="50" clearable />
      </el-form-item>
      <el-form-item label="市" prop="city">
        <el-input v-model.trim="form.city" maxlength="50" clearable />
      </el-form-item>
      <el-form-item label="详细地址" prop="addressDetail">
        <el-input v-model.trim="form.addressDetail" maxlength="255" clearable />
      </el-form-item>
      <el-form-item label="经度" prop="longitude">
        <el-input-number
          v-model="form.longitude"
          :precision="6"
          :step="0.000001"
          :controls="false"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="纬度" prop="latitude">
        <el-input-number
          v-model="form.latitude"
          :precision="6"
          :step="0.000001"
          :controls="false"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => handleSave() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import { addDealer, updateDealer } from '@/api/basic-data/dealer';
  import type { Dealer } from '@/api/basic-data/dealer/model';

  const props = defineProps<{
    data?: Dealer | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData({
    dealerId: void 0 as number | undefined,
    dealerName: '',
    dealerType: '',
    mainBrand: '',
    province: '',
    city: '',
    addressDetail: '',
    longitude: undefined as number | undefined,
    latitude: undefined as number | undefined
  });

  const rules: FormRules = {
    dealerName: [{ required: true, message: '请输入名称', trigger: 'blur' }],
    dealerType: [{ required: true, message: '请输入类型', trigger: 'blur' }],
    mainBrand: [{ required: true, message: '请输入主营品牌', trigger: 'blur' }],
    province: [{ required: true, message: '请输入省', trigger: 'blur' }],
    city: [{ required: true, message: '请输入市', trigger: 'blur' }],
    addressDetail: [
      { required: true, message: '请输入详细地址', trigger: 'blur' }
    ]
  };

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;

      const promise = isUpdate.value
        ? updateDealer(form.dealerId!, {
            dealerName: form.dealerName,
            dealerType: form.dealerType,
            mainBrand: form.mainBrand,
            province: form.province,
            city: form.city,
            addressDetail: form.addressDetail,
            longitude: form.longitude,
            latitude: form.latitude
          })
        : addDealer({
            dealerName: form.dealerName,
            dealerType: form.dealerType,
            mainBrand: form.mainBrand,
            province: form.province,
            city: form.city,
            addressDetail: form.addressDetail,
            longitude: form.longitude,
            latitude: form.latitude
          });

      promise
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
    assignFields({
      dealerId: props.data.dealerId,
      dealerName: props.data.dealerName ?? '',
      dealerType: props.data.dealerType ?? '',
      mainBrand: props.data.mainBrand ?? '',
      province: props.data.province ?? '',
      city: props.data.city ?? '',
      addressDetail: props.data.addressDetail ?? '',
      longitude: props.data.longitude ?? undefined,
      latitude: props.data.latitude ?? undefined
    });
    isUpdate.value = true;
  }
</script>
