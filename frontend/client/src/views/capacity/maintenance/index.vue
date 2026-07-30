<template>
  <ele-page class="fleet-maint-page">
    <ele-card v-if="!featureEnabled" class="fleet-maint-page__upgrade">
      <el-result
        icon="warning"
        title="维修保养为专业版功能"
        sub-title="开通后可登记维修保养、同步运力是否可派，并把养车成本沉淀进经营分析。"
      >
        <template #extra>
          <el-button type="primary" @click="goHome">返回工作台</el-button>
        </template>
      </el-result>
    </ele-card>

    <template v-else>
      <ele-card :body-style="{ paddingBottom: '8px' }">
        <el-tabs v-model="activeTab" @tab-change="onTabChange">
          <el-tab-pane label="维保看板" name="board" />
          <el-tab-pane label="维修工单" name="orders" />
          <el-tab-pane label="保养计划" name="plans" />
        </el-tabs>
      </ele-card>

      <!-- 看板 -->
      <template v-if="activeTab === 'board'">
        <el-row :gutter="12" class="fleet-maint-page__stats">
          <el-col :lg="8" :md="8" :xs="24">
            <ele-card>
              <div class="stat-item">
                <div class="stat-label">待办保养</div>
                <div class="stat-value warning">{{ board.duePlans.length }}</div>
              </div>
            </ele-card>
          </el-col>
          <el-col :lg="8" :md="8" :xs="24">
            <ele-card>
              <div class="stat-item">
                <div class="stat-label">进行中工单</div>
                <div class="stat-value primary">
                  {{ board.inProgressOrders.length }}
                </div>
              </div>
            </ele-card>
          </el-col>
          <el-col :lg="8" :md="8" :xs="24">
            <ele-card>
              <div class="stat-item">
                <div class="stat-label">本周完工</div>
                <div class="stat-value">
                  {{ board.weekSummary.completedCount }}
                  <span class="stat-sub">
                    · 费用 ¥{{ formatMoney(board.weekSummary.costAmount) }}
                  </span>
                </div>
              </div>
            </ele-card>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :lg="12" :md="24">
            <ele-card header="保养待办">
              <el-empty
                v-if="!board.duePlans.length"
                description="暂无待办保养。可先在「保养计划」里为车辆设好周期。"
              />
              <div
                v-for="p in board.duePlans"
                :key="p.id"
                class="due-row"
              >
                <div>
                  <div class="due-title">
                    {{ p.plateNumber }} · {{ p.name }}
                    <el-tag
                      size="small"
                      :type="p.dueLevel === 'overdue' ? 'danger' : 'warning'"
                      style="margin-left: 8px"
                    >
                      {{ p.dueLevel === 'overdue' ? '已到期' : '即将到期' }}
                    </el-tag>
                  </div>
                  <div class="due-meta">
                    下次保养日：{{ p.nextMaintainDate || '—' }}
                  </div>
                </div>
                <el-button
                  type="primary"
                  link
                  :loading="genLoadingId === p.id"
                  @click="onGenerateFromPlan(p)"
                >
                  生成工单
                </el-button>
              </div>
            </ele-card>
          </el-col>
          <el-col :lg="12" :md="24">
            <ele-card header="进行中工单">
              <el-empty
                v-if="!board.inProgressOrders.length"
                description="当前没有进行中的维保工单"
              />
              <div
                v-for="o in board.inProgressOrders"
                :key="o.id"
                class="due-row"
              >
                <div>
                  <div class="due-title">
                    {{ o.plateNumber }} · {{ o.title }}
                  </div>
                  <div class="due-meta">
                    {{ orderTypeLabel(o.orderType) }} · {{ o.workOrderNo }}
                  </div>
                </div>
                <el-button type="primary" link @click="openComplete(o)">
                  完工
                </el-button>
              </div>
            </ele-card>
          </el-col>
        </el-row>
      </template>

      <!-- 工单 -->
      <ele-card v-if="activeTab === 'orders'" :body-style="{ paddingTop: '8px' }">
        <el-form :inline="true" @submit.prevent>
          <el-form-item label="状态">
            <el-select
              v-model="orderWhere.status"
              clearable
              placeholder="全部"
              style="width: 120px"
            >
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select
              v-model="orderWhere.orderType"
              clearable
              placeholder="全部"
              style="width: 120px"
            >
              <el-option label="维修" value="repair" />
              <el-option label="保养" value="maintenance" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键字">
            <el-input
              v-model="orderWhere.keyword"
              clearable
              placeholder="车牌/工单号/标题"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="reloadOrders">查询</el-button>
            <el-button @click="resetOrderSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <ele-pro-table
          ref="orderTableRef"
          row-key="id"
          :columns="orderColumns"
          :datasource="orderDatasource"
          :toolbar="{ theme: 'default' }"
          cache-key="FleetWorkOrderTable"
        >
          <template #toolbar>
            <el-button type="primary" class="ele-btn-icon" @click="openCreateOrder">
              新建工单
            </el-button>
          </template>
          <template #orderType="{ row }">
            {{ orderTypeLabel(row.orderType) }}
          </template>
          <template #status="{ row }">
            <el-tag size="small" :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
          <template #action="{ row }">
            <el-space>
              <el-link
                v-if="row.status === 'draft'"
                type="primary"
                :underline="false"
                @click="onStart(row)"
              >
                开工
              </el-link>
              <el-link
                v-if="row.status === 'in_progress'"
                type="primary"
                :underline="false"
                @click="openComplete(row)"
              >
                完工
              </el-link>
              <el-link
                v-if="row.status === 'draft' || row.status === 'in_progress'"
                type="danger"
                :underline="false"
                @click="onCancel(row)"
              >
                取消
              </el-link>
            </el-space>
          </template>
        </ele-pro-table>
      </ele-card>

      <!-- 计划 -->
      <ele-card v-if="activeTab === 'plans'" :body-style="{ paddingTop: '8px' }">
        <el-form :inline="true" @submit.prevent>
          <el-form-item label="关键字">
            <el-input
              v-model="planWhere.keyword"
              clearable
              placeholder="车牌/计划名"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="reloadPlans">查询</el-button>
            <el-button @click="resetPlanSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <ele-pro-table
          ref="planTableRef"
          row-key="id"
          :columns="planColumns"
          :datasource="planDatasource"
          cache-key="FleetMaintainPlanTable"
        >
          <template #toolbar>
            <el-button type="primary" class="ele-btn-icon" @click="openCreatePlan">
              新建计划
            </el-button>
          </template>
          <template #cycleType="{ row }">
            {{ cycleLabel(row.cycleType) }}
          </template>
          <template #dueLevel="{ row }">
            <el-tag
              v-if="row.dueLevel === 'overdue'"
              size="small"
              type="danger"
            >
              已到期
            </el-tag>
            <el-tag
              v-else-if="row.dueLevel === 'due_soon'"
              size="small"
              type="warning"
            >
              即将到期
            </el-tag>
            <span v-else class="muted">正常</span>
          </template>
          <template #action="{ row }">
            <el-space>
              <el-link
                type="primary"
                :underline="false"
                @click="onGenerateFromPlan(row)"
              >
                生成工单
              </el-link>
              <el-link
                type="danger"
                :underline="false"
                @click="onDeletePlan(row)"
              >
                删除
              </el-link>
            </el-space>
          </template>
        </ele-pro-table>
      </ele-card>
    </template>

    <!-- 新建工单 -->
    <ele-modal
      v-model="orderDialogVisible"
      title="新建维修工单"
      :width="520"
      @ok="submitOrder"
    >
      <el-form ref="orderFormRef" :model="orderForm" :rules="orderRules" label-width="96px">
        <el-form-item label="车辆" prop="vehicleId">
          <el-select
            v-model="orderForm.vehicleId"
            filterable
            remote
            clearable
            placeholder="搜索车牌"
            :remote-method="searchVehicles"
            :loading="vehicleLoading"
            style="width: 100%"
          >
            <el-option
              v-for="v in vehicleOptions"
              :key="v.id"
              :label="v.plateNumber"
              :value="v.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" prop="orderType">
          <el-radio-group v-model="orderForm.orderType">
            <el-radio value="repair">维修</el-radio>
            <el-radio value="maintenance">保养</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="orderForm.title" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="进厂里程">
          <el-input-number
            v-model="orderForm.odometer"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="维修厂">
          <el-input v-model="orderForm.workshop" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="orderForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
    </ele-modal>

    <!-- 完工 -->
    <ele-modal
      v-model="completeVisible"
      title="完工登记"
      :width="480"
      @ok="submitComplete"
    >
      <el-form :model="completeForm" label-width="96px">
        <el-form-item label="费用合计">
          <el-input-number
            v-model="completeForm.costAmount"
            :min="0"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="费用备注">
          <el-input v-model="completeForm.costRemark" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="完工里程">
          <el-input-number
            v-model="completeForm.odometer"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </ele-modal>

    <!-- 新建计划 -->
    <ele-modal
      v-model="planDialogVisible"
      title="新建保养计划"
      :width="520"
      @ok="submitPlan"
    >
      <el-form ref="planFormRef" :model="planForm" :rules="planRules" label-width="110px">
        <el-form-item label="车辆" prop="vehicleId">
          <el-select
            v-model="planForm.vehicleId"
            filterable
            remote
            clearable
            placeholder="搜索车牌"
            :remote-method="searchVehicles"
            :loading="vehicleLoading"
            style="width: 100%"
          >
            <el-option
              v-for="v in vehicleOptions"
              :key="v.id"
              :label="v.plateNumber"
              :value="v.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="planForm.name" placeholder="如：常规保养" />
        </el-form-item>
        <el-form-item label="周期类型" prop="cycleType">
          <el-select v-model="planForm.cycleType" style="width: 100%">
            <el-option label="按时间" value="time" />
            <el-option label="按里程" value="mileage" />
            <el-option label="时间或里程孰先" value="either" />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="planForm.cycleType === 'time' || planForm.cycleType === 'either'"
          label="间隔天数"
          prop="intervalDays"
        >
          <el-input-number
            v-model="planForm.intervalDays"
            :min="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          v-if="planForm.cycleType === 'mileage' || planForm.cycleType === 'either'"
          label="间隔里程(km)"
          prop="intervalMileage"
        >
          <el-input-number
            v-model="planForm.intervalMileage"
            :min="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="提前提醒(天)">
          <el-input-number
            v-model="planForm.remindDays"
            :min="1"
            :max="90"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </ele-modal>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { useRouter } from 'vue-router';
  import { useUserStore } from '@/store/modules/user';
  import { pageVehicles } from '@/api/capacity/self-capacity/vehicle';
  import type { Vehicle } from '@/api/capacity/self-capacity/vehicle/model';
  import {
    cancelWorkOrder,
    completeWorkOrder,
    createMaintainPlan,
    createWorkOrder,
    deleteMaintainPlan,
    generateWorkOrderFromPlan,
    getMaintenanceBoard,
    pageMaintainPlans,
    pageWorkOrders,
    startWorkOrder
  } from '@/api/capacity/maintenance';
  import type {
    MaintainPlan,
    MaintenanceBoard,
    WorkOrder
  } from '@/api/capacity/maintenance/model';

  defineOptions({ name: 'CapacityMaintenance' });

  const router = useRouter();
  const userStore = useUserStore();
  const featureEnabled = computed(() =>
    userStore.hasFeature('fleet_maintenance')
  );

  const activeTab = ref('board');
  const board = reactive<MaintenanceBoard>({
    duePlans: [],
    inProgressOrders: [],
    weekSummary: { completedCount: 0, costAmount: 0 }
  });
  const genLoadingId = ref<number | null>(null);

  const orderTableRef = ref();
  const planTableRef = ref();
  const orderWhere = reactive<{
    status?: string;
    orderType?: string;
    keyword?: string;
  }>({});
  const planWhere = reactive<{ keyword?: string }>({});

  const vehicleOptions = ref<Vehicle[]>([]);
  const vehicleLoading = ref(false);

  const orderDialogVisible = ref(false);
  const orderFormRef = ref<FormInstance>();
  const orderForm = reactive<WorkOrder>({
    orderType: 'repair',
    title: ''
  });
  const orderRules: FormRules = {
    vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
    orderType: [{ required: true, message: '请选择类型', trigger: 'change' }],
    title: [{ required: true, message: '请填写标题', trigger: 'blur' }]
  };

  const completeVisible = ref(false);
  const completeTarget = ref<WorkOrder | null>(null);
  const completeForm = reactive<{
    costAmount?: number;
    costRemark?: string;
    odometer?: number;
  }>({});

  const planDialogVisible = ref(false);
  const planFormRef = ref<FormInstance>();
  const planForm = reactive<MaintainPlan>({
    cycleType: 'time',
    intervalDays: 90,
    remindDays: 7,
    name: ''
  });
  const planRules: FormRules = {
    vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
    name: [{ required: true, message: '请填写计划名称', trigger: 'blur' }],
    cycleType: [{ required: true, message: '请选择周期类型', trigger: 'change' }]
  };

  const orderColumns = computed<Columns>(() => [
    { prop: 'workOrderNo', label: '工单号', minWidth: 140 },
    { prop: 'plateNumber', label: '车牌', width: 110 },
    { prop: 'orderType', label: '类型', width: 80, slot: 'orderType' },
    { prop: 'title', label: '标题', minWidth: 160 },
    { prop: 'status', label: '状态', width: 90, slot: 'status' },
    { prop: 'costAmount', label: '费用', width: 100 },
    { prop: 'updatedAt', label: '更新时间', minWidth: 160 },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const planColumns = computed<Columns>(() => [
    { prop: 'plateNumber', label: '车牌', width: 110 },
    { prop: 'name', label: '计划名称', minWidth: 140 },
    { prop: 'cycleType', label: '周期', width: 120, slot: 'cycleType' },
    { prop: 'nextMaintainDate', label: '下次保养日', width: 120 },
    { prop: 'dueLevel', label: '状态', width: 100, slot: 'dueLevel' },
    { prop: 'remindDays', label: '提前提醒', width: 90 },
    {
      columnKey: 'action',
      label: '操作',
      width: 150,
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const orderDatasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageWorkOrders({
      ...orderWhere,
      page: p,
      limit: l
    });
    const raw = res as { list?: WorkOrder[]; count?: number; total?: number };
    return { list: raw?.list ?? [], count: raw?.count ?? raw?.total ?? 0 };
  };

  const planDatasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageMaintainPlans({
      ...planWhere,
      page: p,
      limit: l
    });
    const raw = res as { list?: MaintainPlan[]; count?: number; total?: number };
    return { list: raw?.list ?? [], count: raw?.count ?? raw?.total ?? 0 };
  };

  const loadBoard = async () => {
    try {
      const data = await getMaintenanceBoard();
      board.duePlans = data.duePlans || [];
      board.inProgressOrders = data.inProgressOrders || [];
      board.weekSummary = data.weekSummary || {
        completedCount: 0,
        costAmount: 0
      };
    } catch (e: any) {
      EleMessage.error(e.message || '加载看板失败，请重试');
    }
  };

  const onTabChange = (name: string | number) => {
    if (name === 'board') loadBoard();
    if (name === 'orders') nextTick(() => orderTableRef.value?.reload?.());
    if (name === 'plans') nextTick(() => planTableRef.value?.reload?.());
  };

  const reloadOrders = () => orderTableRef.value?.reload?.({ page: 1 });
  const reloadPlans = () => planTableRef.value?.reload?.({ page: 1 });
  const resetOrderSearch = () => {
    orderWhere.status = undefined;
    orderWhere.orderType = undefined;
    orderWhere.keyword = undefined;
    reloadOrders();
  };
  const resetPlanSearch = () => {
    planWhere.keyword = undefined;
    reloadPlans();
  };

  const searchVehicles = async (q: string) => {
    vehicleLoading.value = true;
    try {
      const res = await pageVehicles({ keyword: q, page: 1, limit: 20 });
      vehicleOptions.value = res?.list || (res as any)?.records || [];
    } finally {
      vehicleLoading.value = false;
    }
  };

  const openCreateOrder = () => {
    orderForm.vehicleId = undefined;
    orderForm.orderType = 'repair';
    orderForm.title = '';
    orderForm.odometer = undefined;
    orderForm.workshop = '';
    orderForm.description = '';
    orderDialogVisible.value = true;
    searchVehicles('');
  };

  const submitOrder = async () => {
    await orderFormRef.value?.validate?.();
    try {
      EleMessage.loading({ message: '正在保存工单，请稍候…', plain: true });
      const res = await createWorkOrder({ ...orderForm });
      EleMessage.success(res.message || '工单已创建');
      orderDialogVisible.value = false;
      activeTab.value = 'orders';
      await nextTick();
      reloadOrders();
    } catch (e: any) {
      EleMessage.error(e.message || '保存失败，请重试');
    }
  };

  const onStart = async (row: WorkOrder) => {
    try {
      await ElMessageBox.confirm(
        `确认对车辆 ${row.plateNumber} 开工？开工后运力将同步为维修保养中。`,
        '开工确认',
        { type: 'warning' }
      );
      EleMessage.loading({ message: '正在开工，请稍候…', plain: true });
      const res = await startWorkOrder(row.id!);
      EleMessage.success(res.message || '已开工');
      reloadOrders();
      loadBoard();
    } catch (e: any) {
      if (e !== 'cancel' && e?.message) {
        EleMessage.error(e.message);
      }
    }
  };

  const openComplete = (row: WorkOrder) => {
    completeTarget.value = row;
    completeForm.costAmount = row.costAmount ?? undefined;
    completeForm.costRemark = row.costRemark || '';
    completeForm.odometer = row.odometer ?? undefined;
    completeVisible.value = true;
  };

  const submitComplete = async () => {
    if (!completeTarget.value?.id) return;
    try {
      EleMessage.loading({ message: '正在完工，请稍候…', plain: true });
      const res = await completeWorkOrder(completeTarget.value.id, {
        ...completeForm
      });
      EleMessage.success(res.message || '工单已完工');
      completeVisible.value = false;
      reloadOrders();
      loadBoard();
    } catch (e: any) {
      EleMessage.error(e.message || '完工失败，请重试');
    }
  };

  const onCancel = async (row: WorkOrder) => {
    try {
      await ElMessageBox.confirm(
        `确认取消工单 ${row.workOrderNo}？`,
        '取消工单',
        { type: 'warning' }
      );
      const res = await cancelWorkOrder(row.id!);
      EleMessage.success(res.message || '工单已取消');
      reloadOrders();
      loadBoard();
    } catch (e: any) {
      if (e !== 'cancel' && e?.message) {
        EleMessage.error(e.message);
      }
    }
  };

  const openCreatePlan = () => {
    planForm.vehicleId = undefined;
    planForm.name = '';
    planForm.cycleType = 'time';
    planForm.intervalDays = 90;
    planForm.intervalMileage = undefined;
    planForm.remindDays = 7;
    planDialogVisible.value = true;
    searchVehicles('');
  };

  const submitPlan = async () => {
    await planFormRef.value?.validate?.();
    try {
      EleMessage.loading({ message: '正在保存计划，请稍候…', plain: true });
      const res = await createMaintainPlan({ ...planForm });
      EleMessage.success(res.message || '保养计划已创建');
      planDialogVisible.value = false;
      reloadPlans();
      loadBoard();
    } catch (e: any) {
      EleMessage.error(e.message || '保存失败，请重试');
    }
  };

  const onGenerateFromPlan = async (p: MaintainPlan) => {
    if (!p.id) return;
    genLoadingId.value = p.id;
    try {
      const res = await generateWorkOrderFromPlan(p.id);
      EleMessage.success(res.message || '已生成保养工单草稿');
      activeTab.value = 'orders';
      await nextTick();
      reloadOrders();
      loadBoard();
    } catch (e: any) {
      EleMessage.error(e.message || '生成失败，请重试');
    } finally {
      genLoadingId.value = null;
    }
  };

  const onDeletePlan = async (row: MaintainPlan) => {
    try {
      await ElMessageBox.confirm(`确认删除计划「${row.name}」？`, '删除确认', {
        type: 'warning'
      });
      await deleteMaintainPlan(row.id!);
      EleMessage.success('保养计划已删除');
      reloadPlans();
      loadBoard();
    } catch (e: any) {
      if (e !== 'cancel' && e?.message) {
        EleMessage.error(e.message);
      }
    }
  };

  const goHome = () => router.replace('/');

  const formatMoney = (n?: number) =>
    Number(n || 0).toLocaleString('zh-CN', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });

  const orderTypeLabel = (t?: string) =>
    t === 'maintenance' ? '保养' : t === 'repair' ? '维修' : t || '—';
  const statusLabel = (s?: string) =>
    ({
      draft: '草稿',
      in_progress: '进行中',
      completed: '已完成',
      cancelled: '已取消'
    }[s || ''] || s || '—');
  const statusTagType = (s?: string) =>
    ({
      draft: 'info',
      in_progress: 'warning',
      completed: 'success',
      cancelled: 'info'
    }[s || ''] as any) || 'info';
  const cycleLabel = (t?: string) =>
    ({ time: '按时间', mileage: '按里程', either: '时间或里程' }[t || ''] ||
    t ||
    '—');

  onMounted(() => {
    if (featureEnabled.value) {
      loadBoard();
      searchVehicles('');
    }
  });
</script>

<style scoped>
  .fleet-maint-page__stats {
    margin-bottom: 12px;
  }

  .stat-item {
    padding: 4px 0;
  }

  .stat-label {
    color: var(--el-text-color-secondary);
    font-size: 13px;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    line-height: 1.2;
    letter-spacing: -0.02em;
  }

  .stat-value.warning {
    color: var(--el-color-warning);
  }

  .stat-value.primary {
    color: var(--el-color-primary);
  }

  .stat-sub {
    font-size: 13px;
    font-weight: 400;
    color: var(--el-text-color-secondary);
    margin-left: 4px;
  }

  .due-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .due-row:last-child {
    border-bottom: none;
  }

  .due-title {
    font-weight: 500;
    margin-bottom: 4px;
  }

  .due-meta,
  .muted {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
