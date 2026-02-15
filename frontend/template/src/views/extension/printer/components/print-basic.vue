<template>
  <ele-card header="基础用法">
    <el-form label-width="80px" style="max-width: 320px" @submit.prevent="">
      <el-form-item label="纸张方向">
        <el-select
          clearable
          class="ele-fluid"
          placeholder="不设置"
          v-model="option.direction"
        >
          <el-option value="landscape" label="横向" />
          <el-option value="portrait" label="纵向" />
        </el-select>
      </el-form-item>
      <el-form-item label="纸张旋转">
        <el-select
          clearable
          class="ele-fluid"
          placeholder="不旋转"
          v-model="option.orientation"
        >
          <el-option value="rotate-left" label="向左旋转" />
          <el-option value="rotate-right" label="向右旋转" />
        </el-select>
      </el-form-item>
      <el-form-item label="页面间距">
        <el-input clearable v-model="option.margin" placeholder="不设置" />
      </el-form-item>
      <el-form-item label="页面标题">
        <el-input clearable v-model="option.title" placeholder="默认" />
      </el-form-item>
      <el-form-item label="打印位置">
        <el-select class="ele-fluid" v-model="option.target">
          <el-option value="_iframe" label="子窗口" />
          <el-option value="_self" label="当前窗口" />
        </el-select>
      </el-form-item>
      <el-form-item label="始终显示">
        <el-radio-group v-model="option.static">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </el-form-item>
      <el-form-item>
        <el-button :disabled="printing" type="primary" @click="handlePrint">
          {{ printing ? '打印中...' : '打印' }}
        </el-button>
      </el-form-item>
    </el-form>
    <ele-printer
      v-model="printing"
      :direction="option.direction"
      :orientation="option.orientation"
      :margin="option.margin"
      :title="option.title"
      :target="option.target"
      :static="option.static"
      :body-style="{ overflow: 'hidden' }"
    >
      <div style="overflow: auto">
        <ele-table has-footer style="min-width: 600px" size="large">
          <colgroup>
            <col width="38px" />
            <col width="200px" />
            <col width="140px" />
            <col width="138px" />
            <col width="138px" />
            <col width="118px" />
            <col width="180px" />
          </colgroup>
          <thead>
            <tr>
              <th></th>
              <th>项目名称</th>
              <th>金额(万元)</th>
              <th>开始时间</th>
              <th>结束时间</th>
              <th>状态</th>
              <th>进度</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in projectList" :key="row.id">
              <td style="text-align: center">{{ index + 1 }}</td>
              <td>{{ row.projectName }}</td>
              <td>
                <el-input-number
                  :min="0"
                  :max="999"
                  v-model="row.money"
                  placeholder="请输入"
                  controls-position="right"
                  class="ele-fluid"
                />
              </td>
              <td>{{ row.startDate }}</td>
              <td>{{ row.endDate }}</td>
              <td>
                <ele-text v-if="row.status === 0" type="success">
                  进行中
                </ele-text>
                <ele-text v-else-if="row.status === 1" type="danger">
                  已延期
                </ele-text>
                <ele-text v-else-if="row.status === 2" type="warning">
                  未开始
                </ele-text>
                <ele-text v-else-if="row.status === 3" type="info">
                  已结束
                </ele-text>
              </td>
              <td>
                <el-progress :percentage="row.progress" />
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td></td>
              <td>合计</td>
              <td>{{ sumMoney }} 万</td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
          </tfoot>
        </ele-table>
      </div>
      <div style="margin: 12px 0">更多表单组件演示：</div>
      <div>
        <el-radio-group v-model="status">
          <el-radio value="未完成" label="未完成" />
          <el-radio value="已完成" label="已完成" />
        </el-radio-group>
      </div>
      <div>
        <el-checkbox-group v-model="citys">
          <el-checkbox value="武汉" label="武汉" />
          <el-checkbox value="北京" label="北京" />
          <el-checkbox value="上海" label="上海" />
          <el-checkbox value="广州" label="广州" />
          <el-checkbox value="深圳" label="深圳" />
        </el-checkbox-group>
      </div>
      <div style="margin: 12px 0">自定义更加适合打印风格的复选框组件：</div>
      <div>
        <print-checkbox
          v-model="citys"
          :items="[
            { label: '武汉', value: '武汉' },
            { label: '北京', value: '北京' },
            { label: '上海', value: '上海' },
            { label: '广州', value: '广州' },
            { label: '深圳', value: '深圳' }
          ]"
        />
      </div>
    </ele-printer>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed } from 'vue';
  import type {
    PrintDirection,
    PrintOrientation,
    PrintTarget
  } from 'ele-admin-plus/es/ele-printer/types';
  import type { Project } from '@/api/example/model';
  import PrintCheckbox from './print-checkbox.vue';

  interface Option {
    direction?: PrintDirection;
    orientation?: PrintOrientation;
    margin: string;
    title: string;
    target: PrintTarget;
    static: boolean;
  }

  /** 是否打印 */
  const printing = ref(false);

  /** 打印参数 */
  const option = reactive<Option>({
    direction: void 0,
    orientation: void 0,
    margin: '',
    title: '',
    target: '_iframe',
    static: false
  });

  /** 打印 */
  const handlePrint = () => {
    printing.value = true;
  };

  /** 是否完成 */
  const status = ref('未完成');

  /** 城市 */
  const citys = ref(['武汉', '北京']);

  /** 项目进度数据 */
  const projectList = ref<Project[]>([]);

  /** 金额合计 */
  const sumMoney = computed(() => {
    return projectList.value.reduce((sum, d) => {
      const money = d.money ? Number(d.money) : 0;
      return sum + (isNaN(money) ? 0 : money);
    }, 0);
  });

  /** 查询项目进度 */
  const queryProjectList = () => {
    projectList.value = [
      {
        id: '1',
        projectName: '项目000000001',
        status: 0,
        startDate: '2020-03-01',
        endDate: '2020-06-01',
        progress: 30,
        money: 3
      },
      {
        id: '2',
        projectName: '项目000000002',
        status: 0,
        startDate: '2020-03-01',
        endDate: '2020-08-01',
        progress: 10,
        money: 5
      },
      {
        id: '3',
        projectName: '项目000000003',
        status: 1,
        startDate: '2020-01-01',
        endDate: '2020-05-01',
        progress: 60,
        money: 2
      },
      {
        id: '4',
        projectName: '项目000000004',
        status: 1,
        startDate: '2020-06-01',
        endDate: '2020-10-01',
        progress: 0,
        money: 4
      },
      {
        id: '5',
        projectName: '项目000000005',
        status: 2,
        startDate: '2020-03-01',
        endDate: '2020-07-01',
        progress: 100,
        money: 1
      },
      {
        id: '6',
        projectName: '项目000000006',
        status: 3,
        startDate: '2020-02-01',
        endDate: '2020-06-01',
        progress: 100,
        money: 6
      }
    ];
  };

  queryProjectList();
</script>
