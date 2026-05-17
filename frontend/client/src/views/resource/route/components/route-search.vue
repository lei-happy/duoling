<!-- 搜索表单（布局与 driver-search 一致：单行 el-row + el-col） -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="起点"
            type="input"
            v-model.trim="form.originKeyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="终点"
            type="input"
            v-model.trim="form.destinationKeyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="12" :sm="24" :xs="24">
          <floating-label
            v-model="form.createdAtRange"
            label="创建时间"
            type="date"
            date-type="daterange"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            unlink-panels
            start-placeholder="开始"
            end-placeholder="结束"
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
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
  import { onMounted } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { RouteParam } from '@/api/resource/route/model';

  const emit = defineEmits<{
    (e: 'search', where?: RouteParam): void;
  }>();

  type SearchForm = {
    originKeyword: string;
    destinationKeyword: string;
    status: number | undefined;
    createdAtRange: [string, string] | null;
  };

  const [form, resetFields] = useFormData<SearchForm>({
    originKeyword: '',
    destinationKeyword: '',
    status: void 0,
    createdAtRange: null
  });

  const buildWhere = (): RouteParam => {
    const payload: RouteParam = {
      originKeyword: form.originKeyword,
      destinationKeyword: form.destinationKeyword,
      status: form.status
    };
    const range = form.createdAtRange;
    if (Array.isArray(range) && range.length === 2 && range[0] && range[1]) {
      payload.createdAtStart = range[0];
      payload.createdAtEnd = range[1];
    }
    return payload;
  };

  const search = () => {
    emit('search', buildWhere());
  };

  const reset = () => {
    resetFields();
    search();
  };

  onMounted(() => {
    search();
  });
</script>
