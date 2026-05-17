<template>
  <div class="capacity-log-search-wrapper">
    <ele-card search-form>
      <el-form
        class="capacity-log-search-form"
        label-width="0"
        @keyup.enter="search"
        @submit.prevent=""
      >
        <div class="capacity-log-search-toolbar">
        <div class="capacity-log-search-item capacity-log-search-item--keyword">
          <floating-label
            label="请输入驾驶员姓名/车牌号/手机号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </div>
        <div class="capacity-log-search-item capacity-log-search-item--action">
          <floating-label
            v-model="form.action"
            label="请选择操作类型"
            type="select"
            clearable
          >
            <el-option label="上车" :value="1" />
            <el-option label="下车" :value="2" />
          </floating-label>
        </div>
        <div class="capacity-log-search-item capacity-log-search-item--operator">
          <floating-label
            label="请输入操作人"
            type="input"
            v-model.trim="form.operatorName"
            clearable
          />
        </div>
        <div class="capacity-log-search-item capacity-log-search-item--datetime">
          <div class="log-search-datetime-wrap">
            <floating-label
              label="操作时间"
              type="date"
              date-type="datetimerange"
              v-model="actionTimeRange"
              range-separator="-"
              :value-format="DATE_TIME_FORMAT"
              :format="DATE_TIME_FORMAT"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              :unlink-panels="true"
              clearable
            />
          </div>
        </div>
        <div class="capacity-log-search-item capacity-log-search-actions">
          <el-form-item
            label-width="0px"
            class="capacity-log-search-actions-inner"
          >
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => search() },
                { preset: 'reset', onClick: () => reset() }
              ]"
            />
          </el-form-item>
        </div>
        </div>
      </el-form>
    </ele-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import {
    DATE_TIME_FORMAT,
    getLast7DaysDateTimeRange
  } from '@/utils/date-util';
  import type { CapacityLogParam } from '@/api/capacity/self_capacity/log/model';

  type SearchPayload = Pick<
    CapacityLogParam,
    'keyword' | 'action' | 'operatorName' | 'actionTimeStart' | 'actionTimeEnd'
  >;

  const emit = defineEmits<{
    (e: 'search', where: SearchPayload): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    action: number | undefined;
    operatorName: string;
  }>({
    keyword: '',
    action: void 0,
    operatorName: ''
  });

  const actionTimeRange = ref<[string, string]>(getLast7DaysDateTimeRange());

  const search = () => {
    const [actionTimeStart, actionTimeEnd] = actionTimeRange.value || [];
    emit('search', {
      ...form,
      actionTimeStart,
      actionTimeEnd
    });
  };

  const reset = () => {
    resetFields();
    actionTimeRange.value = getLast7DaysDateTimeRange();
    search();
  };
</script>

<style scoped>
  /**
   * 主题 search-form 卡片为 padding: 20px 20px 4px（下边极窄），此处单独拉齐上下内边距
   */
  .capacity-log-search-wrapper :deep(.ele-card.is-search-form > .ele-card-body) {
    padding: 16px 20px;
  }

  .capacity-log-search-wrapper
    :deep(.ele-card.is-search-form > .ele-card-body > .el-form .el-form-item) {
    margin-bottom: 0;
  }

  .capacity-log-search-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 8px;
    width: 100%;
  }

  .capacity-log-search-item {
    flex: 1 1 200px;
    min-width: 0;
    max-width: 100%;
  }

  .capacity-log-search-item--keyword {
    flex: 1.4 1 150px;
  }

  .capacity-log-search-item--action,
  .capacity-log-search-item--operator {
    flex: 1 1 110px;
  }

  .capacity-log-search-item--datetime {
    flex: 1 1 280px;
    max-width: 480px;
  }

  .log-search-datetime-wrap {
    width: 100%;
    max-width: 480px;
  }

  .log-search-datetime-wrap :deep(.ele-fluid) {
    width: 100%;
    max-width: 100%;
  }

  .capacity-log-search-actions {
    flex: 0 0 auto;
    margin-left: auto;
    min-width: auto;
    max-width: 100%;
  }

  .capacity-log-search-actions-inner {
    margin-bottom: 0;
  }

  .capacity-log-search-actions-inner :deep(.el-form-item__content) {
    justify-content: flex-end;
  }
</style>
