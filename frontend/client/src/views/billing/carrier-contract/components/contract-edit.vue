<template>
  <el-dialog
    :title="isEdit ? '编辑合同' : '新增合同'"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    class="contract-edit-dialog"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="contract-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="24">
          <el-form-item prop="carrierId">
            <floating-label
              v-model="form.carrierId"
              label="请选择承运商"
              type="select"
              filterable
              clearable
            >
              <el-option
                v-for="item in carrierOptions"
                :key="item.id"
                :label="item.carrierName"
                :value="item.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="contractName">
            <floating-label
              label="请输入合同名称"
              type="input"
              v-model.trim="form.contractName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="contractNo">
            <floating-label
              label="请输入合同编号"
              type="input"
              v-model.trim="form.contractNo"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="contractPeriod">
            <floating-label
              v-model="form.contractPeriod"
              label="请选择有效期"
              type="date"
              date-type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="~"
              start-placeholder="开始"
              end-placeholder="结束"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入备注"
              type="input"
              input-type="textarea"
              v-model="form.remark"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addContract, updateContract } from '@/api/billing/carrier-contract';
  import { selectCarriers } from '@/api/partner/carrier';
  import type { CarrierContract } from '@/api/billing/carrier-contract/model';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';

  type ContractForm = CarrierContract & {
    contractPeriod: [string, string] | null;
  };

  const props = defineProps<{
    visible: boolean;
    data: CarrierContract | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<ContractForm>({
    contractPeriod: null
  });
  const carrierOptions = ref<CarrierSelectItem[]>([]);

  const rules = reactive<FormRules>({
    contractNo: [
      { required: true, message: '请输入合同编号', trigger: 'blur' }
    ],
    contractName: [
      { required: true, message: '请输入合同名称', trigger: 'blur' }
    ],
    carrierId: [{ required: true, message: '请选择承运商', trigger: 'change' }],
    contractPeriod: [
      {
        required: true,
        message: '请选择有效期',
        trigger: 'change'
      },
      {
        validator: (_r, v, cb) => {
          if (!v || !Array.isArray(v) || v.length !== 2 || !v[0] || !v[1]) {
            cb(new Error('请选择有效期'));
            return;
          }
          if (v[0] > v[1]) {
            cb(new Error('结束日期不能早于开始日期'));
            return;
          }
          cb();
        },
        trigger: 'change'
      }
    ]
  });

  const loadCarriers = async () => {
    try {
      carrierOptions.value = (await selectCarriers()) ?? [];
    } catch (_) {
      carrierOptions.value = [];
    }
  };

  function resetFormForCreate() {
    Object.assign(form, {
      id: undefined,
      contractNo: undefined,
      contractName: undefined,
      carrierId: undefined,
      carrierName: undefined,
      effectiveDate: undefined,
      expiryDate: undefined,
      contractPeriod: null,
      remark: undefined
    });
  }

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      loadCarriers();
      if (props.data?.id) {
        Object.assign(form, props.data);
        form.contractPeriod =
          props.data.effectiveDate && props.data.expiryDate
            ? [props.data.effectiveDate, props.data.expiryDate]
            : null;
      } else {
        resetFormForCreate();
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const buildPayload = (): CarrierContract => {
    const period = form.contractPeriod;
    const selected = carrierOptions.value.find((c) => c.id === form.carrierId);
    const payload: CarrierContract = {
      id: form.id,
      contractNo: form.contractNo,
      contractName: form.contractName,
      carrierId: form.carrierId,
      carrierName: selected?.carrierName ?? form.carrierName,
      effectiveDate: period?.[0],
      expiryDate: period?.[1],
      remark: form.remark,
      status: form.status
    };
    return payload;
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const payload = buildPayload();
        if (isEdit.value) {
          await updateContract(payload);
        } else {
          await addContract(payload);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .contract-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>

<style scoped lang="scss">
  .contract-edit-dialog
    :deep(.floating-label-wrapper.is-focused .floating-label),
  .contract-edit-dialog
    :deep(.floating-label-wrapper.has-value .floating-label) {
    color: var(--el-color-primary);
  }
</style>
