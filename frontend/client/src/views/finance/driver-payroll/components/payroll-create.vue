<template>
  <el-dialog
    :model-value="visible"
    title="新建司机工资单"
    width="920px"
    top="6vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="88px">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="司机" required>
            <el-select
              v-model="form.driverId"
              placeholder="输入姓名或手机号搜索"
              filterable
              remote
              :remote-method="searchDrivers"
              :loading="driverLoading"
              style="width: 100%"
              @change="onDriverChange"
            >
              <el-option
                v-for="d in drivers"
                :key="d.id"
                :value="d.id as number"
                :label="`${d.name || ''}${d.phone ? ' · ' + d.phone : ''}`"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="工资周期" required>
            <el-date-picker
              v-model="period"
              type="daterange"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%"
              @change="loadCandidates"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="工资模式">
            <el-select v-model="form.payrollModel" style="width: 100%">
              <el-option
                v-for="o in PAYROLL_MODEL_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="周期类型">
            <el-select v-model="form.periodType" style="width: 100%">
              <el-option
                v-for="o in PAYROLL_PERIOD_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="发薪账户">
            <el-select
              v-model="form.accountId"
              placeholder="留空用默认账户"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="a in accounts"
                :key="a.accountId"
                :value="a.accountId"
                :label="accountLabel(a)"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="计件口径">
            <el-select v-model="form.billingBase" style="width: 100%">
              <el-option
                v-for="o in BILLING_BASE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="提成单价">
            <el-input-number
              v-model="form.unitPrice"
              :min="0"
              :precision="2"
              :controls="false"
              placeholder="每台/每趟"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="备注">
            <el-input
              v-model="form.remark"
              placeholder="选填"
              maxlength="200"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div class="cand-head">
      <span class="cand-title">可计提成的任务</span>
      <span class="cand-tip">
        已选 {{ selected.length }} 个任务，共
        {{ selectedQuantity }} 台，预计提成 ¥
        {{ formatMoney(estimatedCommission) }}
      </span>
    </div>

    <el-table
      ref="tableRef"
      :data="candidates"
      v-loading="loading"
      height="300"
      row-key="taskId"
      size="small"
      @selection-change="(v: PayrollCandidate[]) => (selected = v)"
    >
      <el-table-column type="selection" width="42" reserve-selection />
      <el-table-column prop="taskNo" label="任务号" min-width="150" />
      <el-table-column prop="plateNumber" label="车牌" width="110" />
      <el-table-column label="起运 → 目的" min-width="170">
        <template #default="{ row }">
          {{ row.origin || '--' }} → {{ row.destination || '--' }}
        </template>
      </el-table-column>
      <el-table-column
        prop="signedQuantity"
        label="台数"
        width="80"
        align="center"
      />
      <el-table-column label="已预支" width="110" align="right">
        <template #default="{ row }">
          <span v-if="row.prepaidPaidAmount" class="offset">
            {{ formatMoney(row.prepaidPaidAmount) }}
          </span>
          <span v-else class="muted">--</span>
        </template>
      </el-table-column>
      <el-table-column label="交车时间" width="160" align="center">
        <template #default="{ row }">
          {{ formatDate(row.signedAt) || '--' }}
        </template>
      </el-table-column>
      <template #empty>
        <div class="cand-empty">
          {{
            form.driverId
              ? '这个司机在所选周期内没有可计提成的任务，换个周期看看'
              : '先选司机与工资周期，这里会列出可计提成的任务'
          }}
        </div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        生成工资单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addPayroll,
    listDriverAccounts,
    listPayrollCandidates
  } from '@/api/finance/driver-payroll';
  import type {
    DriverAccount,
    PayrollCandidate
  } from '@/api/finance/driver-payroll/model';
  import { pageDrivers } from '@/api/capacity/self-capacity/driver';
  import type { Driver } from '@/api/capacity/self-capacity/driver/model';
  import { formatDate } from '@/utils/date-util';
  import {
    BILLING_BASE_OPTIONS,
    formatMoney,
    PAYROLL_MODEL_OPTIONS,
    PAYROLL_PERIOD_OPTIONS
  } from '../../status-config';

  defineProps<{ visible: boolean }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', payrollId?: number): void;
  }>();

  const tableRef = ref();
  const loading = ref(false);
  const saving = ref(false);
  const driverLoading = ref(false);
  const drivers = ref<Driver[]>([]);
  const accounts = ref<DriverAccount[]>([]);
  const period = ref<[string, string] | null>(null);
  const candidates = ref<PayrollCandidate[]>([]);
  const selected = ref<PayrollCandidate[]>([]);

  const form = ref<{
    driverId?: number;
    payrollModel: number;
    periodType: number;
    billingBase: number;
    unitPrice?: number;
    accountId?: number;
    remark?: string;
  }>({ payrollModel: 3, periodType: 1, billingBase: 1 });

  const accountLabel = (a: DriverAccount) =>
    [a.accountTypeLabel, a.accountName, a.accountNoMasked]
      .filter(Boolean)
      .join(' · ');

  const selectedQuantity = computed(() =>
    selected.value.reduce((sum, r) => sum + Number(r.signedQuantity || 0), 0)
  );

  const estimatedCommission = computed(
    () => selectedQuantity.value * Number(form.value.unitPrice || 0)
  );

  const defaultPeriod = (): [string, string] => {
    const now = new Date();
    const first = new Date(now.getFullYear(), now.getMonth(), 1);
    const last = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    const fmt = (d: Date) =>
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
        d.getDate()
      ).padStart(2, '0')}`;
    return [fmt(first), fmt(last)];
  };

  const searchDrivers = async (keyword: string) => {
    driverLoading.value = true;
    try {
      const res = await pageDrivers({ keyword, page: 1, limit: 30 });
      drivers.value = res?.list ?? [];
    } catch {
      // 搜不到时保留上一次结果，用户可换关键词重试
    } finally {
      driverLoading.value = false;
    }
  };

  const onOpen = async () => {
    form.value = { payrollModel: 3, periodType: 1, billingBase: 1 };
    period.value = defaultPeriod();
    candidates.value = [];
    selected.value = [];
    accounts.value = [];
    tableRef.value?.clearSelection?.();
    await searchDrivers('');
  };

  const onDriverChange = async () => {
    accounts.value = [];
    form.value.accountId = void 0;
    await loadCandidates();
    if (!form.value.driverId) return;
    try {
      accounts.value = await listDriverAccounts(form.value.driverId);
    } catch {
      // 账户拉取失败不阻断建单，发放时还能再选
    }
  };

  const loadCandidates = async () => {
    if (!form.value.driverId) {
      candidates.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listPayrollCandidates({
        driverId: form.value.driverId,
        periodStart: period.value?.[0],
        periodEnd: period.value?.[1]
      });
      candidates.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '任务加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const save = async () => {
    if (!form.value.driverId) {
      EleMessage.warning({ message: '请选择司机', plain: true });
      return;
    }
    if (!period.value?.[0] || !period.value?.[1]) {
      EleMessage.warning({ message: '请选择工资周期', plain: true });
      return;
    }
    saving.value = true;
    try {
      const detail = await addPayroll({
        driverId: form.value.driverId,
        periodStart: period.value[0],
        periodEnd: period.value[1],
        taskIds: selected.value.map((r) => r.taskId),
        payrollModel: form.value.payrollModel,
        periodType: form.value.periodType,
        unitPrice: form.value.unitPrice,
        billingBase: form.value.billingBase,
        accountId: form.value.accountId,
        remark: form.value.remark
      });
      EleMessage.success({
        message: selected.value.length
          ? `已生成工资单，含 ${selected.value.length} 个任务`
          : '已生成工资单，可在详情里补任务与工资项',
        plain: true
      });
      emit('update:visible', false);
      emit('done', detail?.id);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '生成失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .cand-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .cand-title {
    font-weight: 600;
  }

  .cand-tip {
    margin-left: auto;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .cand-empty {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
  }

  .offset {
    color: var(--el-color-warning);
    font-variant-numeric: tabular-nums;
  }

  .muted {
    color: var(--el-text-color-secondary);
  }
</style>
