<template>
  <el-dialog
    :title="isEdit ? '编辑能源卡' : '新增能源卡'"
    :model-value="visible"
    width="720px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item prop="accountId">
            <floating-label
              v-model="form.accountId"
              label="请选择所属账户"
              type="select"
              filterable
              :clearable="false"
              :disabled="isEdit"
            >
              <el-option
                v-for="a in accounts"
                :key="a.id"
                :label="`${a.accountName}（${a.accountCode}）`"
                :value="a.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="cardNo">
            <floating-label
              label="请输入卡号"
              type="input"
              v-model.trim="form.cardNo"
              :disabled="isEdit"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.cardType"
              label="请选择卡类型"
              type="select"
              clearable
            >
              <el-option
                v-for="o in CARD_TYPES"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.energyType"
              label="请选择能源类型"
              type="select"
              clearable
            >
              <el-option
                v-for="o in ENERGY_TYPES"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col v-if="isEdit" :span="12">
          <el-form-item>
            <floating-label
              v-model="form.status"
              label="请选择卡状态"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in CARD_STATUSES"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
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
  import { computed, nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addCard, updateCard } from '@/api/energy';
  import { CARD_STATUSES, CARD_TYPES, ENERGY_TYPES } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
    accounts: Array<Record<string, any>>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  const rules = reactive<FormRules>({
    accountId: [
      { required: true, message: '请选择所属账户', trigger: 'change' }
    ],
    cardNo: [{ required: true, message: '请输入卡号', trigger: 'blur' }]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        accountId: props.data?.accountId,
        cardNo: props.data?.cardNo || '',
        cardType: props.data?.cardType || '实体卡',
        energyType: props.data?.energyType || 'OIL',
        status: props.data?.status ?? 1,
        remark: props.data?.remark || ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        if (isEdit.value) await updateCard(form.id, form);
        else await addCard(form);
        EleMessage.success({
          message: isEdit.value ? '已保存能源卡' : '已新增能源卡',
          plain: true
        });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        if (e?.message) EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
