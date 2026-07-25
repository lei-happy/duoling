<!--
  大厅筛选条

  两个大厅共用：差异只有「台数 / 板位」和「货物类别」两处，按 postType 显隐。
  可选项（货物类别、计价方式）由 `/filters` 下发，前端不再抄一份枚举。

  时间做成「7 天内」这类预设而不是日期区间：找货的人想的是「这两天能装的」，
  让他去点两次日历只会更慢。需要精确区间的场景一期先不做。
-->
<template>
  <ele-card :body-style="{ paddingBottom: '4px' }">
    <el-form label-width="64px" class="eco-filter" @submit.prevent="emitSearch">
      <el-row :gutter="12">
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item label="出发地">
            <regions-select
              v-model="fromRegion"
              type="provinceCity"
              value-field="label"
              placeholder="全部出发地"
              @change="emitSearch"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item
            :label="postType === PostType.CARGO ? '目的地' : '流向'"
          >
            <regions-select
              v-model="toProvinces"
              type="province"
              value-field="label"
              multiple
              :cascader-props="{ emitPath: false }"
              placeholder="全部省份"
              @change="emitSearch"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item :label="postType === PostType.CARGO ? '装车' : '可用'">
            <el-select v-model="windowKey" @change="emitSearch">
              <el-option
                v-for="item in WINDOW_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item :label="quantityLabel">
            <div class="eco-filter__range">
              <el-input-number
                v-model="rangeMin"
                :min="1"
                :max="99"
                :controls="false"
                placeholder="最少"
                class="eco-filter__range-input"
              />
              <span class="eco-filter__range-split">-</span>
              <el-input-number
                v-model="rangeMax"
                :min="1"
                :max="99"
                :controls="false"
                placeholder="最多"
                class="eco-filter__range-input"
              />
            </div>
          </el-form-item>
        </el-col>

        <el-col v-if="cargoCategories.length" :lg="6" :md="12" :xs="24">
          <el-form-item label="货物">
            <el-select
              v-model="form.cargoCategory"
              clearable
              placeholder="全部货类"
              @change="emitSearch"
            >
              <el-option
                v-for="item in cargoCategories"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item label="计价">
            <el-select
              v-model="form.priceType"
              clearable
              placeholder="全部计价方式"
              @change="emitSearch"
            >
              <el-option
                v-for="item in filters?.priceTypes ?? []"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item label="关键字">
            <el-input
              v-model="form.keyword"
              clearable
              placeholder="线路、地名或编号"
              @keyup.enter="emitSearch"
              @clear="emitSearch"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :xs="24">
          <el-form-item label-width="0">
            <div class="eco-filter__actions">
              <el-checkbox v-model="form.onlyVerified" @change="emitSearch">
                只看已认证
              </el-checkbox>
              <el-checkbox v-model="form.onlyHighCredit" @change="emitSearch">
                <el-tooltip
                  content="完成率 90% 以上、评分 4.5 以上的企业"
                  placement="top"
                >
                  <span>只看优质企业</span>
                </el-tooltip>
              </el-checkbox>
              <el-button link type="primary" @click="reset">重置</el-button>
            </div>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import RegionsSelect from '@/components/RegionsSelect/index.vue';
  import type {
    EcoHallFilters,
    EcoHallParam
  } from '@/api/ecosystem/hall/model';
  import { PostType } from '@/config/ecosystem/enums';

  const props = defineProps<{
    postType: number;
    filters?: EcoHallFilters | null;
  }>();

  const emit = defineEmits<{
    (e: 'search', params: EcoHallParam): void;
  }>();

  /** 时间预设。value 是天数，0 表示不限 */
  const WINDOW_OPTIONS = [
    { value: 0, label: '不限时间' },
    { value: 1, label: '今天' },
    { value: 3, label: '3 天内' },
    { value: 7, label: '7 天内' },
    { value: 15, label: '15 天内' }
  ];

  const form = reactive<EcoHallParam>({
    keyword: undefined,
    cargoCategory: undefined,
    priceType: undefined,
    onlyVerified: false,
    onlyHighCredit: false
  });

  /** 级联组件给的是 [省, 市] 路径 */
  const fromRegion = ref<string[]>([]);
  const toProvinces = ref<string[]>([]);
  const windowKey = ref(0);
  const rangeMin = ref<number | undefined>(undefined);
  const rangeMax = ref<number | undefined>(undefined);

  const cargoCategories = computed(() => props.filters?.cargoCategories ?? []);

  const quantityLabel = computed(() =>
    props.postType === PostType.CARGO ? '台数' : '板位'
  );

  /** 台数区间输错顺序很常见，提交前兜一下，别让用户看到空结果去猜原因 */
  const normalizedRange = computed(() => {
    const min = rangeMin.value ?? undefined;
    const max = rangeMax.value ?? undefined;
    if (min != null && max != null && min > max) {
      return { min: max, max: min };
    }
    return { min, max };
  });

  function windowRange() {
    const days = windowKey.value;
    if (!days) {
      return {};
    }
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const end = new Date(start);
    end.setDate(end.getDate() + days);
    end.setSeconds(end.getSeconds() - 1);
    return { windowStartFrom: fmt(start), windowStartTo: fmt(end) };
  }

  function fmt(date: Date) {
    const pad = (n: number) => String(n).padStart(2, '0');
    return (
      `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
      ` ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
    );
  }

  function buildParams(): EcoHallParam {
    const { min, max } = normalizedRange.value;
    const isCargo = props.postType === PostType.CARGO;
    return {
      ...form,
      keyword: form.keyword?.trim() || undefined,
      fromProvince: fromRegion.value?.[0] || undefined,
      fromCity: fromRegion.value?.[1] || undefined,
      toProvinces: toProvinces.value?.length
        ? [...toProvinces.value]
        : undefined,
      // 货源筛的是台数，运力筛的是板位数，后端是两个不同的参数
      quantityMin: isCargo ? min : undefined,
      quantityMax: isCargo ? max : undefined,
      slotMin: isCargo ? undefined : min,
      slotMax: isCargo ? undefined : max,
      ...windowRange()
    };
  }

  const emitSearch = () => {
    emit('search', buildParams());
  };

  const reset = () => {
    form.keyword = undefined;
    form.cargoCategory = undefined;
    form.priceType = undefined;
    form.onlyVerified = false;
    form.onlyHighCredit = false;
    fromRegion.value = [];
    toProvinces.value = [];
    windowKey.value = 0;
    rangeMin.value = undefined;
    rangeMax.value = undefined;
    emitSearch();
  };

  // 台数区间用数字输入框，没有 change 时机可靠地触发查询；这里做 400ms 防抖
  let rangeTimer: ReturnType<typeof setTimeout> | undefined;
  watch([rangeMin, rangeMax], () => {
    if (rangeTimer) {
      clearTimeout(rangeTimer);
    }
    rangeTimer = setTimeout(emitSearch, 400);
  });

  defineExpose({ buildParams });
</script>

<style lang="scss" scoped>
  .eco-filter {
    :deep(.el-form-item) {
      margin-bottom: 12px;
    }
  }

  .eco-filter__range {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
  }

  .eco-filter__range-input {
    flex: 1 1 0;
    min-width: 0;

    :deep(.el-input__inner) {
      text-align: left;
    }
  }

  .eco-filter__range-split {
    color: var(--el-text-color-placeholder);
  }

  .eco-filter__actions {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
</style>
