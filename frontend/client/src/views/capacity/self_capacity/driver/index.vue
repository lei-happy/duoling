<template>
  <ele-page>
    <driver-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="ResourceDriverTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增驾驶员', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #driverType="{ row }">
          <el-tag
            v-if="row.driverType === 1"
            size="small"
            :disable-transitions="true"
          >
            自有
          </el-tag>
          <el-tag
            v-else-if="row.driverType === 2"
            type="warning"
            size="small"
            :disable-transitions="true"
          >
            外协
          </el-tag>
          <el-tag
            v-else-if="row.driverType === 3"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            临时
          </el-tag>
          <span v-else>—</span>
        </template>
        <template #operationStatus="{ row }">
          <el-tag
            v-if="row.operationStatus === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            可接单
          </el-tag>
          <el-tag
            v-else-if="row.operationStatus === 2"
            type="warning"
            size="small"
            :disable-transitions="true"
          >
            忙碌
          </el-tag>
          <el-tag
            v-else-if="row.operationStatus === 3"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            休假
          </el-tag>
          <el-tag
            v-else-if="row.operationStatus === 4"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
            停运
          </el-tag>
          <span v-else>—</span>
        </template>
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            在职
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            冻结
          </el-tag>
          <el-tag
            v-else-if="row.status === 2"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
            离职
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
    <driver-edit
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
  import { DeleteOutlined } from '@/components/icons';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import DriverEdit from './components/driver-edit.vue';
  import DriverSearch from './components/driver-search.vue';
  import {
    pageDrivers,
    removeDriver,
    updateDriverStatus
  } from '@/api/resource/driver';
  import type { Driver, DriverParam } from '@/api/resource/driver/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'ResourceDriver' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<Driver | null>(null);

  const columns = ref<Columns>([
    { prop: 'driverCode', label: '司机编号', minWidth: 120 },
    { prop: 'name', label: '姓名', minWidth: 90 },
    { prop: 'phone', label: '手机号', minWidth: 120 },
    { prop: 'licenseType', label: '驾照类型', minWidth: 80, align: 'center' },
    { prop: 'departmentName', label: '所属车队', minWidth: 100 },
    {
      prop: 'driverType',
      label: '司机类型',
      width: 90,
      align: 'center',
      slot: 'driverType'
    },
    {
      prop: 'operationStatus',
      label: '运营状态',
      width: 90,
      align: 'center',
      slot: 'operationStatus'
    },
    {
      prop: 'status',
      label: '人事状态',
      width: 90,
      align: 'center',
      slot: 'status'
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

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const res = await pageDrivers({ ...where, ...orders, ...pages });
    const raw = res as { list?: Driver[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = (where?: DriverParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openEdit = (row?: Driver) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const actionItems = (row: Driver) => [
    { preset: 'edit', onClick: () => openEdit(row) },
    {
      preset: 'more',
      dropdownItems: [
        {
          title: '设为在职',
          disabled: row.status === 1,
          onClick: () => handleStatusCommand('status-1', row)
        },
        {
          title: '设为冻结',
          disabled: row.status === 0,
          onClick: () => handleStatusCommand('status-0', row)
        },
        {
          title: '设为离职',
          disabled: row.status === 2,
          onClick: () => handleStatusCommand('status-2', row)
        },
        {
          title: '删除',
          divided: true,
          danger: true,
          icon: DeleteOutlined,
          onClick: () => handleStatusCommand('delete', row)
        }
      ]
    }
  ];

  const handleStatusCommand = (command: string, row: Driver) => {
    if (command === 'delete') {
      remove(row);
      return;
    }
    const statusVal = Number(command.split('-')[1]);
    const statusMap: Record<number, string> = {
      0: '冻结',
      1: '在职',
      2: '离职'
    };
    ElMessageBox.confirm(
      `确定将"${row.name}"的人事状态修改为"${statusMap[statusVal]}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        try {
          await updateDriverStatus(row.id!, statusVal);
          EleMessage.success({ message: '状态修改成功', plain: true });
          reload();
        } catch (e: any) {
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => {});
  };

  const remove = (row: Driver) => {
    ElMessageBox.confirm(`确定要删除驾驶员"${row.name}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeDriver(row.id!)
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
