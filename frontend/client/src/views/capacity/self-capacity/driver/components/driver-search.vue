<!-- 搜索表单（多行模式，对齐开发手册 06） -->
<template>
  <ele-card search-form class="driver-search-card">
    <el-form
      class="driver-search-bar"
      label-width="0"
      @keyup.enter="search"
      @submit.prevent=""
    >
      <el-row :gutter="10" class="driver-search-bar__row">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="姓名/手机号/编号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="人事状态"
            type="select"
            clearable
          >
            <el-option label="在职" :value="1" />
            <el-option label="冻结" :value="0" />
            <el-option label="离职" :value="2" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.operationStatus"
            label="运营状态"
            type="select"
            clearable
          >
            <el-option label="可接单" :value="1" />
            <el-option label="忙碌" :value="2" />
            <el-option label="休假" :value="3" />
            <el-option label="停运" :value="4" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <dict-select-hint-wrap dict-name="自有驾驶员类型">
            <floating-label
              v-model="form.driverType"
              label="请选择驾驶员类型"
              type="select"
              clearable
            >
              <el-option
                v-for="item in driverTypeDict"
                :key="item.dictDataCode"
                :label="item.dictDataName"
                :value="item.dictDataCode"
              />
            </floating-label>
          </dict-select-hint-wrap>
        </el-col>
      </el-row>
      <el-row
        :gutter="10"
        class="driver-search-bar__row driver-search-bar__row--second"
      >
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <business-entity-select
            v-model="form.enterpriseId"
            placeholder="请选择经营主体"
            clearable
          />
        </el-col>
        <el-col
          :lg="8"
          :md="12"
          :sm="12"
          :xs="24"
          class="driver-search-bar__col-actions"
        >
          <el-form-item label-width="0px">
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => search() },
                { preset: 'reset', onClick: () => reset() }
              ]"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import DictSelectHintWrap from '@/components/DictSelectHintWrap/index.vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import BusinessEntitySelect from '@/components/BusinessEntitySelect/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { useDictData } from '@/utils/use-dict-data';
  import type { DriverParam } from '@/api/capacity/self-capacity/driver/model';
  import { DICT_CODE_SELF_CAPACITY_DRIVER_TYPE } from '@/constants/dict-codes';

  const [driverTypeDict] = useDictData([DICT_CODE_SELF_CAPACITY_DRIVER_TYPE]);

  const emit = defineEmits<{
    (e: 'search', where?: DriverParam): void;
  }>();

  const [form, resetFields] = useFormData<DriverParam>({
    keyword: '',
    status: void 0,
    operationStatus: void 0,
    driverType: void 0,
    enterpriseId: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>

<style scoped>
  .driver-search-bar__row--second {
    margin-top: 12px;
    padding-top: 2px;
  }

  .driver-search-bar__col-actions :deep(.el-form-item) {
    margin-bottom: 0;
    display: flex;
    justify-content: flex-start;
  }

  .driver-search-bar__col-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
    flex-wrap: nowrap;
  }
</style>

<style>
  .driver-search-card.driver-search-card {
    padding-bottom: 6px;
  }
</style>
