<template>
  <ele-page class="contract-detail-page">
    <div class="cd-back">
      <el-button class="cd-back__btn" text bg @click="goList">
        <el-icon class="cd-back__icon"><ArrowLeft /></el-icon>
        返回合同列表
      </el-button>
    </div>

    <template v-if="loadError">
      <ele-card class="cd-error-card">
        <el-empty :description="loadError" />
      </ele-card>
    </template>

    <template v-else-if="contract">
      <div class="cd-hero">
        <div class="cd-hero__main">
          <div class="cd-hero__title-row">
            <h1 class="cd-hero__title">{{ contract.contractName || '—' }}</h1>
            <el-tag
              :type="getContractStatusDisplay(contract).elType"
              size="small"
              effect="plain"
              class="cd-hero__status"
            >
              {{ getContractStatusDisplay(contract).text }}
            </el-tag>
          </div>
          <div class="cd-hero__meta">
            <span class="cd-chip">
              <span class="cd-chip__k">合同编号</span>
              <span class="cd-chip__v">{{ contract.contractNo || '—' }}</span>
            </span>
            <span class="cd-chip">
              <span class="cd-chip__k">客户</span>
              <span class="cd-chip__v">{{ contract.customerName || '—' }}</span>
            </span>
            <span class="cd-chip cd-chip--wide">
              <span class="cd-chip__k">合同有效期</span>
              <span class="cd-chip__v">{{
                formatContractValidPeriod(
                  contract.effectiveDate,
                  contract.expiryDate
                )
              }}</span>
            </span>
          </div>
          <p v-if="contract.remark" class="cd-hero__remark">
            {{ contract.remark }}
          </p>
        </div>
      </div>

      <rate-search @search="(w) => reloadRatesTable(w, 1)" />
      <ele-card :body-style="{ paddingTop: '8px' }" class="cd-rates-card">
        <ele-pro-table
          ref="rateTableRef"
          row-key="id"
          :columns="rateColumns"
          :datasource="ratesDatasource"
          :pagination="{ pageSize: 20 }"
          :show-overflow-tooltip="true"
          :highlight-current-row="true"
          :cache-key="ratesTableCacheKey"
        >
          <template #toolbar>
            <btn-items
              :items="[
                {
                  preset: 'add',
                  title: '新增运价',
                  onClick: () => openRateEdit()
                }
              ]"
            />
          </template>
          <template #billingMode="{ row }">
            <el-tag
              v-if="row.billingMode === 1"
              size="small"
              :disable-transitions="true"
            >
              单公里
            </el-tag>
            <el-tag
              v-else-if="row.billingMode === 2"
              type="warning"
              size="small"
              :disable-transitions="true"
            >
              整单价
            </el-tag>
            <el-tag
              v-else
              type="success"
              size="small"
              :disable-transitions="true"
            >
              台单价
            </el-tag>
          </template>
          <template #unitPrice="{ row }">
            <span class="cd-price-inline">
              <span>{{ row.unitPrice }}</span>
              <span class="cd-unit-suffix">{{
                row.billingMode === 1
                  ? '元/台·km'
                  : row.billingMode === 2
                    ? '元/单'
                    : '元/台'
              }}</span>
              <template v-if="row.billingMode === 1 && row.distanceKm != null">
                <span class="cd-price-sep"> </span>
                <span class="cd-distance-inline">{{ row.distanceKm }} km</span>
              </template>
            </span>
          </template>
          <template #vehicleBrandModel="{ row }">
            <span>{{ formatRateBrandModel(row) }}</span>
          </template>
          <template #priceType="{ row }">
            <el-tag
              v-if="row.priceType === 1"
              type="warning"
              size="small"
              :disable-transitions="true"
            >
              预估
            </el-tag>
            <el-tag
              v-else
              type="success"
              size="small"
              :disable-transitions="true"
            >
              明确
            </el-tag>
          </template>
          <template #status="{ row }">
            <el-tag
              v-if="row.status === 1"
              type="success"
              size="small"
              :disable-transitions="true"
            >
              生效
            </el-tag>
            <el-tag v-else type="info" size="small" :disable-transitions="true">
              停用
            </el-tag>
          </template>
          <template #action="{ row }">
            <div
              class="cd-rate-actions"
              :key="`rate-actions-${row.id}-${row.status ?? ''}`"
            >
              <btn-items
                divider
                type="link"
                :wrap="false"
                :items="rateActionItems(row)"
              />
            </div>
          </template>
        </ele-pro-table>
      </ele-card>
    </template>

    <template v-else>
      <ele-card v-loading="pageLoading" class="cd-skeleton-card">
        <div style="min-height: 200px"></div>
      </ele-card>
    </template>

    <rate-edit
      v-model:visible="rateEditVisible"
      :contract-id="contract?.id"
      :customer-id="contract?.customerId"
      :data="rateEditData"
      @done="onRateEditDone"
    />

    <rate-version-history
      v-model:visible="versionHistoryVisible"
      :rate-id="versionHistoryRateId"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, watch, computed, nextTick } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ArrowLeft, Document, RefreshRight } from '@element-plus/icons-vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import { DeleteOutlined } from '@/components/icons';
  import RateEdit from './components/rate-edit.vue';
  import RateSearch from './components/rate-search.vue';
  import RateVersionHistory from './components/rate-version-history.vue';
  import {
    getContract,
    listRates,
    removeRate,
    recalculateAffectedByRate
  } from '@/api/billing/contract';
  import type {
    FreightContract,
    FreightRate,
    FreightRateFilterParam
  } from '@/api/billing/contract/model';
  import {
    formatContractValidPeriod,
    getContractStatusDisplay
  } from './contract-status';

  defineOptions({ name: 'BillingContractDetailPage' });

  const CONTRACT_LIST_PATH = '/billing/contract';

  const route = useRoute();
  const router = useRouter();

  const contractId = computed(() => {
    const raw = route.params.id;
    const n = Number(Array.isArray(raw) ? raw[0] : raw);
    return Number.isFinite(n) && n > 0 ? n : null;
  });

  const contract = ref<FreightContract | null>(null);
  const ratesCache = ref<FreightRate[]>([]);
  const pageLoading = ref(false);
  const loadError = ref<string | null>(null);

  const rateTableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const rateEditVisible = ref(false);
  const rateEditData = ref<FreightRate | null>(null);
  const versionHistoryVisible = ref(false);
  const versionHistoryRateId = ref<number | null>(null);

  const openVersionHistory = (row: FreightRate) => {
    if (!row?.id) return;
    versionHistoryRateId.value = row.id;
    versionHistoryVisible.value = true;
  };

  const recalcAffected = (row: FreightRate) => {
    if (!row?.id) return;
    ElMessageBox.confirm(
      '将查找受该运价规则影响的运单并入队批量重算，确定继续？',
      '重算受影响运单',
      { type: 'warning' }
    )
      .then(async () => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        try {
          const data = await recalculateAffectedByRate(row.id!);
          loading.close();
          EleMessage.success({
            message: `已入队，影响 ${data?.affectedWaybillCount ?? 0} 单，新增任务 ${data?.enqueuedTaskCount ?? 0} 条`,
            plain: true
          });
        } catch (e: any) {
          loading.close();
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => {});
  };

  const ratesTableCacheKey = computed(
    () => `BillingContractRateTable-${contract.value?.id ?? '0'}`
  );

  const goList = () => {
    router.push(CONTRACT_LIST_PATH);
  };

  const loadContract = async () => {
    loadError.value = null;
    contract.value = null;
    ratesCache.value = [];
    const id = contractId.value;
    if (!id) {
      loadError.value = '无效的合同 ID';
      return;
    }
    pageLoading.value = true;
    try {
      contract.value = await getContract(id);
    } catch (e: any) {
      loadError.value = e?.message || '加载合同失败';
    } finally {
      pageLoading.value = false;
    }
  };

  function filterRates(
    rows: FreightRate[],
    w?: FreightRateFilterParam
  ): FreightRate[] {
    let out = [...rows];
    const kw = w?.keyword?.trim().toLowerCase();
    if (kw) {
      out = out.filter((r) => {
        const hay = [r.origin, r.destination, r.vehicleBrand, r.vehicleModel]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return hay.includes(kw);
      });
    }
    if (typeof w?.billingMode === 'number') {
      out = out.filter((r) => r.billingMode === w.billingMode);
    }
    if (typeof w?.priceType === 'number') {
      out = out.filter((r) => r.priceType === w.priceType);
    }
    if (typeof w?.status === 'number') {
      out = out.filter((r) => r.status === w.status);
    }
    return out;
  }

  const ratesDatasource: DatasourceFunction = async ({ pages, where }) => {
    const filtered = filterRates(
      ratesCache.value,
      where as FreightRateFilterParam | undefined
    );
    const count = filtered.length;
    const page = Number((pages as { page?: number })?.page) || 1;
    const limit = Number((pages as { limit?: number })?.limit) || 20;
    const start = (page - 1) * limit;
    return {
      list: filtered.slice(start, start + limit),
      count
    };
  };

  const rateColumns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'origin', label: '出发地', minWidth: 110 },
    { prop: 'destination', label: '目的地', minWidth: 110 },
    {
      prop: 'billingMode',
      label: '计费模式',
      width: 100,
      align: 'center',
      slot: 'billingMode'
    },
    {
      columnKey: 'vehicleBrandModel',
      label: '品牌/车型',
      minWidth: 120,
      slot: 'vehicleBrandModel',
      formatter: (row: FreightRate) => formatRateBrandModel(row)
    },
    {
      columnKey: 'unitPrice',
      prop: 'unitPrice',
      label: '单价',
      minWidth: 168,
      align: 'right',
      slot: 'unitPrice',
      formatter: (row: FreightRate) => formatRateUnitPriceText(row)
    },
    {
      prop: 'priceType',
      label: '运价类型',
      width: 96,
      align: 'center',
      slot: 'priceType'
    },
    {
      prop: 'priority',
      label: '优先级',
      width: 70,
      align: 'center'
    },
    {
      prop: 'isBidirectional',
      label: '双向',
      width: 64,
      align: 'center',
      formatter: (row: FreightRate) => (row.isBidirectional === 1 ? '是' : '否')
    },
    {
      prop: 'minAmount',
      label: '最低运费',
      width: 100,
      align: 'right',
      formatter: (row: FreightRate) =>
        row.minAmount != null ? Number(row.minAmount).toFixed(2) : '--'
    },
    {
      prop: 'effectiveDate',
      label: '生效日期',
      minWidth: 112,
      align: 'center'
    },
    {
      prop: 'expiryDate',
      label: '失效日期',
      minWidth: 112,
      align: 'center'
    },
    {
      prop: 'ruleVersion',
      label: '版本',
      width: 64,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 80,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 132,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const rateUnitSuffix = (row: FreightRate) =>
    row.billingMode === 1
      ? '元/台·km'
      : row.billingMode === 2
        ? '元/单'
        : '元/台';

  const formatRateUnitPriceText = (row: FreightRate) => {
    const price = row.unitPrice ?? '';
    const suf = rateUnitSuffix(row);
    if (row.billingMode === 1 && row.distanceKm != null) {
      return `${price} ${suf} ${row.distanceKm} km`;
    }
    return `${price} ${suf}`;
  };

  const formatRateBrandModel = (row: FreightRate) => {
    const b = row.vehicleBrand?.trim();
    const m = row.vehicleModel?.trim();
    if (!b && !m) return '不限';
    return `${b || '不限'}/${m || '不限'}`;
  };

  const rateActionItems = (row: FreightRate): ButtonItem[] => {
    const dropdown: ButtonDropdownItem[] = [
      {
        title: '版本',
        icon: Document,
        onClick: () => openVersionHistory(row)
      },
      {
        title: '重算受影响',
        icon: RefreshRight,
        onClick: () => recalcAffected(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        divided: true,
        danger: true,
        onClick: () => removeRateRow(row)
      }
    ];
    return [
      {
        preset: 'edit',
        title: '修改',
        type: 'link',
        onClick: () => openRateEdit(row)
      },
      { preset: 'more', dropdownItems: dropdown }
    ];
  };

  const loadRates = async () => {
    const id = contract.value?.id ?? contractId.value;
    if (!id) return;
    try {
      ratesCache.value = (await listRates(id)) ?? [];
    } catch (_) {
      ratesCache.value = [];
    }
    await nextTick();
    rateTableRef.value?.reload?.({ page: 1 });
  };

  const reloadRatesTable = (where?: FreightRateFilterParam, page?: number) => {
    rateTableRef.value?.reload?.({ where, page: page ?? 1 });
  };

  const onRateEditDone = () => {
    loadRates();
  };

  watch(
    contractId,
    async (id) => {
      if (!id) {
        loadError.value = '无效的合同 ID';
        return;
      }
      await loadContract();
      if (contract.value?.id) {
        await loadRates();
      }
    },
    { immediate: true }
  );

  const openRateEdit = (row?: FreightRate) => {
    if (!contract.value?.id) return;
    rateEditData.value = row ?? null;
    rateEditVisible.value = true;
  };

  const removeRateRow = (row: FreightRate) => {
    ElMessageBox.confirm('确定要删除该运价明细吗?', '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeRate(row.id!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            loadRates();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>

<style scoped lang="scss">
  .contract-detail-page {
    --cd-hero-radius: 12px;
  }

  .contract-detail-page :deep(.ele-card.search-form) {
    margin-bottom: 12px;
  }

  .cd-back {
    margin-bottom: 12px;
  }

  .cd-back__btn {
    padding: 6px 12px;
    font-weight: 500;
    border-radius: 8px;
  }

  .cd-back__icon {
    margin-right: 4px;
    vertical-align: middle;
  }

  .cd-hero {
    margin-bottom: 16px;
    padding: 22px 24px;
    border-radius: var(--cd-hero-radius);
    background: linear-gradient(
      125deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-blank) 52%,
      var(--el-fill-color-light) 100%
    );
    border: 1px solid var(--el-border-color-lighter);
    box-shadow: var(--el-box-shadow-light);
  }

  .cd-hero__title-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px 12px;
    margin-bottom: 14px;
  }

  .cd-hero__title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--el-text-color-primary);
    line-height: 1.3;
  }

  .cd-hero__status {
    border-radius: 6px;
  }

  .cd-hero__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 12px;
  }

  .cd-chip {
    display: inline-flex;
    align-items: baseline;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 8px;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-extra-light);
    font-size: 13px;
    line-height: 1.4;
  }

  .cd-chip__k {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    white-space: nowrap;
  }

  .cd-chip__v {
    color: var(--el-text-color-primary);
    font-weight: 500;
  }

  .cd-chip--wide {
    // flex: 1 1 220px;
    min-width: min(100%, 220px);
  }

  .cd-hero__remark {
    margin: 14px 0 0;
    padding-top: 12px;
    border-top: 1px dashed var(--el-border-color-lighter);
    font-size: 13px;
    color: var(--el-text-color-secondary);
    line-height: 1.55;
  }

  .cd-rates-card {
    border-radius: var(--cd-hero-radius);
  }

  .cd-price-inline {
    display: inline;
    white-space: nowrap;
  }

  .cd-unit-suffix {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    margin-left: 2px;
  }

  .cd-price-sep {
    display: inline;
    margin: 0 2px;
  }

  .cd-distance-inline {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .cd-rate-actions {
    text-align: center;
    white-space: nowrap;
  }

  .cd-error-card,
  .cd-skeleton-card {
    border-radius: var(--cd-hero-radius);
  }
</style>
