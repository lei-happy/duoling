<template>
  <div class="item-table">
    <div class="item-table__title">
      <span>
        费用项明细（合计：
        <span style="color: var(--el-color-primary); font-weight: 600">
          ¥ {{ totalAmount.toFixed(2) }}
        </span>
        ）
      </span>
      <el-button
        v-if="!disabled"
        type="primary"
        link
        :icon="Plus"
        @click="addRow"
      >
        新增费用项
      </el-button>
    </div>
    <el-table :data="modelValue" border size="small" empty-text="请添加费用项">
      <el-table-column label="项目" min-width="150">
        <template #default="{ row }">
          <el-select
            v-model="row.itemType"
            placeholder="选择"
            :disabled="disabled"
            @change="(v: string) => onTypeChange(row, v)"
          >
            <el-option
              v-for="o in EXPENSE_TYPE_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="数量" width="110">
        <template #default="{ row }">
          <el-input-number
            v-model="row.quantity"
            :min="0"
            :precision="2"
            :disabled="disabled"
            controls-position="right"
            size="small"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="单位" width="90">
        <template #default="{ row }">
          <el-input v-model="row.unit" :disabled="disabled" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="单价" width="110">
        <template #default="{ row }">
          <el-input-number
            v-model="row.unitPrice"
            :min="0"
            :precision="2"
            :disabled="disabled"
            controls-position="right"
            size="small"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="金额" width="130">
        <template #default="{ row }">
          <el-input-number
            v-model="row.amount"
            :min="0.01"
            :precision="2"
            :disabled="disabled"
            controls-position="right"
            size="small"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="160">
        <template #default="{ row }">
          <el-input v-model="row.remark" :disabled="disabled" size="small" />
        </template>
      </el-table-column>
      <el-table-column v-if="!disabled" label="操作" width="60" align="center">
        <template #default="{ $index }">
          <el-button type="danger" link @click="removeRow($index)">
            移除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
  import { computed, watch } from 'vue';
  import { Plus } from '@element-plus/icons-vue';
  import type { TaskFinanceItem } from '@/api/operation/task-finance/model';
  import { EXPENSE_TYPE_OPTIONS } from '../status-config';

  const props = defineProps<{
    modelValue: TaskFinanceItem[];
    disabled?: boolean;
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: TaskFinanceItem[]): void;
    (e: 'total-change', total: number): void;
  }>();

  const addRow = () => {
    emit('update:modelValue', [
      ...props.modelValue,
      {
        itemType: 'oil',
        itemName: '油费',
        quantity: undefined,
        unit: '',
        unitPrice: undefined,
        amount: 0,
        sortOrder: props.modelValue.length
      }
    ]);
  };

  const removeRow = (idx: number) => {
    const next = [...props.modelValue];
    next.splice(idx, 1);
    emit('update:modelValue', next);
  };

  const onTypeChange = (row: TaskFinanceItem, v: string) => {
    const opt = EXPENSE_TYPE_OPTIONS.find((o) => o.value === v);
    row.itemName = opt?.label || '';
  };

  const totalAmount = computed(() =>
    props.modelValue.reduce((s, x) => s + (Number(x.amount) || 0), 0)
  );

  watch(totalAmount, (v) => emit('total-change', v));
</script>

<style lang="scss" scoped>
  .item-table {
    &__title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
  }
</style>
