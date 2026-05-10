<!-- 挂车列表搜索 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入挂车号牌"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.trailerType"
            label="请选择挂车类型"
            type="select"
            :filterable="true"
            clearable
          >
            <el-option
              v-for="item in trailerTypeDict"
              :key="item.dictDataCode"
              :label="item.dictDataName"
              :value="item.dictDataCode"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </floating-label>
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
  import { useFormData } from '@/utils/use-form-data';
  import { useDictData } from '@/utils/use-dict-data';
  import type { TrailerParam } from '@/api/capacity/self_capacity/trailer/model';
  import { DICT_CODE_TRAILER_TYPE } from '@/constants/dict-codes';

  const [trailerTypeDict] = useDictData([DICT_CODE_TRAILER_TYPE]);

  const emit = defineEmits<{
    (
      e: 'search',
      where: Pick<TrailerParam, 'keyword' | 'status' | 'trailerType'>
    ): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    trailerType: string | undefined;
    status: number | undefined;
  }>({
    keyword: '',
    trailerType: void 0,
    status: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
