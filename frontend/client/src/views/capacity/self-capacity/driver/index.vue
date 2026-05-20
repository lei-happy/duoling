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
          <dict-data
            type="text"
            :code="dictCodeSelfCapacityDriverType"
            :model-value="row.driverType"
          />
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
            v-if="normalizeHrStatus(row.status) === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            在职
          </el-tag>
          <el-tag
            v-else-if="normalizeHrStatus(row.status) === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            冻结
          </el-tag>
          <el-tag
            v-else-if="normalizeHrStatus(row.status) === 2"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
            离职
          </el-tag>
          <span v-else>—</span>
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

    <el-dialog
      v-model="hrStatusVisible"
      title="调整人事状态"
      width="440px"
      append-to-body
      align-center
      :close-on-click-modal="false"
      @closed="onHrDialogClosed"
    >
      <div v-loading="hrStatusLoading" class="driver-hr-dialog">
        <template v-if="hrStatusRow">
          <p class="driver-hr-dialog__line">
            当前状态：<strong>{{ hrStatusLabel(hrStatusNormalized) }}</strong>
          </p>
          <p class="driver-hr-dialog__line">目标状态</p>
          <el-select
            v-model="hrTargetStatus"
            placeholder="请选择"
            class="driver-hr-dialog__select"
          >
            <el-option
              v-for="opt in hrTargetOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </template>
      </div>
      <template #footer>
        <el-button @click="hrStatusVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmHrStatus">确定</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
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
  import DictData from '@/components/DictData/index.vue';
  import {
    pageDrivers,
    getDriver,
    removeDriver,
    updateDriverStatus
  } from '@/api/capacity/self-capacity/driver';
  import type {
    Driver,
    DriverParam
  } from '@/api/capacity/self-capacity/driver/model';
  import { formatDateTime } from '@/utils/date-util';
  import { DICT_CODE_SELF_CAPACITY_DRIVER_TYPE } from '@/constants/dict-codes';

  defineOptions({ name: 'ResourceDriver' });

  const dictCodeSelfCapacityDriverType = DICT_CODE_SELF_CAPACITY_DRIVER_TYPE;

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<Driver | null>(null);

  const HR_STATUS_LABEL: Record<number, string> = {
    0: '冻结',
    1: '在职',
    2: '离职'
  };

  /** 人事状态统一为 0/1/2，避免列表行里 string 或与表格缓存不一致 */
  const normalizeHrStatus = (value: unknown): number | undefined => {
    if (value === null || value === undefined || value === '') return undefined;
    const n = Number(value);
    if (!Number.isFinite(n)) return undefined;
    if (n === 0 || n === 1 || n === 2) return n;
    return undefined;
  };

  const hrStatusVisible = ref(false);
  const hrStatusRow = ref<Driver | null>(null);
  const hrStatusLoading = ref(false);
  const hrTargetStatus = ref<number | undefined>(undefined);

  const hrStatusNormalized = computed(() =>
    normalizeHrStatus(hrStatusRow.value?.status)
  );

  const hrStatusLabel = (s: number | undefined) =>
    s == null ? '' : (HR_STATUS_LABEL[s] ?? String(s));

  const hrTargetOptions = computed(() => {
    const s = hrStatusNormalized.value;
    if (s === undefined) return [];
    if (s === 1) {
      return [
        { value: 0, label: '冻结' },
        { value: 2, label: '离职' }
      ];
    }
    if (s === 0) {
      return [
        { value: 1, label: '取消冻结，恢复在职' },
        { value: 2, label: '离职' }
      ];
    }
    if (s === 2) {
      return [{ value: 1, label: '恢复在职' }];
    }
    return [];
  });

  const columns = ref<Columns>([
    { prop: 'driverCode', label: '驾驶员编号', minWidth: 120 },
    { prop: 'name', label: '姓名', minWidth: 90 },
    { prop: 'phone', label: '手机号', minWidth: 120 },
    { prop: 'licenseType', label: '驾照类型', minWidth: 80, align: 'center' },
    { prop: 'departmentName', label: '所属车队', minWidth: 100 },
    {
      prop: 'driverType',
      label: '驾驶员类型',
      width: 100,
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

  const normalizeSortOrders = (
    orders: Record<string, string | undefined> | undefined
  ) => {
    if (!orders?.sort && !orders?.order) return {};
    const sort = orders.sort;
    let order = orders.order;
    if (typeof order === 'string') {
      const lo = order.toLowerCase();
      if (lo === 'descending') order = 'desc';
      else if (lo === 'ascending') order = 'asc';
    }
    const out: Record<string, string> = {};
    if (sort) out.sort = sort;
    if (order) out.order = order;
    return out;
  };

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const res = await pageDrivers({
      ...where,
      ...normalizeSortOrders(orders as Record<string, string | undefined>),
      ...pages
    });
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

  const openHrStatusDialog = async (row: Driver) => {
    if (!row?.id) return;
    hrStatusLoading.value = true;
    hrStatusRow.value = null;
    hrTargetStatus.value = undefined;
    hrStatusVisible.value = true;
    try {
      const fresh = await getDriver(row.id);
      hrStatusRow.value = fresh;
      const s = normalizeHrStatus(fresh.status);
      const opts =
        s === 1
          ? [
              { value: 0, label: '冻结' },
              { value: 2, label: '离职' }
            ]
          : s === 0
            ? [
                { value: 1, label: '取消冻结，恢复在职' },
                { value: 2, label: '离职' }
              ]
            : s === 2
              ? [{ value: 1, label: '恢复在职' }]
              : [];
      hrTargetStatus.value = opts[0]?.value;
    } catch (e: any) {
      hrStatusVisible.value = false;
      EleMessage.error({
        message: e?.message ?? '加载驾驶员信息失败',
        plain: true
      });
    } finally {
      hrStatusLoading.value = false;
    }
  };

  const onHrDialogClosed = () => {
    hrStatusRow.value = null;
    hrTargetStatus.value = undefined;
    hrStatusLoading.value = false;
  };

  const confirmHrStatus = async () => {
    const row = hrStatusRow.value;
    const target = hrTargetStatus.value;
    if (!row?.id || target === undefined) {
      EleMessage.warning({ message: '请选择目标状态', plain: true });
      return;
    }
    const current = normalizeHrStatus(row.status);
    if (current === undefined) {
      EleMessage.warning({ message: '无法识别当前人事状态', plain: true });
      return;
    }
    if (target === current) {
      EleMessage.warning({ message: '目标状态与当前相同', plain: true });
      return;
    }
    const fromL = hrStatusLabel(current);
    const toL = hrStatusLabel(target);
    try {
      await ElMessageBox.confirm(
        `确定将「${row.name}」的人事状态从「${fromL}」调整为「${toL}」吗？`,
        '系统提示',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    try {
      await updateDriverStatus(row.id!, target);
      EleMessage.success({ message: '状态修改成功', plain: true });
      hrStatusVisible.value = false;
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const actionItems = (row: Driver) => [
    { preset: 'edit', onClick: () => openEdit(row) },
    {
      preset: 'more',
      dropdownItems: [
        {
          title: '调整人事状态',
          onClick: () => openHrStatusDialog(row)
        },
        {
          title: '删除',
          divided: true,
          danger: true,
          icon: DeleteOutlined,
          onClick: () => remove(row)
        }
      ]
    }
  ];

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

<style scoped>
  .driver-hr-dialog {
    min-height: 120px;
  }
  .driver-hr-dialog__line {
    margin: 0 0 8px;
    font-size: 14px;
  }
  .driver-hr-dialog__select {
    width: 100%;
  }
</style>
