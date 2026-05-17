<template>
  <el-dialog
    :title="isEdit ? '编辑运单' : '新增运单'"
    :model-value="visible"
    width="880px"
    draggable
    class="waybill-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    append-to-body
    destroy-on-close
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="waybill-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-tabs
        v-model="activeTab"
        class="waybill-edit-tabs"
        @tab-change="onTabChange"
      >
        <el-tab-pane name="basic">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': basicStepDone }"
              >
                <el-icon v-if="basicStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('basic') }}</template>
              </span>
              <span class="waybill-tab-text">基础信息</span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <el-row :gutter="10">
              <el-col :xs="24" :sm="12">
                <el-form-item prop="customerId">
                  <floating-label
                    v-model="form.customerId"
                    label="请选择客户"
                    type="select"
                    filterable
                    :filter-method="setCustomerFilter"
                    clearable
                    @change="onCustomerChange"
                  >
                    <el-option
                      v-for="item in customersShown"
                      :key="item.id"
                      :label="item.customerName"
                      :value="item.id"
                    />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item prop="waybillNo">
                  <floating-label
                    label="运单编号（唯一）"
                    type="input"
                    v-model.trim="form.waybillNo"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item prop="originCode">
                  <floating-label
                    label="请选择出发地"
                    type="cascader"
                    v-model="originCodes"
                    :cascader-options="regionTree"
                    :cascader-option-props="regionCascaderProps"
                    :cascader-filterable="true"
                    @change="onOriginChange"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item prop="destinationCode">
                  <floating-label
                    label="请选择目的地"
                    type="cascader"
                    v-model="destCodes"
                    :cascader-options="regionTree"
                    :cascader-option-props="regionCascaderProps"
                    :cascader-filterable="true"
                    @change="onDestChange"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item prop="planIssueTime">
                  <floating-label
                    label="计划下达时间"
                    type="date"
                    date-type="datetime"
                    v-model="form.planIssueTime"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item prop="requiredDeliverTime">
                  <floating-label
                    label="要求送达时间"
                    type="date"
                    date-type="datetime"
                    v-model="form.requiredDeliverTime"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane name="cargo">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': cargoStepDone }"
              >
                <el-icon v-if="cargoStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('cargo') }}</template>
              </span>
              <span class="waybill-tab-text">
                商品车信息
                <span v-if="cargoTabTotalVisible" class="waybill-tab-sub">
                  · 合计 {{ cargoTotalQty }} 台
                </span>
              </span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <div
              v-for="(row, idx) in cargoRows"
              :key="idx"
              class="waybill-cargo-row"
            >
              <div class="waybill-cargo-row__line">
                <div class="waybill-cargo-row__meta">
                  <span class="waybill-cargo-row__label"
                    >商品车 {{ idx + 1 }}</span
                  >
                  <el-button
                    v-if="cargoRows.length > 1"
                    type="danger"
                    link
                    size="small"
                    class="waybill-cargo-row__del"
                    @click="removeCargoRow(idx)"
                  >
                    删除
                  </el-button>
                </div>
                <div class="waybill-cargo-row__fields">
                  <el-form-item
                    class="waybill-cargo-field waybill-cargo-field--brand"
                  >
                    <floating-label
                      v-model="row.vehicleBrand"
                      label="品牌"
                      type="select"
                      filterable
                      :filter-method="setBrandFilter"
                      clearable
                      @change="() => onCargoBrandChange(row)"
                    >
                      <el-option
                        v-for="b in brandsShown"
                        :key="b.brandId"
                        :label="b.brandNameCn"
                        :value="b.brandNameCn"
                      />
                    </floating-label>
                  </el-form-item>
                  <el-form-item
                    class="waybill-cargo-field waybill-cargo-field--model"
                  >
                    <floating-label
                      v-model="row.vehicleModel"
                      label="车型"
                      type="select"
                      filterable
                      :filter-method="setSeriesFilter"
                      :disabled="!row.brandId"
                      clearable
                    >
                      <el-option
                        v-for="s in seriesShownForRow(row)"
                        :key="s.seriesId"
                        :label="s.seriesName"
                        :value="s.seriesName"
                      />
                    </floating-label>
                  </el-form-item>
                  <el-form-item
                    class="waybill-cargo-field waybill-cargo-field--qty"
                  >
                    <floating-label
                      label="台数"
                      type="input"
                      input-type="number"
                      v-model="row.quantityStr"
                      clearable
                      @blur="normalizeCargoQty(row)"
                    />
                  </el-form-item>
                </div>
              </div>
            </div>
            <el-button
              type="primary"
              plain
              class="waybill-cargo-add"
              @click="addCargoRow"
            >
              添加新车
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane name="receive">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': receiveStepDone }"
              >
                <el-icon v-if="receiveStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('receive') }}</template>
              </span>
              <span class="waybill-tab-text">收车信息</span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <el-row :gutter="10">
              <el-col :xs="24" :sm="8">
                <el-form-item prop="dealerName">
                  <floating-label
                    v-model="selectedDealerId"
                    label="收车门店"
                    type="select"
                    filterable
                    :filter-method="setDealerFilter"
                    clearable
                    @change="onDealerChange"
                  >
                    <el-option
                      v-for="d in dealersShown"
                      :key="d.dealerId"
                      :label="d.dealerName"
                      :value="d.dealerId"
                    />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item prop="dealerContact">
                  <floating-label
                    label="联系人姓名"
                    type="input"
                    v-model.trim="form.dealerContact"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item prop="dealerPhone">
                  <floating-label
                    label="联系电话"
                    type="input"
                    v-model.trim="form.dealerPhone"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item>
                  <floating-label
                    label="门店地址"
                    type="input"
                    v-model="form.dealerAddress"
                    :disabled="true"
                    :clearable="false"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane v-if="showFreightTab" name="freight">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': freightStepDone }"
              >
                <el-icon v-if="freightStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('freight') }}</template>
              </span>
              <span class="waybill-tab-text">运费信息</span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <template v-if="freightCalcMode !== 'auto_required'">
              <el-row :gutter="10" align="middle">
                <el-col :xs="24" :sm="10" :md="8">
                  <el-form-item prop="freightAmount">
                    <floating-label
                      label="请输入运费金额（元）"
                      type="input"
                      v-model="freightAmountStr"
                      clearable
                      @blur="syncFreightAmountFromStr"
                    />
                  </el-form-item>
                </el-col>
                <el-col
                  v-if="freightCalcMode !== 'manual_only'"
                  :xs="24"
                  :sm="14"
                  :md="16"
                >
                  <el-form-item
                    :label-width="0"
                    class="waybill-freight-actions"
                  >
                    <el-button
                      type="success"
                      :loading="calcLoading"
                      @click="calcFreight"
                    >
                      计算运费
                    </el-button>
                    <span v-if="calcHint" class="waybill-calc-hint">{{
                      calcHint
                    }}</span>
                  </el-form-item>
                </el-col>
              </el-row>
            </template>
            <template v-else>
              <p class="waybill-freight-auto-note">
                当前为运费自动必填模式，保存时将按商品车明细逐行匹配运价并汇总。
              </p>
            </template>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <div class="waybill-edit-dialog__footer">
        <el-button @click="updateVisible(false)">取消</el-button>
        <el-button :disabled="stepActive <= 0" @click="prevStep"
          >上一步</el-button
        >
        <el-button
          :disabled="isLastTabStep"
          type="primary"
          plain
          @click="onClickNextStep"
        >
          下一步
        </el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit"
          >保存</el-button
        >
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules, CascaderProps } from 'element-plus';
  import { CircleCheck } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    addWaybill,
    updateWaybill,
    getWaybill,
    checkWaybillNoAvailable
  } from '@/api/waybill';
  import { previewFreight } from '@/api/waybill';
  import { selectCustomers } from '@/api/partner/customer';
  import { listVehicleBrandOptions } from '@/api/basic-data/vehicle-brand';
  import { pageVehicleSeries } from '@/api/basic-data/vehicle-series';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import { pageDealers } from '@/api/basic-data/dealer';
  import { listConfigsByGroup } from '@/api/system/config';
  import type { Waybill } from '@/api/waybill/model';
  import type { FreightCalcResult } from '@/api/billing/contract/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import type { Dealer } from '@/api/basic-data/dealer/model';
  import {
    findLeafRegionByCodePath,
    findRegionCodePath
  } from '@/utils/region-nav-tree';
  import { pinyinMatch } from '@/utils/pinyin-match';

  /** 经销商全量分页较慢，短时缓存减轻重复打开弹窗等待 */
  let _waybillDealersCache: Dealer[] | null = null;
  let _waybillDealersCacheAt = 0;
  const WAYBILL_DEALERS_CACHE_MS = 45_000;

  type CargoEditRow = {
    vehicleBrand?: string;
    vehicleModel?: string;
    quantityStr: string;
    brandId?: number | null;
    seriesOptions: VehicleSeries[];
  };

  const TAB_ORDER = ['basic', 'cargo', 'receive', 'freight'] as const;
  type TabName = (typeof TAB_ORDER)[number];

  const freightCalcMode = ref('auto_preferred');
  /** 与系统设置 waybill.list_show_freight_amount 一致，默认不展示运费 Tab */
  const showFreightTab = ref(false);

  const visibleTabOrder = computed((): TabName[] =>
    showFreightTab.value ? [...TAB_ORDER] : ['basic', 'cargo', 'receive']
  );

  function tabStepNo(tab: TabName): number {
    const order = visibleTabOrder.value;
    const i = order.indexOf(tab);
    return i >= 0 ? i + 1 : 1;
  }

  const FIELD_TAB: Record<string, TabName> = {
    customerId: 'basic',
    waybillNo: 'basic',
    planIssueTime: 'basic',
    requiredDeliverTime: 'basic',
    originCode: 'basic',
    destinationCode: 'basic',
    dealerName: 'receive',
    dealerContact: 'receive',
    dealerPhone: 'receive',
    freightAmount: 'freight'
  };

  const props = defineProps<{
    visible: boolean;
    data: Waybill | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const activeTab = ref<TabName>('basic');
  const stepActive = computed(() => {
    const i = visibleTabOrder.value.indexOf(activeTab.value);
    return i >= 0 ? i : 0;
  });
  const isLastTabStep = computed(() => {
    const order = visibleTabOrder.value;
    const i = order.indexOf(activeTab.value);
    if (i < 0) return true;
    return i >= order.length - 1;
  });
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const calcLoading = ref(false);
  const calcResults = ref<(FreightCalcResult | null)[]>([]);
  const form = reactive<Waybill>({});
  const cargoRows = ref<CargoEditRow[]>([]);
  const freightAmountStr = ref('');

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const customerOptions = ref<CustomerSelectItem[]>([]);
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const regionTree = ref<RegionNavNode[]>([]);
  const dealerOptions = ref<Dealer[]>([]);
  const selectedDealerId = ref<number | null>(null);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);

  /** 按 Tab 懒加载：本弹窗内是否已拉品牌 / 经销商、是否已 hydrate 商品车下拉 */
  const brandsReadyThisOpen = ref(false);
  const dealersReadyThisOpen = ref(false);
  const cargoRowsSeriesHydrated = ref(false);

  const basicStepDone = computed(
    () =>
      !!(
        form.customerId &&
        form.waybillNo?.trim() &&
        form.originCode &&
        form.destinationCode
      )
  );

  /** 商品车明细台数合计（仅统计已填有效整数台数） */
  const cargoTotalQty = computed(() => {
    let sum = 0;
    for (const row of cargoRows.value) {
      const q = parseRowQty(row);
      if (Number.isFinite(q)) sum += q;
    }
    return sum;
  });

  const cargoStepDone = computed(() => {
    if (!cargoRows.value.length) return false;
    return cargoRows.value.every((r) => {
      const n = parseInt(String(r.quantityStr ?? '').trim(), 10);
      const qtyOk = Number.isFinite(n) && n >= 1;
      return !!(r.vehicleBrand?.trim() && r.vehicleModel?.trim() && qtyOk);
    });
  });

  /** Tab 上合计台数：新建须商品车行全部填写完整；编辑则只要有有效台数即展示 */
  const cargoTabTotalVisible = computed(
    () => cargoTotalQty.value > 0 && (isEdit.value || cargoStepDone.value)
  );

  const receiveStepDone = computed(
    () =>
      !!(
        form.dealerName?.trim() &&
        form.dealerContact?.trim() &&
        form.dealerPhone?.trim()
      )
  );

  /** 未开启运费 Tab 时不在此页校验手工金额（与列表敏感信息策略一致） */
  const freightStepDone = computed(() => {
    if (!showFreightTab.value) return true;
    const raw = freightAmountStr.value.trim();
    if (raw === '') return false;
    const n = parseFloat(raw);
    return Number.isFinite(n) && n >= 0;
  });

  const filterQ = reactive({
    customer: '',
    brand: '',
    series: '',
    dealer: ''
  });

  const customersShown = computed(() => {
    const q = filterQ.customer.trim();
    if (!q) return customerOptions.value;
    return customerOptions.value.filter((c) =>
      pinyinMatch(c.customerName ?? '', q)
    );
  });

  const brandsShown = computed(() => {
    const q = filterQ.brand.trim();
    if (!q) return brandOptions.value;
    return brandOptions.value.filter((b) =>
      pinyinMatch(b.brandNameCn ?? '', q)
    );
  });

  const dealersShown = computed(() => {
    const q = filterQ.dealer.trim();
    if (!q) return dealerOptions.value;
    return dealerOptions.value.filter((d) =>
      pinyinMatch(d.dealerName ?? '', q)
    );
  });

  function seriesShownForRow(row: CargoEditRow) {
    const q = filterQ.series.trim();
    if (!q) return row.seriesOptions;
    return row.seriesOptions.filter((s) => pinyinMatch(s.seriesName ?? '', q));
  }

  const setCustomerFilter = (q: string) => {
    filterQ.customer = q;
  };
  const setBrandFilter = (q: string) => {
    filterQ.brand = q;
  };
  const setSeriesFilter = (q: string) => {
    filterQ.series = q;
  };
  const setDealerFilter = (q: string) => {
    filterQ.dealer = q;
  };

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const calcHint = computed(() => {
    const rs = calcResults.value;
    if (!rs.length) return '';
    const parts = rs
      .map((r, i) =>
        r ? `#${i + 1} ${r.contractNo} (${r.matchLevel})` : `#${i + 1} 未匹配`
      )
      .filter(Boolean);
    return parts.length ? `分行匹配: ${parts.join('；')}` : '';
  });

  const rules = reactive<FormRules>({
    customerId: [{ required: true, message: '请选择客户', trigger: 'change' }],
    waybillNo: [
      { required: true, message: '请输入运单编号', trigger: 'blur' },
      {
        validator: (_rule, value, callback) => {
          const v = String(value ?? '').trim();
          if (!v) {
            callback();
            return;
          }
          const excludeId = isEdit.value ? form.id : undefined;
          checkWaybillNoAvailable(v, excludeId)
            .then((available) => {
              if (!available) callback(new Error('运单编号已存在'));
              else callback();
            })
            .catch(() => callback());
        },
        trigger: 'blur'
      }
    ],
    originCode: [
      { required: true, message: '请选择出发地', trigger: 'change' }
    ],
    destinationCode: [
      { required: true, message: '请选择目的地', trigger: 'change' }
    ],
    dealerName: [
      { required: true, message: '请选择收车门店', trigger: 'change' }
    ],
    dealerContact: [
      { required: true, message: '请输入联系人姓名', trigger: 'blur' }
    ],
    dealerPhone: [
      { required: true, message: '请输入联系电话', trigger: 'blur' }
    ],
    freightAmount: [
      {
        validator: (_rule, _val, callback) => {
          if (!showFreightTab.value) {
            callback();
            return;
          }
          if (freightCalcMode.value !== 'manual_only') {
            callback();
            return;
          }
          const raw = freightAmountStr.value.trim();
          if (raw === '') {
            callback(new Error('请输入运费金额'));
            return;
          }
          const n = parseFloat(raw);
          if (!Number.isFinite(n) || n < 0) {
            callback(new Error('请输入有效的运费金额'));
            return;
          }
          callback();
        },
        trigger: 'blur'
      }
    ]
  });

  function parseRowQty(row: CargoEditRow): number {
    const n = parseInt(String(row.quantityStr ?? '').trim(), 10);
    return Number.isFinite(n) && n >= 1 ? n : NaN;
  }

  function normalizeCargoQty(row: CargoEditRow) {
    const q = parseRowQty(row);
    row.quantityStr = Number.isFinite(q) ? String(q) : '1';
  }

  function syncFreightAmountFromStr() {
    const raw = freightAmountStr.value.trim();
    if (raw === '') {
      form.freightAmount = undefined;
      return;
    }
    const n = parseFloat(raw);
    if (Number.isFinite(n) && n >= 0) {
      form.freightAmount = Math.round(n * 100) / 100;
    }
  }

  function emptyCargoRow(): CargoEditRow {
    return {
      quantityStr: '1',
      brandId: null,
      seriesOptions: []
    };
  }

  function addCargoRow() {
    cargoRows.value.push(emptyCargoRow());
  }

  function removeCargoRow(idx: number) {
    cargoRows.value.splice(idx, 1);
  }

  function prevStep() {
    const order = visibleTabOrder.value;
    const i = order.indexOf(activeTab.value);
    if (i > 0) activeTab.value = order[i - 1]!;
  }

  async function validateFieldsOrCatch(fields: string[]): Promise<boolean> {
    if (!formRef.value) return false;
    try {
      return await formRef.value.validateField(fields);
    } catch {
      return false;
    }
  }

  async function onClickNextStep() {
    const order = visibleTabOrder.value;
    const i = order.indexOf(activeTab.value);
    if (i < 0) return;
    const tab = order[i]!;
    let ok = true;
    if (tab === 'basic') {
      ok = await validateFieldsOrCatch([
        'customerId',
        'waybillNo',
        'originCode',
        'destinationCode'
      ]);
    } else if (tab === 'cargo') {
      ok = validateCargoes();
    } else if (tab === 'receive') {
      ok = await validateFieldsOrCatch([
        'dealerName',
        'dealerContact',
        'dealerPhone'
      ]);
    }
    if (!ok) return;
    if (i < order.length - 1) activeTab.value = order[i + 1]!;
  }

  function onTabChange(name: string | number) {
    const n = String(name) as TabName;
    const order = visibleTabOrder.value;
    if (order.includes(n)) activeTab.value = n;
    void (async () => {
      try {
        if (n === 'cargo') await ensureCargoSeriesHydrated();
        else if (n === 'receive') await ensureReceiveTabReady();
      } catch (_) {
        /* ignore */
      }
    })();
  }

  async function fetchAllDealersPaged(): Promise<Dealer[]> {
    const limit = 200;
    const all: Dealer[] = [];
    let page = 1;
    for (;;) {
      const data = await pageDealers({ page, limit }).catch(() => ({
        list: [] as Dealer[],
        count: 0
      }));
      const chunk = data?.list ?? [];
      all.push(...chunk);
      const total = data?.count ?? 0;
      if (!chunk.length || all.length >= total || page > 100) break;
      page += 1;
    }
    return all;
  }

  async function fetchAllDealersCached(): Promise<Dealer[]> {
    const now = Date.now();
    if (
      _waybillDealersCache &&
      now - _waybillDealersCacheAt < WAYBILL_DEALERS_CACHE_MS
    ) {
      return _waybillDealersCache;
    }
    const all = await fetchAllDealersPaged();
    _waybillDealersCache = all;
    _waybillDealersCacheAt = now;
    return all;
  }

  const loadBasicTabData = async () => {
    try {
      const [customers, regions, configs] = await Promise.all([
        selectCustomers().catch(() => []),
        getRegionNavTree().catch(() => []),
        listConfigsByGroup('waybill').catch(() => [])
      ]);
      customerOptions.value = customers ?? [];
      regionTree.value = regions ?? [];

      const modeConfig = (configs ?? []).find(
        (c: { configKey?: string }) =>
          c.configKey === 'waybill.freight_calc_mode'
      );
      if (modeConfig?.configValue) {
        freightCalcMode.value = modeConfig.configValue;
      }
      const listFreightCfg = (configs ?? []).find(
        (c: { configKey?: string }) =>
          c.configKey === 'waybill.list_show_freight_amount'
      );
      showFreightTab.value = listFreightCfg?.configValue === 'true';
    } catch (_) {
      /* ignore */
    }
  };

  async function ensureBrandOptionsLoaded() {
    if (brandsReadyThisOpen.value && brandOptions.value.length) return;
    try {
      brandOptions.value = await listVehicleBrandOptions().catch(() => []);
    } catch {
      brandOptions.value = [];
    }
    brandsReadyThisOpen.value = true;
  }

  async function ensureDealersLoaded() {
    if (dealersReadyThisOpen.value && dealerOptions.value.length) return;
    try {
      dealerOptions.value = await fetchAllDealersCached();
    } catch {
      dealerOptions.value = [];
    }
    dealersReadyThisOpen.value = true;
  }

  function matchDealerSelection() {
    if (!form.dealerName?.trim()) {
      selectedDealerId.value = null;
      return;
    }
    const dealer = dealerOptions.value.find(
      (d) => d.dealerName === form.dealerName
    );
    selectedDealerId.value = dealer?.dealerId ?? null;
  }

  async function ensureCargoSeriesHydrated() {
    if (cargoRowsSeriesHydrated.value) return;
    await ensureBrandOptionsLoaded();
    for (let i = 0; i < cargoRows.value.length; i++) {
      const row = cargoRows.value[i];
      const savedModel = row.vehicleModel;
      if (row.vehicleBrand?.trim()) {
        await hydrateCargoRowSeries(row);
        if (savedModel) row.vehicleModel = savedModel;
      }
    }
    cargoRowsSeriesHydrated.value = true;
  }

  async function ensureReceiveTabReady() {
    await ensureDealersLoaded();
    matchDealerSelection();
  }

  async function hydrateCargoRowSeries(row: CargoEditRow) {
    row.vehicleModel = undefined;
    row.seriesOptions = [];
    const brand = brandOptions.value.find(
      (b) => b.brandNameCn === row.vehicleBrand
    );
    if (brand) {
      row.brandId = brand.brandId;
      try {
        const data = await pageVehicleSeries({
          brandId: brand.brandId,
          page: 1,
          limit: 200
        });
        row.seriesOptions = data?.list ?? [];
      } catch (_) {
        row.seriesOptions = [];
      }
    } else {
      row.brandId = null;
    }
  }

  const findRegionName = (codes: string[]): string => {
    if (!codes.length) return '';
    const names: string[] = [];
    let nodes = regionTree.value;
    for (const code of codes) {
      const node = nodes.find((n) => n.code === code);
      if (node) {
        names.push(node.name);
        nodes = node.children ?? [];
      }
    }
    return names.join('/');
  };

  const onOriginChange = (val: string[] | undefined) => {
    if (val && val.length) {
      form.originCode = val[val.length - 1];
      form.origin = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.originRegionId = leaf?.regionId ?? undefined;
    } else {
      form.originCode = undefined;
      form.origin = undefined;
      form.originRegionId = undefined;
    }
    calcResults.value = [];
  };

  const onDestChange = (val: string[] | undefined) => {
    if (val && val.length) {
      form.destinationCode = val[val.length - 1];
      form.destination = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.destinationRegionId = leaf?.regionId ?? undefined;
    } else {
      form.destinationCode = undefined;
      form.destination = undefined;
      form.destinationRegionId = undefined;
    }
    calcResults.value = [];
  };

  const onDealerChange = (dealerId: number | undefined) => {
    if (dealerId == null) {
      form.dealerName = undefined;
      form.dealerAddress = undefined;
      return;
    }
    const dealer = dealerOptions.value.find((d) => d.dealerId === dealerId);
    if (dealer) {
      form.dealerName = dealer.dealerName;
      form.dealerAddress = [dealer.province, dealer.city, dealer.addressDetail]
        .filter(Boolean)
        .join(' ');
    }
  };

  const onCustomerChange = () => {
    const customer = customerOptions.value.find(
      (c) => c.id === form.customerId
    );
    if (customer) {
      form.customerName = customer.customerName;
    }
    calcResults.value = [];
  };

  function buildCargoRowsFromWaybill(data: Waybill) {
    const lines =
      data.cargoes?.length && data.cargoes.length > 0
        ? data.cargoes
        : [
            {
              vehicleBrand: data.vehicleBrand,
              vehicleModel: data.vehicleModel,
              quantity: data.quantity ?? 1
            }
          ];
    cargoRows.value = lines.map((c) => ({
      vehicleBrand: c.vehicleBrand,
      vehicleModel: c.vehicleModel,
      quantityStr: String(c.quantity ?? 1),
      brandId: null,
      seriesOptions: [] as VehicleSeries[]
    }));
  }

  const onCargoBrandChange = async (row: CargoEditRow) => {
    await hydrateCargoRowSeries(row);
    calcResults.value = [];
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      brandsReadyThisOpen.value = false;
      dealersReadyThisOpen.value = false;
      cargoRowsSeriesHydrated.value = false;
      brandOptions.value = [];
      dealerOptions.value = [];

      filterQ.customer = '';
      filterQ.brand = '';
      filterQ.series = '';
      filterQ.dealer = '';
      calcResults.value = [];
      selectedDealerId.value = null;
      originCodes.value = [];
      destCodes.value = [];
      activeTab.value = 'basic';

      const editId = props.data?.id;
      const detailPromise = editId
        ? getWaybill(editId).catch(() => null)
        : Promise.resolve<Waybill | null>(null);

      const [, remote] = await Promise.all([loadBasicTabData(), detailPromise]);

      if (editId) {
        const detail = remote ?? (props.data as Waybill);
        Object.assign(form, detail);
        freightAmountStr.value =
          form.freightAmount != null ? String(form.freightAmount) : '';
        if (detail.originCode) {
          const op = findRegionCodePath(regionTree.value, detail.originCode);
          originCodes.value = op ?? [detail.originCode];
        }
        if (detail.destinationCode) {
          const dp = findRegionCodePath(
            regionTree.value,
            detail.destinationCode
          );
          destCodes.value = dp ?? [detail.destinationCode];
        }
        const oLeaf = findLeafRegionByCodePath(
          regionTree.value,
          originCodes.value
        );
        const dLeaf = findLeafRegionByCodePath(
          regionTree.value,
          destCodes.value
        );
        if (oLeaf) form.originRegionId = oLeaf.regionId;
        if (dLeaf) form.destinationRegionId = dLeaf.regionId;
        buildCargoRowsFromWaybill(detail);
      } else {
        Object.keys(form).forEach((k) => {
          (form as Record<string, unknown>)[k] = undefined;
        });
        freightAmountStr.value = '';
        cargoRows.value = [emptyCargoRow()];
      }
      await nextTick(() => {
        formRef.value?.clearValidate();
      });
    }
  );

  watch(showFreightTab, (show) => {
    if (!show && activeTab.value === 'freight') {
      activeTab.value = 'receive';
    }
  });

  const updateVisible = (v: boolean) => {
    emit('update:visible', v);
  };

  function validateCargoes(): boolean {
    if (!cargoRows.value.length) {
      EleMessage.warning({ message: '请至少添加一行商品车', plain: true });
      activeTab.value = 'cargo';
      return false;
    }
    for (let i = 0; i < cargoRows.value.length; i++) {
      const row = cargoRows.value[i];
      if (!row.vehicleBrand?.trim()) {
        EleMessage.warning({
          message: `商品车第 ${i + 1} 行：请选择品牌`,
          plain: true
        });
        activeTab.value = 'cargo';
        return false;
      }
      if (!row.vehicleModel?.trim()) {
        EleMessage.warning({
          message: `商品车第 ${i + 1} 行：请选择车型`,
          plain: true
        });
        activeTab.value = 'cargo';
        return false;
      }
      const q = parseRowQty(row);
      if (!Number.isFinite(q)) {
        EleMessage.warning({
          message: `商品车第 ${i + 1} 行：台数至少为 1`,
          plain: true
        });
        activeTab.value = 'cargo';
        return false;
      }
    }
    return true;
  }

  function buildCargoesPayload() {
    return cargoRows.value.map((row, i) => ({
      vehicleBrand: row.vehicleBrand?.trim(),
      vehicleModel: row.vehicleModel?.trim(),
      quantity: parseRowQty(row),
      sortOrder: i
    }));
  }

  const calcFreight = async () => {
    if (!form.customerId) {
      EleMessage.warning({ message: '请先选择客户', plain: true });
      return;
    }
    if (!form.originCode || !form.destinationCode) {
      EleMessage.warning({ message: '请先选择出发地和目的地', plain: true });
      return;
    }
    if (!validateCargoes()) return;

    calcLoading.value = true;
    calcResults.value = [];
    try {
      const cargoes = cargoRows.value.map((row) => ({
        vehicleBrand: row.vehicleBrand,
        vehicleModel: row.vehicleModel,
        quantity: parseRowQty(row)
      }));
      const preview = (await previewFreight({
        customerId: form.customerId!,
        originCode: form.originCode!,
        originRegionId: form.originRegionId ?? null,
        origin: form.origin,
        destinationCode: form.destinationCode!,
        destinationRegionId: form.destinationRegionId ?? null,
        destination: form.destination,
        cargoes
      })) as {
        calcStatus: string;
        totalAmount?: number | null;
        items: Array<{
          calcStatus: string;
          amount?: number | null;
          unitPrice?: number | null;
          matchedContractId?: number | null;
          matchedContractNo?: string | null;
          matchedRuleId?: number | null;
          modelMatchType?: string | null;
          direction?: string | null;
          score?: number | null;
          errorMessage?: string | null;
        }>;
      };

      const items = preview?.items ?? [];
      const results: (FreightCalcResult | null)[] = items.map((it) => {
        if (it.calcStatus !== 'success') return null;
        return {
          contractId: it.matchedContractId ?? undefined,
          contractNo: it.matchedContractNo ?? '',
          rateId: it.matchedRuleId ?? undefined,
          unitPrice: it.unitPrice ?? 0,
          totalAmount: it.amount ?? 0,
          matchLevel:
            it.modelMatchType || (it.direction === 'reverse' ? '反向' : '匹配')
        } as FreightCalcResult;
      });
      calcResults.value = results;

      const anyHit = results.some(Boolean);
      if (anyHit) {
        const sum = preview?.totalAmount ?? 0;
        form.freightAmount = Math.round(Number(sum) * 100) / 100;
        freightAmountStr.value =
          form.freightAmount != null ? String(form.freightAmount) : '';
        form.freightSource = 0;
        const firstHit = items.find((it) => it.calcStatus === 'success');
        if (firstHit?.matchedContractId != null)
          form.contractId = firstHit.matchedContractId;
        if (firstHit?.matchedRuleId != null)
          form.rateId = firstHit.matchedRuleId;

        if (preview.calcStatus === 'partial_success') {
          EleMessage.warning({
            message: `部分明细未匹配到运价，请检查后手动调整`,
            plain: true
          });
        } else {
          EleMessage.success({ message: '运费计算成功', plain: true });
        }
      } else {
        EleMessage.warning({
          message: '未匹配到运价，请手动填写运费',
          plain: true
        });
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      EleMessage.error({ message: msg, plain: true });
    } finally {
      calcLoading.value = false;
    }
  };

  function focusTabForField(fieldKey: string) {
    if (fieldKey === 'freightAmount' && !showFreightTab.value) {
      activeTab.value = 'receive';
      return;
    }
    const tab = FIELD_TAB[fieldKey];
    if (tab) activeTab.value = tab;
  }

  const handleSubmit = () => {
    syncFreightAmountFromStr();
    if (!validateCargoes()) return;

    formRef.value?.validate((valid, fields) => {
      if (!valid) {
        const first = fields ? Object.keys(fields)[0] : null;
        if (first) focusTabForField(first);
        return;
      }

      loading.value = true;
      const payload = {
        ...form,
        cargoes: buildCargoesPayload()
      };

      const done = () => {
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      };

      const fail = (e: { message?: string }) => {
        EleMessage.error({ message: e.message, plain: true });
      };

      if (isEdit.value) {
        updateWaybill(payload)
          .then(() => done())
          .catch(fail)
          .finally(() => {
            loading.value = false;
          });
      } else {
        addWaybill(payload)
          .then(() => done())
          .catch(fail)
          .finally(() => {
            loading.value = false;
          });
      }
    });
  };
</script>

<style scoped>
  .waybill-edit-dialog__footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
  }

  .waybill-tab-label {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    max-width: 100%;
    white-space: nowrap;
  }

  .waybill-tab-idx {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 22px;
    min-width: 22px;
    height: 22px;
    padding: 0;
    box-sizing: border-box;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
    background: var(--el-fill-color-dark);
    color: var(--el-text-color-secondary);
  }

  .waybill-tab-idx.is-done {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }

  .waybill-tab-check {
    font-size: 14px;
  }

  .waybill-tab-sub {
    font-size: 11px;
    font-weight: 400;
    color: var(--el-text-color-secondary);
  }

  .waybill-tab-text {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .waybill-edit-tabs :deep(.el-tabs__item.is-active) .waybill-tab-idx {
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }

  .waybill-edit-form {
    margin: 0;
  }

  .waybill-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .waybill-edit-tabs :deep(.el-tabs__item) {
    flex: 1;
    min-width: 0;
    margin: 0;
    padding: 0 6px;
    height: 36px;
    line-height: 36px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    transition:
      color 0.2s,
      background 0.2s,
      box-shadow 0.2s;
  }

  .waybill-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .waybill-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .waybill-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .waybill-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .waybill-tab-pane {
    max-height: min(420px, calc(100vh - 320px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .waybill-edit-dialog
    :deep(.floating-label-wrapper.is-focused .floating-label),
  .waybill-edit-dialog
    :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .waybill-edit-dialog
    :deep(.waybill-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }

  .waybill-item-tight-label :deep(.el-form-item__label) {
    padding-bottom: 2px;
    line-height: 1.2;
    font-size: 12px;
  }

  .waybill-freight-actions {
    margin-bottom: 8px;
  }

  .waybill-freight-actions :deep(.el-form-item__content) {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .waybill-calc-hint {
    font-size: 12px;
    color: var(--el-color-success);
    line-height: 1.4;
  }

  .waybill-freight-auto-note {
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
  }

  .waybill-cargo-row {
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px dashed var(--el-border-color-lighter);
  }

  .waybill-cargo-row:last-of-type {
    border-bottom: none;
  }

  .waybill-cargo-row__line {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 8px 12px;
  }

  .waybill-cargo-row__meta {
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding-top: 8px;
  }

  .waybill-cargo-row__fields {
    flex: 1 1 320px;
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 8px;
    min-width: 0;
  }

  .waybill-cargo-field {
    flex: 1 1 130px;
    min-width: 108px;
    margin-bottom: 0 !important;
  }

  .waybill-cargo-field--qty {
    flex: 0 1 96px;
    max-width: 104px;
  }

  .waybill-cargo-field :deep(.el-form-item__content) {
    width: 100%;
  }

  .waybill-cargo-row__label {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-regular);
    white-space: nowrap;
  }

  .waybill-cargo-add {
    margin-top: 4px;
  }
</style>
