<template>
  <ele-page class="smart-stowage-page">
    <!-- 非专业版：升级引导 -->
    <ele-card v-if="!featureEnabled" class="smart-stowage-page__upgrade">
      <el-result
        icon="warning"
        title="智能配载为专业版功能"
        sub-title="通过 AI 算法自动推荐商品车组合成配载单，最大化运力利用率。升级专业版即可使用。"
      >
        <template #extra>
          <el-button type="primary" @click="goUpgrade">查看版本方案</el-button>
        </template>
      </el-result>
    </ele-card>

    <template v-else>
      <!-- 筛选 + 生成 -->
      <ele-card
        class="smart-stowage-page__filter"
        :body-style="{ padding: '16px' }"
      >
        <el-form
          :inline="true"
          :model="filter"
          class="smart-stowage-page__form"
        >
          <el-form-item label="起点">
            <el-input
              v-model="filter.originKeyword"
              placeholder="起点关键字"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="终点">
            <el-input
              v-model="filter.destinationKeyword"
              placeholder="终点关键字"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="品牌/车型">
            <el-input
              v-model="filter.modelKeyword"
              placeholder="品牌或车型"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="板车车位">
            <el-input-number
              v-model="filter.targetSpots"
              :min="1"
              :max="30"
              controls-position="right"
              style="width: 110px"
            />
          </el-form-item>
          <el-form-item label="装载率下限">
            <el-input-number
              v-model="filter.minLoadRate"
              :min="0"
              :max="100"
              :step="5"
              controls-position="right"
              style="width: 120px"
            />
            <span class="smart-stowage-page__unit">%</span>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :icon="MagicStick"
              :loading="generating"
              @click="handleGenerate"
            >
              一键生成方案
            </el-button>
          </el-form-item>
        </el-form>
      </ele-card>

      <!-- 结果 -->
      <ele-card
        class="smart-stowage-page__result"
        :body-style="{ padding: '16px' }"
        v-loading="generating"
      >
        <template v-if="task">
          <div class="smart-stowage-page__summary">
            <el-tag type="info" effect="plain">
              候选商品车行：{{ task.candidateCount }}
            </el-tag>
            <el-tag type="success" effect="plain">
              推荐方案：{{ task.planCount }}
            </el-tag>
            <el-tag v-if="task.adoptedCount > 0" type="warning" effect="plain">
              已采纳：{{ task.adoptedCount }}
            </el-tag>
          </div>
        </template>

        <el-empty
          v-if="!generating && plans.length === 0"
          :description="
            task
              ? '未生成可行方案，请调整筛选条件或装载率下限'
              : '设置条件后点击「一键生成方案」'
          "
        />

        <div v-else class="smart-stowage-page__plans">
          <el-card
            v-for="plan in plans"
            :key="plan.id"
            class="stowage-plan-card"
            :class="{
              'is-adopted': plan.status === 1,
              'is-ignored': plan.status === 2
            }"
            shadow="hover"
          >
            <div class="stowage-plan-card__head">
              <div class="stowage-plan-card__title">
                <span class="stowage-plan-card__no"
                  >方案 {{ plan.planNo }}</span
                >
                <span class="stowage-plan-card__line">
                  {{ plan.origin || '未知' }}
                  <el-icon><Right /></el-icon>
                  {{ plan.destination || '未知' }}
                </span>
              </div>
              <el-tag
                v-if="plan.status === 1"
                type="success"
                size="small"
                effect="dark"
              >
                已采纳
              </el-tag>
              <el-tag v-else-if="plan.status === 2" type="info" size="small">
                已忽略
              </el-tag>
            </div>

            <div class="stowage-plan-card__metrics">
              <div class="stowage-plan-card__load">
                <el-progress
                  type="dashboard"
                  :width="88"
                  :percentage="Math.round(plan.loadRate)"
                  :color="loadColor(plan.loadRate)"
                >
                  <template #default>
                    <span class="stowage-plan-card__load-val">
                      {{ Math.round(plan.loadRate) }}%
                    </span>
                    <span class="stowage-plan-card__load-label">装载率</span>
                  </template>
                </el-progress>
              </div>
              <ul class="stowage-plan-card__kpis">
                <li
                  ><b>{{ plan.vehicleCount }}</b> 台商品车</li
                >
                <li
                  >占位 <b>{{ plan.occupiedSpots }}</b> /
                  {{ plan.targetSpots }} 车位</li
                >
                <li
                  >{{ plan.customerCount }} 家客户 ·
                  {{ plan.waybillCount }} 张运单</li
                >
                <li class="stowage-plan-card__score"
                  >评分 {{ plan.score.toFixed(3) }}</li
                >
              </ul>
            </div>

            <div class="stowage-plan-card__reason">
              <el-icon><InfoFilled /></el-icon>
              {{ plan.reason }}
            </div>

            <el-collapse class="stowage-plan-card__detail">
              <el-collapse-item
                :title="`商品车明细（${plan.items.length} 行）`"
              >
                <el-table
                  :data="plan.items"
                  size="small"
                  border
                  max-height="220"
                >
                  <el-table-column
                    prop="waybillNo"
                    label="运单号"
                    width="130"
                  />
                  <el-table-column
                    prop="customerName"
                    label="客户"
                    min-width="100"
                  />
                  <el-table-column label="品牌车型" min-width="130">
                    <template #default="{ row }">
                      {{
                        [row.vehicleBrand, row.vehicleModel]
                          .filter(Boolean)
                          .join(' ')
                      }}
                    </template>
                  </el-table-column>
                  <el-table-column
                    prop="quantity"
                    label="台数"
                    width="70"
                    align="center"
                  />
                  <el-table-column
                    prop="occupyCoefficient"
                    label="占位系数"
                    width="90"
                    align="center"
                  />
                </el-table>
              </el-collapse-item>
            </el-collapse>

            <div class="stowage-plan-card__actions">
              <el-button
                v-if="plan.status === 0"
                type="primary"
                :icon="Check"
                :loading="adoptingId === plan.id"
                @click="handleAdopt(plan)"
              >
                采纳并建单
              </el-button>
              <el-button
                v-if="plan.status === 0"
                :icon="Close"
                @click="handleIgnore(plan)"
              >
                忽略
              </el-button>
              <el-button
                v-if="plan.status === 1 && plan.adoptedTaskId"
                link
                type="primary"
                @click="goWorkbench"
              >
                前往调度工作台
              </el-button>
            </div>
          </el-card>
        </div>
      </ele-card>
    </template>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    Check,
    Close,
    InfoFilled,
    MagicStick,
    Right
  } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { useUserStore } from '@/store/modules/user';
  import {
    adoptStowagePlan,
    generateStowagePlans,
    ignoreStowagePlan
  } from '@/api/operation/smart-stowage';
  import type {
    SmartStowagePlan,
    SmartStowageTask
  } from '@/api/operation/smart-stowage/model';

  defineOptions({ name: 'OperationSmartStowage' });

  const router = useRouter();
  const userStore = useUserStore();

  const featureEnabled = computed(() => userStore.hasFeature('smart_stowage'));

  const filter = reactive({
    originKeyword: '',
    destinationKeyword: '',
    modelKeyword: '',
    targetSpots: 8,
    minLoadRate: 40
  });

  const generating = ref(false);
  const adoptingId = ref<number | null>(null);
  const task = ref<SmartStowageTask | null>(null);
  const plans = ref<SmartStowagePlan[]>([]);

  const loadColor = (rate: number) => {
    if (rate >= 85) return '#67c23a';
    if (rate >= 60) return '#e6a23c';
    return '#f56c6c';
  };

  const handleGenerate = async () => {
    if (generating.value) return;
    generating.value = true;
    try {
      const res = await generateStowagePlans({
        originKeyword: filter.originKeyword || undefined,
        destinationKeyword: filter.destinationKeyword || undefined,
        modelKeyword: filter.modelKeyword || undefined,
        targetSpots: filter.targetSpots,
        minLoadRate: filter.minLoadRate
      });
      if (!res) return;
      task.value = res.task;
      plans.value = res.plans;
      if (res.plans.length > 0) {
        EleMessage.success({
          message: `已生成 ${res.plans.length} 个配载方案`,
          plain: true
        });
      }
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '生成失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      generating.value = false;
    }
  };

  const handleAdopt = async (plan: SmartStowagePlan) => {
    if (adoptingId.value) return;
    adoptingId.value = plan.id;
    try {
      const res = await adoptStowagePlan(plan.id, plan.reason);
      plan.status = 1;
      plan.adoptedTaskId = res?.taskId;
      if (task.value) task.value.adoptedCount += 1;
      EleMessage.success({ message: '已采纳并创建配载单', plain: true });
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '采纳失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      adoptingId.value = null;
    }
  };

  const handleIgnore = async (plan: SmartStowagePlan) => {
    try {
      await ignoreStowagePlan(plan.id);
      plan.status = 2;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '操作失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const goUpgrade = () => {
    router.push('/upgrade-plans').catch(() => {});
  };

  const goWorkbench = () => {
    router.push('/operation/task-workbench').catch(() => {});
  };
</script>

<style scoped lang="scss">
  .smart-stowage-page {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    gap: 12px;
  }

  .smart-stowage-page__form {
    display: flex;
    flex-wrap: wrap;
    row-gap: 8px;
  }

  .smart-stowage-page__unit {
    margin-left: 4px;
    color: var(--el-text-color-secondary);
  }

  .smart-stowage-page__result {
    flex: 1;
    min-height: 0;
    overflow: auto;
  }

  .smart-stowage-page__summary {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }

  .smart-stowage-page__plans {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 16px;
  }

  .stowage-plan-card {
    border-radius: 8px;

    &.is-adopted {
      border-color: var(--el-color-success);
    }

    &.is-ignored {
      opacity: 0.6;
    }

    &__head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    &__title {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    &__no {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    &__line {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 16px;
      font-weight: 600;
    }

    &__metrics {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    &__load-val {
      display: block;
      font-size: 18px;
      font-weight: 600;
    }

    &__load-label {
      display: block;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    &__kpis {
      flex: 1;
      margin: 0;
      padding: 0;
      list-style: none;
      font-size: 13px;
      line-height: 1.9;
      color: var(--el-text-color-regular);

      b {
        color: var(--el-text-color-primary);
        font-size: 15px;
      }
    }

    &__score {
      color: var(--el-color-primary);
    }

    &__reason {
      display: flex;
      align-items: flex-start;
      gap: 6px;
      margin: 12px 0;
      padding: 8px 10px;
      font-size: 13px;
      line-height: 1.6;
      color: var(--el-text-color-regular);
      background: var(--el-fill-color-light);
      border-radius: 6px;

      .el-icon {
        margin-top: 2px;
        color: var(--el-color-primary);
      }
    }

    &__actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }
  }
</style>
