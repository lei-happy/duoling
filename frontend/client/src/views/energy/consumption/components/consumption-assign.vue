<template>
  <el-dialog
    title="人工归属"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <p class="form-tip">把这条消费补到车辆、司机或能源账户上，方便后续对账和算成本。</p>
    <el-form
      :model="form"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item>
        <floating-label
          v-model="form.vehicleId"
          label="请选择车辆"
          type="select"
          filterable
          clearable
        >
          <el-option
            v-for="v in vehicles"
            :key="v.id"
            :label="v.plateNumber"
            :value="v.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.driverId"
          label="请选择司机"
          type="select"
          filterable
          clearable
        >
          <el-option
            v-for="d in drivers"
            :key="d.id"
            :label="d.name"
            :value="d.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.accountId"
          label="请选择能源账户"
          type="select"
          filterable
          clearable
        >
          <el-option
            v-for="a in accounts"
            :key="a.id"
            :label="a.accountName"
            :value="a.id"
          />
        </floating-label>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确认归属
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { assignConsumption } from '@/api/energy';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
    accounts: Array<Record<string, any>>;
    vehicles: Array<Record<string, any>>;
    drivers: Array<Record<string, any>>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        vehicleId: undefined,
        driverId: undefined,
        accountId: props.data?.accountId
      });
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = async () => {
    if (!form.id) return;
    loading.value = true;
    try {
      await assignConsumption(form.id, form);
      EleMessage.success({ message: '已归属', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '归属失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };
</script>

<style scoped>
  .form-tip {
    margin: 0 0 16px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.7;
  }

  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
