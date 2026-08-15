<template>
  <el-dialog
    :model-value="visible"
    title="新建客户对账单"
    width="900px"
    top="6vh"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="0" class="finance-edit-form">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.customerId"
              label="请选择客户"
              type="select"
              filterable
              :clearable="false"
              @change="loadCandidates"
            >
              <el-option
                v-for="c in customers"
                :key="c.id"
                :value="c.id"
                :label="c.customerName"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="period"
              label="请选择对账周期"
              type="date"
              date-type="daterange"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              unlink-panels
              :clearable="false"
              @update:model-value="loadCandidates"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.billingBase"
              label="请选择计费基础"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in BILLING_BASE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入备注，选填"
              type="input"
              v-model="form.remark"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div class="finance-cand-head">
      <span class="finance-cand-title">可对账运单</span>
      <el-input
        v-model="keyword"
        placeholder="运单号/经销商"
        clearable
        style="width: 200px"
        @change="loadCandidates"
      />
      <span class="finance-cand-tip">
        已选 {{ selected.length }} 单，合计 ¥ {{ formatMoney(selectedAmount) }}
      </span>
    </div>

    <el-table
      ref="tableRef"
      :data="candidates"
      v-loading="loading"
      height="320"
      row-key="waybillId"
      :highlight-current-row="true"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="42" reserve-selection />
      <el-table-column prop="waybillNo" label="运单号" min-width="150" />
      <el-table-column prop="dealerName" label="经销商" min-width="130" />
      <el-table-column label="起运 → 目的" min-width="180">
        <template #default="{ row }">
          {{ row.origin || '--' }} → {{ row.destination || '--' }}
        </template>
      </el-table-column>
      <el-table-column label="台数" width="90" align="center">
        <template #default="{ row }">
          {{ row.signedQuantity }} / {{ row.quantity }}
        </template>
      </el-table-column>
      <el-table-column label="运费" width="110" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.freightAmount) }}
        </template>
      </el-table-column>
      <el-table-column label="交车时间" width="160" align="center">
        <template #default="{ row }">
          {{ formatDate(row.signedAt) || '--' }}
        </template>
      </el-table-column>
      <template #empty>
        <div class="finance-cand-empty">
          {{
            form.customerId
              ? '这个客户在所选周期内没有可对账的运单，换个周期看看'
              : '先选客户与对账周期，这里会列出可对账的运单'
          }}
        </div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        生成对账单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addRecon, listReconCandidates } from '@/api/finance/customer-recon';
  import type { ReconCandidate } from '@/api/finance/customer-recon/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDate } from '@/utils/date-util';
  import { BILLING_BASE_OPTIONS, formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    customerId?: number;
    customers: CustomerSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', reconId?: number): void;
  }>();

  const tableRef = ref();
  const loading = ref(false);
  const saving = ref(false);
  const keyword = ref('');
  const period = ref<[string, string] | null>(null);
  const candidates = ref<ReconCandidate[]>([]);
  const selected = ref<ReconCandidate[]>([]);

  const form = ref<{
    customerId?: number;
    billingBase: number;
    remark?: string;
  }>({ billingBase: 1 });

  const selectedAmount = computed(() =>
    selected.value.reduce((sum, r) => sum + Number(r.freightAmount || 0), 0)
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

  const onOpen = () => {
    form.value = { customerId: props.customerId, billingBase: 1 };
    period.value = defaultPeriod();
    keyword.value = '';
    candidates.value = [];
    selected.value = [];
    tableRef.value?.clearSelection?.();
    if (props.customerId) {
      loadCandidates();
    }
  };

  const onSelectionChange = (rows: ReconCandidate[]) => {
    selected.value = rows;
  };

  const loadCandidates = async () => {
    if (!form.value.customerId) {
      candidates.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listReconCandidates({
        customerId: form.value.customerId,
        periodStart: period.value?.[0],
        periodEnd: period.value?.[1],
        keyword: keyword.value || void 0
      });
      candidates.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '运单加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const save = async () => {
    if (!form.value.customerId) {
      EleMessage.warning({ message: '请选择客户', plain: true });
      return;
    }
    if (!period.value?.[0] || !period.value?.[1]) {
      EleMessage.warning({ message: '请选择对账周期', plain: true });
      return;
    }
    if (!selected.value.length) {
      EleMessage.warning({ message: '请勾选要对账的运单', plain: true });
      return;
    }
    saving.value = true;
    try {
      const detail = await addRecon({
        customerId: form.value.customerId,
        periodStart: period.value[0],
        periodEnd: period.value[1],
        waybillIds: selected.value.map((r) => r.waybillId),
        billingBase: form.value.billingBase,
        remark: form.value.remark
      });
      EleMessage.success({
        message: `已生成对账单，共 ${selected.value.length} 张运单`,
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
  @use '../../_shared/ui.scss';
</style>
