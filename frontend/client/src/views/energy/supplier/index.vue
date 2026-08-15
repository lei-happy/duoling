<template>
  <ele-page>
    <el-tabs v-model="tab" @tab-change="onTabChange">
      <el-tab-pane label="供应商" name="supplier">
        <supplier-search @search="(where) => reloadSuppliers(where, 1)" />
        <ele-card :body-style="{ paddingTop: '8px' }">
          <ele-pro-table
            ref="supplierTableRef"
            row-key="id"
            :columns="supplierColumns"
            :datasource="supplierDatasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            cache-key="EnergySupplierTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新增供应商',
                    permission: 'energy:supplier:add',
                    onClick: () => openSupplier()
                  }
                ]"
              />
            </template>
            <template #supplierType="{ row }">
              {{ labelOf(SUPPLIER_TYPES, row.supplierType) }}
            </template>
            <template #stationCount="{ row }">
              <el-button link type="primary" @click="goStations(row)">
                {{ row.stationCount || 0 }} 个
              </el-button>
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :wrap="false"
                :items="supplierActions(row)"
              />
            </template>
          </ele-pro-table>
        </ele-card>
      </el-tab-pane>

      <el-tab-pane label="站点" name="station">
        <station-search
          ref="stationSearchRef"
          :suppliers="supplierOptions"
          @search="(where) => reloadStations(where, 1)"
        />
        <ele-card :body-style="{ paddingTop: '8px' }">
          <ele-pro-table
            ref="stationTableRef"
            row-key="id"
            :columns="stationColumns"
            :datasource="stationDatasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            cache-key="EnergyStationTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新增站点',
                    permission: 'energy:supplier:add',
                    onClick: () => openStation()
                  }
                ]"
              />
            </template>
            <template #location="{ row }">
              {{ formatLocation(row) }}
            </template>
            <template #products="{ row }">
              <div v-if="row.products?.length" class="price-list">
                <span v-for="p in row.products" :key="p.id" class="price-chip">
                  {{ productLabel(p) }}
                  {{ formatMoney(p.settlementPrice) }} 元/{{ p.unit || 'L' }}
                </span>
              </div>
              <span v-else class="muted">未维护</span>
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :wrap="false"
                :items="stationActions(row)"
              />
            </template>
          </ele-pro-table>
        </ele-card>
      </el-tab-pane>
    </el-tabs>

    <supplier-edit
      v-model:visible="supplierVisible"
      :data="supplierEditData"
      @done="onSupplierDone"
    />
    <station-edit
      v-model:visible="stationVisible"
      :data="stationEditData"
      :suppliers="supplierOptions"
      :products="products"
      :default-supplier-id="stationWhere.supplierId"
      @done="onStationDone"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { nextTick, onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { Location } from '@element-plus/icons-vue';
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
    pageStations,
    pageSuppliers,
    removeStation,
    removeSupplier
  } from '@/api/energy';
  import {
    ENERGY_TYPES,
    SUPPLIER_TYPES,
    asPage,
    formatMoney,
    labelOf
  } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import SupplierSearch from './components/supplier-search.vue';
  import StationSearch from './components/station-search.vue';
  import SupplierEdit from './components/supplier-edit.vue';
  import StationEdit from './components/station-edit.vue';
  import type { SupplierSearchParam } from './components/supplier-search.vue';
  import type { StationSearchParam } from './components/station-search.vue';

  defineOptions({ name: 'EnergySupplier' });

  const tab = ref('supplier');
  const supplierTableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const stationTableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const stationSearchRef = ref<InstanceType<typeof StationSearch> | null>(null);
  const { products, loadProducts, loadSuppliers, suppliers: supplierOptions } =
    useEnergyLookups();

  const supplierWhere = reactive<SupplierSearchParam>({});
  const stationWhere = reactive<StationSearchParam>({});
  const supplierVisible = ref(false);
  const stationVisible = ref(false);
  const supplierEditData = ref<Record<string, any> | null>(null);
  const stationEditData = ref<Record<string, any> | null>(null);

  const supplierColumns = ref<Columns>([
    { prop: 'supplierCode', label: '编码', minWidth: 150 },
    { prop: 'supplierName', label: '名称', minWidth: 180 },
    {
      prop: 'supplierType',
      label: '类型',
      width: 120,
      align: 'center',
      slot: 'supplierType'
    },
    { prop: 'contactName', label: '联系人', minWidth: 110 },
    { prop: 'contactPhone', label: '联系电话', minWidth: 140 },
    {
      prop: 'stationCount',
      label: '站点',
      width: 90,
      align: 'center',
      slot: 'stationCount'
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

  const stationColumns = ref<Columns>([
    { prop: 'stationName', label: '站点名称', minWidth: 160 },
    { prop: 'stationCode', label: '编码', minWidth: 140 },
    { prop: 'supplierName', label: '供应商', minWidth: 140 },
    { prop: 'address', label: '地址', minWidth: 180 },
    {
      prop: 'location',
      label: '位置',
      width: 160,
      slot: 'location'
    },
    {
      prop: 'products',
      label: '结算价',
      minWidth: 240,
      slot: 'products'
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

  const supplierDatasource: DatasourceFunction = async ({ pages, where }) => {
    return asPage(
      await pageSuppliers({ ...(where || supplierWhere), ...pages })
    );
  };

  const stationDatasource: DatasourceFunction = async ({ pages, where }) => {
    return asPage(await pageStations({ ...(where || stationWhere), ...pages }));
  };

  const reloadSuppliers = (where?: SupplierSearchParam, page?: number) => {
    if (where) Object.assign(supplierWhere, where);
    supplierTableRef.value?.reload?.({ where: { ...supplierWhere }, page });
  };

  const reloadStations = (where?: StationSearchParam, page?: number) => {
    if (where) Object.assign(stationWhere, where);
    stationTableRef.value?.reload?.({ where: { ...stationWhere }, page });
  };

  const onTabChange = (name: string | number) => {
    nextTick(() => {
      if (name === 'station') reloadStations();
      if (name === 'supplier') reloadSuppliers();
    });
  };

  const productLabel = (p: any) =>
    p.productName || labelOf(ENERGY_TYPES, p.energyType);

  const formatLocation = (row: any) => {
    if (row.longitude == null || row.latitude == null) return '—';
    return `${row.longitude}, ${row.latitude}`;
  };

  const goStations = (row: any) => {
    tab.value = 'station';
    nextTick(() => stationSearchRef.value?.setSupplier(row.id));
  };

  const openSupplier = (row?: any) => {
    supplierEditData.value = row ?? null;
    supplierVisible.value = true;
  };

  const openStation = (row?: any) => {
    stationEditData.value = row ?? null;
    stationVisible.value = true;
  };

  const supplierActions = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'energy:supplier:edit',
        onClick: () => openSupplier(row)
      },
      {
        title: '查看站点',
        icon: Location,
        onClick: () => goStations(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        permission: 'energy:supplier:edit',
        divided: true,
        danger: true,
        onClick: () => doRemoveSupplier(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  const stationActions = (row: any): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'energy:supplier:edit',
        onClick: () => openStation(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        permission: 'energy:supplier:edit',
        danger: true,
        onClick: () => doRemoveStation(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  const doRemoveSupplier = (row: any) => {
    ElMessageBox.confirm(`确定删除供应商「${row.supplierName}」？`, '删除确认', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        const loading = EleMessage.loading({
          message: '正在删除供应商，请稍候…',
          plain: true
        });
        try {
          await removeSupplier(row.id);
          loading.close();
          EleMessage.success({ message: '已删除供应商', plain: true });
          reloadSuppliers();
          loadSuppliers();
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

  const doRemoveStation = (row: any) => {
    ElMessageBox.confirm(`确定删除站点「${row.stationName}」？`, '删除确认', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        const loading = EleMessage.loading({
          message: '正在删除站点，请稍候…',
          plain: true
        });
        try {
          await removeStation(row.id);
          loading.close();
          EleMessage.success({ message: '已删除站点', plain: true });
          reloadStations();
          reloadSuppliers();
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

  const onSupplierDone = () => {
    reloadSuppliers();
    loadSuppliers();
  };

  const onStationDone = () => {
    reloadStations();
    reloadSuppliers();
  };

  onMounted(async () => {
    await Promise.all([loadSuppliers(), loadProducts()]);
  });
</script>

<style scoped>
  .price-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .price-chip {
    display: inline-flex;
    align-items: center;
    padding: 0 8px;
    height: 22px;
    border-radius: 11px;
    background: var(--el-fill-color);
    font-size: 12px;
    color: var(--el-text-color-regular);
  }

  .muted {
    color: var(--el-text-color-placeholder);
  }
</style>
