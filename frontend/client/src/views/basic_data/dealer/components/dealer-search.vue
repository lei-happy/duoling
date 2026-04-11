<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入名称 / 省 / 市 / 主营品牌"
            type="input"
            v-model.trim="form.keyword"
            clearable
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { DealerParam } from '@/api/basic-data/dealer/model';

  const emit = defineEmits<{
    (e: 'search', where?: DealerParam): void;
  }>();

  const [form, resetFields] = useFormData<DealerParam>({
    keyword: ''
  });

  const search = () => {
    const keyword = form.keyword?.trim();
    emit('search', { ...form, keyword: keyword || undefined });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
