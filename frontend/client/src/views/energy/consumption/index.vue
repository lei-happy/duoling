<template>
  <ele-page>
    <consumption-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyConsumptionTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '手工录入',
                permission: 'energy:consumption:add',
                onClick: () => openAdd()
              }
            ]"
          />
        </template>
        <template #matchStatus="{ row }">
          <el-tag
            :type="matchTagType(row.matchStatus)"
            size="small"
            :disable-transitions="true"
          >
            {{ labelOf(MATCH_STATUSES, row.matchStatus) }}
          </el-tag>
        </template>
        <template #sourceChannel="{ row }">
          {{ labelOf(SOURCE_CHANNELS, row.sourceChannel) }}
        </template>
        <template #ledger="{ row }">
          {{ row.isLedgerAffecting === 0 ? '否' : '是' }}
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
    <consumption-add
      v-model:visible="addVisible"
      :accounts="accounts"
      :products="products"
      :vehicles="vehicles"
      :drivers="drivers"
      @done="reload"
    />
    <consumption-assign
      v-model:visible="assignVisible"
      :data="assignData"
      :accounts="accounts"
      :vehicles="vehicles"
      :drivers="drivers"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { User } from '@element-plus/icons-vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageConsumptions } from '@/api/energy';
  import { formatDateTime } from '@/utils/date-util';
  import {
    MATCH_STATUSES,
    SOURCE_CHANNELS,
    asPage,
    formatMoney,
    labelOf
  } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import ConsumptionSearch from './components/consumption-search.vue';
  import ConsumptionAdd from './components/consumption-add.vue';
  import ConsumptionAssign from './components/consumption-assign.vue';
  import type { ConsumptionSearchParam } from './components/consumption-search.vue';

  defineOptions({ name: 'EnergyConsumption' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const {
    accounts,
    products,
    vehicles,
    drivers,
    loadAccounts,
    loadProducts,
    loadVehicles,
    loadDrivers
  } = useEnergyLookups();
  const where = reactive<ConsumptionSearchParam>({});
  const addVisible = ref(false);
  const assignVisible = ref(false);
  const assignData = ref<Record<string, any> | null>(null);

  const columns = ref<Columns>([
    {
      prop: 'consumptionTime',
      label: '消费时间',
      minWidth: 170,
      formatter: (row) => formatDateTime(row.consumptionTime)
    },
    { prop: 'plateNumber', label: '车牌', width: 110 },
    { prop: 'cardNo', label: '卡号', minWidth: 130 },
    { prop: 'productName', label: '商品', width: 100 },
    { prop: 'quantity', label: '数量', width: 80, align: 'right' },
    {
      prop: 'amount',
      label: '金额',
      width: 100,
      align: 'right',
      formatter: (row) => formatMoney(row.amount)
    },
    {
      prop: 'matchStatus',
      label: '匹配',
      width: 100,
      align: 'center',
      slot: 'matchStatus'
    },
    {
      prop: 'sourceChannel',
      label: '来源',
      width: 130,
      slot: 'sourceChannel'
    },
    {
      prop: 'isLedgerAffecting',
      label: '入账',
      width: 80,
      align: 'center',
      slot: 'ledger'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 100,
      minWidth: 100,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const matchTagType = (status?: string) => {
    if (status === 'MATCHED') return 'success';
    if (status === 'PARTIAL') return 'warning';
    if (status === 'CONFLICT') return 'danger';
    return 'info';
  };

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(
      await pageConsumptions({ ...(tableWhere || where), ...pages })
    );
  };

  const reload = (next?: ConsumptionSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openAdd = async () => {
    await Promise.all([
      loadAccounts(),
      loadProducts(),
      loadVehicles(),
      loadDrivers()
    ]);
    addVisible.value = true;
  };

  const openAssign = async (row: any) => {
    await Promise.all([loadVehicles(), loadDrivers(), loadAccounts()]);
    assignData.value = row;
    assignVisible.value = true;
  };

  const actionItems = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '归属',
        icon: User,
        onClick: () => openAssign(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  onMounted(() => {
    loadVehicles();
    loadDrivers();
  });
</script>
