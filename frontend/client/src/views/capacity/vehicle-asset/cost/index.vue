<template>
  <ele-page class="fleet-cost-page">
    <ele-card v-if="!featureEnabled" class="fleet-cost-page__upgrade">
      <el-result
        icon="warning"
        title="资产成本为专业版功能"
        sub-title="开通后可登记保险/年检费用、维护资产卡片，并按车辆汇总养车成本。"
      >
        <template #extra>
          <el-button type="primary" @click="goHome">返回工作台</el-button>
        </template>
      </el-result>
    </ele-card>

    <template v-else>
      <ele-card :body-style="{ paddingBottom: '8px' }">
        <el-tabs v-model="activeTab" @tab-change="onTabChange">
          <el-tab-pane label="成本汇总" name="summary" />
          <el-tab-pane label="续期台账" name="renewals" />
          <el-tab-pane label="资产卡片" name="asset" />
        </el-tabs>
      </ele-card>

      <!-- 成本汇总 -->
      <template v-if="activeTab === 'summary'">
        <ele-card>
          <el-form inline @submit.prevent>
            <el-form-item label="统计区间">
              <el-date-picker
                v-model="range"
                type="daterange"
                value-format="YYYY-MM-DD"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                :clearable="false"
              />
            </el-form-item>
            <el-form-item label="车辆">
              <el-select
                v-model="summaryVehicleId"
                clearable
                filterable
                remote
                :remote-method="searchVehicles"
                :loading="vehicleLoading"
                placeholder="全部车辆"
                style="width: 180px"
              >
                <el-option
                  v-for="v in vehicleOptions"
                  :key="v.id"
                  :label="v.plateNumber"
                  :value="v.id!"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="summaryLoading" @click="loadSummary">
                查询
              </el-button>
            </el-form-item>
          </el-form>
          <el-alert
            type="info"
            :closable="false"
            show-icon
            :title="summary.disclaimer || '本页为经营视角的资产成本汇总，不等于会计总账。'"
            style="margin-bottom: 16px"
          />
          <el-row :gutter="12" class="fleet-cost-page__stats">
            <el-col :lg="4" :md="8" :xs="12">
              <div class="stat-item">
                <div class="stat-label">合计</div>
                <div class="stat-value">¥{{ formatMoney(summary.totals.total) }}</div>
              </div>
            </el-col>
            <el-col :lg="5" :md="8" :xs="12">
              <div class="stat-item">
                <div class="stat-label">维保</div>
                <div class="stat-value">¥{{ formatMoney(summary.totals.maintenance) }}</div>
              </div>
            </el-col>
            <el-col :lg="5" :md="8" :xs="12">
              <div class="stat-item">
                <div class="stat-label">保险</div>
                <div class="stat-value">¥{{ formatMoney(summary.totals.insurance) }}</div>
              </div>
            </el-col>
            <el-col :lg="5" :md="8" :xs="12">
              <div class="stat-item">
                <div class="stat-label">年检</div>
                <div class="stat-value">¥{{ formatMoney(summary.totals.inspection) }}</div>
              </div>
            </el-col>
            <el-col :lg="5" :md="8" :xs="12">
              <div class="stat-item">
                <div class="stat-label">折旧</div>
                <div class="stat-value">¥{{ formatMoney(summary.totals.depreciation) }}</div>
              </div>
            </el-col>
          </el-row>
        </ele-card>

        <ele-card header="单车明细">
          <el-empty
            v-if="!summary.vehicles.length && !summaryLoading"
            description="所选区间暂无资产成本。可先完工维保工单、登记续期或完善资产卡片。"
          />
          <el-table v-else :data="summary.vehicles" v-loading="summaryLoading" stripe>
            <el-table-column prop="plateNumber" label="车牌" width="120" />
            <el-table-column prop="maintenance" label="维保" min-width="100">
              <template #default="{ row }">¥{{ formatMoney(row.maintenance) }}</template>
            </el-table-column>
            <el-table-column prop="insurance" label="保险" min-width="100">
              <template #default="{ row }">¥{{ formatMoney(row.insurance) }}</template>
            </el-table-column>
            <el-table-column prop="inspection" label="年检" min-width="100">
              <template #default="{ row }">¥{{ formatMoney(row.inspection) }}</template>
            </el-table-column>
            <el-table-column prop="depreciation" label="折旧" min-width="100">
              <template #default="{ row }">¥{{ formatMoney(row.depreciation) }}</template>
            </el-table-column>
            <el-table-column prop="total" label="合计" min-width="110">
              <template #default="{ row }">
                <strong>¥{{ formatMoney(row.total) }}</strong>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="openAsset(row.vehicleId)">
                  资产卡片
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </ele-card>
      </template>

      <!-- 续期台账 -->
      <template v-else-if="activeTab === 'renewals'">
        <ele-card>
          <ele-pro-table
            ref="renewalTableRef"
            row-key="id"
            :columns="renewalColumns"
            :datasource="renewalDatasource"
            :show-overflow-tooltip="true"
          >
            <template #toolbar>
              <el-space wrap>
                <el-input
                  v-model="renewalWhere.keyword"
                  clearable
                  placeholder="车牌 / 保单号"
                  style="width: 180px"
                  @keyup.enter="reloadRenewals"
                />
                <el-select
                  v-model="renewalWhere.renewalType"
                  clearable
                  placeholder="类型"
                  style="width: 120px"
                  @change="reloadRenewals"
                >
                  <el-option label="保险" value="insurance" />
                  <el-option label="年检" value="inspection" />
                </el-select>
                <el-button type="primary" @click="openRenewalCreate">登记续期</el-button>
              </el-space>
            </template>
            <template #renewalType="{ row }">
              {{ row.renewalType === 'insurance' ? '保险' : '年检' }}
            </template>
            <template #status="{ row }">
              <el-tag
                size="small"
                :type="
                  row.status === 'effective'
                    ? 'success'
                    : row.status === 'cancelled'
                      ? 'info'
                      : 'warning'
                "
              >
                {{
                  row.status === 'effective'
                    ? '已生效'
                    : row.status === 'cancelled'
                      ? '已取消'
                      : '草稿'
                }}
              </el-tag>
            </template>
            <template #action="{ row }">
              <el-space>
                <el-button
                  v-if="row.status === 'draft'"
                  type="primary"
                  link
                  @click="onEffect(row)"
                >
                  生效
                </el-button>
                <el-button
                  v-if="row.status === 'draft'"
                  type="danger"
                  link
                  @click="onCancelRenewal(row)"
                >
                  取消
                </el-button>
              </el-space>
            </template>
          </ele-pro-table>
        </ele-card>
      </template>

      <!-- 资产卡片 -->
      <template v-else>
        <ele-card>
          <el-form inline @submit.prevent>
            <el-form-item label="选择车辆" required>
              <el-select
                v-model="assetVehicleId"
                filterable
                remote
                :remote-method="searchVehicles"
                :loading="vehicleLoading"
                placeholder="请选择车辆"
                style="width: 200px"
                @change="loadAssetCard"
              >
                <el-option
                  v-for="v in vehicleOptions"
                  :key="v.id"
                  :label="v.plateNumber"
                  :value="v.id!"
                />
              </el-select>
            </el-form-item>
          </el-form>

          <el-empty
            v-if="!assetVehicleId"
            description="请先选择车辆，再维护资产卡片。"
          />
          <el-form
            v-else
            ref="assetFormRef"
            :model="assetForm"
            label-width="120px"
            style="max-width: 640px"
            v-loading="assetLoading"
          >
            <el-form-item label="车牌">
              <span>{{ assetForm.plateNumber || '—' }}</span>
            </el-form-item>
            <el-form-item label="购入日">
              <el-date-picker
                v-model="assetForm.purchaseDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="购入日期"
              />
            </el-form-item>
            <el-form-item label="资产原值">
              <el-input-number
                v-model="assetForm.originalValue"
                :min="0"
                :precision="2"
                :controls="false"
                style="width: 220px"
              />
            </el-form-item>
            <el-form-item label="预计残值">
              <el-input-number
                v-model="assetForm.residualValue"
                :min="0"
                :precision="2"
                :controls="false"
                style="width: 220px"
              />
            </el-form-item>
            <el-form-item label="折旧月数">
              <el-input-number
                v-model="assetForm.depreciableMonths"
                :min="1"
                :precision="0"
                style="width: 220px"
              />
            </el-form-item>
            <el-form-item label="折旧起算日">
              <el-date-picker
                v-model="assetForm.depreciationStartDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="默认取购入日"
              />
            </el-form-item>
            <el-form-item label="折旧方法">
              <el-tag>直线法</el-tag>
            </el-form-item>
            <el-divider />
            <el-form-item label="月折旧额">
              <span>¥{{ formatMoney(assetForm.monthlyDepreciation) }}</span>
            </el-form-item>
            <el-form-item label="累计折旧">
              <span>¥{{ formatMoney(assetForm.accumulatedDepreciation) }}</span>
            </el-form-item>
            <el-form-item label="净值">
              <span>¥{{ formatMoney(assetForm.netValue) }}</span>
            </el-form-item>
            <el-form-item label="保险到期">
              <span>{{ assetForm.insuranceExpire || '—' }}</span>
            </el-form-item>
            <el-form-item label="年检到期">
              <span>{{ assetForm.inspectionExpire || '—' }}</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="assetSaving" @click="saveAssetCard">
                保存资产卡片
              </el-button>
            </el-form-item>
          </el-form>
        </ele-card>
      </template>
    </template>

    <el-dialog
      v-model="renewalDialogVisible"
      title="登记续期"
      width="520px"
      destroy-on-close
      @closed="resetRenewalForm"
    >
      <el-form
        ref="renewalFormRef"
        :model="renewalForm"
        :rules="renewalRules"
        label-width="100px"
      >
        <el-form-item label="车辆" prop="vehicleId">
          <el-select
            v-model="renewalForm.vehicleId"
            filterable
            remote
            :remote-method="searchVehicles"
            :loading="vehicleLoading"
            placeholder="请选择车辆"
            style="width: 100%"
          >
            <el-option
              v-for="v in vehicleOptions"
              :key="v.id"
              :label="v.plateNumber"
              :value="v.id!"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" prop="renewalType">
          <el-radio-group v-model="renewalForm.renewalType">
            <el-radio value="insurance">保险</el-radio>
            <el-radio value="inspection">年检</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="生效日" prop="effectiveDate">
          <el-date-picker
            v-model="renewalForm.effectiveDate"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="新到期日" prop="expireDate">
          <el-date-picker
            v-model="renewalForm.expireDate"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="费用">
          <el-input-number
            v-model="renewalForm.amount"
            :min="0"
            :precision="2"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item v-if="renewalForm.renewalType === 'insurance'" label="保单号">
          <el-input v-model="renewalForm.policyNo" maxlength="64" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="renewalForm.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="立即生效">
          <el-switch v-model="renewalForm.effectNow" />
          <span class="hint">开启后会更新车辆到期日，并关闭对应证照待办</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewalDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="renewalSaving" @click="submitRenewal">
          保存
        </el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { useRouter } from 'vue-router';
  import dayjs from 'dayjs';
  import { useUserStore } from '@/store/modules/user';
  import { pageVehicles } from '@/api/capacity/self-capacity/vehicle';
  import type { Vehicle } from '@/api/capacity/self-capacity/vehicle/model';
  import {
    cancelRenewal,
    createRenewal,
    effectRenewal,
    getAssetCard,
    getCostSummary,
    pageRenewals,
    updateAssetCard
  } from '@/api/capacity/maintenance';
  import type {
    AssetCard,
    CostSummary,
    FleetRenewal
  } from '@/api/capacity/maintenance/model';

  defineOptions({ name: 'CapacityVehicleAssetCost' });

  const router = useRouter();
  const userStore = useUserStore();
  const featureEnabled = computed(() =>
    userStore.hasFeature('fleet_maintenance')
  );

  const activeTab = ref('summary');
  const range = ref<[string, string]>([
    dayjs().startOf('year').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD')
  ]);
  const summaryVehicleId = ref<number>();
  const summaryLoading = ref(false);
  const summary = reactive<CostSummary>({
    dateFrom: range.value[0],
    dateTo: range.value[1],
    totals: {
      maintenance: 0,
      insurance: 0,
      inspection: 0,
      depreciation: 0,
      total: 0
    },
    vehicles: [],
    disclaimer: '本页为经营视角的资产成本汇总，不等于会计总账。'
  });

  const vehicleOptions = ref<Vehicle[]>([]);
  const vehicleLoading = ref(false);

  const renewalTableRef = ref();
  const renewalWhere = reactive<{ keyword?: string; renewalType?: string }>({});
  const renewalDialogVisible = ref(false);
  const renewalSaving = ref(false);
  const renewalFormRef = ref<FormInstance>();
  const renewalForm = reactive<FleetRenewal>({
    renewalType: 'insurance',
    effectNow: true
  });
  const renewalRules: FormRules = {
    vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
    renewalType: [{ required: true, message: '请选择类型', trigger: 'change' }],
    effectiveDate: [{ required: true, message: '请选择生效日', trigger: 'change' }],
    expireDate: [{ required: true, message: '请选择新到期日', trigger: 'change' }]
  };

  const assetVehicleId = ref<number>();
  const assetLoading = ref(false);
  const assetSaving = ref(false);
  const assetForm = reactive<AssetCard>({});

  const renewalColumns = computed<Columns>(() => [
    { prop: 'plateNumber', label: '车牌', width: 110 },
    { prop: 'renewalType', label: '类型', width: 80, slot: 'renewalType' },
    { prop: 'effectiveDate', label: '生效日', width: 120 },
    { prop: 'expireDate', label: '新到期日', width: 120 },
    { prop: 'amount', label: '费用', width: 100 },
    { prop: 'policyNo', label: '保单号', minWidth: 140 },
    { prop: 'status', label: '状态', width: 90, slot: 'status' },
    {
      columnKey: 'action',
      label: '操作',
      width: 120,
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const renewalDatasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageRenewals({
      ...renewalWhere,
      page: p,
      limit: l
    });
    const raw = res as { list?: FleetRenewal[]; count?: number; total?: number };
    return { list: raw?.list ?? [], count: raw?.count ?? raw?.total ?? 0 };
  };

  const formatMoney = (n?: number | null) => {
    const v = Number(n || 0);
    return v.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const goHome = () => router.push('/');

  const searchVehicles = async (keyword: string) => {
    vehicleLoading.value = true;
    try {
      const res = await pageVehicles({
        keyword: keyword || undefined,
        page: 1,
        limit: 30
      });
      const raw = res as { list?: Vehicle[] };
      vehicleOptions.value = raw?.list ?? [];
    } finally {
      vehicleLoading.value = false;
    }
  };

  const loadSummary = async () => {
    if (!range.value?.[0] || !range.value?.[1]) {
      EleMessage.warning('请选择统计区间');
      return;
    }
    summaryLoading.value = true;
    try {
      const data = await getCostSummary({
        dateFrom: range.value[0],
        dateTo: range.value[1],
        vehicleId: summaryVehicleId.value
      });
      Object.assign(summary, data);
    } catch (e: any) {
      EleMessage.error(e?.message || '加载成本汇总失败，请重试');
    } finally {
      summaryLoading.value = false;
    }
  };

  const reloadRenewals = () => renewalTableRef.value?.reload?.();

  const openRenewalCreate = () => {
    renewalDialogVisible.value = true;
  };

  const resetRenewalForm = () => {
    Object.assign(renewalForm, {
      vehicleId: undefined,
      renewalType: 'insurance',
      effectiveDate: undefined,
      expireDate: undefined,
      amount: undefined,
      policyNo: undefined,
      remark: undefined,
      effectNow: true
    });
  };

  const submitRenewal = async () => {
    await renewalFormRef.value?.validate?.();
    renewalSaving.value = true;
    try {
      const res = await createRenewal({ ...renewalForm });
      EleMessage.success(res.message || '续期已登记');
      renewalDialogVisible.value = false;
      reloadRenewals();
    } catch (e: any) {
      EleMessage.error(e?.message || '保存失败，请重试');
    } finally {
      renewalSaving.value = false;
    }
  };

  const onEffect = async (row: FleetRenewal) => {
    try {
      await ElMessageBox.confirm(
        `确认将「${row.plateNumber}」的续期生效？生效后会更新车辆到期日。`,
        '确认生效',
        { type: 'warning' }
      );
      const res = await effectRenewal(row.id!);
      EleMessage.success(res.message || '续期已生效');
      reloadRenewals();
    } catch (e: any) {
      if (e !== 'cancel' && e?.message) {
        EleMessage.error(e.message);
      }
    }
  };

  const onCancelRenewal = async (row: FleetRenewal) => {
    try {
      await ElMessageBox.confirm('确定取消这条草稿续期吗？', '取消续期', {
        type: 'warning'
      });
      const res = await cancelRenewal(row.id!);
      EleMessage.success(res.message || '已取消');
      reloadRenewals();
    } catch (e: any) {
      if (e !== 'cancel' && e?.message) {
        EleMessage.error(e.message);
      }
    }
  };

  const openAsset = (vehicleId: number) => {
    activeTab.value = 'asset';
    assetVehicleId.value = vehicleId;
    loadAssetCard();
  };

  const loadAssetCard = async () => {
    if (!assetVehicleId.value) return;
    assetLoading.value = true;
    try {
      const data = await getAssetCard(assetVehicleId.value);
      Object.assign(assetForm, data);
    } catch (e: any) {
      EleMessage.error(e?.message || '加载资产卡片失败，请重试');
    } finally {
      assetLoading.value = false;
    }
  };

  const saveAssetCard = async () => {
    if (!assetVehicleId.value) {
      EleMessage.warning('请先选择车辆');
      return;
    }
    assetSaving.value = true;
    try {
      const res = await updateAssetCard(assetVehicleId.value, {
        purchaseDate: assetForm.purchaseDate,
        originalValue: assetForm.originalValue,
        residualValue: assetForm.residualValue,
        depreciableMonths: assetForm.depreciableMonths,
        depreciationMethod: 'straight_line',
        depreciationStartDate: assetForm.depreciationStartDate
      });
      EleMessage.success(res.message || '资产卡片已保存');
      if (res.data) Object.assign(assetForm, res.data);
      else await loadAssetCard();
    } catch (e: any) {
      EleMessage.error(e?.message || '保存失败，请重试');
    } finally {
      assetSaving.value = false;
    }
  };

  const onTabChange = (name: string | number) => {
    if (name === 'summary') loadSummary();
    if (name === 'renewals') reloadRenewals();
  };

  onMounted(async () => {
    if (!featureEnabled.value) return;
    await searchVehicles('');
    await loadSummary();
  });
</script>

<style scoped>
  .fleet-cost-page__stats {
    margin-bottom: 4px;
  }

  .stat-item {
    padding: 8px 4px 12px;
  }

  .stat-label {
    color: var(--el-text-color-secondary);
    font-size: 13px;
    margin-bottom: 6px;
  }

  .stat-value {
    font-size: 22px;
    font-weight: 600;
    line-height: 1.2;
  }

  .hint {
    margin-left: 10px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
</style>
