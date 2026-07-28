<template>
  <el-dialog
    :title="isEdit ? '编辑计划' : '新增计划'"
    :model-value="visible"
    width="1000px"
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
      <div class="waybill-edit-layout">
        <aside class="waybill-edit-steps" aria-label="计划步骤">
          <button
            v-for="tab in visibleTabOrder"
            :key="tab"
            type="button"
            class="waybill-edit-step-btn"
            :class="{
              'is-active': activeTab === tab,
              'is-done': stepDoneMap[tab]
            }"
            @click="onStepClick(tab)"
          >
            <span
              class="waybill-edit-step-btn__idx"
              :class="{ 'is-done': stepDoneMap[tab] }"
            >
              <el-icon
                v-if="stepDoneMap[tab] && activeTab !== tab"
                class="waybill-edit-step-btn__check"
              >
                <CircleCheck />
              </el-icon>
              <template v-else>{{ tabStepNo(tab) }}</template>
            </span>
            <span class="waybill-edit-step-btn__text">
              <span class="waybill-edit-step-btn__title">{{
                stepTitle(tab)
              }}</span>
              <span
                v-if="tab === 'cargo' && cargoTabTotalVisible"
                class="waybill-edit-step-btn__sub"
              >
                合计 {{ cargoTotalQty }} 台
              </span>
            </span>
          </button>
        </aside>

        <div class="waybill-edit-main">
          <div
            v-show="activeTab === 'basic'"
            class="waybill-edit-pane"
            :class="{ 'is-active-pane': activeTab === 'basic' }"
          >
            <waybill-edit-basic
              :form="form"
              :origin-codes="originCodes"
              :dest-codes="destCodes"
              :region-tree="regionTree"
              :region-cascader-props="regionCascaderProps"
              :customers-shown="customersShown"
              :set-customer-filter="setCustomerFilter"
              @update:origin-codes="originCodes = $event"
              @update:dest-codes="destCodes = $event"
              @customer-change="onCustomerChange"
              @origin-change="onOriginChange"
              @dest-change="onDestChange"
            />
          </div>

          <div
            v-show="activeTab === 'cargo'"
            class="waybill-edit-pane"
            :class="{ 'is-active-pane': activeTab === 'cargo' }"
          >
            <waybill-edit-cargo
              :cargo-rows="cargoRows"
              :brands-shown="brandsShown"
              :series-shown-for-row="seriesShownForRow"
              :set-brand-filter="setBrandFilter"
              :set-series-filter="setSeriesFilter"
              @add="addCargoRow"
              @remove="removeCargoRow"
              @brand-change="onCargoBrandChange"
              @normalize-vin="normalizeRowVin"
              @normalize-qty="normalizeCargoQty"
            />
          </div>

          <div
            v-show="activeTab === 'receive'"
            class="waybill-edit-pane"
            :class="{ 'is-active-pane': activeTab === 'receive' }"
          >
            <waybill-edit-receive
              :form="form"
              :selected-dealer-id="selectedDealerId"
              :dealers-shown="dealersShown"
              :set-dealer-filter="setDealerFilter"
              :dealer-longitude="selectedDealerLng"
              :dealer-latitude="selectedDealerLat"
              :map-visible="activeTab === 'receive'"
              @update:selected-dealer-id="selectedDealerId = $event"
              @dealer-change="onDealerChange"
            />
          </div>

          <div
            v-if="showFreightTab"
            v-show="activeTab === 'freight'"
            class="waybill-edit-pane"
            :class="{ 'is-active-pane': activeTab === 'freight' }"
          >
            <waybill-edit-freight
              :freight-calc-mode="freightCalcMode"
              :freight-amount-str="freightAmountStr"
              :calc-loading="calcLoading"
              :calc-hint="calcHint"
              @update:freight-amount-str="freightAmountStr = $event"
              @sync-amount="syncFreightAmountFromStr"
              @calc="calcFreight"
            />
          </div>
        </div>
      </div>
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
  import type { CargoEditRow, WaybillEditTabName } from './waybill-edit-types';
  import WaybillEditBasic from './waybill-edit-basic.vue';
  import WaybillEditCargo from './waybill-edit-cargo.vue';
  import WaybillEditReceive from './waybill-edit-receive.vue';
  import WaybillEditFreight from './waybill-edit-freight.vue';

  /** 经销商全量分页较慢，短时缓存减轻重复打开弹窗等待 */
  let _waybillDealersCache: Dealer[] | null = null;
  let _waybillDealersCacheAt = 0;
  const WAYBILL_DEALERS_CACHE_MS = 45_000;

  const TAB_ORDER: WaybillEditTabName[] = [
    'basic',
    'cargo',
    'receive',
    'freight'
  ];
  type TabName = WaybillEditTabName;

  const STEP_TITLES: Record<TabName, string> = {
    basic: '基础信息',
    cargo: '商品车信息',
    receive: '收车信息',
    freight: '运费信息'
  };

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

  function stepTitle(tab: TabName): string {
    return STEP_TITLES[tab];
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
    padding: '0 16px 8px'
  };

  const customerOptions = ref<CustomerSelectItem[]>([]);
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const regionTree = ref<RegionNavNode[]>([]);
  const dealerOptions = ref<Dealer[]>([]);
  const selectedDealerId = ref<number | null>(null);
  const selectedDealerLng = ref<number | null>(null);
  const selectedDealerLat = ref<number | null>(null);
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

  function normalizeVinStr(s: string | undefined | null): string {
    if (s == null || s === '') return '';
    return [...String(s).trim().toUpperCase()]
      .filter((c) => /[A-Z0-9]/.test(c))
      .join('');
  }

  function vinLenOk(v: string): boolean {
    return v.length >= 10 && v.length <= 50;
  }

  function normalizeRowVin(row: CargoEditRow) {
    row.vinStr = normalizeVinStr(row.vinStr);
  }

  /** 商品车明细台数合计（VIN 行计 1 台；仅台数行按整数累加） */
  const cargoTotalQty = computed(() => {
    let sum = 0;
    for (const row of cargoRows.value) {
      if (row.requireVin) sum += 1;
      else {
        const q = parseRowQty(row);
        if (Number.isFinite(q)) sum += q;
      }
    }
    return sum;
  });

  const cargoStepDone = computed(() => {
    if (!cargoRows.value.length) return false;
    return cargoRows.value.every((r) => {
      const brandOk = !!(r.vehicleBrand?.trim() && r.vehicleModel?.trim());
      if (!brandOk) return false;
      if (r.requireVin) {
        const v = normalizeVinStr(r.vinStr);
        return vinLenOk(v);
      }
      const n = parseInt(String(r.quantityStr ?? '').trim(), 10);
      return Number.isFinite(n) && n >= 1;
    });
  });

  /** 步骤上合计台数：新建须商品车行全部填写完整；编辑则只要有有效台数即展示 */
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

  const stepDoneMap = computed(
    (): Record<TabName, boolean> => ({
      basic: basicStepDone.value,
      cargo: cargoStepDone.value,
      receive: receiveStepDone.value,
      freight: freightStepDone.value
    })
  );

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
      { required: true, message: '请输入计划编号', trigger: 'blur' },
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
              if (!available) callback(new Error('计划编号已存在'));
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
      vinStr: '',
      cargoId: undefined,
      requireVin: true,
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
    if (i < order.length - 1) {
      const next = order[i + 1]!;
      activeTab.value = next;
      await ensureTabReady(next);
    }
  }

  async function ensureTabReady(n: TabName) {
    try {
      if (n === 'cargo') await ensureCargoSeriesHydrated();
      else if (n === 'receive') await ensureReceiveTabReady();
    } catch (_) {
      /* ignore */
    }
  }

  function onStepClick(tab: TabName) {
    const order = visibleTabOrder.value;
    if (!order.includes(tab)) return;
    activeTab.value = tab;
    void ensureTabReady(tab);
  }

  function syncDealerCoords(dealer: Dealer | undefined | null) {
    if (!dealer) {
      selectedDealerLng.value = null;
      selectedDealerLat.value = null;
      return;
    }
    const lng = dealer.longitude != null ? Number(dealer.longitude) : NaN;
    const lat = dealer.latitude != null ? Number(dealer.latitude) : NaN;
    selectedDealerLng.value = Number.isFinite(lng) ? lng : null;
    selectedDealerLat.value = Number.isFinite(lat) ? lat : null;
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
      syncDealerCoords(null);
      return;
    }
    const dealer = dealerOptions.value.find(
      (d) => d.dealerName === form.dealerName
    );
    selectedDealerId.value = dealer?.dealerId ?? null;
    syncDealerCoords(dealer);
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
      syncDealerCoords(null);
      return;
    }
    const dealer = dealerOptions.value.find((d) => d.dealerId === dealerId);
    if (dealer) {
      form.dealerName = dealer.dealerName;
      form.dealerAddress = [dealer.province, dealer.city, dealer.addressDetail]
        .filter(Boolean)
        .join(' ');
      syncDealerCoords(dealer);
    } else {
      syncDealerCoords(null);
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
    cargoRows.value = lines.map((c) => {
      const vinNorm = normalizeVinStr(c.vin ?? undefined);
      const cid = c.id;
      const requireVin = cid != null ? !!vinNorm : true;
      return {
        vehicleBrand: c.vehicleBrand,
        vehicleModel: c.vehicleModel,
        quantityStr: String(c.quantity ?? 1),
        vinStr: vinNorm || (c.vin != null ? String(c.vin).trim() : '') || '',
        cargoId: cid,
        requireVin,
        brandId: null,
        seriesOptions: [] as VehicleSeries[]
      };
    });
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
      syncDealerCoords(null);
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
    const seenVins = new Set<string>();
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
      if (row.requireVin) {
        const v = normalizeVinStr(row.vinStr);
        if (!vinLenOk(v)) {
          EleMessage.warning({
            message: `商品车第 ${i + 1} 行：请填写有效 VIN（10~50 位字母或数字）`,
            plain: true
          });
          activeTab.value = 'cargo';
          return false;
        }
        if (seenVins.has(v)) {
          EleMessage.warning({
            message: `商品车第 ${i + 1} 行：VIN 与本单其他行重复`,
            plain: true
          });
          activeTab.value = 'cargo';
          return false;
        }
        seenVins.add(v);
      } else {
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
    }
    return true;
  }

  function buildCargoesPayload() {
    return cargoRows.value.map((row, i) => {
      const base: Record<string, unknown> = {
        vehicleBrand: row.vehicleBrand?.trim(),
        vehicleModel: row.vehicleModel?.trim(),
        sortOrder: i
      };
      if (row.cargoId != null) base.id = row.cargoId;
      if (row.requireVin) {
        base.quantity = 1;
        base.vin = normalizeVinStr(row.vinStr);
      } else {
        base.quantity = parseRowQty(row);
      }
      return base;
    });
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
        quantity: row.requireVin ? 1 : parseRowQty(row),
        vin: row.requireVin ? normalizeVinStr(row.vinStr) : undefined
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

  .waybill-edit-form {
    margin: 0;
  }

  .waybill-edit-layout {
    display: flex;
    gap: 16px;
    align-items: stretch;
    min-height: 0;
  }

  .waybill-edit-steps {
    flex: 0 0 168px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 4px 0;
  }

  .waybill-edit-step-btn {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    width: 100%;
    margin: 0;
    padding: 10px 12px;
    border: 1px solid transparent;
    border-radius: 10px;
    background: transparent;
    cursor: pointer;
    text-align: left;
    color: var(--el-text-color-regular);
    transition:
      background 0.15s ease,
      border-color 0.15s ease,
      color 0.15s ease;
  }

  .waybill-edit-step-btn:hover {
    background: var(--el-fill-color-light);
  }

  .waybill-edit-step-btn.is-active {
    background: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary-light-7);
    color: var(--el-color-primary);
  }

  .waybill-edit-step-btn__idx {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
    background: var(--el-fill-color-dark);
    color: var(--el-text-color-secondary);
  }

  .waybill-edit-step-btn.is-active .waybill-edit-step-btn__idx {
    background: var(--el-color-primary);
    color: #fff;
  }

  .waybill-edit-step-btn__idx.is-done {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }

  .waybill-edit-step-btn.is-active .waybill-edit-step-btn__idx.is-done {
    background: var(--el-color-primary);
    color: #fff;
  }

  .waybill-edit-step-btn__check {
    font-size: 14px;
  }

  .waybill-edit-step-btn__text {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    padding-top: 2px;
  }

  .waybill-edit-step-btn__title {
    font-size: 13px;
    font-weight: 500;
    line-height: 1.3;
  }

  .waybill-edit-step-btn.is-active .waybill-edit-step-btn__title {
    font-weight: 600;
  }

  .waybill-edit-step-btn__sub {
    font-size: 11px;
    font-weight: 400;
    color: var(--el-text-color-secondary);
    line-height: 1.3;
  }

  .waybill-edit-main {
    flex: 1 1 auto;
    min-width: 0;
    border-left: 1px solid var(--el-border-color-extra-light);
    padding-left: 16px;
  }

  .waybill-edit-pane {
    max-height: min(520px, calc(100vh - 280px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 12px 4px 8px 0;
    scrollbar-gutter: stable;
  }

  @media (prefers-reduced-motion: no-preference) {
    .waybill-edit-pane.is-active-pane {
      animation: waybill-pane-in 0.15s ease;
    }
  }

  @keyframes waybill-pane-in {
    from {
      opacity: 0.55;
      transform: translateY(4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media (max-width: 767.99px) {
    .waybill-edit-layout {
      flex-direction: column;
      gap: 10px;
    }

    .waybill-edit-steps {
      flex: none;
      flex-direction: row;
      flex-wrap: nowrap;
      width: 100%;
      overflow-x: auto;
      gap: 4px;
      padding: 0 0 4px;
    }

    .waybill-edit-step-btn {
      flex: 0 0 auto;
      min-width: 120px;
      padding: 8px 10px;
    }

    .waybill-edit-main {
      border-left: none;
      border-top: 1px solid var(--el-border-color-extra-light);
      padding-left: 0;
      padding-top: 10px;
    }

    .waybill-edit-pane {
      max-height: min(480px, calc(100vh - 300px));
    }
  }
</style>

<!-- 弹框挂到 body，需非 scoped 覆盖校验与浮动标签间距 -->
<style lang="scss">
  .waybill-edit-dialog {
    .waybill-edit-form {
      .el-form-item {
        margin-bottom: 18px;
      }

      .el-form-item.is-error {
        margin-bottom: 26px;
      }

      .el-form-item__error {
        position: static;
        padding-top: 4px;
        line-height: 1.3;
        left: auto;
        top: auto;
        transform: none;
      }

      .waybill-edit-pane {
        padding-top: 16px;
      }

      .waybill-cargo-field {
        margin-bottom: 0;
      }

      .waybill-cargo-field.is-error {
        margin-bottom: 8px;
      }
    }

    .floating-label-wrapper.is-focused .floating-label,
    .floating-label-wrapper.has-value .floating-label {
      transform: translateY(-62%);
      padding: 2px 6px;
      z-index: 4;
      background-color: var(--el-bg-color) !important;
      box-shadow: 0 0 0 2px var(--el-bg-color);
    }
  }

  @media (max-width: 767.99px) {
    .waybill-edit-dialog.el-dialog {
      width: 92vw !important;
      max-width: 1000px;
    }
  }
</style>
