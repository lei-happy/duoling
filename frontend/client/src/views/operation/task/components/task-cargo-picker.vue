<template>
  <div class="cargo-picker">
    <div class="cargo-picker__panel">
      <div class="cargo-picker__title">
        候选商品车（运单明细）
        <span class="cargo-picker__hint">仅展示剩余可分配台数 &gt; 0</span>
      </div>
      <div class="cargo-picker__filter">
        <el-input
          v-model="filter.keyword"
          placeholder="运单号/客户"
          clearable
          size="small"
          style="width: 200px"
          @change="loadCandidates"
        />
        <el-input
          v-model="filter.originKeyword"
          placeholder="起点"
          clearable
          size="small"
          style="width: 130px"
          @change="loadCandidates"
        />
        <el-input
          v-model="filter.destinationKeyword"
          placeholder="终点"
          clearable
          size="small"
          style="width: 130px"
          @change="loadCandidates"
        />
        <el-button size="small" :icon="Refresh" @click="loadCandidates">
          刷新
        </el-button>
      </div>
      <el-table
        :data="candidates"
        size="small"
        border
        height="320"
        v-loading="loading"
      >
        <el-table-column label="运单号" prop="waybillNo" width="140" />
        <el-table-column label="客户" prop="customerName" min-width="120" />
        <el-table-column label="起→终" min-width="180">
          <template #default="{ row }">
            <span>{{ row.origin || '--' }}</span>
            <el-icon style="margin: 0 4px"><Right /></el-icon>
            <span>{{ row.destination || '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="品牌/车型" min-width="140">
          <template #default="{ row }">
            {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
          </template>
        </el-table-column>
        <el-table-column
          label="原台数"
          prop="quantity"
          width="76"
          align="center"
        />
        <el-table-column label="剩余" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{
              row.remainingQuantity
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              :disabled="isPicked(row)"
              @click="addPick(row)"
            >
              添加
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="cargo-picker__panel">
      <div class="cargo-picker__title">
        已选商品车（{{ modelValue.length }} 项 / {{ totalQuantity }} 台）
        <span class="cargo-picker__hint">支持指定走某段</span>
      </div>
      <el-table
        :data="modelValue"
        size="small"
        border
        height="320"
        empty-text="请从左侧添加商品车"
      >
        <el-table-column label="运单号" prop="waybillNo" width="140" />
        <el-table-column label="品牌/车型" min-width="160">
          <template #default="{ row }">
            {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="本任务台数" width="130" align="center">
          <template #default="{ row, $index }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              :max="getMax(row)"
              :precision="0"
              controls-position="right"
              size="small"
              style="width: 100%"
              @change="syncQuantity($index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="归属段" width="120">
          <template #default="{ row }">
            <el-select
              v-model="row.segmentId"
              size="small"
              clearable
              placeholder="跟随主任务"
            >
              <el-option
                v-for="seg in segments"
                :key="seg.segmentNo"
                :value="seg.segmentNo"
                :label="`第 ${seg.segmentNo} 段`"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removePick($index)">
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { Refresh, Right } from '@element-plus/icons-vue';
  import { listCandidateWaybills } from '@/api/operation/task';
  import type {
    CandidateCargo,
    TaskSegment,
    TaskWaybillItem
  } from '@/api/operation/task/model';

  type PickedItem = TaskWaybillItem & {
    /** 候选行剩余台数（用于动态计算最大可输入） */
    _availableRemaining?: number;
  };

  const props = defineProps<{
    modelValue: PickedItem[];
    segments: TaskSegment[];
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: PickedItem[]): void;
  }>();

  const candidates = ref<CandidateCargo[]>([]);
  const loading = ref(false);
  const filter = reactive({
    keyword: '',
    originKeyword: '',
    destinationKeyword: ''
  });

  onMounted(() => {
    loadCandidates();
  });

  const loadCandidates = async () => {
    loading.value = true;
    try {
      candidates.value = await listCandidateWaybills({
        keyword: filter.keyword || undefined,
        originKeyword: filter.originKeyword || undefined,
        destinationKeyword: filter.destinationKeyword || undefined,
        limit: 200
      });
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载候选失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const isPicked = (row: CandidateCargo) =>
    props.modelValue.some((p) => p.waybillCargoId === row.cargoId);

  const addPick = (row: CandidateCargo) => {
    if (isPicked(row)) return;
    const next: PickedItem = {
      waybillId: row.waybillId,
      waybillCargoId: row.cargoId,
      waybillNo: row.waybillNo,
      customerId: row.customerId,
      customerName: row.customerName,
      vehicleBrand: row.vehicleBrand,
      vehicleModel: row.vehicleModel,
      dealerName: row.dealerName,
      quantity: 1,
      segmentId: undefined,
      _availableRemaining: row.remainingQuantity
    };
    emit('update:modelValue', [...props.modelValue, next]);
  };

  const removePick = (idx: number) => {
    const next = [...props.modelValue];
    next.splice(idx, 1);
    emit('update:modelValue', next);
  };

  const getMax = (row: PickedItem) => row._availableRemaining ?? 999;

  const syncQuantity = (_idx: number) => {
    // 仅供 v-model 触发响应
    emit('update:modelValue', [...props.modelValue]);
  };

  const totalQuantity = computed(() =>
    props.modelValue.reduce((s, x) => s + (x.quantity || 0), 0)
  );

  defineExpose({ reload: loadCandidates });
</script>

<style lang="scss" scoped>
  .cargo-picker {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    &__panel {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    &__title {
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    &__hint {
      color: #999;
      font-weight: normal;
      font-size: 12px;
    }
    &__filter {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
  }
</style>
