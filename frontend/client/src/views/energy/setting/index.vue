<template>
  <ele-page>
    <el-tabs v-model="tab" @tab-change="onTabChange">
      <el-tab-pane label="能源商品" name="product">
        <ele-card :body-style="{ paddingTop: '8px' }">
          <ele-pro-table
            ref="productTableRef"
            row-key="id"
            :columns="productColumns"
            :datasource="productDatasource"
            :pagination="false"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            cache-key="EnergyProductTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新增商品',
                    permission: 'energy:setting:edit',
                    onClick: () => openProduct()
                  }
                ]"
              />
            </template>
            <template #energyType="{ row }">
              {{ labelOf(ENERGY_TYPES, row.energyType) }}
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :wrap="false"
                :items="productActions(row)"
              />
            </template>
          </ele-pro-table>
        </ele-card>
      </el-tab-pane>

      <el-tab-pane label="车辆能源档案" name="profile">
        <ele-card :body-style="{ paddingTop: '8px' }">
          <ele-pro-table
            ref="profileTableRef"
            row-key="id"
            :columns="profileColumns"
            :datasource="profileDatasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            cache-key="EnergyProfileTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '维护档案',
                    permission: 'energy:setting:edit',
                    onClick: () => openProfile()
                  }
                ]"
              />
            </template>
            <template #vehicle="{ row }">
              {{ plateOf(row.vehicleId) }}
            </template>
            <template #energyType="{ row }">
              {{ labelOf(ENERGY_TYPES, row.energyType) }}
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :wrap="false"
                :items="profileActions(row)"
              />
            </template>
          </ele-pro-table>
        </ele-card>
      </el-tab-pane>

      <el-tab-pane label="风控阈值" name="rule">
        <ele-card :body-style="{ paddingTop: '8px' }">
          <ele-pro-table
            ref="ruleTableRef"
            row-key="id"
            :columns="ruleColumns"
            :datasource="ruleDatasource"
            :pagination="false"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            cache-key="EnergyRuleTable"
          >
            <template #riskLevel="{ row }">
              {{ labelOf(RISK_LEVELS, row.riskLevel) }}
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :wrap="false"
                :items="ruleActions(row)"
              />
            </template>
          </ele-pro-table>
        </ele-card>
      </el-tab-pane>
    </el-tabs>

    <product-edit
      v-model:visible="productVisible"
      :data="productData"
      @done="reloadProducts"
    />
    <profile-edit
      v-model:visible="profileVisible"
      :data="profileData"
      :vehicles="vehicles"
      :products="productList"
      @done="reloadProfiles"
    />
    <rule-edit
      v-model:visible="ruleVisible"
      :data="ruleData"
      @done="reloadRules"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { nextTick, onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { Setting } from '@element-plus/icons-vue';
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
  import {
    listProducts,
    listRules,
    pageProfiles,
    removeProduct
  } from '@/api/energy';
  import { ENERGY_TYPES, RISK_LEVELS, asPage, labelOf } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import ProductEdit from './components/product-edit.vue';
  import ProfileEdit from './components/profile-edit.vue';
  import RuleEdit from './components/rule-edit.vue';

  defineOptions({ name: 'EnergySetting' });

  const tab = ref('product');
  const productTableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const profileTableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const ruleTableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const { vehicles, loadVehicles } = useEnergyLookups();
  const productList = ref<any[]>([]);

  const productVisible = ref(false);
  const profileVisible = ref(false);
  const ruleVisible = ref(false);
  const productData = ref<Record<string, any> | null>(null);
  const profileData = ref<Record<string, any> | null>(null);
  const ruleData = ref<Record<string, any> | null>(null);

  const productColumns = ref<Columns>([
    { prop: 'productCode', label: '编码', minWidth: 140 },
    { prop: 'productName', label: '名称', minWidth: 160 },
    {
      prop: 'energyType',
      label: '类型',
      width: 90,
      align: 'center',
      slot: 'energyType'
    },
    { prop: 'standardUnit', label: '单位', width: 80, align: 'center' },
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

  const profileColumns = ref<Columns>([
    { prop: 'vehicleId', label: '车辆', minWidth: 140, slot: 'vehicle' },
    {
      prop: 'energyType',
      label: '能源',
      width: 90,
      align: 'center',
      slot: 'energyType'
    },
    { prop: 'tankCapacity', label: '油箱容量', width: 110, align: 'right' },
    { prop: 'batteryCapacity', label: '电池容量', width: 110, align: 'right' },
    {
      prop: 'standardConsumptionPer100km',
      label: '标准百公里',
      width: 120,
      align: 'right'
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

  const ruleColumns = ref<Columns>([
    { prop: 'ruleName', label: '规则', minWidth: 180 },
    { prop: 'thresholdValue', label: '阈值', width: 120, align: 'right' },
    {
      prop: 'riskLevel',
      label: '等级',
      width: 90,
      align: 'center',
      slot: 'riskLevel'
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

  const productDatasource: DatasourceFunction = async () => {
    const list = (await listProducts()) || [];
    productList.value = list;
    return { list, count: list.length };
  };

  const profileDatasource: DatasourceFunction = async ({ pages }) => {
    return asPage(await pageProfiles({ ...pages }));
  };

  const ruleDatasource: DatasourceFunction = async () => {
    const list = (await listRules()) || [];
    return { list, count: list.length };
  };

  const plateOf = (id?: number) =>
    vehicles.value.find((v) => v.id === id)?.plateNumber ||
    (id ? `车辆 ${id}` : '-');

  const reloadProducts = () => productTableRef.value?.reload?.();
  const reloadProfiles = () => profileTableRef.value?.reload?.();
  const reloadRules = () => ruleTableRef.value?.reload?.();

  const onTabChange = (name: string | number) => {
    nextTick(() => {
      if (name === 'product') reloadProducts();
      if (name === 'profile') reloadProfiles();
      if (name === 'rule') reloadRules();
    });
  };

  const openProduct = (row?: any) => {
    productData.value = row ?? null;
    productVisible.value = true;
  };

  const openProfile = async (row?: any) => {
    await loadVehicles();
    profileData.value = row ?? null;
    profileVisible.value = true;
  };

  const openRule = (row: any) => {
    ruleData.value = row;
    ruleVisible.value = true;
  };

  const productActions = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'energy:setting:edit',
        onClick: () => openProduct(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        permission: 'energy:setting:edit',
        danger: true,
        onClick: () => doRemoveProduct(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  const profileActions = (row: any): ButtonItem[] => {
    return buildActionColumnItems([
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'energy:setting:edit',
        onClick: () => openProfile(row)
      }
    ]);
  };

  const ruleActions = (row: any): ButtonItem[] => {
    return buildActionColumnItems([
      {
        title: '调整',
        icon: Setting,
        permission: 'energy:setting:edit',
        onClick: () => openRule(row)
      }
    ]);
  };

  const doRemoveProduct = (row: any) => {
    ElMessageBox.confirm(`确定删除商品「${row.productName}」？`, '删除确认', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        await removeProduct(row.id);
        EleMessage.success({ message: '已删除商品', plain: true });
        reloadProducts();
      })
      .catch(() => undefined);
  };

  onMounted(async () => {
    await loadVehicles();
  });
</script>
