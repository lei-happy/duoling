<template>
  <ele-card header="组件美化">
    <div style="max-width: 480px">
      <option-item label="日期选择器" label-width="90px">
        <el-date-picker
          type="date"
          v-model="value"
          placeholder="请选择日期"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="带快捷选项" label-width="90px">
        <el-date-picker
          type="date"
          v-model="value1"
          :shortcuts="shortcuts"
          :disabled-date="disabledDate"
          placeholder="请选择日期"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="周选择器" label-width="90px">
        <el-date-picker
          type="week"
          v-model="value2"
          format="YYYY第ww周"
          placeholder="请选择周"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="月选择器" label-width="90px">
        <el-date-picker
          type="month"
          v-model="value3"
          placeholder="请选择月"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="年选择器" label-width="90px">
        <el-date-picker
          type="year"
          v-model="value4"
          placeholder="请选择年"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="日期多选" label-width="90px">
        <el-date-picker
          type="dates"
          v-model="value5"
          placeholder="请选择日期"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="年多选" label-width="90px">
        <el-date-picker
          type="years"
          v-model="value16"
          placeholder="请选择年"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="月多选" label-width="90px">
        <el-date-picker
          type="months"
          v-model="value17"
          placeholder="请选择月"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="日期范围选择" label-width="90px">
        <el-date-picker
          type="daterange"
          v-model="value19"
          unlink-panels
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="带快捷选项" label-width="90px">
        <el-date-picker
          type="daterange"
          v-model="value6"
          unlink-panels
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="shortcuts2"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="月份范围选择" label-width="90px">
        <el-date-picker
          type="monthrange"
          v-model="value7"
          unlink-panels
          range-separator="-"
          start-placeholder="开始月"
          end-placeholder="结束月"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="年范围选择" label-width="90px">
        <el-date-picker
          type="yearrange"
          v-model="value18"
          unlink-panels
          range-separator="-"
          start-placeholder="开始年"
          end-placeholder="结束年"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="日期时间选择" label-width="90px">
        <el-date-picker
          type="datetime"
          v-model="value8"
          placeholder="请选择日期时间"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="带快捷选项" label-width="90px">
        <el-date-picker
          type="datetime"
          v-model="value9"
          :shortcuts="shortcuts3"
          placeholder="请选择日期时间"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="日期时间范围" label-width="90px">
        <el-date-picker
          type="datetimerange"
          v-model="value10"
          unlink-panels
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="带快捷选项" label-width="90px">
        <el-date-picker
          type="datetimerange"
          v-model="value11"
          unlink-panels
          :shortcuts="shortcuts4"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="时间选择器" label-width="90px">
        <el-time-picker
          v-model="value12"
          placeholder="请选择时间"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="箭头控制模式" label-width="90px">
        <el-time-picker
          arrow-control
          v-model="value13"
          :disabled-hours="disabledHours"
          :disabled-minutes="disabledMinutes"
          :disabled-seconds="disabledSeconds"
          placeholder="请选择时间"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="时间范围选择" label-width="90px">
        <el-time-picker
          v-model="value14"
          is-range
          range-separator="-"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item label="箭头控制模式" label-width="90px">
        <el-time-picker
          v-model="value15"
          is-range
          arrow-control
          range-separator="-"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        />
      </option-item>
      <option-item
        label="单选框"
        label-width="90px"
        style="align-items: flex-start"
        :label-style="{ paddingTop: '10px' }"
      >
        <div>
          <el-radio-group v-model="radio" size="large">
            <el-radio :value="1" label="Apple" />
            <el-radio :value="2" label="Pear" disabled />
            <el-radio :value="3" label="Orange" />
            <el-radio :value="4" label="Banana" />
          </el-radio-group>
        </div>
        <div>
          <el-radio-group v-model="radio">
            <el-radio :value="1" label="Apple" />
            <el-radio :value="2" label="Pear" />
            <el-radio :value="3" label="Orange" disabled />
            <el-radio :value="4" label="Banana" />
          </el-radio-group>
        </div>
        <div style="margin-top: 4px">
          <el-radio-group v-model="radio" size="small">
            <el-radio :value="1" label="Apple" />
            <el-radio :value="2" label="Pear" />
            <el-radio :value="3" label="Orange" />
            <el-radio :value="4" label="Banana" disabled />
          </el-radio-group>
        </div>
      </option-item>
      <option-item
        label="多选框"
        label-width="90px"
        style="align-items: flex-start"
        :label-style="{ paddingTop: '10px' }"
      >
        <div>
          <el-checkbox-group v-model="checkbox" size="large">
            <el-checkbox :value="1" label="Apple" />
            <el-checkbox :value="2" label="Pear" disabled />
            <el-checkbox :value="3" label="Orange" />
            <el-checkbox :value="4" label="Banana" />
          </el-checkbox-group>
        </div>
        <div>
          <el-checkbox-group v-model="checkbox">
            <el-checkbox :value="1" label="Apple" />
            <el-checkbox :value="2" label="Pear" />
            <el-checkbox :value="3" label="Orange" disabled />
            <el-checkbox :value="4" label="Banana" />
          </el-checkbox-group>
        </div>
        <div style="margin-top: 4px">
          <el-checkbox-group v-model="checkbox" size="small">
            <el-checkbox :value="1" label="Apple" />
            <el-checkbox :value="2" label="Pear" />
            <el-checkbox :value="3" label="Orange" />
            <el-checkbox :value="4" label="Banana" disabled />
          </el-checkbox-group>
        </div>
      </option-item>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  /** 日期选择 */
  const value = ref('');

  /** 带快捷选项 */
  const value1 = ref('');

  /** 日期选择快捷项 */
  const shortcuts = ref([
    {
      text: 'Today',
      value: new Date()
    },
    {
      text: 'Yesterday',
      value: () => {
        const date = new Date();
        date.setTime(date.getTime() - 3600 * 1000 * 24);
        return date;
      }
    },
    {
      text: 'A week ago',
      value: () => {
        const date = new Date();
        date.setTime(date.getTime() - 3600 * 1000 * 24 * 7);
        return date;
      }
    }
  ]);

  /** 日期选择禁用 */
  const disabledDate = (time: Date) => {
    return time.getTime() > Date.now();
  };

  /** 周选择 */
  const value2 = ref('');

  /** 月选择 */
  const value3 = ref('');

  /** 年选择 */
  const value4 = ref('');

  /** 日期选择 */
  const value5 = ref('');

  /** 日期范围选择带快捷选项 */
  const value6 = ref('');

  /** 快捷选项 */
  const shortcuts2 = ref([
    {
      text: 'Last week',
      value: () => {
        const end = new Date();
        const start = new Date();
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
        return [start, end];
      }
    },
    {
      text: 'Last month',
      value: () => {
        const end = new Date();
        const start = new Date();
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
        return [start, end];
      }
    },
    {
      text: 'Last 3 months',
      value: () => {
        const end = new Date();
        const start = new Date();
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
        return [start, end];
      }
    }
  ]);

  /** 月份范围选择 */
  const value7 = ref('');

  /** 日期时间选择 */
  const value8 = ref('');

  /** 日期时间选择 */
  const value9 = ref('');

  /** 快捷选项 */
  const shortcuts3 = ref([
    {
      text: 'Today',
      value: new Date()
    },
    {
      text: 'Yesterday',
      value: () => {
        const date = new Date();
        date.setTime(date.getTime() - 3600 * 1000 * 24);
        return date;
      }
    },
    {
      text: 'A week ago',
      value: () => {
        const date = new Date();
        date.setTime(date.getTime() - 3600 * 1000 * 24 * 7);
        return date;
      }
    }
  ]);

  /** 日期时间范围 */
  const value10 = ref(void 0);

  /** 日期时间范围 */
  const value11 = ref(void 0);

  /** 快捷选项 */
  const shortcuts4 = ref([
    {
      text: 'Last week',
      value: () => {
        const end = new Date();
        const start = new Date();
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
        return [start, end];
      }
    },
    {
      text: 'Last month',
      value: () => {
        const end = new Date();
        const start = new Date();
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
        return [start, end];
      }
    },
    {
      text: 'Last 3 months',
      value: () => {
        const end = new Date();
        const start = new Date();
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
        return [start, end];
      }
    }
  ]);

  /** 时间 */
  const value12 = ref(void 0);

  /** 时间 */
  const value13 = ref(void 0);

  const makeRange = (start: number, end: number) => {
    const result: number[] = [];
    for (let i = start; i <= end; i++) {
      result.push(i);
    }
    return result;
  };

  const disabledHours = () => {
    return makeRange(0, 16).concat(makeRange(19, 23));
  };

  const disabledMinutes = (hour: number) => {
    if (hour === 17) {
      return makeRange(0, 29);
    }
    if (hour === 18) {
      return makeRange(31, 59);
    }
    return [];
  };

  const disabledSeconds = (hour: number, minute: number) => {
    if (hour === 18 && minute === 30) {
      return makeRange(1, 59);
    }
    return [];
  };

  /** 时间范围 */
  const value14 = ref(void 0);

  /** 时间范围 */
  const value15 = ref(void 0);

  /** 单选框 */
  const radio = ref(1);

  /** 多选框 */
  const checkbox = ref([]);

  /** 年多选 */
  const value16 = ref('');

  /** 月多选 */
  const value17 = ref('');

  /** 年范围选择 */
  const value18 = ref('');

  /** 日期范围选择 */
  const value19 = ref('');
</script>
