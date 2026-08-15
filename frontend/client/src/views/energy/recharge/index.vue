<template>
  <ele-page>
    <recharge-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyRechargeTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '登记充值',
                permission: 'energy:recharge:add',
                onClick: () => openAdd()
              }
            ]"
          />
        </template>
        <template #status="{ row }">
          <el-tag
            :type="statusTagType(row.status)"
            size="small"
            :disable-transitions="true"
          >
            {{ RECHARGE_STATUSES[row.status] || row.status }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>
    <recharge-add
      v-model:visible="addVisible"
      :accounts="accounts"
      @done="reload"
    />
    <recharge-pay v-model:visible="payVisible" :data="payData" @done="reload" />
    <recharge-cancel
      v-model:visible="cancelVisible"
      :data="cancelData"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { CircleCheck, CircleClose } from '@element-plus/icons-vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageRecharges } from '@/api/energy';
  import {
    RECHARGE_STATUSES,
    asPage,
    formatMoney
  } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import RechargeSearch from './components/recharge-search.vue';
  import RechargeAdd from './components/recharge-add.vue';
  import RechargePay from './components/recharge-pay.vue';
  import RechargeCancel from './components/recharge-cancel.vue';
  import type { RechargeSearchParam } from './components/recharge-search.vue';

  defineOptions({ name: 'EnergyRecharge' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const { accounts, loadAccounts } = useEnergyLookups();
  const where = reactive<RechargeSearchParam>({});
  const addVisible = ref(false);
  const payVisible = ref(false);
  const cancelVisible = ref(false);
  const payData = ref<Record<string, any> | null>(null);
  const cancelData = ref<Record<string, any> | null>(null);

  const columns = ref<Columns>([
    { prop: 'docNo', label: '单号', minWidth: 160 },
    { prop: 'accountName', label: '能源账户', minWidth: 140 },
    {
      prop: 'plannedAmount',
      label: '充值金额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.plannedAmount)
    },
    {
      prop: 'actualAmount',
      label: '实付金额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.actualAmount)
    },
    { prop: 'bankAccountLabel', label: '付款账户', minWidth: 140 },
    { prop: 'paymentReference', label: '回单号', minWidth: 140 },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      minWidth: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const statusTagType = (status: number) => {
    if (status === 3 || status === 5) return 'success';
    if (status === 4) return 'info';
    if (status === 1 || status === 2) return 'warning';
    return 'info';
  };

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(await pageRecharges({ ...(tableWhere || where), ...pages }));
  };

  const reload = (next?: RechargeSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openAdd = async () => {
    await loadAccounts();
    addVisible.value = true;
  };

  const actionItems = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [];
    if (row.status !== 3 && row.status !== 4) {
      visible.push({
        title: '登记入账',
        icon: CircleCheck,
        permission: 'energy:recharge:pay',
        onClick: () => {
          payData.value = row;
          payVisible.value = true;
        }
      });
      visible.push({
        title: '撤销',
        icon: CircleClose,
        permission: 'energy:recharge:submit',
        danger: true,
        onClick: () => {
          cancelData.value = row;
          cancelVisible.value = true;
        }
      });
    }
    return buildActionColumnItems(visible);
  };

  onMounted(() => {
    loadAccounts();
  });
</script>
