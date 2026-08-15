<template>
  <ele-page>
    <recon-search
      :accounts="accounts"
      @search="(where) => reload(where, 1)"
    />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyReconTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '账户余额对账',
                permission: 'energy:recon:add',
                onClick: () => openBalance()
              },
              {
                title: '消费流水对账',
                permission: 'energy:recon:add',
                onClick: () => openConsumption()
              }
            ]"
          />
        </template>
        <template #reconType="{ row }">
          {{ row.reconType === 1 ? '余额' : '流水' }}
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

    <recon-balance
      v-model:visible="balanceVisible"
      :accounts="accounts"
      @done="reload"
    />
    <recon-consumption
      v-model:visible="consVisible"
      :accounts="accounts"
      @done="reload"
    />

    <el-drawer v-model="itemVisible" title="对账明细" size="720px">
      <ele-pro-table
        row-key="id"
        :columns="itemColumns"
        :datasource="items"
        :pagination="false"
        :show-overflow-tooltip="true"
      >
        <template #reconResult="{ row }">
          {{ RECON_RESULTS[row.reconResult] || row.reconResult }}
        </template>
        <template #processStatus="{ row }">
          {{ RECON_PROCESS[row.processStatus] || row.processStatus }}
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="itemActions(row)"
          />
        </template>
      </ele-pro-table>
    </el-drawer>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { CircleCheck, CircleClose, View } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    pageRecons,
    processReconItem,
    reconItems,
    settleRecon
  } from '@/api/energy';
  import {
    RECON_PROCESS,
    RECON_RESULTS,
    asPage,
    formatMoney
  } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import ReconSearch from './components/recon-search.vue';
  import ReconBalance from './components/recon-balance.vue';
  import ReconConsumption from './components/recon-consumption.vue';
  import type { ReconSearchParam } from './components/recon-search.vue';

  defineOptions({ name: 'EnergyRecon' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const { accounts, loadAccounts } = useEnergyLookups();
  const where = reactive<ReconSearchParam>({});
  const items = ref<any[]>([]);
  const currentReconId = ref(0);
  const balanceVisible = ref(false);
  const consVisible = ref(false);
  const itemVisible = ref(false);

  const columns = ref<Columns>([
    { prop: 'docNo', label: '对账单号', minWidth: 160 },
    {
      prop: 'reconType',
      label: '类型',
      width: 90,
      align: 'center',
      slot: 'reconType'
    },
    {
      prop: 'internalAmount',
      label: '系统金额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.internalAmount)
    },
    {
      prop: 'externalAmount',
      label: '外部金额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.externalAmount)
    },
    {
      prop: 'differenceAmount',
      label: '差异',
      width: 110,
      align: 'right',
      formatter: (row) => formatMoney(row.differenceAmount)
    },
    { prop: 'diffCount', label: '差异笔数', width: 90, align: 'center' },
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

  const itemColumns = ref<Columns>([
    {
      prop: 'reconResult',
      label: '结果',
      width: 110,
      slot: 'reconResult'
    },
    { prop: 'externalTransactionId', label: '外部流水号', minWidth: 140 },
    {
      prop: 'externalAmount',
      label: '外部金额',
      width: 100,
      align: 'right',
      formatter: (row) => formatMoney(row.externalAmount)
    },
    {
      prop: 'internalAmount',
      label: '系统金额',
      width: 100,
      align: 'right',
      formatter: (row) => formatMoney(row.internalAmount)
    },
    {
      prop: 'differenceAmount',
      label: '差异',
      width: 90,
      align: 'right',
      formatter: (row) => formatMoney(row.differenceAmount)
    },
    {
      prop: 'processStatus',
      label: '处理',
      width: 90,
      slot: 'processStatus'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 140,
      align: 'center',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(await pageRecons({ ...(tableWhere || where), ...pages }));
  };

  const reload = (next?: ReconSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openBalance = async () => {
    await loadAccounts();
    balanceVisible.value = true;
  };

  const openConsumption = async () => {
    await loadAccounts();
    consVisible.value = true;
  };

  const openItems = async (row: any) => {
    currentReconId.value = row.id;
    items.value = (await reconItems(row.id)) || [];
    itemVisible.value = true;
  };

  const actionItems = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '明细',
        icon: View,
        onClick: () => openItems(row)
      },
      {
        title: '确认核销',
        icon: CircleCheck,
        permission: 'energy:recon:execute',
        onClick: () => doSettle(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  const itemActions = (row: any): ButtonItem[] => {
    if (row.processStatus !== 'pending' || row.reconResult === 'MATCHED') {
      return [];
    }
    return buildActionColumnItems([
      {
        title: '确认',
        icon: CircleCheck,
        onClick: () => processItem(row, 'confirmed')
      },
      {
        title: '忽略',
        icon: CircleClose,
        onClick: () => processItem(row, 'ignored')
      }
    ]);
  };

  const processItem = async (row: any, processStatus: string) => {
    await processReconItem(row.id, { processStatus });
    EleMessage.success({
      message: processStatus === 'ignored' ? '已忽略这条差异' : '已确认这条差异',
      plain: true
    });
    items.value = (await reconItems(currentReconId.value)) || [];
  };

  const doSettle = (row: any) => {
    ElMessageBox.confirm(
      '确认核销这张对账单？未处理的差异需要先确认或忽略。',
      '核销确认',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        await settleRecon(row.id);
        EleMessage.success({ message: '已核销', plain: true });
        reload();
      })
      .catch(() => undefined);
  };

  onMounted(() => {
    loadAccounts();
  });
</script>
