<template>
  <ele-page>
    <contract-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="BillingContractTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增合同', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            草稿
          </el-tag>
          <el-tag
            v-else-if="row.status === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            生效
          </el-tag>
          <el-tag
            v-else-if="row.status === 2"
            type="warning"
            size="small"
            :disable-transitions="true"
          >
            已过期
          </el-tag>
          <el-tag
            v-else-if="row.status === 3"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
            已终止
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
    <contract-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
    <contract-detail v-model:visible="detailVisible" :data="detailData" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type { ButtonItem } from 'ele-admin-plus/es/ele-buttons/types';
  import ContractEdit from './components/contract-edit.vue';
  import ContractDetail from './components/contract-detail.vue';
  import ContractSearch from './components/contract-search.vue';
  import {
    pageContracts,
    activateContract,
    terminateContract,
    removeContract
  } from '@/api/billing/contract';
  import type {
    FreightContract,
    FreightContractParam
  } from '@/api/billing/contract/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'BillingContract' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<FreightContract | null>(null);
  const detailVisible = ref(false);
  const detailData = ref<FreightContract | null>(null);

  const statusLabel = (s?: number) => {
    if (s === 0) return '草稿';
    if (s === 1) return '生效';
    if (s === 2) return '已过期';
    if (s === 3) return '已终止';
    return '-';
  };

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'contractNo', label: '合同编号', minWidth: 140 },
    { prop: 'contractName', label: '合同名称', minWidth: 160 },
    { prop: 'customerName', label: '客户名称', minWidth: 140 },
    {
      prop: 'effectiveDate',
      label: '生效日期',
      minWidth: 120,
      align: 'center'
    },
    {
      prop: 'expiryDate',
      label: '失效日期',
      minWidth: 120,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row) => statusLabel(row.status)
    },
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
      width: 260,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const actionItems = (row: FreightContract): ButtonItem[] => {
    const items: ButtonItem[] = [
      { preset: 'edit', onClick: () => openEdit(row) },
      { preset: 'detail', onClick: () => openDetail(row) }
    ];
    if (row.status === 1) {
      items.push({
        title: '终止',
        onClick: () => terminate(row)
      });
    }
    if (row.status === 0) {
      items.push(
        {
          title: '激活',
          onClick: () => activate(row)
        },
        { preset: 'del', onClick: () => remove(row) }
      );
    }
    return items;
  };

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const res = await pageContracts({
      ...where,
      ...orders,
      ...pages
    });
    const raw = res as {
      list?: FreightContract[];
      count?: number;
      total?: number;
    };
    return {
      list: raw.list ?? [],
      count: raw.count ?? raw.total ?? 0
    };
  };

  const reload = (where?: FreightContractParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openEdit = (row?: FreightContract) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openDetail = (row: FreightContract) => {
    detailData.value = row;
    detailVisible.value = true;
  };

  const activate = (row: FreightContract) => {
    ElMessageBox.confirm(
      `确定要激活合同"${row.contractName}"吗？激活后将参与运费匹配。`,
      '系统提示',
      { type: 'info', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        activateContract(row.id!)
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

  const terminate = (row: FreightContract) => {
    ElMessageBox.confirm(
      `确定要终止合同"${row.contractName}"吗？终止后不可恢复。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        terminateContract(row.id!)
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

  const remove = (row: FreightContract) => {
    ElMessageBox.confirm(`确定要删除合同"${row.contractName}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeContract(row.id!)
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
