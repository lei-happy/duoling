<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <div class="dealer-search">
        <el-input
          v-model="keyword"
          clearable
          placeholder="名称 / 省 / 市 / 主营品牌"
          style="width: 280px"
          @keyup.enter="doSearch"
        />
        <el-button type="primary" @click="doSearch">查询</el-button>
      </div>
      <ele-pro-table
        ref="tableRef"
        row-key="dealerId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        highlight-current-row
        cache-key="BasicDataDealerTable"
      >
        <template #toolbar>
          <btn-items
            :items="[{ preset: 'add', title: '新增', onClick: () => openEdit() }]"
          />
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[
              { preset: 'edit', onClick: () => openEdit(row) },
              { preset: 'del', onClick: () => remove(row) }
            ]"
          />
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
  import { pageDealers, removeDealer } from '@/api/basic-data/dealer';
  import type { Dealer } from '@/api/basic-data/dealer/model';

  defineOptions({ name: 'BasicDataDealer' });

  const { openModal } = useModal();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const keyword = ref('');

  const doSearch = () => {
    reload({ keyword: keyword.value?.trim() || undefined }, 1);
  };

  const columns = ref<Columns>([
    { prop: 'dealerId', label: 'ID', width: 90, align: 'center' },
    { prop: 'dealerName', label: '经销商名称', minWidth: 160 },
    { prop: 'dealerType', label: '类型', width: 110 },
    { prop: 'mainBrand', label: '主营品牌', width: 120 },
    { prop: 'province', label: '省', width: 90 },
    { prop: 'city', label: '市', width: 90 },
    { prop: 'addressDetail', label: '地址', minWidth: 200 },
    {
      columnKey: 'action',
      label: '操作',
      width: 148,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageDealers({
      ...pages,
      keyword: where?.keyword as string | undefined
    }).then((res) => ({
      list: res.list,
      count: res.count
    }));
  };

  const reload = (where?: Record<string, unknown>, page?: number) => {
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
    ElMessageBox.confirm(
      `确定要删除「${row.dealerName}」吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
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

<style scoped>
  .dealer-search {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }
</style>
