<!--
  计划工作台 - 按 pool 配置的列表壳层
  ====================================

  Props:
    - poolKey: 状态池 key（与 waybill-pool-registry 对齐，决定列、排序、status 筛选）
    - searchWhere: 父级统一筛选条件（切换阶段卡时保留）
    - reloadToken: 父组件通过修改此值触发强制刷新
    - listShowFreightAmount: 是否展示「运费金额」列（由 index.vue 读 system_config 传入）

  Emits:
    - syncStats: 列表加载完成 / 行级动作成功后，请父级刷新 KPI 卡片
    - openEdit(row?)  / openDetail(row) / openCargoDetail(row) / openFreightDetail(row)
    - openImport: 顶部"批量导入"按钮（路由跳转由父级决定）

  设计要点：
    - 列、筛选、行内动作全部由 pool 注册表驱动；新增/调整某状态的差异仅改 registry
    - 所有 cell slot（waybillNo / customerName / origin / destination / vehicleInfo /
      quantity / allocatedQuantity / calcStatus / isLocked / status / createdAt / action）
      集中在本文件，与 registry.buildWaybillTableColumns 的 slot 名一一对应
    - 行内可变操作（确认 / 重算 / 锁定 / 解锁 / 删除）由本组件直接调用 API，
      成功后 emit syncStats 由父级刷新统计与列表
-->
<template>
  <div class="waybill-pool">
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
        :default-sort="pool.defaultSort"
        :cache-key="`WaybillPool-${pool.key}`"
        @done="onTableDone"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新增计划',
                onClick: () => emit('openEdit')
              }
            ]"
          />
          <el-button
            v-if="pool.allowBatchConfirm"
            type="primary"
            plain
            class="ele-btn-icon"
            :disabled="selections.length === 0"
            @click="onBatchConfirm"
          >
            批量确认 ({{ selections.length }})
          </el-button>
          <el-button
            type="success"
            plain
            class="ele-btn-icon"
            @click="emit('openImport')"
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
              title="复制计划号"
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
              >{{ row.customerName }}</span
            >
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
              >{{ row.origin || '-' }}</span
            >
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
              >{{ row.destination || '-' }}</span
            >
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
            @click.stop="emit('openCargoDetail', row)"
          >
            {{ row.quantity ?? 0 }}
          </el-tag>
        </template>

        <template #allocatedQuantity="{ row }">
          <span class="waybill-alloc">
            <span class="waybill-alloc__num">{{
              row.allocatedQuantity ?? 0
            }}</span>
            <span class="waybill-alloc__sep">/</span>
            <span class="waybill-alloc__total">{{ row.quantity ?? 0 }}</span>
          </span>
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

        <template #createdAt="{ row }">
          {{ formatDateTime(row.createdAt) || '--' }}
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
  </div>
</template>

