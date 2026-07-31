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
          <el-col :lg="6" :md="12" :xs="24">
            <ele-card>
              <div class="stat-item">
                <div class="stat-label">待办保养</div>
                <div class="stat-value warning">{{ board.duePlans.length }}</div>
              </div>
            </ele-card>
          </el-col>
          <el-col :lg="6" :md="12" :xs="24">
            <ele-card>
              <div class="stat-item">
                <div class="stat-label">进行中工单</div>
                <div class="stat-value primary">
                  {{ board.inProgressOrders.length }}
                </div>
              </div>
            </ele-card>
          </el-col>
          <el-col :lg="6" :md="12" :xs="24">
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
          <el-col :lg="6" :md="12" :xs="24">
            <ele-card>
              <div class="stat-item">
                <div class="stat-label">低库存备件</div>
                <div
                  class="stat-value"
                  :class="{ danger: (board.lowStockCount || 0) > 0 }"
                >
                  {{ board.lowStockCount || 0 }}
                </div>
                <el-button
                  v-if="(board.lowStockCount || 0) > 0"
                  type="primary"
                  link
                  style="margin-top: 4px; padding: 0"
                  @click="goParts"
                >
                  去备件库存查看
                </el-button>
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
                    {{ orderTypeLabel(o.orderType) }}
                    <template v-if="o.faultCategory">
                      · {{ faultCategoryLabel(o.faultCategory) }}
                    </template>
                    · {{ o.workOrderNo }}
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
          <template #faultCategory="{ row }">
            {{ faultCategoryLabel(row.faultCategory) }}
          </template>
          <template #status="{ row }">
            <el-tag size="small" :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
          <template #action="{ row }">
            <el-space>
              <el-link
                v-if="row.status === 'draft' || row.status === 'in_progress'"
                type="primary"
                :underline="false"
                @click="openEditOrder(row)"
              >
                编辑
              </el-link>
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

    <!-- 新建/编辑工单 -->
    <ele-drawer
      v-model="orderDialogVisible"
      :title="orderForm.id ? '编辑维修工单' : '新建维修工单'"
      :size="720"
      :body-style="{ paddingBottom: '8px' }"
    >
      <el-form
        ref="orderFormRef"
        :model="orderForm"
        :rules="orderRules"
        label-width="96px"
      >
        <el-form-item label="车辆" prop="vehicleId">
          <el-select
            v-model="orderForm.vehicleId"
            filterable
            remote
            clearable
            placeholder="搜索车牌"
            :disabled="!!orderForm.id"
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
          <el-radio-group v-model="orderForm.orderType" :disabled="!!orderForm.id">
            <el-radio value="repair">维修</el-radio>
            <el-radio value="maintenance">保养</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分类" prop="faultCategory">
          <el-select
            v-model="orderForm.faultCategory"
            clearable
            placeholder="故障/作业分类"
            style="width: 100%"
          >
            <el-option
              v-for="c in FAULT_CATEGORIES"
              :key="c.value"
              :label="c.label"
              :value="c.value"
            />
          </el-select>
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
          <el-select
            v-model="orderForm.workshopId"
            filterable
            clearable
            allow-create
            default-first-option
            placeholder="选择或输入维修厂"
            style="width: 100%"
            @change="onWorkshopChange"
          >
            <el-option
              v-for="w in workshopOptions"
              :key="w.id"
              :label="w.name!"
              :value="w.id!"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="orderForm.description" type="textarea" :rows="2" />
        </el-form-item>

        <div class="section-title">
          项目 / 工时
          <el-button type="primary" link @click="addLaborLine">添加行</el-button>
        </div>
        <el-table :data="laborLines" border size="small" class="line-table">
          <el-table-column label="项目名称" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.title" placeholder="如：更换刹车片" />
            </template>
          </el-table-column>
          <el-table-column label="工时(h)" width="110">
            <template #default="{ row }">
              <el-input-number
                v-model="row.laborHours"
                :min="0"
                :precision="1"
                controls-position="right"
                style="width: 100%"
                @change="recalcLine(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.unitPrice"
                :min="0"
                :precision="2"
                controls-position="right"
                style="width: 100%"
                @change="recalcLine(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="金额" width="100">
            <template #default="{ row }">
              {{ formatMoney(row.amount) }}
            </template>
          </el-table-column>
          <el-table-column label="" width="56" align="center">
            <template #default="{ $index }">
              <el-button
                type="danger"
                link
                @click="laborLines.splice($index, 1)"
              >
                删
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title" style="margin-top: 16px">
          备件
          <el-button type="primary" link @click="addPartLine">添加行</el-button>
        </div>
        <el-table :data="partLines" border size="small" class="line-table">
          <el-table-column label="备件" min-width="200">
            <template #default="{ row }">
              <el-select
                v-model="row.partId"
                filterable
                remote
                clearable
                placeholder="搜索备件"
                :remote-method="searchParts"
                :loading="partLoading"
                style="width: 100%"
                @change="(id: number) => onPartLineChange(row, id)"
              >
                <el-option
                  v-for="p in partOptions"
                  :key="p.id"
                  :label="`${p.partCode} · ${p.partName}（库存 ${formatQty(p.qtyOnHand)}）`"
                  :value="p.id!"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="110">
            <template #default="{ row }">
              <el-input-number
                v-model="row.qty"
                :min="0.01"
                :precision="2"
                controls-position="right"
                style="width: 100%"
                @change="recalcLine(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.unitPrice"
                :min="0"
                :precision="2"
                controls-position="right"
                style="width: 100%"
                @change="recalcLine(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="金额" width="100">
            <template #default="{ row }">
              {{ formatMoney(row.amount) }}
            </template>
          </el-table-column>
          <el-table-column label="" width="56" align="center">
            <template #default="{ $index }">
              <el-button
                type="danger"
                link
                @click="partLines.splice($index, 1)"
              >
                删
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="line-summary">
          工时/项目 ¥{{ formatMoney(laborTotal) }}
          · 备件 ¥{{ formatMoney(partsTotal) }}
          · 合计
          <strong>¥{{ formatMoney(laborTotal + partsTotal) }}</strong>
          <span class="muted">（完工时扣减备件库存）</span>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">保存</el-button>
      </template>
    </ele-drawer>

    <!-- 完工 -->
    <ele-modal
      v-model="completeVisible"
      title="完工登记"
      :width="560"
      @ok="submitComplete"
    >
      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="完工后将按备件行扣减库存；库存不足时无法完工。"
        style="margin-bottom: 12px"
      />
      <div class="complete-summary">
        <div>工时/项目：¥{{ formatMoney(completeTarget?.laborAmount) }}</div>
        <div>备件：¥{{ formatMoney(completeTarget?.partsAmount) }}</div>
        <div class="complete-total">
          合计：¥{{ formatMoney(completeTarget?.costAmount) }}
        </div>
      </div>
      <el-form :model="completeForm" label-width="96px">
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
    getWorkOrder,
    pageMaintainPlans,
    pageParts,
    pageWorkOrders,
    pageWorkshops,
    startWorkOrder,
    updateWorkOrder
  } from '@/api/capacity/maintenance';
  import type {
    FleetPart,
    FleetWorkshop,
    MaintainPlan,
    MaintenanceBoard,
    WorkOrder,
    WorkOrderLine
  } from '@/api/capacity/maintenance/model';

  defineOptions({ name: 'CapacityMaintenance' });

  const FAULT_CATEGORIES = [
    { value: 'engine', label: '发动机' },
    { value: 'brake', label: '制动' },
    { value: 'electrical', label: '电气' },
    { value: 'body', label: '车身' },
    { value: 'tire', label: '轮胎' },
    { value: 'routine', label: '常规保养' },
    { value: 'other', label: '其他' }
  ];

  const router = useRouter();
  const userStore = useUserStore();
  const featureEnabled = computed(() =>
    userStore.hasFeature('fleet_maintenance')
  );

  const activeTab = ref('board');
  const board = reactive<MaintenanceBoard>({
    duePlans: [],
    inProgressOrders: [],
    weekSummary: { completedCount: 0, costAmount: 0 },
    lowStockCount: 0
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
  const partOptions = ref<FleetPart[]>([]);
  const partLoading = ref(false);
  const workshopOptions = ref<FleetWorkshop[]>([]);

  const orderDialogVisible = ref(false);
  const orderFormRef = ref<FormInstance>();
  const orderForm = reactive<WorkOrder>({
    orderType: 'repair',
    title: '',
    lines: []
  });
  const laborLines = ref<WorkOrderLine[]>([]);
  const partLines = ref<WorkOrderLine[]>([]);
  const orderRules: FormRules = {
    vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
    orderType: [{ required: true, message: '请选择类型', trigger: 'change' }],
    title: [{ required: true, message: '请填写标题', trigger: 'blur' }]
  };

  const laborTotal = computed(() =>
    laborLines.value.reduce((s, r) => s + Number(r.amount || 0), 0)
  );
  const partsTotal = computed(() =>
    partLines.value.reduce((s, r) => s + Number(r.amount || 0), 0)
  );

  const completeVisible = ref(false);
  const completeTarget = ref<WorkOrder | null>(null);
  const completeForm = reactive<{
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
    { prop: 'orderType', label: '类型', width: 70, slot: 'orderType' },
    {
      prop: 'faultCategory',
      label: '分类',
      width: 90,
      slot: 'faultCategory'
    },
    { prop: 'title', label: '标题', minWidth: 140 },
    { prop: 'status', label: '状态', width: 90, slot: 'status' },
    { prop: 'laborAmount', label: '工时费', width: 90 },
    { prop: 'partsAmount', label: '备件费', width: 90 },
    { prop: 'costAmount', label: '总费用', width: 90 },
    { prop: 'updatedAt', label: '更新时间', minWidth: 150 },
    {
      columnKey: 'action',
      label: '操作',
      width: 180,
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
      board.lowStockCount = data.lowStockCount || 0;
    } catch (e: any) {
      EleMessage.error(e.message || '加载看板失败，请重试');
    }
  };

  const loadWorkshops = async () => {
    try {
      const res = await pageWorkshops({ enabled: 1, page: 1, limit: 100 });
      workshopOptions.value = res?.list || [];
    } catch {
      workshopOptions.value = [];
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

  const searchParts = async (q: string) => {
    partLoading.value = true;
    try {
      const res = await pageParts({ keyword: q, status: 1, page: 1, limit: 30 });
      partOptions.value = res?.list || [];
    } finally {
      partLoading.value = false;
    }
  };

  const recalcLine = (row: WorkOrderLine) => {
    const qty =
      row.lineType === 'labor'
        ? Number(row.laborHours || 0) || 1
        : Number(row.qty || 1);
    if (row.lineType === 'labor') {
      row.qty = 1;
    }
    const price = Number(row.unitPrice || 0);
    const base =
      row.lineType === 'labor' ? Number(row.laborHours || 0) || 1 : qty;
    row.amount = Math.round(base * price * 100) / 100;
  };

  const addLaborLine = () => {
    laborLines.value.push({
      lineType: 'labor',
      title: '',
      qty: 1,
      laborHours: 1,
      unitPrice: 0,
      amount: 0
    });
  };

  const addPartLine = () => {
    partLines.value.push({
      lineType: 'part',
      title: '',
      partId: undefined,
      qty: 1,
      unitPrice: 0,
      amount: 0
    });
    searchParts('');
  };

  const onPartLineChange = (row: WorkOrderLine, partId?: number) => {
    const p = partOptions.value.find((x) => x.id === partId);
    if (!p) return;
    row.title = p.partName || '';
    row.unitPrice = p.refPrice != null ? Number(p.refPrice) : 0;
    recalcLine(row);
  };

  const onWorkshopChange = (id: number | string) => {
    if (typeof id === 'string') {
      orderForm.workshopId = undefined;
      orderForm.workshop = id;
      return;
    }
    const w = workshopOptions.value.find((x) => x.id === id);
    orderForm.workshop = w?.name || '';
  };

  const resetOrderForm = () => {
    Object.assign(orderForm, {
      id: undefined,
      vehicleId: undefined,
      orderType: 'repair',
      title: '',
      faultCategory: undefined,
      odometer: undefined,
      workshopId: undefined,
      workshop: '',
      description: ''
    });
    laborLines.value = [];
    partLines.value = [];
  };

  const openCreateOrder = () => {
    resetOrderForm();
    addLaborLine();
    orderDialogVisible.value = true;
    searchVehicles('');
    loadWorkshops();
    searchParts('');
  };

  const openEditOrder = async (row: WorkOrder) => {
    if (!row.id) return;
    try {
      EleMessage.loading({ message: '正在加载工单，请稍候…', plain: true });
      const detail = await getWorkOrder(row.id);
      Object.assign(orderForm, {
        id: detail.id,
        vehicleId: detail.vehicleId,
        orderType: detail.orderType,
        title: detail.title,
        faultCategory: detail.faultCategory,
        odometer: detail.odometer,
        workshopId: detail.workshopId,
        workshop: detail.workshop,
        description: detail.description
      });
      if (detail.plateNumber) {
        vehicleOptions.value = [
          {
            id: detail.vehicleId,
            plateNumber: detail.plateNumber
          } as Vehicle
        ];
      }
      const lines = detail.lines || [];
      laborLines.value = lines
        .filter((l) => l.lineType !== 'part')
        .map((l) => ({ ...l }));
      partLines.value = lines
        .filter((l) => l.lineType === 'part')
        .map((l) => ({ ...l }));
      orderDialogVisible.value = true;
      loadWorkshops();
      searchParts('');
    } catch (e: any) {
      EleMessage.error(e.message || '加载失败，请重试');
    }
  };

  const buildLinesPayload = (): WorkOrderLine[] => {
    const lines: WorkOrderLine[] = [];
    laborLines.value.forEach((l, i) => {
      if (!(l.title || '').trim()) return;
      recalcLine(l);
      lines.push({
        lineType: l.lineType || 'labor',
        title: l.title.trim(),
        qty: 1,
        unitPrice: l.unitPrice,
        laborHours: l.laborHours,
        amount: l.amount,
        sortOrder: i
      });
    });
    partLines.value.forEach((l, i) => {
      if (!l.partId) return;
      recalcLine(l);
      lines.push({
        lineType: 'part',
        partId: l.partId,
        title: l.title || '备件',
        qty: l.qty || 1,
        unitPrice: l.unitPrice,
        amount: l.amount,
        sortOrder: laborLines.value.length + i
      });
    });
    return lines;
  };

  const submitOrder = async () => {
    await orderFormRef.value?.validate?.();
    const lines = buildLinesPayload();
    try {
      EleMessage.loading({ message: '正在保存工单，请稍候…', plain: true });
      const payload = { ...orderForm, lines };
      if (orderForm.id) {
        const res = await updateWorkOrder(orderForm.id, payload);
        EleMessage.success(res.message || '工单已保存');
      } else {
        const res = await createWorkOrder(payload);
        EleMessage.success(res.message || '工单已创建');
      }
      orderDialogVisible.value = false;
      activeTab.value = 'orders';
      await nextTick();
      reloadOrders();
      loadBoard();
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

  const openComplete = async (row: WorkOrder) => {
    try {
      const detail = row.lines
        ? row
        : row.id
          ? await getWorkOrder(row.id)
          : row;
      completeTarget.value = detail;
      completeForm.costRemark = detail.costRemark || '';
      completeForm.odometer = detail.odometer ?? undefined;
      completeVisible.value = true;
    } catch (e: any) {
      EleMessage.error(e.message || '加载工单失败，请重试');
    }
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
        `确认取消工单 ${row.workOrderNo}？取消不会扣减库存。`,
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
  const goParts = () => router.push('/capacity/vehicle-asset/parts');

  const formatMoney = (n?: number | null) =>
    Number(n || 0).toLocaleString('zh-CN', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });

  const formatQty = (n?: number | null) =>
    Number(n || 0).toLocaleString('zh-CN', { maximumFractionDigits: 2 });

  const orderTypeLabel = (t?: string) =>
    t === 'maintenance' ? '保养' : t === 'repair' ? '维修' : t || '—';
  const faultCategoryLabel = (c?: string | null) =>
    FAULT_CATEGORIES.find((x) => x.value === c)?.label || c || '—';
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

  .stat-value.danger {
    color: var(--el-color-danger);
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

  .section-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
    margin: 8px 0 8px;
  }

  .line-table {
    width: 100%;
  }

  .line-summary {
    margin-top: 12px;
    font-size: 13px;
  }

  .complete-summary {
    margin-bottom: 12px;
    padding: 12px;
    background: var(--el-fill-color-light);
    border-radius: 6px;
    line-height: 1.8;
  }

  .complete-total {
    font-weight: 600;
    font-size: 15px;
  }
</style>
