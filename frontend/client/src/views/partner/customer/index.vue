<template>
  <ele-page>
    <customer-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="PartnerCustomerTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增客户', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #customerType="{ row }">
          <el-tag
            v-if="row.customerType === 0"
            size="small"
            :disable-transitions="true"
          >
            主机厂
          </el-tag>
          <el-tag
            v-else-if="row.customerType === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            贸易商
          </el-tag>
          <el-tag
            v-else-if="row.customerType === 2"
            type="warning"
            size="small"
            :disable-transitions="true"
          >
            经销商
          </el-tag>
          <el-tag
            v-else-if="row.customerType === 3"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            个人
          </el-tag>
          <el-tag v-else type="danger" size="small" :disable-transitions="true">
            其他
          </el-tag>
        </template>
        <template #settlementType="{ row }">
          <span v-if="row.settlementType === 0">月结</span>
          <span v-else-if="row.settlementType === 1">票结</span>
          <span v-else-if="row.settlementType === 2">预付</span>
        </template>
        <template #creditStatus="{ row }">
          <el-tooltip
            v-if="row.creditLimit != null"
            :content="`信用额度 ¥ ${Number(row.creditLimit).toLocaleString('zh-CN')}`"
          >
            <el-tag
              :type="CREDIT_TAG_TYPE[row.creditStatus ?? 1]"
              size="small"
              effect="plain"
            >
              {{ row.creditStatusLabel || '正常' }}
            </el-tag>
          </el-tooltip>
          <el-tag
            v-else
            :type="CREDIT_TAG_TYPE[row.creditStatus ?? 1]"
            size="small"
            effect="plain"
          >
            {{ row.creditStatusLabel || '正常' }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-switch
            v-if="row.id != null"
            size="small"
            :model-value="row.status === 1"
            :loading="statusLoadingId === row.id"
            @change="(checked: boolean) => toggleStatus(checked, row)"
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
    <customer-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
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
  import CustomerEdit from './components/customer-edit.vue';
  import CustomerSearch from './components/customer-search.vue';
  import {
    pageCustomers,
    removeCustomer,
    updateCustomer
  } from '@/api/partner/customer';
  import type { Customer, CustomerParam } from '@/api/partner/customer/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'PartnerCustomer' });

  /** 0-暂停合作 1-正常 2-重点关注 */
  const CREDIT_TAG_TYPE: Record<number, 'danger' | 'success' | 'warning'> = {
    0: 'danger',
    1: 'success',
    2: 'warning'
  };

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<Customer | null>(null);
  const statusLoadingId = ref<number | null>(null);

  const columns = ref<Columns>([
    { prop: 'customerName', label: '客户名称', minWidth: 210 },
    { prop: 'customerCode', label: '客户编码', minWidth: 180 },
    { prop: 'shortName', label: '简称', minWidth: 100 },
    {
      prop: 'customerType',
      label: '客户类型',
      minWidth: 100,
      align: 'center',
      slot: 'customerType'
    },
    {
      prop: 'settlementType',
      label: '结算方式',
      minWidth: 100,
      align: 'center',
      slot: 'settlementType'
    },
    {
      prop: 'paymentDays',
      label: '账期',
      width: 90,
      align: 'center',
      formatter: (row) =>
        row.paymentDays == null ? '未设置' : `${row.paymentDays} 天`
    },
    {
      prop: 'creditStatus',
      label: '信用',
      width: 100,
      align: 'center',
      slot: 'creditStatus'
    },
    { prop: 'contactPerson', label: '联系人', minWidth: 100 },
    { prop: 'contactPhone', label: '联系电话', minWidth: 120 },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status',
      formatter: (row) => (row.status === 1 ? '正常' : '停用')
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
      width: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageCustomers({ ...where, ...orders, ...pages });
  };

  const reload = (where?: CustomerParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openEdit = (row?: Customer) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const toggleStatus = (checked: boolean, row: Customer) => {
    if (row.id == null) return;
    statusLoadingId.value = row.id;
    updateCustomer({ id: row.id, status: checked ? 1 : 0 })
      .then((msg) => {
        row.status = checked ? 1 : 0;
        EleMessage.success({ message: msg ?? '操作成功', plain: true });
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      })
      .finally(() => {
        statusLoadingId.value = null;
      });
  };

  const remove = (row: Customer) => {
    ElMessageBox.confirm(`确定要删除客户"${row.customerName}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeCustomer(row.id!)
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
