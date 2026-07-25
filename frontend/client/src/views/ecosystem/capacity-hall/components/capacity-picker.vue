<!--
  发布运力时选车

  只列「可接单」的运力：运输中、休假、维修的车挂上去，找车的人打过来才发现
  用不了，比没挂更糟。与后端 CapacityDraftBuilder.assert_bindable 的判断一致。
-->
<template>
  <div class="eco-picker">
    <div class="eco-picker__bar">
      <el-input
        v-model="keyword"
        clearable
        placeholder="搜车牌、司机"
        :prefix-icon="Search"
        @change="reload"
      />
    </div>

    <el-table
      v-loading="loading"
      :data="rows"
      height="300"
      highlight-current-row
      @current-change="onPick"
    >
      <el-table-column width="42">
        <template #default="{ row }">
          <el-radio
            :value="row.id"
            :model-value="picked?.id"
            @change="onPick(row)"
          >
            <span></span>
          </el-radio>
        </template>
      </el-table-column>
      <el-table-column label="车牌" prop="plateNumber" width="120" />
      <el-table-column label="挂车" width="120">
        <template #default="{ row }">
          {{ row.trailerPlateNumber || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="司机" width="100">
        <template #default="{ row }">{{ row.driverName || '—' }}</template>
      </el-table-column>
      <el-table-column label="车型" min-width="120">
        <template #default="{ row }">
          <dict-data
            v-if="row.vehicleType"
            type="text"
            :code="DICT_CODE_VEHICLE_TYPE"
            :model-value="row.vehicleType"
          />
          <span v-else>—</span>
        </template>
      </el-table-column>
    </el-table>

    <div class="eco-picker__foot">
      <el-pagination
        v-model:current-page="page"
        layout="total, prev, pager, next"
        :page-size="pageSize"
        :total="total"
        :pager-count="5"
        @current-change="load"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { Search } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import DictData from '@/components/DictData/index.vue';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';
  import { pageCapacities } from '@/api/capacity/self-capacity/list';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';

  /** 可接单。与后端「这台车当前不是可接单状态」的判断一致 */
  const OPERATION_AVAILABLE = 1;

  const emit = defineEmits<{ (e: 'pick', capacity: Capacity): void }>();

  const loading = ref(false);
  const rows = ref<Capacity[]>([]);
  const keyword = ref('');
  const page = ref(1);
  const pageSize = ref(8);
  const total = ref(0);
  const picked = ref<Capacity>();

  const load = async () => {
    loading.value = true;
    try {
      const result = await pageCapacities({
        page: page.value,
        limit: pageSize.value,
        operationStatus: OPERATION_AVAILABLE,
        keyword: keyword.value || void 0
      });
      rows.value = result?.list ?? [];
      total.value = result?.count ?? 0;
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能读取运力列表，请稍后再试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const reload = () => {
    page.value = 1;
    load();
  };

  const onPick = (capacity?: Capacity | null) => {
    if (!capacity?.id) {
      return;
    }
    picked.value = capacity;
    emit('pick', capacity);
  };

  onMounted(load);
</script>

<style lang="scss" scoped>
  .eco-picker__bar {
    max-width: 280px;
    margin-bottom: 10px;
  }

  .eco-picker__foot {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }

  :deep(.el-radio__label) {
    display: none;
  }
</style>
