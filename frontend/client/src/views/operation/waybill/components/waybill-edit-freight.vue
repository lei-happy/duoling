<template>
  <div class="waybill-edit-step waybill-edit-step--freight">
    <template v-if="freightCalcMode !== 'auto_required'">
      <el-row :gutter="12" align="middle">
        <el-col :xs="24" :sm="10" :md="8">
          <el-form-item prop="freightAmount">
            <floating-label
              label="请输入运费金额（元）"
              type="input"
              v-model="freightAmountStrProxy"
              clearable
              @blur="emit('sync-amount')"
            />
          </el-form-item>
        </el-col>
        <el-col
          v-if="freightCalcMode !== 'manual_only'"
          :xs="24"
          :sm="14"
          :md="16"
        >
          <el-form-item :label-width="0" class="waybill-freight-actions">
            <el-button
              type="success"
              :loading="calcLoading"
              @click="emit('calc')"
            >
              计算运费
            </el-button>
            <span v-if="calcHint" class="waybill-calc-hint">{{
              calcHint
            }}</span>
          </el-form-item>
        </el-col>
      </el-row>
    </template>
    <template v-else>
      <p class="waybill-freight-auto-note">
        当前为运费自动必填模式，保存时将按商品车明细逐行匹配运价并汇总。
      </p>
    </template>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';

  const props = defineProps<{
    freightCalcMode: string;
    freightAmountStr: string;
    calcLoading: boolean;
    calcHint: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:freightAmountStr', v: string): void;
    (e: 'sync-amount'): void;
    (e: 'calc'): void;
  }>();

  const freightAmountStrProxy = computed({
    get: () => props.freightAmountStr,
    set: (v: string) => emit('update:freightAmountStr', v ?? '')
  });
</script>

<style scoped>
  .waybill-freight-actions {
    margin-bottom: 8px;
  }

  .waybill-freight-actions :deep(.el-form-item__content) {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .waybill-calc-hint {
    font-size: 12px;
    color: var(--el-color-success);
    line-height: 1.4;
  }

  .waybill-freight-auto-note {
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
  }
</style>
