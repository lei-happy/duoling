<!-- 运力列表搜索（仅展示绑定中运力，已解绑见变动记录） -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="10" :sm="12" :xs="24">
          <floating-label
            label="驾驶员姓名 / 手机号 / 车牌号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <business-entity-select
            v-model="form.enterpriseId"
            placeholder="请选择经营主体"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import BusinessEntitySelect from '@/components/BusinessEntitySelect/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { CapacityParam } from '@/api/capacity/self-capacity/list/model';

  const emit = defineEmits<{
    (e: 'search', where: Pick<CapacityParam, 'keyword' | 'enterpriseId'>): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    enterpriseId: number | undefined;
  }>({
    keyword: '',
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
