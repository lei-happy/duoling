<template>
  <div class="seg-table">
    <div class="seg-table__title">
      <span>运输分段（{{ modelValue.length }} 段）</span>
      <el-button
        type="primary"
        link
        :icon="Plus"
        :disabled="modelValue.length >= 5"
        @click="addRow"
      >
        新增分段
      </el-button>
    </div>
    <el-table
      :data="modelValue"
      border
      size="small"
      empty-text="请至少添加 1 段运输"
    >
      <el-table-column label="段" width="60" align="center">
        <template #default="{ $index }">{{ $index + 1 }}</template>
      </el-table-column>
      <el-table-column label="起点" min-width="180">
        <template #default="{ row }">
          <el-input
            v-model="row.fromLocation"
            placeholder="如：北京市顺义区"
            clearable
          />
        </template>
      </el-table-column>
      <el-table-column label="终点" min-width="180">
        <template #default="{ row }">
          <el-input
            v-model="row.toLocation"
            placeholder="如：上海市浦东新区"
            clearable
          />
        </template>
      </el-table-column>
      <el-table-column label="计划装车" min-width="170">
        <template #default="{ row }">
          <el-date-picker
            v-model="row.plannedLoadTime"
            type="datetime"
            placeholder="选择"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="计划到达" min-width="170">
        <template #default="{ row }">
          <el-date-picker
            v-model="row.plannedArriveTime"
            type="datetime"
            placeholder="选择"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="公里数" width="100">
        <template #default="{ row }">
          <el-input-number
            v-model="row.mileage"
            :min="0"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center">
        <template #default="{ $index }">
          <el-button
            type="primary"
            link
            :disabled="$index === 0"
            @click="move($index, -1)"
          >
            上移
          </el-button>
          <el-button
            type="primary"
            link
            :disabled="$index === modelValue.length - 1"
            @click="move($index, 1)"
          >
            下移
          </el-button>
          <el-button
            type="danger"
            link
            :disabled="modelValue.length <= 1"
            @click="removeRow($index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
  import { Plus } from '@element-plus/icons-vue';
  import type { TaskSegment } from '@/api/operation/task/model';

  const props = defineProps<{
    modelValue: TaskSegment[];
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: TaskSegment[]): void;
  }>();

  const renumber = (arr: TaskSegment[]) =>
    arr.map((s, i) => ({ ...s, segmentNo: i + 1 }));

  const addRow = () => {
    if (props.modelValue.length >= 5) return;
    const last = props.modelValue[props.modelValue.length - 1];
    const next: TaskSegment = {
      segmentNo: props.modelValue.length + 1,
      fromLocation: last?.toLocation || '',
      toLocation: '',
      plannedLoadTime: last?.plannedArriveTime
    };
    emit('update:modelValue', renumber([...props.modelValue, next]));
  };

  const removeRow = (idx: number) => {
    if (props.modelValue.length <= 1) return;
    const next = [...props.modelValue];
    next.splice(idx, 1);
    emit('update:modelValue', renumber(next));
  };

  const move = (idx: number, delta: number) => {
    const targetIdx = idx + delta;
    if (targetIdx < 0 || targetIdx >= props.modelValue.length) return;
    const next = [...props.modelValue];
    const [item] = next.splice(idx, 1);
    next.splice(targetIdx, 0, item);
    emit('update:modelValue', renumber(next));
  };
</script>

<style lang="scss" scoped>
  .seg-table {
    &__title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
  }
</style>
