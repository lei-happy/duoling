<template>
  <ele-page class="fleet-parts-page">
    <ele-card v-if="!featureEnabled" class="fleet-parts-page__upgrade">
      <el-result
        icon="warning"
        title="备件库存为专业版功能"
        sub-title="开通后可管理备件档案、手工入库，并在维保完工时自动扣减库存。"
      >
        <template #extra>
          <el-button type="primary" @click="goHome">返回工作台</el-button>
        </template>
      </el-result>
    </ele-card>

    <template v-else>
      <ele-card :body-style="{ paddingBottom: '8px' }">
        <el-tabs v-model="activeTab" @tab-change="onTabChange">
          <el-tab-pane label="备件档案" name="parts" />
          <el-tab-pane label="入库" name="inbound" />
          <el-tab-pane label="流水" name="txns" />
        </el-tabs>
      </ele-card>

      <!-- 备件档案 -->
      <ele-card v-if="activeTab === 'parts'" :body-style="{ paddingTop: '8px' }">
        <el-form :inline="true" @submit.prevent>
          <el-form-item label="关键字">
            <el-input
              v-model="partWhere.keyword"
              clearable
              placeholder="编码/名称"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="partWhere.status"
              clearable
              placeholder="全部"
              style="width: 120px"
            >
              <el-option label="启用" :value="1" />
              <el-option label="停用" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="partWhere.lowStockOnly">仅低库存</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="reloadParts">查询</el-button>
            <el-button @click="resetPartSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <ele-pro-table
          ref="partTableRef"
          row-key="id"
          :columns="partColumns"
          :datasource="partDatasource"
          cache-key="FleetPartTable"
        >
          <template #toolbar>
            <el-button type="primary" class="ele-btn-icon" @click="openCreatePart">
              新建备件
            </el-button>
          </template>
          <template #qtyOnHand="{ row }">
            <span :class="{ 'is-low': row.lowStock }">
              {{ formatQty(row.qtyOnHand) }}
              <el-tag v-if="row.lowStock" size="small" type="danger" style="margin-left: 6px">
                低于安全库存
              </el-tag>
            </span>
          </template>
          <template #status="{ row }">
            <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
          <template #action="{ row }">
            <el-space>
              <el-link type="primary" :underline="false" @click="openEditPart(row)">
                编辑
              </el-link>
              <el-link type="primary" :underline="false" @click="openAdjust(row)">
                调整库存
              </el-link>
              <el-link
                :type="row.status === 1 ? 'danger' : 'success'"
                :underline="false"
                @click="togglePartStatus(row)"
              >
                {{ row.status === 1 ? '停用' : '启用' }}
              </el-link>
            </el-space>
          </template>
        </ele-pro-table>
      </ele-card>

      <!-- 入库 -->
      <ele-card v-if="activeTab === 'inbound'">
        <el-form
          ref="inboundFormRef"
          :model="inboundForm"
          :rules="inboundRules"
          label-width="96px"
          style="max-width: 520px"
        >
          <el-form-item label="备件" prop="partId">
            <el-select
              v-model="inboundForm.partId"
              filterable
              remote
              clearable
              placeholder="搜索备件编码/名称"
              :remote-method="searchParts"
              :loading="partLoading"
              style="width: 100%"
              @change="onInboundPartChange"
            >
              <el-option
                v-for="p in partOptions"
                :key="p.id"
                :label="`${p.partCode} · ${p.partName}`"
                :value="p.id!"
              />
            </el-select>
          </el-form-item>
          <el-form-item v-if="inboundPartHint" label="当前库存">
            <span>{{ inboundPartHint }}</span>
          </el-form-item>
          <el-form-item label="入库数量" prop="qty">
            <el-input-number
              v-model="inboundForm.qty"
              :min="0.01"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="单价">
            <el-input-number
              v-model="inboundForm.unitCost"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="inboundForm.remark" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="inboundSubmitting" @click="submitInbound">
              确认入库
            </el-button>
          </el-form-item>
        </el-form>
      </ele-card>

      <!-- 流水 -->
      <ele-card v-if="activeTab === 'txns'" :body-style="{ paddingTop: '8px' }">
        <el-form :inline="true" @submit.prevent>
          <el-form-item label="类型">
            <el-select
              v-model="txnWhere.txnType"
              clearable
              placeholder="全部"
              style="width: 120px"
            >
              <el-option label="入库" value="in" />
              <el-option label="出库" value="out" />
              <el-option label="调整" value="adjust" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键字">
            <el-input
              v-model="txnWhere.keyword"
              clearable
              placeholder="备件编码/名称"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="reloadTxns">查询</el-button>
            <el-button @click="resetTxnSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <ele-pro-table
          ref="txnTableRef"
          row-key="id"
          :columns="txnColumns"
          :datasource="txnDatasource"
          cache-key="FleetStockTxnTable"
        >
          <template #txnType="{ row }">
            {{ txnTypeLabel(row.txnType) }}
          </template>
        </ele-pro-table>
      </ele-card>
    </template>

    <!-- 新建/编辑备件 -->
    <ele-modal
      v-model="partDialogVisible"
      :title="partForm.id ? '编辑备件' : '新建备件'"
      :width="520"
      @ok="submitPart"
    >
      <el-form ref="partFormRef" :model="partForm" :rules="partRules" label-width="96px">
        <el-form-item label="编码" prop="partCode">
          <el-input
            v-model="partForm.partCode"
            :disabled="!!partForm.id"
            maxlength="50"
            placeholder="唯一编码"
          />
        </el-form-item>
        <el-form-item label="名称" prop="partName">
          <el-input v-model="partForm.partName" maxlength="100" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="partForm.category" placeholder="如：滤清器、刹车" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="partForm.unit" style="width: 120px" />
        </el-form-item>
        <el-form-item label="参考价">
          <el-input-number
            v-model="partForm.refPrice"
            :min="0"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="安全库存">
          <el-input-number
            v-model="partForm.safetyStock"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="partForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
    </ele-modal>

    <!-- 调整库存 -->
    <ele-modal v-model="adjustVisible" title="调整库存" :width="440" @ok="submitAdjust">
      <el-form :model="adjustForm" label-width="110px">
        <el-form-item label="备件">
          <span>{{ adjustForm.partName }}</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <span>{{ formatQty(adjustForm.qtyOnHand) }}</span>
        </el-form-item>
        <el-form-item label="调整数量">
          <el-input-number
            v-model="adjustForm.qtyDelta"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
          <div class="hint">正数盘盈，负数盘亏</div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="adjustForm.remark" />
        </el-form-item>
      </el-form>
    </ele-modal>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { useRouter } from 'vue-router';
  import { useUserStore } from '@/store/modules/user';
  import {
    adjustPart,
    createPart,
    inboundPart,
    pageParts,
    pageStockTxns,
    updatePart
  } from '@/api/capacity/maintenance';
  import type {
    FleetPart,
    StockTxn
  } from '@/api/capacity/maintenance/model';

  defineOptions({ name: 'CapacityVehicleAssetParts' });

  const router = useRouter();
  const userStore = useUserStore();
  const featureEnabled = computed(() =>
    userStore.hasFeature('fleet_maintenance')
  );

  const activeTab = ref('parts');
  const partTableRef = ref();
  const txnTableRef = ref();
  const partWhere = reactive<{
    keyword?: string;
    status?: number;
    lowStockOnly?: boolean;
  }>({});
  const txnWhere = reactive<{ txnType?: string; keyword?: string }>({});

  const partDialogVisible = ref(false);
  const partFormRef = ref<FormInstance>();
  const partForm = reactive<FleetPart>({
    partCode: '',
    partName: '',
    unit: '个',
    safetyStock: 0
  });
  const partRules: FormRules = {
    partCode: [{ required: true, message: '请填写备件编码', trigger: 'blur' }],
    partName: [{ required: true, message: '请填写备件名称', trigger: 'blur' }]
  };

  const partOptions = ref<FleetPart[]>([]);
  const partLoading = ref(false);
  const inboundFormRef = ref<FormInstance>();
  const inboundSubmitting = ref(false);
  const inboundForm = reactive<{
    partId?: number;
    qty?: number;
    unitCost?: number;
    remark?: string;
  }>({ qty: 1 });
  const inboundRules: FormRules = {
    partId: [{ required: true, message: '请选择备件', trigger: 'change' }],
    qty: [{ required: true, message: '请填写入库数量', trigger: 'change' }]
  };
  const inboundPartHint = ref('');

  const adjustVisible = ref(false);
  const adjustForm = reactive<{
    partId?: number;
    partName?: string;
    qtyOnHand?: number;
    qtyDelta?: number;
    remark?: string;
  }>({});

  const partColumns = computed<Columns>(() => [
    { prop: 'partCode', label: '编码', minWidth: 120 },
    { prop: 'partName', label: '名称', minWidth: 140 },
    { prop: 'category', label: '分类', width: 100 },
    { prop: 'unit', label: '单位', width: 70 },
    { prop: 'refPrice', label: '参考价', width: 100 },
    { prop: 'qtyOnHand', label: '库存', minWidth: 160, slot: 'qtyOnHand' },
    { prop: 'safetyStock', label: '安全库存', width: 90 },
    { prop: 'status', label: '状态', width: 80, slot: 'status' },
    {
      columnKey: 'action',
      label: '操作',
      width: 200,
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const txnColumns = computed<Columns>(() => [
    { prop: 'createdAt', label: '时间', minWidth: 160 },
    { prop: 'txnType', label: '类型', width: 80, slot: 'txnType' },
    { prop: 'partCode', label: '编码', width: 110 },
    { prop: 'partName', label: '名称', minWidth: 140 },
    { prop: 'qty', label: '数量', width: 90 },
    { prop: 'unitCost', label: '单价', width: 90 },
    { prop: 'amount', label: '金额', width: 100 },
    { prop: 'remark', label: '备注', minWidth: 140 }
  ]);

  const partDatasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageParts({
      ...partWhere,
      page: p,
      limit: l
    });
    const raw = res as { list?: FleetPart[]; count?: number; total?: number };
    return { list: raw?.list ?? [], count: raw?.count ?? raw?.total ?? 0 };
  };

  const txnDatasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageStockTxns({
      ...txnWhere,
      page: p,
      limit: l
    });
    const raw = res as { list?: StockTxn[]; count?: number; total?: number };
    return { list: raw?.list ?? [], count: raw?.count ?? raw?.total ?? 0 };
  };

  const onTabChange = (name: string | number) => {
    if (name === 'parts') nextTick(() => partTableRef.value?.reload?.());
    if (name === 'txns') nextTick(() => txnTableRef.value?.reload?.());
    if (name === 'inbound') searchParts('');
  };

  const reloadParts = () => partTableRef.value?.reload?.({ page: 1 });
  const reloadTxns = () => txnTableRef.value?.reload?.({ page: 1 });
  const resetPartSearch = () => {
    partWhere.keyword = undefined;
    partWhere.status = undefined;
    partWhere.lowStockOnly = false;
    reloadParts();
  };
  const resetTxnSearch = () => {
    txnWhere.txnType = undefined;
    txnWhere.keyword = undefined;
    reloadTxns();
  };

  const openCreatePart = () => {
    Object.assign(partForm, {
      id: undefined,
      partCode: '',
      partName: '',
      category: '',
      unit: '个',
      refPrice: undefined,
      safetyStock: 0,
      remark: ''
    });
    partDialogVisible.value = true;
  };

  const openEditPart = (row: FleetPart) => {
    Object.assign(partForm, {
      id: row.id,
      partCode: row.partCode,
      partName: row.partName,
      category: row.category,
      unit: row.unit || '个',
      refPrice: row.refPrice ?? undefined,
      safetyStock: row.safetyStock ?? 0,
      remark: row.remark || ''
    });
    partDialogVisible.value = true;
  };

  const submitPart = async () => {
    await partFormRef.value?.validate?.();
    try {
      EleMessage.loading({ message: '正在保存备件，请稍候…', plain: true });
      if (partForm.id) {
        const res = await updatePart(partForm.id, { ...partForm });
        EleMessage.success(res.message || '备件已保存');
      } else {
        const res = await createPart({ ...partForm });
        EleMessage.success(res.message || '备件已创建');
      }
      partDialogVisible.value = false;
      reloadParts();
    } catch (e: any) {
      EleMessage.error(e.message || '保存失败，请重试');
    }
  };

  const togglePartStatus = async (row: FleetPart) => {
    if (!row.id) return;
    try {
      const next = row.status === 1 ? 0 : 1;
      const res = await updatePart(row.id, { status: next });
      EleMessage.success(res.message || (next === 1 ? '已启用' : '已停用'));
      reloadParts();
    } catch (e: any) {
      EleMessage.error(e.message || '操作失败，请重试');
    }
  };

  const openAdjust = (row: FleetPart) => {
    adjustForm.partId = row.id;
    adjustForm.partName = `${row.partCode} · ${row.partName}`;
    adjustForm.qtyOnHand = Number(row.qtyOnHand || 0);
    adjustForm.qtyDelta = 0;
    adjustForm.remark = '';
    adjustVisible.value = true;
  };

  const submitAdjust = async () => {
    if (!adjustForm.partId) return;
    if (!adjustForm.qtyDelta) {
      EleMessage.warning('请填写不为 0 的调整数量');
      return;
    }
    try {
      EleMessage.loading({ message: '正在调整库存，请稍候…', plain: true });
      const res = await adjustPart(adjustForm.partId, {
        qtyDelta: adjustForm.qtyDelta,
        remark: adjustForm.remark
      });
      EleMessage.success(res.message || '库存已调整');
      adjustVisible.value = false;
      reloadParts();
    } catch (e: any) {
      EleMessage.error(e.message || '调整失败，请重试');
    }
  };

  const searchParts = async (q: string) => {
    partLoading.value = true;
    try {
      const res = await pageParts({ keyword: q, status: 1, page: 1, limit: 30 });
      partOptions.value = res?.list || [];
    } finally {
      partLoading.value = false;
    }
  };

  const onInboundPartChange = (id?: number) => {
    const p = partOptions.value.find((x) => x.id === id);
    if (!p) {
      inboundPartHint.value = '';
      return;
    }
    inboundPartHint.value = `${formatQty(p.qtyOnHand)} ${p.unit || ''}`;
    if (inboundForm.unitCost == null && p.refPrice != null) {
      inboundForm.unitCost = Number(p.refPrice);
    }
  };

  const submitInbound = async () => {
    await inboundFormRef.value?.validate?.();
    if (!inboundForm.partId || !inboundForm.qty) return;
    inboundSubmitting.value = true;
    try {
      EleMessage.loading({ message: '正在入库，请稍候…', plain: true });
      const res = await inboundPart(inboundForm.partId, {
        qty: inboundForm.qty,
        unitCost: inboundForm.unitCost,
        remark: inboundForm.remark
      });
      EleMessage.success(res.message || '入库成功');
      inboundForm.partId = undefined;
      inboundForm.qty = 1;
      inboundForm.unitCost = undefined;
      inboundForm.remark = '';
      inboundPartHint.value = '';
      searchParts('');
    } catch (e: any) {
      EleMessage.error(e.message || '入库失败，请重试');
    } finally {
      inboundSubmitting.value = false;
    }
  };

  const formatQty = (n?: number) =>
    Number(n || 0).toLocaleString('zh-CN', {
      maximumFractionDigits: 2
    });

  const txnTypeLabel = (t?: string) =>
    ({ in: '入库', out: '出库', adjust: '调整' }[t || ''] || t || '—');

  const goHome = () => router.replace('/');

  onMounted(() => {
    if (featureEnabled.value) {
      searchParts('');
    }
  });
</script>

<style scoped>
  .is-low {
    color: var(--el-color-danger);
    font-weight: 600;
  }

  .hint {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
