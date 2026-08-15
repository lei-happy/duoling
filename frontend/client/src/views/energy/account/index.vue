<template>
  <ele-page>
    <account-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyAccountTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新增账户',
                permission: 'energy:account:add',
                onClick: () => openEdit()
              }
            ]"
          />
        </template>
        <template #energyType="{ row }">
          {{ labelOf(ENERGY_TYPES, row.energyType) }}
        </template>
        <template #accountType="{ row }">
          {{ labelOf(ACCOUNT_TYPES, row.accountType) }}
        </template>
        <template #status="{ row }">
          <el-tag
            :type="row.status === 1 ? 'success' : row.status === 2 ? 'warning' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ labelOf(ACCOUNT_STATUSES, row.status) }}
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
    <account-edit
      v-model:visible="editVisible"
      :data="editData"
      :suppliers="suppliers"
      @done="reload"
    />
    <account-adjust
      v-model:visible="adjustVisible"
      :account="adjustData"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { Wallet } from '@element-plus/icons-vue';
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
  import { DeleteOutlined, EditOutlined } from '@/components/icons';
  import { pageAccounts, removeAccount } from '@/api/energy';
  import {
    ACCOUNT_STATUSES,
    ACCOUNT_TYPES,
    ENERGY_TYPES,
    asPage,
    formatMoney,
    labelOf
  } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import AccountSearch from './components/account-search.vue';
  import AccountEdit from './components/account-edit.vue';
  import AccountAdjust from './components/account-adjust.vue';
  import type { AccountSearchParam } from './components/account-search.vue';

  defineOptions({ name: 'EnergyAccount' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const { suppliers, loadSuppliers } = useEnergyLookups();
  const where = reactive<AccountSearchParam>({});
  const editVisible = ref(false);
  const adjustVisible = ref(false);
  const editData = ref<Record<string, any> | null>(null);
  const adjustData = ref<Record<string, any> | null>(null);

  const columns = ref<Columns>([
    { prop: 'accountCode', label: '账户编码', minWidth: 140 },
    { prop: 'accountName', label: '账户名称', minWidth: 180 },
    { prop: 'supplierName', label: '供应商', minWidth: 140 },
    {
      prop: 'energyType',
      label: '能源',
      width: 80,
      align: 'center',
      slot: 'energyType'
    },
    {
      prop: 'accountType',
      label: '类型',
      width: 110,
      align: 'center',
      slot: 'accountType'
    },
    {
      prop: 'ledgerBalance',
      label: '账面余额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.ledgerBalance)
    },
    {
      prop: 'availableBalance',
      label: '可用余额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.availableBalance)
    },
    {
      prop: 'diffAmount',
      label: '差异',
      width: 100,
      align: 'right',
      formatter: (row) => formatMoney(row.diffAmount)
    },
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

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(await pageAccounts({ ...(tableWhere || where), ...pages }));
  };

  const reload = (next?: AccountSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openEdit = (row?: any) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openAdjust = (row: any) => {
    adjustData.value = row;
    adjustVisible.value = true;
  };

  const actionItems = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'energy:account:edit',
        onClick: () => openEdit(row)
      },
      {
        title: '调账',
        icon: Wallet,
        permission: 'energy:account:adjust',
        onClick: () => openAdjust(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        permission: 'energy:account:delete',
        divided: true,
        danger: true,
        onClick: () => doRemove(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  const doRemove = (row: any) => {
    ElMessageBox.confirm(`确定删除账户「${row.accountName}」？`, '删除确认', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        const loading = EleMessage.loading({
          message: '正在删除账户，请稍候…',
          plain: true
        });
        try {
          await removeAccount(row.id);
          loading.close();
          EleMessage.success({ message: '已删除账户', plain: true });
          reload();
        } catch (e: any) {
          loading.close();
          EleMessage.error({
            message: e.message || '删除失败，请稍后重试',
            plain: true
          });
        }
      })
      .catch(() => undefined);
  };

  onMounted(() => {
    loadSuppliers();
  });
</script>