<script lang="ts" setup>
  import { computed, nextTick, ref, watch } from 'vue';
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
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import WaybillStatusTag from './waybill-status-tag.vue';
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
  import {
    WAYBILL_POOLS,
    WAYBILL_STATUS_TO_POOL_KEY,
    buildWaybillTableColumns,
    getWaybillPool
  } from '../waybill-pool-registry';
  import type {
    WaybillPool,
    WaybillRowActionKey
  } from '../waybill-pool-registry';

  /** 提交重新计算后的提示（避免「worker」等技术用语） */
  const FREIGHT_RECALC_SUBMIT_MSG =
    '已提交运费重新计算，请稍候查看「计算明细」或列表中的计算状态。';

  const props = defineProps<{
    poolKey: string;
    /** 父级统一筛选条件（切换阶段卡时不丢失） */
    searchWhere?: WaybillParam;
    reloadToken?: number;
    /** 来自 system_config waybill.list_show_freight_amount，控制是否展示运费列 */
    listShowFreightAmount?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'syncStats'): void;
    (e: 'autoSwitchPool', poolKey: string): void;
    (e: 'openEdit', row?: Waybill): void;
    (e: 'openDetail', row: Waybill): void;
    (e: 'openCargoDetail', row: Waybill): void;
    (e: 'openFreightDetail', row: Waybill): void;
    (e: 'openImport'): void;
  }>();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Waybill[]>([]);

  const pool = computed<WaybillPool>(
    () => getWaybillPool(props.poolKey) ?? WAYBILL_POOLS[0]!
  );

  /** 按 list_show_freight_amount 动态隐藏 freightAmount 列 */
  const columns = computed<Columns>(() => {
    const all = buildWaybillTableColumns(pool.value);
    if (props.listShowFreightAmount) return all;
    return all.filter(
      (c) => (c as { prop?: string }).prop !== 'freightAmount'
    );
  });

  const buildQuery = (pages?: Record<string, unknown>): WaybillParam => {
    const search = props.searchWhere ?? {};
    const keyword = search.keyword?.trim();
    // 计划号唯一：有 keyword 时仅按单号查，不受阶段/日期等其它条件限制
    if (keyword) {
      return { keyword, ...(pages as WaybillParam | undefined) };
    }
    return {
      ...search,
      status: pool.value.status,
      ...(pages as WaybillParam | undefined)
    };
  };

  const datasource: DatasourceFunction = ({ pages }) => {
    const merged = buildQuery(pages);
    return pageWaybills(merged).then((res) => {
      const list = res?.list ?? [];
      const keyword = merged.keyword?.trim();
      if (keyword && list.length > 0) {
        const targetPool = WAYBILL_STATUS_TO_POOL_KEY[list[0]!.status ?? -1];
        if (targetPool && targetPool !== props.poolKey) {
          emit('autoSwitchPool', targetPool);
        }
      }
      return {
        list,
        count: res?.count ?? 0
      };
    });
  };

  /** 与下拉、弹层关闭错开一帧再拉表，避免操作列状态不同步 */
  const reloadAfterMutation = () => {
    nextTick(() => {
      tableRef.value?.reload?.();
      emit('syncStats');
    });
  };

  const doReload = (page?: number) => {
    const t = tableRef.value;
    if (!t) return;
    if (page !== undefined) {
      t.reload?.({ page });
      return;
    }
    nextTick(() => t.reload?.());
  };

  const onTableDone = () => {
    emit('syncStats');
  };

  watch(
    () => props.poolKey,
    () => {
      selections.value = [];
      doReload(1);
    }
  );

  watch(
    () => props.searchWhere,
    () => {
      selections.value = [];
      doReload(1);
    },
    { deep: true }
  );

  watch(
    () => props.reloadToken,
    () => doReload()
  );

  // ========================================================
  // 单元格 / 行内辅助
  // ========================================================

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

  const isWaybillLocked = (row: Waybill) => Number(row.isLocked) === 1;

  /**
   * 是否允许编辑核心字段：
   * - 状态必须 ≤ 1（待调度）
   * - 不能存在活跃任务挂接（与后端 WaybillStateMachine.allows_delete 对齐）
   */
  const canEditWaybill = (row: Waybill) =>
    (row.status === 0 || row.status === 1) && !row.hasActiveTaskItems;

  /** 状态 ≤ 1 或 = 6 已关闭，且无活跃挂接才允许删除 */
  const canDeleteWaybill = (row: Waybill) =>
    (row.status === 0 || row.status === 1 || row.status === 6) &&
    !row.hasActiveTaskItems;

  // ========================================================
  // 复制按钮
  // ========================================================

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
    copyTextWithFeedback(no, '无可复制的单号', '已复制计划号');
  const copyCustomerName = (name?: string) =>
    copyTextWithFeedback(name, '无可复制的客户名称', '已复制客户名称');
  const copyOrigin = (v?: string | null) =>
    copyTextWithFeedback(v ?? undefined, '无可复制的出发地', '已复制出发地');
  const copyDestination = (v?: string | null) =>
    copyTextWithFeedback(v ?? undefined, '无可复制的目的地', '已复制目的地');

  // ========================================================
  // 行内动作
  // ========================================================

  /**
   * 注册表 key → 渲染规则（visible/disabled/label/icon/onClick）
   *
   * 集中维护可避免 actionItems 内逻辑散落。各动作之"是否显示"严格依据当前行状态判断，
   * 即便 pool 的 rowActions 数组里包含某 key，行不满足条件时也不会渲染。
   */
  const buildAction = (
    key: WaybillRowActionKey,
    row: Waybill
  ): ButtonDropdownItem | null => {
    switch (key) {
      case 'confirm':
        // 草稿 → 待调度（仅遗留 status=0 数据时显示）
        if (row.status !== 0) return null;
        return {
          title: '确认',
          icon: CircleCheck,
          onClick: () => confirmWaybill(row)
        };
      case 'detail':
        return {
          title: '详情',
          icon: Document,
          onClick: () => emit('openDetail', row)
        };
      case 'freight-detail':
        return {
          title: '计算明细',
          icon: Document,
          onClick: () => emit('openFreightDetail', row)
        };
      case 'recalc':
        if (isWaybillLocked(row)) return null;
        return {
          title: '重算',
          icon: RefreshRight,
          onClick: () => recalcRow(row)
        };
      case 'lock':
        if (isWaybillLocked(row)) return null;
        return {
          title: '锁定',
          icon: Lock,
          onClick: () => lockRow(row)
        };
      case 'unlock':
        if (!isWaybillLocked(row)) return null;
        return {
          title: '解锁',
          icon: Unlock,
          onClick: () => unlockRow(row)
        };
      case 'remove':
        if (!canDeleteWaybill(row)) return null;
        return {
          title: '删除',
          icon: DeleteOutlined,
          divided: true,
          danger: true,
          onClick: () => remove(row)
        };
      default:
        return null;
    }
  };

  const actionItems = (row: Waybill): ButtonItem[] => {
    const items: ButtonItem[] = [];
    const dropdown: ButtonDropdownItem[] = [];

    /** 修改按钮：仅 pool 包含 'edit' 时展示为顶层主按钮 */
    if (pool.value.rowActions.includes('edit')) {
      items.push({
        preset: 'edit',
        title: '修改',
        type: 'link',
        props: { disabled: !canEditWaybill(row) },
        onClick: () => {
          if (canEditWaybill(row)) emit('openEdit', row);
        }
      });
    }

    for (const k of pool.value.rowActions) {
      if (k === 'edit') continue;
      const it = buildAction(k, row);
      if (it) dropdown.push(it);
    }

    if (dropdown.length === 1) {
      // 仅一个下拉项时直接平铺为顶层链接，避免点"更多"再点的二次操作
      const only = dropdown[0]!;
      items.push({
        title: only.title,
        type: 'link',
        icon: only.icon,
        onClick: only.onClick
      });
    } else if (dropdown.length > 1) {
      items.push({ preset: 'more', dropdownItems: dropdown });
    }

    return items;
  };

  // ========================================================
  // 行级状态操作（直接调用 API，成功后通知父级刷新）
  // ========================================================

  /**
   * 「确认」语义说明：
   * - 历史：status=0 草稿 → status=1 待调度（原 confirmWaybill 行为）
   * - 新设计：状态机已废弃 0 草稿，所有计划创建即 status=1，"确认"按钮仅在
   *   存在遗留 0 数据时显示，对仍然存在的 0 数据沿用 0→1 推进。
   */
  const confirmWaybill = (row: Waybill) => {
    ElMessageBox.confirm(
      `确认计划「${row.waybillNo}」？确认后将变为「待调度」状态。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在确认计划，请稍候…',
          plain: true
        });
        updateWaybillStatus(row.id!, 1)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reloadAfterMutation();
          })
          .catch((e: Error) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const onBatchConfirm = () => {
    const pending = selections.value.filter(
      (r) => r.status === 0 && r.id != null
    );
    if (!pending.length) {
      EleMessage.warning({
        message: '当前所选计划中无待确认（status=0）记录',
        plain: true
      });
      return;
    }
    ElMessageBox.confirm(
      `将确认 ${pending.length} 条计划，状态将变为「待调度」，是否继续？`,
      '批量确认',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在确认计划，请稍候…',
          plain: true
        });
        Promise.allSettled(pending.map((r) => updateWaybillStatus(r.id!, 1)))
          .then((results) => {
            loading.close();
            const ok = results.filter((r) => r.status === 'fulfilled').length;
            const fail = results.length - ok;
            if (fail === 0) {
              EleMessage.success({
                message: `已成功确认 ${ok} 条计划`,
                plain: true
              });
            } else {
              EleMessage.warning({
                message: `成功 ${ok} 条，失败 ${fail} 条，请刷新后核对`,
                plain: true
              });
            }
            selections.value = [];
            reloadAfterMutation();
          })
          .catch((e: Error) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
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
      '锁定后该计划将不再被自动重算，确定继续？',
      '锁定计划',
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

  const remove = (row: Waybill) => {
    ElMessageBox.confirm(`确定要删除计划"${row.waybillNo}"吗?`, '系统提示', {
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
            reloadAfterMutation();
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

  .waybill-alloc {
    display: inline-flex;
    align-items: baseline;
    gap: 2px;
    font-variant-numeric: tabular-nums;
  }

  .waybill-alloc__num {
    font-weight: 600;
    color: var(--el-color-primary);
  }

  .waybill-alloc__sep {
    color: var(--el-text-color-placeholder);
  }

  .waybill-alloc__total {
    color: var(--el-text-color-regular);
  }
</style>
