<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        cache-key="FinanceCustomerReconTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="对账单号/客户"
                clearable
                style="width: 190px"
                @change="reload()"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.customerId"
                placeholder="客户"
                clearable
                filterable
                style="width: 200px"
                @change="reload()"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :value="c.id"
                  :label="c.customerName"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                style="width: 110px"
                @change="reload()"
              >
                <el-option
                  v-for="o in RECON_STATUS_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-date-picker
                v-model="period"
                type="daterange"
                value-format="YYYY-MM-DD"
                start-placeholder="周期开始"
                end-placeholder="周期结束"
                style="width: 240px"
                @change="onPeriodChange"
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="where.onlyDirty" @change="reload()">
                只看待重核
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="where.onlyDiff" @change="reload()">
                只看有差异
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新建对账单',
                    permission: 'finance:cust-recon:create',
                    onClick: () => openCreate()
                  }
                ]"
              />
            </el-form-item>
          </el-form>
        </template>

        <template #period="{ row }">
          <span v-if="row.periodStart || row.periodEnd">
            {{ formatDate(row.periodStart) }} ~ {{ formatDate(row.periodEnd) }}
          </span>
          <span v-else>--</span>
        </template>

        <template #amount="{ row }">
          <div class="num-cell">¥ {{ formatMoney(row.plannedAmount) }}</div>
          <div v-if="row.adjustAmountTotal" class="num-cell sub-adjust">
            含调整 {{ formatMoney(row.adjustAmountTotal) }}
          </div>
        </template>

        <template #progress="{ row }">
          <div class="num-cell"
            >已结算 {{ formatMoney(row.appliedAmountTotal) }}</div
          >
          <div class="num-cell sub-received">
            已收款 {{ formatMoney(row.receivedAmountTotal) }}
          </div>
        </template>

        <template #marks="{ row }">
          <el-tag
            v-if="row.dirtyLineCount"
            type="warning"
            size="small"
            effect="plain"
          >
            待重核 {{ row.dirtyLineCount }}
          </el-tag>
          <el-tag
            v-if="row.diffOpenCount"
            type="danger"
            size="small"
            effect="plain"
            style="margin-left: 4px"
          >
            差异 {{ row.diffOpenCount }}
          </el-tag>
          <el-tag
            v-if="row.diffForcedCount"
            type="info"
            size="small"
            effect="plain"
            style="margin-left: 4px"
          >
            强制放行 {{ row.diffForcedCount }}
          </el-tag>
          <span
            v-if="
              !row.dirtyLineCount && !row.diffOpenCount && !row.diffForcedCount
            "
          >
            —
          </span>
        </template>

        <template #status="{ row }">
          <el-tag
            :type="(RECON_STATUS_MAP[row.status]?.type as any) || 'info'"
            size="small"
          >
            {{ row.statusLabel || RECON_STATUS_MAP[row.status]?.label }}
          </el-tag>
          <div v-if="row.confirmedByCustomerAt" class="sign-hint">已回签</div>
        </template>

        <template #action="{ row }">
          <el-link
            type="primary"
            :underline="false"
            v-permission="'finance:cust-recon:detail'"
            @click="openDetail(row.id)"
          >
            详情
          </el-link>
          <template v-if="row.status === 0">
            <el-divider direction="vertical" />
            <el-link
              type="success"
              :underline="false"
              v-permission="'finance:cust-recon:confirm'"
              @click="confirmRow(row)"
            >
              确认
            </el-link>
          </template>
          <template v-if="row.status === 2 && !row.confirmedByCustomerAt">
            <el-divider direction="vertical" />
            <el-link
              type="primary"
              :underline="false"
              v-permission="'finance:cust-recon:customer-sign'"
              @click="openDetail(row.id)"
            >
              登记回签
            </el-link>
          </template>
        </template>
      </ele-pro-table>
    </ele-card>

    <recon-create
      v-model:visible="createVisible"
      :customer-id="presetCustomerId"
      :customers="customers"
      @done="onCreated"
    />

    <recon-detail
      v-model:visible="detailVisible"
      :recon-id="detailId"
      @changed="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, reactive, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import ReconCreate from './components/recon-create.vue';
  import ReconDetail from './components/recon-detail.vue';
  import { confirmRecon, pageRecons } from '@/api/finance/customer-recon';
  import type {
    ReconListItem,
    ReconParam
  } from '@/api/finance/customer-recon/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDate } from '@/utils/date-util';
  import {
    formatMoney,
    RECON_STATUS_MAP,
    RECON_STATUS_OPTIONS
  } from '../status-config';

  defineOptions({ name: 'FinanceCustomerRecon' });

  const route = useRoute();
  const router = useRouter();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<ReconParam>({});
  const period = ref<[string, string] | null>(null);
  const customers = ref<CustomerSelectItem[]>([]);

  const createVisible = ref(false);
  const presetCustomerId = ref<number | undefined>(void 0);
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);

  const columns = computed<Columns>(() => [
    { prop: 'docNo', label: '对账单号', minWidth: 170 },
    { prop: 'customerName', label: '客户', minWidth: 180 },
    {
      columnKey: 'period',
      label: '对账周期',
      width: 200,
      align: 'center',
      slot: 'period'
    },
    {
      prop: 'waybillCount',
      label: '运单数',
      width: 90,
      align: 'center'
    },
    {
      columnKey: 'amount',
      label: '对账金额',
      width: 160,
      align: 'right',
      slot: 'amount'
    },
    {
      columnKey: 'progress',
      label: '结算进度',
      width: 170,
      align: 'right',
      slot: 'progress'
    },
    {
      columnKey: 'marks',
      label: '核对标记',
      width: 170,
      align: 'center',
      slot: 'marks'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 160,
      align: 'center',
      formatter: (row) => formatDate(row.createdAt) || '--'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 180,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageRecons({ ...where, ...pages }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = () => {
    nextTick(() => tableRef.value?.reload?.());
  };

  const onPeriodChange = () => {
    where.periodStart = period.value?.[0];
    where.periodEnd = period.value?.[1];
    reload();
  };

  const openCreate = (customerId?: number) => {
    presetCustomerId.value = customerId;
    createVisible.value = true;
  };

  const onCreated = (reconId?: number) => {
    reload();
    if (reconId) {
      openDetail(reconId);
    }
  };

  const openDetail = (reconId: number) => {
    detailId.value = reconId;
    detailVisible.value = true;
  };

  const confirmRow = async (row: ReconListItem) => {
    try {
      await ElMessageBox.confirm(
        `确认对账单「${row.docNo}」？确认后客户方可回签，运单将不能再改动。`,
        '确认对账',
        {
          type: 'warning',
          confirmButtonText: '确认',
          cancelButtonText: '再看看'
        }
      );
    } catch {
      return;
    }
    const loading = EleMessage.loading({
      message: '正在确认对账单，请稍候…',
      plain: true
    });
    try {
      await confirmRecon(row.id);
      loading.close();
      EleMessage.success({ message: '对账单已确认', plain: true });
      reload();
    } catch (e: unknown) {
      loading.close();
      const msg = (e as { message?: string }).message || '确认失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  onMounted(async () => {
    try {
      customers.value = (await selectCustomers()) || [];
    } catch {
      // 客户下拉拉取失败不影响列表，用户仍可用关键词搜索
    }
    // 对账工作台「生成对账单」跳转带参：直接把客户预置进新建弹窗
    const q = route.query;
    if (q.create === '1' && q.customerId) {
      openCreate(Number(q.customerId));
      router.replace({ path: route.path });
    }
  });
</script>

<style lang="scss" scoped>
  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .sub-adjust {
    color: var(--el-color-warning);
    font-size: 12px;
  }

  .sub-received {
    color: var(--el-color-success);
    font-size: 12px;
  }

  .sign-hint {
    margin-top: 2px;
    color: var(--el-color-success);
    font-size: 12px;
  }
</style>
