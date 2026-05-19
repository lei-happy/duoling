<template>
  <ele-page>
    <waybill-search @search="(w) => reload(w, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
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
              size="small"
              class="waybill-no-cell__copy"
              title="复制运单号"
              @click.stop="copyWaybillNo(row.waybillNo)"
            >
              <el-icon :size="14"><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </template>
        <template #customerName="{ row }">
          <div class="waybill-no-cell">
            <span
              class="waybill-no-cell__text"
              :title="row.customerName || undefined"
            >{{ row.customerName }}</span>
            <el-button
              text
              size="small"
              class="waybill-no-cell__copy"
              title="复制客户名称"
              @click.stop="copyCustomerName(row.customerName)"
            >
              <el-icon :size="14"><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </template>
        <template #origin="{ row }">
          <div class="waybill-no-cell">
            <span
              class="waybill-no-cell__text"
              :title="row.origin?.trim() || undefined"
            >{{ row.origin || '-' }}</span>
            <el-button
              text
              size="small"
              class="waybill-no-cell__copy"
              title="复制出发地"
              @click.stop="copyOrigin(row.origin)"
            >
              <el-icon :size="14"><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </template>
        <template #destination="{ row }">
          <div class="waybill-no-cell">
            <span
              class="waybill-no-cell__text"
              :title="row.destination?.trim() || undefined"
            >{{ row.destination || '-' }}</span>
            <el-button
              text
              size="small"
              class="waybill-no-cell__copy"
              title="复制目的地"
              @click.stop="copyDestination(row.destination)"
            >
              <el-icon :size="14"><DocumentCopy /></el-icon>
            </el-button>
          </div>
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
            :type="isWaybillLocked(row) ? 'warning' : 'info'"
            size="small"
          >
            {{ isWaybillLocked(row) ? '已锁' : '正常' }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <waybill-status-tag :status="row.status" />
          <el-tooltip
            v-if="row.hasActiveTaskItems"
            content="存在活跃任务挂接，编辑/删除受限"
            placement="top"
          >
            <el-tag
              type="warning"
              size="small"
              effect="plain"
              style="margin-left: 4px"
            >
              挂接中
            </el-tag>
          </el-tooltip>
        </template>
        <template #action="{ row }">
          <div
            class="waybill-actions"
            :key="`waybill-actions-${row.id}-${row.status ?? ''}-${row.isLocked ?? ''}-${row.calcStatus ?? ''}`"
          >
            <btn-items
              divider
              type="link"
              :wrap="false"
              :items="actionItems(row)"
            />
          </div>
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
      @sync-list="reloadAfterMutation"
    />
    <waybill-detail
      v-model:visible="detailVisible"
      :waybill-id="detailWaybillId"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onActivated, onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import {
    CircleCheck,
    Document,
    DocumentCopy,
    Lock,
    RefreshRight,
    Unlock
  } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import { useRouter } from 'vue-router';
  import WaybillEdit from './components/waybill-edit.vue';
  import WaybillSearch from './components/waybill-search.vue';
  import WaybillCargoesDetail from './components/waybill-cargoes-detail.vue';
  import WaybillFreightDetail from './components/waybill-freight-detail.vue';
  import WaybillStatusTag from './components/waybill-status-tag.vue';
  import WaybillDetail from './components/waybill-detail.vue';
  import { listConfigsByGroup } from '@/api/system/config';
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
  import { DeleteOutlined } from '@/components/icons';

  const router = useRouter();

  /** 提交重新计算后的提示（避免「worker」等技术用语） */
  const FREIGHT_RECALC_SUBMIT_MSG =
    '已提交运费重新计算，请稍候查看「计算明细」或列表中的计算状态。';

  defineOptions({ name: 'Waybill' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Waybill[]>([]);
  const editVisible = ref(false);
  const editData = ref<Waybill | null>(null);
  const cargoDetailVisible = ref(false);
  const cargoDetailWaybill = ref<Waybill | null>(null);
  const freightDetailVisible = ref(false);
  const freightDetailWaybillId = ref<number | null>(null);
  const detailVisible = ref(false);
  const detailWaybillId = ref<number | null>(null);

  /** 与系统设置 waybill.list_show_freight_amount 一致，默认不展示列表运费 */
  const listShowFreightAmount = ref(false);

  const syncListFreightSetting = () => {
    listConfigsByGroup('waybill')
      .then((list) => {
        const item = list?.find(
          (i) => i.configKey === 'waybill.list_show_freight_amount'
        );
        listShowFreightAmount.value = item?.configValue === 'true';
      })
      .catch(() => {});
  };

  onMounted(syncListFreightSetting);
  onActivated(syncListFreightSetting);

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

  const allWaybillColumns: Columns = [
    {
      type: 'selection',
      columnKey: 'selection',
      width: 48,
      align: 'center',
      fixed: 'left',
      selectable: (row: Waybill) => row.status === 0
    },
    { prop: 'waybillNo', label: '运单编号', minWidth: 168, slot: 'waybillNo' },
    {
      prop: 'customerName',
      label: '客户名称',
      minWidth: 210,
      slot: 'customerName'
    },
    {
      prop: 'origin',
      label: '出发地',
      minWidth: 200,
      slot: 'origin'
    },
    {
      prop: 'destination',
      label: '目的地',
      minWidth: 200,
      slot: 'destination'
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
      width: 132,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ];

  const columns = computed<Columns>(() => {
    if (listShowFreightAmount.value) return allWaybillColumns;
    return allWaybillColumns.filter((c) => c.prop !== 'freightAmount');
  });

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
    const t = tableRef.value;
    if (!t) return;
    const hasWhere = where !== undefined;
    const hasPage = page !== undefined;
    if (!hasWhere && !hasPage) {
      nextTick(() => t.reload?.());
      return;
    }
    const opt: { where?: WaybillParam; page?: number } = {};
    if (hasWhere) opt.where = where;
    if (hasPage) opt.page = page;
    t.reload?.(opt);
  };

  /** 与下拉、弹层关闭错开一帧再拉表，避免操作列状态不同步 */
  const reloadAfterMutation = () => {
    nextTick(() => {
      tableRef.value?.reload?.();
    });
  };

  const copyTextWithFeedback = async (
    raw: string | undefined,
    emptyTip: string,
    successTip: string
  ) => {
    const t = raw?.trim();
    if (!t) {
      EleMessage.warning({ message: emptyTip, plain: true });
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
      EleMessage.success({ message: successTip, plain: true });
    } catch {
      EleMessage.error({ message: '复制失败', plain: true });
    }
  };

  const copyWaybillNo = (no?: string) =>
    copyTextWithFeedback(no, '无可复制的单号', '已复制运单号');

  const copyCustomerName = (name?: string) =>
    copyTextWithFeedback(name, '无可复制的客户名称', '已复制客户名称');

  const copyOrigin = (v?: string | null) =>
    copyTextWithFeedback(v ?? undefined, '无可复制的出发地', '已复制出发地');

  const copyDestination = (v?: string | null) =>
    copyTextWithFeedback(v ?? undefined, '无可复制的目的地', '已复制目的地');

  /**
   * 是否允许编辑核心字段：
   * - 状态必须 ≤ 1（待调度）
   * - 不能存在活跃任务挂接（与后端 WaybillStateMachine.allows_delete 对齐）
   */
  const canEditWaybill = (row: Waybill) =>
    (row.status === 0 || row.status === 1) && !row.hasActiveTaskItems;

  const isWaybillLocked = (row: Waybill) => Number(row.isLocked) === 1;

  /** 状态 ≤ 1 或 = 6 已关闭，且无活跃挂接才允许删除 */
  const canDeleteWaybill = (row: Waybill) =>
    (row.status === 0 || row.status === 1 || row.status === 6) &&
    !row.hasActiveTaskItems;

  const openDetail = (row: Waybill) => {
    detailWaybillId.value = row.id ?? null;
    detailVisible.value = true;
  };

  const actionItems = (row: Waybill): ButtonItem[] => {
    const dropdown: ButtonDropdownItem[] = [];
    if (row.status === 0) {
      dropdown.push({
        title: '确认',
        icon: CircleCheck,
        onClick: () => confirmWaybill(row)
      });
    }
    dropdown.push({
      title: '详情',
      icon: Document,
      onClick: () => openDetail(row)
    });
    dropdown.push({
      title: '计算明细',
      icon: Document,
      onClick: () => openFreightDetail(row)
    });
    if (!isWaybillLocked(row)) {
      dropdown.push({
        title: '重算',
        icon: RefreshRight,
        onClick: () => recalcRow(row)
      });
      dropdown.push({
        title: '锁定',
        icon: Lock,
        onClick: () => lockRow(row)
      });
    } else {
      dropdown.push({
        title: '解锁',
        icon: Unlock,
        onClick: () => unlockRow(row)
      });
    }
    if (canDeleteWaybill(row)) {
      dropdown.push({
        title: '删除',
        icon: DeleteOutlined,
        divided: true,
        danger: true,
        onClick: () => remove(row)
      });
    }
    return [
      {
        preset: 'edit',
        title: '修改',
        type: 'link',
        props: { disabled: !canEditWaybill(row) },
        onClick: () => {
          if (canEditWaybill(row)) openEdit(row);
        }
      },
      { preset: 'more', dropdownItems: dropdown }
    ];
  };

  const goImportPage = () => {
    router.push('/operation/waybill/import');
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
        EleMessage.success({
          message: FREIGHT_RECALC_SUBMIT_MSG,
          plain: true
        });
        reloadAfterMutation();
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
        reloadAfterMutation();
      })
      .catch(() => {});
  };

  const unlockRow = (row: Waybill) => {
    if (!row.id) return;
    unlockWaybill(row.id)
      .then(() => {
        EleMessage.success({ message: '已解锁', plain: true });
        reloadAfterMutation();
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
    const pending = selections.value.filter(
      (r) => r.status === 0 && r.id != null
    );
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

  .waybill-actions {
    text-align: center;
    white-space: nowrap;
  }
</style>
