<template>
  <ele-page>
    <card-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyCardTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新增能源卡',
                permission: 'energy:card:add',
                onClick: () => openEdit()
              }
            ]"
          />
        </template>
        <template #energyType="{ row }">
          {{ labelOf(ENERGY_TYPES, row.energyType) }}
        </template>
        <template #bind="{ row }">
          {{ bindText(row) }}
        </template>
        <template #status="{ row }">
          <el-tag
            :type="row.status === 1 ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ labelOf(CARD_STATUSES, row.status) }}
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
    <card-edit
      v-model:visible="editVisible"
      :data="editData"
      :accounts="accounts"
      @done="reload"
    />
    <card-bind
      v-model:visible="bindVisible"
      :card="bindData"
      :vehicles="vehicles"
      :drivers="drivers"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { Link, Unlock } from '@element-plus/icons-vue';
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
  import { pageCards, removeCard, unbindCard } from '@/api/energy';
  import {
    CARD_STATUSES,
    ENERGY_TYPES,
    asPage,
    labelOf
  } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import CardSearch from './components/card-search.vue';
  import CardEdit from './components/card-edit.vue';
  import CardBind from './components/card-bind.vue';
  import type { CardSearchParam } from './components/card-search.vue';

  defineOptions({ name: 'EnergyCard' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const { accounts, vehicles, drivers, loadAccounts, loadVehicles, loadDrivers } =
    useEnergyLookups();
  const where = reactive<CardSearchParam>({});
  const editVisible = ref(false);
  const bindVisible = ref(false);
  const editData = ref<Record<string, any> | null>(null);
  const bindData = ref<Record<string, any> | null>(null);

  const columns = ref<Columns>([
    { prop: 'cardNo', label: '卡号', minWidth: 160 },
    { prop: 'accountName', label: '所属账户', minWidth: 160 },
    {
      prop: 'energyType',
      label: '能源',
      width: 80,
      align: 'center',
      slot: 'energyType'
    },
    { prop: 'cardType', label: '卡类型', width: 100, align: 'center' },
    { prop: 'bind', label: '当前绑定', minWidth: 180, slot: 'bind' },
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

  const bindText = (row: any) => {
    const parts: string[] = [];
    const plate = vehicles.value.find((v) => v.id === row.vehicleId)?.plateNumber;
    const driver = drivers.value.find((d) => d.id === row.driverId);
    if (row.vehicleId) parts.push(plate || `车辆 ${row.vehicleId}`);
    if (row.driverId) parts.push(driver?.name || `司机 ${row.driverId}`);
    return parts.join(' / ') || '未绑定';
  };

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(await pageCards({ ...(tableWhere || where), ...pages }));
  };

  const reload = (next?: CardSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openEdit = (row?: any) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openBind = async (row: any) => {
    await Promise.all([loadVehicles(), loadDrivers()]);
    bindData.value = row;
    bindVisible.value = true;
  };

  const actionItems = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'energy:card:edit',
        onClick: () => openEdit(row)
      },
      {
        title: '绑定',
        icon: Link,
        permission: 'energy:card:bind',
        onClick: () => openBind(row)
      }
    ];
    if (row.vehicleId || row.driverId) {
      visible.push({
        title: '解绑',
        icon: Unlock,
        permission: 'energy:card:bind',
        onClick: () => doUnbind(row)
      });
    }
    visible.push({
      title: '删除',
      icon: DeleteOutlined,
      permission: 'energy:card:edit',
      divided: true,
      danger: true,
      onClick: () => doRemove(row)
    });
    return buildActionColumnItems(visible);
  };

  const doUnbind = (row: any) => {
    ElMessageBox.confirm(
      '解绑后这张卡不再对应当前车辆/司机，历史绑定会保留。',
      '解绑确认',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        await unbindCard(row.id);
        EleMessage.success({ message: '已解绑', plain: true });
        reload();
      })
      .catch(() => undefined);
  };

  const doRemove = (row: any) => {
    ElMessageBox.confirm(`确定删除卡「${row.cardNo}」？`, '删除确认', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        await removeCard(row.id);
        EleMessage.success({ message: '已删除能源卡', plain: true });
        reload();
      })
      .catch(() => undefined);
  };

  onMounted(async () => {
    await Promise.all([loadAccounts(), loadVehicles(), loadDrivers()]);
  });
</script>
