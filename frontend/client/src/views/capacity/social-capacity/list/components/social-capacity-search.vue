<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="编号/姓名/手机号/车牌号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <dict-select-hint-wrap dict-name="社会运力来源">
            <floating-label
              v-model="form.source"
              label="请选择来源"
              type="select"
              clearable
            >
              <el-option
                v-for="item in sourceDict"
                :key="item.dictDataCode"
                :label="item.dictDataName"
                :value="item.dictDataCode"
              />
            </floating-label>
          </dict-select-hint-wrap>
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
  import DictSelectHintWrap from '@/components/DictSelectHintWrap/index.vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { useDictData } from '@/utils/use-dict-data';
  import type { SocialCapacityParam } from '@/api/capacity/social-capacity/list/model';
  import { DICT_CODE_SOCIAL_CAPACITY_SOURCE } from '@/constants/dict-codes';

  const [sourceDict] = useDictData([DICT_CODE_SOCIAL_CAPACITY_SOURCE]);

  const emit = defineEmits<{
    (e: 'search', where?: SocialCapacityParam): void;
    (e: 'reset'): void;
  }>();

  const [form, resetFields] = useFormData<Pick<SocialCapacityParam, 'keyword' | 'source'>>({
    keyword: '',
    source: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    emit('reset');
  };
</script>
