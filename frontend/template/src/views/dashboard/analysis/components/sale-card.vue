<template>
  <ele-card
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
    :body-style="{ padding: 0 }"
  >
    <template #header>
      <ele-tabs
        type="plain"
        size="large"
        v-model="saleSearch.type"
        :items="[
          { name: 'saleroom', label: '销售额' },
          { name: 'visits', label: '访问量' }
        ]"
        @tabChange="handleSaleTypeChange"
      />
    </template>
    <template #extra>
      <div class="hidden-xs-only" style="display: flex; align-items: center">
        <el-radio-group
          v-model="saleSearch.dateType"
          @change="handleDateTypeChange"
        >
          <el-radio-button value="1" label="今天" />
          <el-radio-button value="2" label="本周" />
          <el-radio-button value="3" label="本月" />
          <el-radio-button value="4" label="本年" />
        </el-radio-group>
        <div class="hidden-md-and-down" style="width: 320px; margin-left: 12px">
          <el-date-picker
            unlink-panels
            type="datetimerange"
            v-model="saleSearch.datetime"
            range-separator="-"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            class="ele-fluid"
          />
        </div>
      </div>
    </template>
    <div class="sale-body">
      <el-row :gutter="16">
        <el-col :md="17" :sm="15" :xs="24">
          <div class="sale-body-title">
            {{ saleSearch.type === 'saleroom' ? '销售量趋势' : '访问量趋势' }}
          </div>
          <v-chart
            ref="saleChartRef"
            :option="saleChartOption"
            style="height: 320px"
            @click="handleSaleChartClick"
          />
        </el-col>
        <el-col :md="7" :sm="9" :xs="24">
          <div v-if="saleSearch.type === 'saleroom'" style="padding: 0 0 8px 0">
            <div class="sale-body-title">门店销售额排名</div>
            <div
              v-for="(item, index) in saleroomRankData"
              :key="index"
              class="sale-rank-item"
            >
              <el-tag
                size="small"
                :disable-transitions="true"
                :type="index < 3 ? void 0 : 'info'"
                :effect="index < 3 ? 'dark' : 'light'"
                :color="index < 3 ? '#314659' : void 0"
                style="border: none; border-radius: 50%; width: 20px"
              >
                {{ index + 1 }}
              </el-tag>
              <ele-ellipsis class="sale-rank-item-text">
                {{ item.name }}
              </ele-ellipsis>
              <ele-text type="placeholder">{{ item.value }}</ele-text>
            </div>
          </div>
          <div v-else style="padding: 0 0 8px 0">
            <div class="sale-body-title">门店访问量排名</div>
            <div
              v-for="(item, index) in visitsRankData"
              :key="index"
              class="sale-rank-item"
            >
              <el-tag
                size="small"
                :disable-transitions="true"
                :type="index < 3 ? void 0 : 'info'"
                :effect="index < 3 ? 'dark' : 'light'"
                :color="index < 3 ? '#314659' : void 0"
                style="border: none; border-radius: 50%; width: 20px"
              >
                {{ index + 1 }}
              </el-tag>
              <ele-ellipsis class="sale-rank-item-text">
                {{ item.name }}
              </ele-ellipsis>
              <ele-text type="placeholder">{{ item.value }}</ele-text>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import dayjs from 'dayjs';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { getSaleroomList } from '@/api/dashboard/analysis';
  import type { SaleroomData } from '@/api/dashboard/analysis/model';
  import { useEcharts } from '@/utils/use-echarts';

  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

  const saleChartRef = ref<InstanceType<typeof VChart> | null>(null);

  useEcharts([saleChartRef]);

  /** 销售额柱状图配置 */
  const saleChartOption: EChartsCoreOption = reactive({});

  /** 门店销售排名数据 */
  const saleroomRankData = ref([
    { name: '工专路 1 号店', value: '333,001' },
    { name: '工专路 2 号店', value: '333,002' },
    { name: '工专路 3 号店', value: '333,003' },
    { name: '工专路 4 号店', value: '333,004' },
    { name: '工专路 5 号店', value: '333,005' },
    { name: '工专路 6 号店', value: '333,006' },
    { name: '工专路 7 号店', value: '333,007' }
  ]);

  /** 门店访问排名数据 */
  const visitsRankData = ref([
    { name: '工专路 1 号店', value: '222,001' },
    { name: '工专路 2 号店', value: '222,002' },
    { name: '工专路 3 号店', value: '222,002' },
    { name: '工专路 4 号店', value: '222,004' },
    { name: '工专路 5 号店', value: '222,005' },
    { name: '工专路 6 号店', value: '222,006' },
    { name: '工专路 7 号店', value: '222,007' }
  ]);

  /** 销售量趋势数据 */
  const saleroomData1 = ref<SaleroomData[]>([]);

  /** 访问量趋势数据 */
  const saleroomData2 = ref<SaleroomData[]>([]);

  interface SaleSearchType {
    type: string;
    dateType: string;
    datetime?: [string, string];
  }

  /** 销售量搜索参数 */
  const saleSearch = reactive<SaleSearchType>({
    type: 'saleroom',
    dateType: '2',
    datetime: void 0
  });

  /** 获取销售量数据 */
  const getSaleroomData = () => {
    getSaleroomList()
      .then((data) => {
        saleroomData1.value = data.list1;
        saleroomData2.value = data.list2;
        handleSaleTypeChange();
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 销售量tab选择改变事件 */
  const handleSaleTypeChange = () => {
    const chartData =
      saleSearch.type === 'saleroom'
        ? saleroomData1.value
        : saleroomData2.value;
    Object.assign(saleChartOption, {
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
  };

  /** 图表点击事件 */
  const handleSaleChartClick = (params: any) => {
    const type = saleSearch.type === 'saleroom' ? '销售量' : '访问量';
    EleMessage.info({
      message: `点击了: ${params.name} , ${type}: ${params.value}`,
      plain: true
    });
  };

  /** 日期单选切换事件 */
  const handleDateTypeChange = (dateType: string) => {
    const type: any = ['day', 'week', 'month', 'year'][Number(dateType) - 1];
    const now = dayjs();
    const formatter = 'YYYY-MM-DD HH:mm';
    const start = now.startOf(type).format(formatter);
    const end = now.endOf(type).format(formatter);
    saleSearch.datetime = [start, end];
  };

  handleDateTypeChange('2');

  getSaleroomData();
</script>

<style lang="scss" scoped>
  .sale-body {
    padding: 16px 0 10px 0;
  }

  .sale-body-title {
    padding: 6px 20px;
  }

  .sale-rank-item {
    display: flex;
    align-items: center;
    padding: 0 20px;
    margin-top: 18px;
    box-sizing: border-box;

    .sale-rank-item-text {
      flex: 1;
      padding-left: 12px;
    }
  }
</style>
