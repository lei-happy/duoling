<!--
  计划回单台账
  ============

  概念（与任务状态机彼此独立）：
  - 回单 = 计划全量签收后，把签收底单返还货主的人工动作（计划维度）。
  - 待回单 = 计划 status=5 已签收；已回单 = 计划 status=6 已回单。
  - 任务侧只读展示其下计划状态分布，但任务状态机不含"回单"。

  能力：
  - 顶部切换「待回单 / 已回单」两个池；
  - 待回单：确认回单（上传底单 + 回收时间）→ 计划 5→6；
  - 已回单：查看底单凭证 / 撤销回单 → 计划 6→5。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="WaybillReceiptLedger"
      >
        <template #toolbar>
          <div class="receipt-toolbar">
            <el-radio-group v-model="poolKey" @change="reload">
              <el-radio-button label="pending">待回单</el-radio-button>
              <el-radio-button label="done">已回单</el-radio-button>
            </el-radio-group>
            <el-input
              v-model="where.keyword"
              placeholder="计划号"
              clearable
              style="width: 220px"
              @change="reload"
            />
          </div>
        </template>

        <template #route="{ row }">
          {{ row.origin || '--' }} → {{ row.destination || '--' }}
        </template>

        <template #status="{ row }">
          <waybill-status-tag :status="row.status" />
        </template>

        <template #receiptAt="{ row }">
          {{ row.receiptAt ? formatDateTime(row.receiptAt) : '--' }}
        </template>

        <template #action="{ row }">
          <template v-if="poolKey === 'pending'">
            <el-link
              v-permission="'operation:waybill:confirm-receipt'"
              type="primary"
              :underline="false"
              @click="openConfirm(row)"
            >
              确认回单
            </el-link>
          </template>
          <template v-else>
            <el-link
              type="primary"
              :underline="false"
              @click="viewReceipts(row)"
            >
              查看凭证
            </el-link>
            <el-divider direction="vertical" />
            <el-link
              v-permission="'operation:waybill:revert-receipt'"
              type="danger"
              :underline="false"
              @click="handleRevoke(row)"
            >
              撤销回单
            </el-link>
          </template>
        </template>
      </ele-pro-table>
    </ele-card>

    <receipt-confirm-dialog
      v-model:visible="confirmVisible"
      :waybill="currentWaybill"
      @done="reload"
    />

    <el-dialog
      v-model="receiptViewVisible"
      title="回单凭证"
      width="620px"
      destroy-on-close
    >
      <div v-loading="receiptLoading">
        <el-empty v-if="!receipts.length" description="暂无回单凭证" />
        <div v-for="r in receipts" :key="r.id" class="receipt-record">
          <div class="receipt-record__meta">
            <span>回收时间：{{ formatDateTime(r.receivedAt) }}</span>
            <span v-if="r.operatorName">操作人：{{ r.operatorName }}</span>
          </div>
          <div v-if="r.remark" class="ele-text-secondary">
            备注：{{ r.remark }}
          </div>
          <div v-if="r.fileUrls?.length" class="receipt-record__files">
            <el-image
              v-for="(url, idx) in r.fileUrls"
              :key="url"
              :src="url"
              fit="cover"
              :preview-src-list="r.fileUrls"
              :initial-index="idx"
              class="receipt-record__img"
            />
          </div>
          <div v-else class="ele-text-secondary">（未上传底单图片）</div>
        </div>
      </div>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    pageWaybills,
    listWaybillReceipts,
    revokeWaybillReceipt
  } from '@/api/waybill';
  import type { Waybill, WaybillReceipt } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';
  import WaybillStatusTag from '../waybill/components/waybill-status-tag.vue';
  import ReceiptConfirmDialog from './components/receipt-confirm-dialog.vue';

  defineOptions({ name: 'BusinessReceipt' });

  /** 待回单=已签收(5)，已回单=已回单(6) */
  const POOL_STATUS: Record<string, number> = {
    pending: 5,
    done: 6
  };

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const poolKey = ref<'pending' | 'done'>('pending');
  const where = reactive({ keyword: '' });

  const columns = computed<Columns>(() => {
    // ele-admin-plus 的 Column 类型未导出 type/prop/columnKey 等运行时合法字段，
    // 故用 Record<string, unknown>[] 承载后整体 cast（同 waybill-pool-registry.ts）。
    const base: Record<string, unknown>[] = [
      { type: 'index', columnKey: 'index', width: 50, align: 'center' },
      { prop: 'waybillNo', label: '计划号', minWidth: 160 },
      { prop: 'customerName', label: '客户名称', minWidth: 140 },
      { columnKey: 'route', label: '路线', minWidth: 200, slot: 'route' },
      { prop: 'quantity', label: '台数', width: 80, align: 'center' },
      {
        prop: 'freightAmount',
        label: '运费金额',
        minWidth: 100,
        align: 'right'
      },
      {
        prop: 'status',
        label: '状态',
        width: 90,
        align: 'center',
        slot: 'status'
      }
    ];
    if (poolKey.value === 'done') {
      base.push({
        prop: 'receiptAt',
        label: '回单时间',
        width: 170,
        align: 'center',
        slot: 'receiptAt'
      });
    }
    base.push({
      columnKey: 'action',
      label: '操作',
      width: poolKey.value === 'done' ? 150 : 100,
      align: 'center',
      slot: 'action'
    });
    return base as Columns;
  });

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageWaybills({
      keyword: where.keyword || undefined,
      status: POOL_STATUS[poolKey.value],
      page,
      limit
    });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  // —— 确认回单
  const confirmVisible = ref(false);
  const currentWaybill = ref<Waybill | null>(null);

  const openConfirm = (row: Waybill) => {
    currentWaybill.value = row;
    confirmVisible.value = true;
  };

  // —— 撤销回单
  const handleRevoke = (row: Waybill) => {
    ElMessageBox.confirm(
      `确定撤销计划"${row.waybillNo}"的回单吗？撤销后计划回到「已签收」。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        try {
          await revokeWaybillReceipt(row.id!);
          loading.close();
          EleMessage.success({ message: '已撤销回单', plain: true });
          reload();
        } catch (e: unknown) {
          loading.close();
          EleMessage.error({
            message: (e as { message?: string }).message || '撤销回单失败',
            plain: true
          });
        }
      })
      .catch(() => {});
  };

  // —— 查看凭证
  const receiptViewVisible = ref(false);
  const receiptLoading = ref(false);
  const receipts = ref<WaybillReceipt[]>([]);

  const viewReceipts = async (row: Waybill) => {
    receiptViewVisible.value = true;
    receiptLoading.value = true;
    receipts.value = [];
    try {
      receipts.value = await listWaybillReceipts(row.id!);
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载回单凭证失败',
        plain: true
      });
    } finally {
      receiptLoading.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .receipt-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .receipt-record {
    padding: 10px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);

    &:last-child {
      border-bottom: none;
    }

    &__meta {
      display: flex;
      gap: 16px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    &__files {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    &__img {
      width: 96px;
      height: 96px;
      border-radius: 4px;
      border: 1px solid var(--el-border-color);
    }
  }
</style>
