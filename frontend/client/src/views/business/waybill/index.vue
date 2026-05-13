<template>
  <ele-page>
    <waybill-search @search="(w) => reload(w, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        v-model:selections="selections"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="WaybillTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增运单', onClick: () => openEdit() }
            ]"
          />
          <el-button
            type="primary"
            plain
            class="ele-btn-icon"
            :disabled="!selections.some((r) => r.status === 0)"
            @click="batchConfirm"
          >
            批量确认
          </el-button>
          <el-button
            type="success"
            plain
            class="ele-btn-icon"
            @click="goImportPage"
          >
            批量导入
          </el-button>
        </template>
        <template #waybillNo="{ row }">
          <div class="waybill-no-cell">
            <span class="waybill-no-cell__text" :title="row.waybillNo">{{
              row.waybillNo
            }}</span>
            <el-button
              text
              class="waybill-no-cell__copy"
              title="复制运单号"
              @click.stop="copyWaybillNo(row.waybillNo)"
            >
              <el-icon :size="14"><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </template>
        <template #route="{ row }">
          {{ row.origin }} → {{ row.destination }}
        </template>
        <template #vehicleInfo="{ row }">
          <span v-if="row.cargoSummary">{{ row.cargoSummary }}</span>
          <span v-else-if="row.vehicleBrand || row.vehicleModel">
            {{ row.vehicleBrand
            }}{{ row.vehicleModel ? '/' + row.vehicleModel : '' }}
          </span>
          <span v-else>-</span>
        </template>
        <template #quantity="{ row }">
          <el-tag
            type="primary"
            effect="plain"
            size="small"
            class="waybill-qty-tag"
            @click.stop="openCargoDetail(row)"
          >
            {{ row.quantity ?? 0 }}
          </el-tag>
        </template>
        <template #calcStatus="{ row }">
          <el-tag :type="calcStatusType(row.calcStatus)" size="small">
            {{ calcStatusText(row.calcStatus) }}
          </el-tag>
        </template>
        <template #isLocked="{ row }">
          <el-tag
            :type="row.isLocked === 1 ? 'warning' : 'info'"
            size="small"
          >
            {{ row.isLocked === 1 ? '已锁' : '正常' }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 0" type="info" size="small">
            待确认
          </el-tag>
          <el-tag v-else-if="row.status === 1" type="primary" size="small">
            已确认
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            已调度
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="warning" size="small">
            运输中
          </el-tag>
          <el-tag v-else-if="row.status === 4" type="success" size="small">
            已送达
          </el-tag>
          <el-tag v-else-if="row.status === 5" type="success" size="small">
            已完成
          </el-tag>
          <el-tag v-else-if="row.status === 6" type="danger" size="small">
            已取消
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
    <waybill-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
    <waybill-cargoes-detail
      v-model:visible="cargoDetailVisible"
      :waybill="cargoDetailWaybill"
    />
    <waybill-freight-detail
      v-model:visible="freightDetailVisible"
      :waybill-id="freightDetailWaybillId"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { DocumentCopy } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { useRouter } from 'vue-router';
  import WaybillEdit from './components/waybill-edit.vue';
  import WaybillSearch from './components/waybill-search.vue';
  import WaybillCargoesDetail from './components/waybill-cargoes-detail.vue';
  import WaybillFreightDetail from './components/waybill-freight-detail.vue';
  import {
    pageWaybills,
    removeWaybill,
    updateWaybillStatus,
    recalculateWaybill,
    lockWaybill,
    unlockWaybill
  } from '@/api/waybill';
  import type { Waybill, WaybillParam } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';

  const router = useRouter();

  defineOptions({ name: 'Waybill' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Waybill[]>([]);
  const editVisible = ref(false);
  const editData = ref<Waybill | null>(null);
  const cargoDetailVisible = ref(false);
  const cargoDetailWaybill = ref<Waybill | null>(null);
  const freightDetailVisible = ref(false);
  const freightDetailWaybillId = ref<number | null>(null);

  const calcStatusType = (s?: string) => {
    if (s === 'calculated') return 'success';
    if (s === 'pending') return 'info';
    if (s === 'calculating') return 'primary';
    if (s === 'exception') return 'danger';
    if (s === 'locked') return 'warning';
    return 'info';
  };
  const calcStatusText = (s?: string) => {
    const m: Record<string, string> = {
      pending: '待计算',
      calculating: '计算中',
      calculated: '已计算',
      exception: '异常',
      locked: '已锁定'
    };
    return s ? m[s] || s : '--';
  };

  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 48,
      align: 'center',
      fixed: 'left',
      selectable: (row: Waybill) => row.status === 0
    },
    { prop: 'waybillNo', label: '运单编号', minWidth: 168, slot: 'waybillNo' },
    { prop: 'customerName', label: '客户名称', minWidth: 120 },
    {
      columnKey: 'route',
      label: '出发地→目的地',
      minWidth: 180,
      slot: 'route'
    },
    {
      columnKey: 'vehicleInfo',
      label: '品牌/车型',
      minWidth: 120,
      slot: 'vehicleInfo'
    },
    {
      columnKey: 'quantity',
      prop: 'quantity',
      label: '台数',
      width: 88,
      align: 'center',
      slot: 'quantity'
    },
    {
      prop: 'freightAmount',
      label: '运费金额',
      minWidth: 100,
      align: 'right'
    },
    {
      prop: 'calcStatus',
      label: '计算状态',
      width: 100,
      align: 'center',
      slot: 'calcStatus'
    },
    {
      prop: 'isLocked',
      label: '锁定',
      width: 64,
      align: 'center',
      slot: 'isLocked'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 200,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageWaybills({
      ...(where as WaybillParam | undefined),
      ...pages
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = (where?: WaybillParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const copyWaybillNo = async (no?: string) => {
    const t = no?.trim();
    if (!t) {
      EleMessage.warning({ message: '无可复制的单号', plain: true });
      return;
    }
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(t);
      } else {
        const ta = document.createElement('textarea');
        ta.value = t;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      EleMessage.success({ message: '已复制运单号', plain: true });
    } catch {
      EleMessage.error({ message: '复制失败', plain: true });
    }
  };

  const actionItems = (row: Waybill) => {
    const items: Array<{ preset?: string; title?: string; onClick: () => void }> = [];
    if (row.status === 0) {
      items.push({ title: '确认', onClick: () => confirmWaybill(row) });
    }
    if (row.status === 0 || row.status === 1) {
      items.push({ preset: 'edit', onClick: () => openEdit(row) });
    }
    items.push({ title: '计算明细', onClick: () => openFreightDetail(row) });
    if ((row as any).isLocked !== 1) {
      items.push({ title: '重算', onClick: () => recalcRow(row) });
      items.push({ title: '锁定', onClick: () => lockRow(row) });
    } else {
      items.push({ title: '解锁', onClick: () => unlockRow(row) });
    }
    if (row.status === 0 || row.status === 1 || row.status === 6) {
      items.push({ preset: 'del', onClick: () => remove(row) });
    }
    return items;
  };

  const goImportPage = () => {
    router.push('/business/waybill/import');
  };

  const openFreightDetail = (row: Waybill) => {
    if (!row.id) return;
    freightDetailWaybillId.value = row.id;
    freightDetailVisible.value = true;
  };

  const recalcRow = (row: Waybill) => {
    if (!row.id) return;
    const loading = EleMessage.loading({ message: '请求中..', plain: true });
    recalculateWaybill(row.id)
      .then(() => {
        loading.close();
        EleMessage.success({ message: '已入队，等待 worker 处理', plain: true });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const lockRow = (row: Waybill) => {
    if (!row.id) return;
    ElMessageBox.confirm(
      '锁定后该运单将不再被自动重算，确定继续？',
      '锁定运单',
      { type: 'warning' }
    )
      .then(() => lockWaybill(row.id!))
      .then(() => {
        EleMessage.success({ message: '已锁定', plain: true });
        reload();
      })
      .catch(() => {});
  };

  const unlockRow = (row: Waybill) => {
    if (!row.id) return;
    unlockWaybill(row.id)
      .then(() => {
        EleMessage.success({ message: '已解锁', plain: true });
        reload();
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const confirmWaybill = (row: Waybill) => {
    ElMessageBox.confirm(
      `确认运单「${row.waybillNo}」？确认后将变为「已确认」状态。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        updateWaybillStatus(row.id!, 1)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e: Error) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const batchConfirm = () => {
    const pending = selections.value.filter((r) => r.status === 0 && r.id != null);
    if (!pending.length) {
      EleMessage.warning({ message: '请勾选待确认的运单', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `将确认 ${pending.length} 条运单，状态将变为「已确认」，是否继续？`,
      '批量确认',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        Promise.allSettled(pending.map((r) => updateWaybillStatus(r.id!, 1)))
          .then((results) => {
            loading.close();
            const ok = results.filter((r) => r.status === 'fulfilled').length;
            const fail = results.length - ok;
            if (fail === 0) {
              EleMessage.success({
                message: `已成功确认 ${ok} 条运单`,
                plain: true
              });
            } else {
              EleMessage.warning({
                message: `成功 ${ok} 条，失败 ${fail} 条，请刷新后核对`,
                plain: true
              });
            }
            selections.value = [];
            reload();
          })
          .catch((e: Error) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const openEdit = (row?: Waybill) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openCargoDetail = (row: Waybill) => {
    cargoDetailWaybill.value = row;
    cargoDetailVisible.value = true;
  };

  const remove = (row: Waybill) => {
    ElMessageBox.confirm(`确定要删除运单"${row.waybillNo}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeWaybill(row.id!)
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
  .waybill-no-cell {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    max-width: 100%;
    vertical-align: middle;
  }

  .waybill-no-cell__text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .waybill-no-cell__copy {
    flex-shrink: 0;
    margin-left: 0;
    padding: 2px 4px;
    min-height: auto;
    color: var(--el-text-color-secondary);
  }

  .waybill-no-cell__copy:hover {
    color: var(--el-color-primary);
  }

  .waybill-qty-tag {
    cursor: pointer;
    user-select: none;
  }

  .waybill-qty-tag:hover {
    opacity: 0.88;
  }
</style>
