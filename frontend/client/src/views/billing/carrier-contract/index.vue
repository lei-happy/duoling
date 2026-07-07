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
        cache-key="BillingCarrierContractTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增合同', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #validPeriod="{ row }">
          <span>{{
            formatContractValidPeriod(row.effectiveDate, row.expiryDate)
          }}</span>
        </template>
        <template #status="{ row }">
          <el-tag
            :type="getContractStatusDisplay(row).elType"
            size="small"
            :disable-transitions="true"
          >
            {{ getContractStatusDisplay(row).text }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <div
            class="billing-contract-actions"
            :key="`carrier-contract-actions-${row.id}-${row.status ?? ''}`"
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
    <contract-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reloadAfterMutation"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    CircleCheck,
    CircleClose,
    EditPen,
    RefreshRight
  } from '@element-plus/icons-vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { DeleteOutlined } from '@/components/icons';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import ContractEdit from './components/contract-edit.vue';
  import ContractSearch from './components/contract-search.vue';
  import {
    pageContracts,
    activateContract,
    terminateContract,
    resumeContract,
    removeContract
  } from '@/api/billing/carrier-contract';
  import type {
    CarrierContract,
    CarrierContractParam
  } from '@/api/billing/carrier-contract/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    formatContractValidPeriod,
    getContractStatusDisplay
  } from './contract-status';

  defineOptions({ name: 'BillingCarrierContract' });

  const router = useRouter();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<CarrierContract | null>(null);

  const formatRateCountSummary = (row: CarrierContract) => {
    const active = row.activeRateCount ?? 0;
    const total = row.totalRateCount ?? 0;
    return `${active}/${total}`;
  };

  const columns = ref([
    { prop: 'carrierName', label: '承运商名称', minWidth: 210, fixed: 'left' },
    { prop: 'contractNo', label: '合同编号', minWidth: 140 },
    { prop: 'contractName', label: '合同名称', minWidth: 160 },
    {
      columnKey: 'rateCountSummary',
      label: '承运价数量',
      minWidth: 110,
      align: 'center',
      formatter: (row: CarrierContract) => formatRateCountSummary(row)
    },
    {
      columnKey: 'validPeriod',
      label: '合同有效期',
      minWidth: 200,
      align: 'center',
      slot: 'validPeriod',
      formatter: (row) =>
        formatContractValidPeriod(row.effectiveDate, row.expiryDate)
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row) => getContractStatusDisplay(row).text
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
      width: 128,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ] as unknown as Columns);

  const normalizeContractStatus = (s: unknown): number | undefined => {
    if (s == null || s === '') return undefined;
    const n = Number(s);
    return Number.isFinite(n) ? n : undefined;
  };

  const actionItems = (row: CarrierContract): ButtonItem[] => {
    const st = normalizeContractStatus(row.status);
    const rowNorm: CarrierContract = { ...row, status: st ?? row.status };
    const dropdown: ButtonDropdownItem[] = [
      { title: '修改', icon: EditPen, onClick: () => openEdit(rowNorm) }
    ];
    if (st === 0) {
      dropdown.push(
        {
          title: '激活',
          icon: CircleCheck,
          onClick: () => activate(rowNorm)
        },
        {
          title: '删除',
          icon: DeleteOutlined,
          divided: true,
          danger: true,
          onClick: () => remove(rowNorm)
        }
      );
    }
    if (st === 1) {
      dropdown.push({
        title: '终止',
        icon: CircleClose,
        divided: true,
        onClick: () => terminate(rowNorm)
      });
    }
    if (st === 2) {
      dropdown.push(
        {
          title: '恢复生效',
          icon: RefreshRight,
          divided: true,
          onClick: () => resume(rowNorm)
        },
        {
          title: '删除',
          icon: DeleteOutlined,
          divided: true,
          danger: true,
          onClick: () => remove(rowNorm)
        }
      );
    }
    return [
      { preset: 'detail', onClick: () => openDetail(rowNorm) },
      {
        preset: 'more',
        dropdownItems: dropdown
      }
    ];
  };

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const res = await pageContracts({
      ...where,
      ...orders,
      ...pages
    });
    const raw = res as {
      list?: CarrierContract[];
      count?: number;
      total?: number;
    };
    const list = (raw.list ?? []).map((r) => {
      const st = normalizeContractStatus(r.status);
      return st === undefined ? r : { ...r, status: st };
    });
    return {
      list,
      count: raw.count ?? raw.total ?? 0
    };
  };

  const reload = (where?: CarrierContractParam, page?: number) => {
    const t = tableRef.value;
    if (!t) return;
    const hasWhere = where !== undefined;
    const hasPage = page !== undefined;
    if (!hasWhere && !hasPage) {
      t.reload();
      return;
    }
    const opt: { where?: CarrierContractParam; page?: number } = {};
    if (hasWhere) opt.where = where;
    if (hasPage) opt.page = page;
    t.reload(opt);
  };

  /** 操作成功后刷新：下一帧再请求，避免与下拉层关闭等 DOM 更新冲突 */
  const reloadAfterMutation = () => {
    nextTick(() => {
      tableRef.value?.reload?.();
    });
  };

  const openEdit = (row?: CarrierContract) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openDetail = (row: CarrierContract) => {
    if (row.id == null) return;
    router.push({
      name: 'BillingCarrierContractDetail',
      params: { id: String(row.id) }
    });
  };

  const activate = (row: CarrierContract) => {
    ElMessageBox.confirm(
      `确定要激活合同"${row.contractName}"吗？激活后将参与承运运费匹配。`,
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
            reloadAfterMutation();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const terminate = (row: CarrierContract) => {
    ElMessageBox.confirm(
      `确定要终止合同「${row.contractName}」吗？终止后仍可在「更多」中恢复生效。`,
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
            reloadAfterMutation();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const resume = (row: CarrierContract) => {
    ElMessageBox.confirm(
      `确定将合同「${row.contractName}」恢复为生效吗？恢复后将重新参与承运运费匹配（仍受合同有效期约束）。`,
      '系统提示',
      { type: 'info', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        resumeContract(row.id!)
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

  const remove = (row: CarrierContract) => {
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
  .billing-contract-actions {
    text-align: center;
    white-space: nowrap;
  }
</style>
