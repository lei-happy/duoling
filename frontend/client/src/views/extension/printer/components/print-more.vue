<template>
  <ele-card header="更多示例">
    <div style="margin-bottom: 16px">
      <el-button type="default" @click="printing1 = true">打印表格</el-button>
    </div>
    <div style="margin-bottom: 16px">
      <el-button type="default" @click="printing2 = true">打印图片</el-button>
    </div>
    <div style="margin-bottom: 16px">
      <el-button type="default" @click="printing3 = true">打印二维码</el-button>
    </div>
    <div style="margin-bottom: 16px">
      <el-button type="default" @click="printing4 = true">
        结合水印组件
      </el-button>
    </div>
    <div>
      <el-button type="default" @click="printing5 = true">
        打印echarts图表
      </el-button>
    </div>
    <ele-printer v-model="printing1" target="_iframe">
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        表格打印示例：
      </div>
      <ele-table size="large" :border="true" style="page-break-after: always">
        <colgroup>
          <col width="60px" />
          <col width="200px" />
          <col width="120px" />
          <col width="160px" />
          <col width="160px" />
          <col width="100px" />
        </colgroup>
        <thead>
          <tr>
            <th :rowspan="2"></th>
            <th :rowspan="2">项目名称</th>
            <th :rowspan="2">金额</th>
            <th :colspan="2" style="text-align: center">项目周期</th>
            <th :rowspan="2">状态</th>
          </tr>
          <tr>
            <th>开始时间</th>
            <th>结束时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in projects" :key="row.id">
            <td style="text-align: center">{{ index + 1 }}</td>
            <td>{{ row.projectName }}</td>
            <td>{{ row.money }}(万元)</td>
            <td>{{ row.startDate }}</td>
            <td>{{ row.endDate }}</td>
            <td>
              <ele-text v-if="row.status === 0" type="success">进行中</ele-text>
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
          </tr>
        </tbody>
      </ele-table>
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        表格颜色修改：
      </div>
      <ele-table
        size="large"
        :border="true"
        :style="{
          pageBreakAfter: 'always',
          '--ele-table-bg': '#fff',
          '--ele-table-color': '#000',
          '--ele-table-border-color': '#000',
          '--ele-table-th-color': '#000',
          '--ele-table-th-font-weight': 'bold',
          '--ele-table-th-bg': 'transparent',
          '--ele-table-tr-bg': 'transparent',
          '--ele-table-tr-hover-bg': 'transparent',
          '--ele-table-radius': 0,
          '--ele-table-sm-radius': 0,
          '--ele-table-lg-radius': 0,
          borderCollapse: 'collapse'
        }"
      >
        <colgroup>
          <col width="60px" />
          <col width="200px" />
          <col width="120px" />
          <col width="160px" />
          <col width="160px" />
          <col width="100px" />
        </colgroup>
        <thead>
          <tr>
            <th :rowspan="2"></th>
            <th :rowspan="2">项目名称</th>
            <th :rowspan="2">金额</th>
            <th :colspan="2" style="text-align: center">项目周期</th>
            <th :rowspan="2">状态</th>
          </tr>
          <tr>
            <th>开始时间</th>
            <th>结束时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in projects" :key="row.id">
            <td style="text-align: center">{{ index + 1 }}</td>
            <td>{{ row.projectName }}</td>
            <td>{{ row.money }}(万元)</td>
            <td>{{ row.startDate }}</td>
            <td>{{ row.endDate }}</td>
            <td>
              <span v-if="row.status === 0">进行中</span>
              <span v-else-if="row.status === 1">已延期</span>
              <span v-else-if="row.status === 2">未开始</span>
              <span v-else-if="row.status === 3">已结束</span>
            </td>
          </tr>
        </tbody>
      </ele-table>
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        表格增加水印：
      </div>
      <ele-watermark
        content="Ele Admin Plus"
        :gap="[60, 40]"
        :width="111"
        :height="16"
      >
        <ele-table>
          <colgroup>
            <col width="38px" />
            <col width="200px" />
            <col width="140px" />
            <col width="138px" />
            <col width="138px" />
            <col width="118px" />
          </colgroup>
          <thead>
            <tr>
              <th></th>
              <th>项目名称</th>
              <th>金额(万元)</th>
              <th>开始时间</th>
              <th>结束时间</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in projects" :key="row.id">
              <td style="text-align: center">{{ index + 1 }}</td>
              <td>{{ row.projectName }}</td>
              <td>{{ row.money }}(万元)</td>
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
            </tr>
          </tbody>
        </ele-table>
      </ele-watermark>
    </ele-printer>
    <ele-printer v-model="printing2" target="_iframe">
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        图片打印示例：
      </div>
      <img
        src="https://cdn.eleadmin.com/20200610/4Z0QR2L0J1XStxBh99jVJ8qLfsGsOgjU.jpg"
        style="width: 100%; display: block; page-break-after: always"
      />
    </ele-printer>
    <ele-printer v-model="printing3" target="_iframe">
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        二维码打印示例：
      </div>
      <div
        style="text-align: center; page-break-after: always; padding: 40px 0"
      >
        <ele-qr-code-svg :value="partyA" :size="180" />
        <div style="font-size: 14px; line-height: 1.2">{{ partyA }}</div>
      </div>
    </ele-printer>
    <ele-printer v-model="printing4" target="_iframe">
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        水印组件：
      </div>
      <ele-watermark
        content="Ele Admin Plus"
        :gap="[60, 40]"
        :width="111"
        :height="16"
        :svg-render="true"
      >
        <ele-table>
          <colgroup>
            <col width="38px" />
            <col width="200px" />
            <col width="140px" />
            <col width="138px" />
            <col width="138px" />
            <col width="118px" />
          </colgroup>
          <thead>
            <tr>
              <th></th>
              <th>项目名称</th>
              <th>金额(万元)</th>
              <th>开始时间</th>
              <th>结束时间</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in projects" :key="row.id">
              <td style="text-align: center">{{ index + 1 }}</td>
              <td>{{ row.projectName }}</td>
              <td>{{ row.money }}(万元)</td>
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
            </tr>
          </tbody>
        </ele-table>
      </ele-watermark>
    </ele-printer>
    <ele-printer v-model="printing5" target="_iframe">
      <div style="font-size: 22px; margin-bottom: 24px; line-height: 1.2">
        echarts图表打印示例：
      </div>
      <v-chart
        :option="saleChartOption"
        :initOptions="{ width: 660, height: 320, renderer: 'svg' }"
      />
      <div style="font-size: 22px; margin: 24px 0; line-height: 1.2">
        折线图：
      </div>
      <v-chart
        :option="visitHourChartOption"
        :initOptions="{ width: 660, height: 320, renderer: 'svg' }"
      />
      <div style="font-size: 22px; margin: 24px 0; line-height: 1.2">
        饼图：
      </div>
      <v-chart
        :option="browserChartOption"
        :initOptions="{ width: 480, height: 236, renderer: 'svg' }"
      />
    </ele-printer>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, provide } from 'vue';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { SVGRenderer } from 'echarts/renderers';
  import { BarChart, LineChart, PieChart } from 'echarts/charts';
  import {
    GridComponent,
    TooltipComponent,
    LegendComponent
  } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { THEME_KEY } from 'vue-echarts';
  import { ChartTheme } from 'ele-admin-plus';

  use([
    SVGRenderer,
    BarChart,
    LineChart,
    PieChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ]);

  provide(THEME_KEY, { ...ChartTheme });

  const printing1 = ref(false);

  const printing2 = ref(false);

  const printing3 = ref(false);

  const printing4 = ref(false);

  const printing5 = ref(false);

  interface Project {
    /** id */
    id: string;
    /** 项目名称 */
    projectName: string;
    /** 状态 */
    status: number;
    /** 开始时间 */
    startDate: string;
    /** 结束时间 */
    endDate: string;
    /** 进度 */
    progress: number;
    /** 金额 */
    money: number;
  }

  const projects = ref<Project[]>([
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
    },
    {
      id: '7',
      projectName: '项目000000007',
      status: 0,
      startDate: '2020-03-01',
      endDate: '2020-06-01',
      progress: 30,
      money: 3
    },
    {
      id: '8',
      projectName: '项目000000008',
      status: 0,
      startDate: '2020-03-01',
      endDate: '2020-08-01',
      progress: 10,
      money: 5
    },
    {
      id: '9',
      projectName: '项目000000009',
      status: 1,
      startDate: '2020-01-01',
      endDate: '2020-05-01',
      progress: 60,
      money: 2
    },
    {
      id: '10',
      projectName: '项目000000010',
      status: 1,
      startDate: '2020-06-01',
      endDate: '2020-10-01',
      progress: 0,
      money: 4
    },
    {
      id: '11',
      projectName: '项目000000011',
      status: 2,
      startDate: '2020-03-01',
      endDate: '2020-07-01',
      progress: 100,
      money: 1
    },
    {
      id: '12',
      projectName: '项目000000012',
      status: 3,
      startDate: '2020-02-01',
      endDate: '2020-06-01',
      progress: 100,
      money: 6
    },
    {
      id: '13',
      projectName: '项目000000013',
      status: 0,
      startDate: '2020-03-01',
      endDate: '2020-06-01',
      progress: 30,
      money: 3
    },
    {
      id: '14',
      projectName: '项目000000014',
      status: 0,
      startDate: '2020-03-01',
      endDate: '2020-08-01',
      progress: 10,
      money: 5
    },
    {
      id: '15',
      projectName: '项目000000015',
      status: 1,
      startDate: '2020-01-01',
      endDate: '2020-05-01',
      progress: 60,
      money: 2
    },
    {
      id: '16',
      projectName: '项目000000016',
      status: 1,
      startDate: '2020-06-01',
      endDate: '2020-10-01',
      progress: 0,
      money: 4
    },
    {
      id: '17',
      projectName: '项目000000017',
      status: 2,
      startDate: '2020-03-01',
      endDate: '2020-07-01',
      progress: 100,
      money: 1
    },
    {
      id: '18',
      projectName: '项目000000018',
      status: 3,
      startDate: '2020-02-01',
      endDate: '2020-06-01',
      progress: 100,
      money: 6
    },
    {
      id: '19',
      projectName: '项目000000019',
      status: 0,
      startDate: '2020-03-01',
      endDate: '2020-06-01',
      progress: 30,
      money: 3
    },
    {
      id: '20',
      projectName: '项目000000020',
      status: 0,
      startDate: '2020-03-01',
      endDate: '2020-08-01',
      progress: 10,
      money: 5
    },
    {
      id: '21',
      projectName: '项目000000021',
      status: 1,
      startDate: '2020-01-01',
      endDate: '2020-05-01',
      progress: 60,
      money: 2
    },
    {
      id: '22',
      projectName: '项目000000022',
      status: 1,
      startDate: '2020-06-01',
      endDate: '2020-10-01',
      progress: 0,
      money: 4
    },
    {
      id: '23',
      projectName: '项目000000023',
      status: 2,
      startDate: '2020-03-01',
      endDate: '2020-07-01',
      progress: 100,
      money: 1
    },
    {
      id: '24',
      projectName: '项目000000024',
      status: 3,
      startDate: '2020-02-01',
      endDate: '2020-06-01',
      progress: 100,
      money: 6
    }
  ]);

  const partyA = ref('XX房屋租赁有限公司');

  const chartData = [
    {
      month: '1月',
      value: 816
    },
    {
      month: '2月',
      value: 542
    },
    {
      month: '3月',
      value: 914
    },
    {
      month: '4月',
      value: 781
    },
    {
      month: '5月',
      value: 355
    },
    {
      month: '6月',
      value: 796
    },
    {
      month: '7月',
      value: 714
    },
    {
      month: '8月',
      value: 1195
    },
    {
      month: '9月',
      value: 1055
    },
    {
      month: '10月',
      value: 271
    },
    {
      month: '11月',
      value: 384
    },
    {
      month: '12月',
      value: 1098
    }
  ];

  const saleChartOption: EChartsCoreOption = reactive({
    animation: false,
    tooltip: { trigger: 'axis' },
    xAxis: [
      {
        type: 'category',
        data: chartData.map((d) => d.month)
      }
    ],
    yAxis: [{ type: 'value' }],
    series: [
      {
        type: 'bar',
        data: chartData.map((d) => d.value),
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#b0d0ff' },
              { offset: 0.4, color: '#80a9fa' },
              { offset: 1, color: '#5b8ff9' }
            ]
          }
        }
      }
    ]
  });

  const chartData2 = [
    {
      time: '16:00',
      visits: 15,
      views: 45
    },
    {
      time: '16:05',
      visits: 39,
      views: 169
    },
    {
      time: '16:10',
      visits: 152,
      views: 400
    },
    {
      time: '16:15',
      visits: 94,
      views: 285
    },
    {
      time: '16:20',
      visits: 102,
      views: 316
    },
    {
      time: '16:25',
      visits: 86,
      views: 148
    },
    {
      time: '16:30',
      visits: 39,
      views: 150
    },
    {
      time: '16:35',
      visits: 38,
      views: 234
    },
    {
      time: '16:40',
      visits: 95,
      views: 158
    },
    {
      time: '16:45',
      visits: 30,
      views: 100
    },
    {
      time: '16:50',
      visits: 86,
      views: 266
    }
  ];

  const visitHourChartOption: EChartsCoreOption = reactive({
    animation: false,
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['浏览量', '访问量'],
      right: 20
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: chartData2.map((d) => d.time)
      }
    ],
    yAxis: [{ type: 'value' }],
    series: [
      {
        name: '浏览量',
        type: 'line',
        smooth: true,
        symbol: 'none',
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(91, 143, 249, 0.6)' },
              { offset: 1, color: 'rgba(91, 143, 249, 0.2)' }
            ]
          }
        },
        data: chartData2.map((d) => d.views)
      },
      {
        name: '访问量',
        type: 'line',
        smooth: true,
        symbol: 'none',
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(97, 221, 170, 0.6)' },
              { offset: 1, color: 'rgba(97, 221, 170, 0.2)' }
            ]
          }
        },
        data: chartData2.map((d) => d.visits)
      }
    ]
  });

  const chartData3 = [
    {
      name: 'Chrome',
      value: 9052
    },
    {
      name: 'Safari',
      value: 535
    },
    {
      name: 'Firefox',
      value: 1610
    },
    {
      name: 'Edge',
      value: 2800
    },
    {
      name: 'IE',
      value: 3200
    },
    {
      name: 'Other',
      value: 1700
    }
  ];

  const browserChartOption: EChartsCoreOption = reactive({
    animation: false,
    tooltip: {
      trigger: 'item',
      confine: true,
      borderWidth: 1
    },
    legend: {
      bottom: 5,
      itemWidth: 10,
      itemHeight: 10,
      icon: 'circle',
      data: chartData3.map((d) => d.name)
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '43%'],
        label: { show: false },
        data: chartData3,
        itemStyle: { borderRadius: 6 }
      }
    ]
  });
</script>
