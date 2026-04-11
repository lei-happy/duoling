<template>
  <ele-page>
    <dealer-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="dealerId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="BasicDataDealerTable"
      >
        <template #toolbar>
          <btn-items
            v-if="hasPermission(PERM_ADD)"
            :items="[
              { preset: 'add', title: '新增', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import DealerSearch from './components/dealer-search.vue';
  import { pageDealers, removeDealer } from '@/api/basic-data/dealer';
  import type { Dealer, DealerParam } from '@/api/basic-data/dealer/model';
  import { usePermission } from '@/utils/use-permission';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'BasicDataDealer' });

  const PERM_ADD = 'basic_data:dealer:add';
  const PERM_EDIT = 'basic_data:dealer:edit';
  const PERM_DEL = 'basic_data:dealer:delete';

  const { hasPermission } = usePermission();
  const { openModal } = useModal();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    { prop: 'dealerName', label: '经销商名称', minWidth: 160 },
    { prop: 'dealerType', label: '类型', width: 110 },
    { prop: 'mainBrand', label: '主营品牌', width: 120 },
    { prop: 'province', label: '省', width: 90 },
    { prop: 'city', label: '市', width: 90 },
    { prop: 'addressDetail', label: '地址', minWidth: 200 },
    {
      prop: 'createdAt',
      label: '创建时间',
      sortable: 'custom',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 148,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const actionItems = (row: Dealer) => {
    const items: any[] = [];
    if (hasPermission(PERM_EDIT)) {
      items.push({ preset: 'edit', onClick: () => openEdit(row) });
    }
    if (hasPermission(PERM_DEL)) {
      items.push({ preset: 'del', onClick: () => remove(row) });
    }
    return items;
  };

  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageDealers({ ...where, ...orders, ...pages });
  };

  const reload = (where?: DealerParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openEdit = (row?: Dealer) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/dealer-edit.vue'),
      componentProps: {
        data: row ?? null,
        onDone: () => reload()
      }
    });
  };

  const remove = (row: Dealer) => {
    ElMessageBox.confirm(`确定要删除「${row.dealerName}」吗？`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeDealer(row.dealerId)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
