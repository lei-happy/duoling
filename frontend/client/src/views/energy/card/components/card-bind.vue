<template>
  <el-dialog
    title="绑定车辆 / 司机"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="card" class="bind-identity">
      <div class="bind-identity__name">卡号 {{ card.cardNo }}</div>
      <div class="bind-identity__meta">
        {{ card.accountName || '未关联账户' }}
      </div>
    </div>
    <p class="form-tip">
      绑定会记下开始时间。以后改绑不会覆盖历史，三个月前的消费仍能还原当时绑的是谁。
    </p>
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
            :label="`${d.name || '未命名'}${d.phone ? ' · ' + d.phone : ''}`"
            :value="d.id"
          />
        </floating-label>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确认绑定
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { bindCard } from '@/api/energy';

  const props = defineProps<{
    visible: boolean;
    card: Record<string, any> | null;
    vehicles: Array<Record<string, any>>;
    drivers: Array<Record<string, any>>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const form = reactive<{ vehicleId?: number; driverId?: number }>({});

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        vehicleId: props.card?.vehicleId,
        driverId: props.card?.driverId
      });
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = async () => {
    if (!form.vehicleId && !form.driverId) {
      EleMessage.error({ message: '请至少选择车辆或司机', plain: true });
      return;
    }
    if (!props.card?.id) return;
    loading.value = true;
    try {
      await bindCard(props.card.id, {
        vehicleId: form.vehicleId,
        driverId: form.driverId
      });
      EleMessage.success({ message: '已绑定', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '绑定失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };
</script>

<style scoped>
  .bind-identity {
    margin-bottom: 12px;
    padding: 12px 14px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .bind-identity__name {
    font-weight: 600;
  }

  .bind-identity__meta {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

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
