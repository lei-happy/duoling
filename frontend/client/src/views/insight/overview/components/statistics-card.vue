<!-- 统计卡片 -->
<template>
  <el-row :gutter="16">
    <el-col :md="6" :sm="12" :xs="24">
      <ele-card class="statistics-card">
        <ele-text type="placeholder" class="statistics-header">
          <div class="statistics-header-text">总销售额</div>
          <ele-tooltip content="指标说明" placement="top" :offset="6">
            <el-icon class="statistics-header-tip">
              <QuestionCircleOutlined />
            </el-icon>
          </ele-tooltip>
        </ele-text>
        <ele-text size="xxl" class="statistics-value">¥ 126,560</ele-text>
        <div class="statistics-body">
          <div class="statistics-trend-text">
            <div>周同比12%</div>
            <ele-text type="danger" :icon="CaretUpFilled" />
          </div>
          <div class="statistics-trend-text">
            <div>日同比11%</div>
            <ele-text type="success" :icon="CaretDownFilled" />
          </div>
        </div>
        <el-divider />
        <div>日销售额 ￥12,423</div>
      </ele-card>
    </el-col>
    <el-col :md="6" :sm="12" :xs="24">
      <ele-card class="statistics-card">
        <ele-text type="placeholder" class="statistics-header">
          <div class="statistics-header-text">访问量</div>
          <el-tag type="danger" size="small" :disable-transitions="true">
            日
          </el-tag>
        </ele-text>
        <ele-text size="xxl" class="statistics-value">8,846</ele-text>
        <v-chart
          ref="visitChartRef"
          :option="visitChartOption"
          style="height: 36px"
        />
        <el-divider />
        <div>日访问量 1,234</div>
      </ele-card>
    </el-col>
    <el-col :md="6" :sm="12" :xs="24">
      <ele-card class="statistics-card">
        <ele-text type="placeholder" class="statistics-header">
          <div class="statistics-header-text">支付笔数</div>
          <el-tag size="small" :disable-transitions="true">月</el-tag>
        </ele-text>
        <ele-text size="xxl" class="statistics-value">6,560</ele-text>
        <v-chart
          ref="payNumChartRef"
          :option="payNumChartOption"
          style="height: 36px"
        />
        <el-divider />
        <div>转化率 60%</div>
      </ele-card>
    </el-col>
    <el-col :md="6" :sm="12" :xs="24">
      <ele-card class="statistics-card">
        <ele-text type="placeholder" class="statistics-header">
          <div class="statistics-header-text">活动运营效果</div>
          <el-tag type="success" size="small" :disable-transitions="true">
            周
          </el-tag>
        </ele-text>
        <ele-text size="xxl" class="statistics-value">78%</ele-text>
        <div class="statistics-body">
          <el-progress
            color="linear-gradient(to right, #52C41A, #13c2c2  68%)"
            :percentage="78"
            :show-text="false"
            :stroke-width="8"
            style="width: 100%"
          />
        </div>
        <el-divider />
        <div class="statistics-footer">
          <div class="statistics-trend-text">
            <div>周同比12% </div>
            <ele-text type="danger" :icon="CaretUpFilled" />
          </div>
          <div class="statistics-trend-text">
            <div>日同比11% </div>
            <ele-text type="success" :icon="CaretDownFilled" />
          </div>
        </div>
      </ele-card>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { LineChart, BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import {
    QuestionCircleOutlined,
    CaretUpFilled,
    CaretDownFilled
  } from '@/components/icons';
  import { getPayNumList } from '@/api/dashboard/analysis';
  import { useEcharts } from '@/utils/use-echarts';

  use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent]);

  /** 访问量图表 */
  const visitChartRef = ref<InstanceType<typeof VChart> | null>(null);

  /** 支付笔数图表 */
  const payNumChartRef = ref<InstanceType<typeof VChart> | null>(null);

  useEcharts([visitChartRef, payNumChartRef]);

  /** 访问量折线图配置 */
  const visitChartOption: EChartsCoreOption = reactive({});

  /** 支付笔数柱状图配置 */
  const payNumChartOption: EChartsCoreOption = reactive({});

  /** 获取支付笔数数据 */
  const getPayNumData = () => {
    getPayNumList()
      .then((data) => {
        Object.assign(visitChartOption, {
          color: '#975fe5',
          tooltip: {
            trigger: 'axis',
            formatter: `<i style="background: #975fe5;
                                  width: 10px;
                                  height: 10px;
                                  margin-right: 5px;
                                  border-radius: 50%;
                                  display: inline-block;"
                        ></i>{b0}: {c0}`
          },
          grid: { top: 0, bottom: 0, left: 0, right: 0 },
          xAxis: [
            {
              show: false,
              type: 'category',
              boundaryGap: false,
              data: data.map((d) => d.date)
            }
          ],
          yAxis: [
            {
              show: false,
              type: 'value',
              splitLine: { show: false }
            }
          ],
          series: [
            {
              type: 'line',
              smooth: true,
              symbol: 'none',
              lineStyle: { width: 1.38 },
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: 'rgba(151, 95, 229, 0.6)' },
                    { offset: 1, color: 'rgba(151, 95, 229, 0.2)' }
                  ]
                }
              },
              data: data.map((d) => d.value)
            }
          ]
        });

        Object.assign(payNumChartOption, {
          tooltip: {
            trigger: 'axis',
            formatter: `<i style="background: #5b8ff9;
                                  width: 10px;
                                  height: 10px;
                                  margin-right: 5px;
                                  border-radius: 50%;
                                  display: inline-block;"
                        ></i>{b0}: {c0}`
          },
          grid: { top: 0, bottom: 0, left: 0, right: 0 },
          xAxis: [
            {
              show: false,
              type: 'category',
              data: data.map((d) => d.date)
            }
          ],
          yAxis: [
            {
              show: false,
              type: 'value',
              splitLine: { show: false }
            }
          ],
          series: [
            {
              type: 'bar',
              data: data.map((d) => d.value),
              itemStyle: {
                borderRadius: [2, 2, 0, 0],
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
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  getPayNumData();
</script>

<style lang="scss" scoped>
  .statistics-card {
    :deep(.ele-card-body) {
      padding: 16px 22px 12px 22px;
    }

    :deep(.el-divider) {
      margin: 12px 0;
      opacity: 0.6;
    }

    .statistics-header {
      display: flex;
      align-items: center;

      .statistics-header-text {
        flex: 1;
      }

      .statistics-header-tip {
        font-size: 15px;
        cursor: help;
      }
    }

    .statistics-value {
      margin-top: 4px;
    }

    .statistics-body {
      height: 36px;
      display: flex;
      padding-top: 18px;
      box-sizing: border-box;
    }

    .statistics-trend-text {
      display: flex;
      align-items: center;
      white-space: nowrap;
      word-break: break-all;
      overflow: hidden;

      .el-icon {
        font-size: 16px;
        margin-left: 4px;
      }

      & + .statistics-trend-text {
        margin-left: 14px;
      }
    }

    .statistics-footer {
      display: flex;
      align-items: center;
    }
  }
</style>
