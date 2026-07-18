<template>
  <el-drawer
    :model-value="visible"
    title="任务单详情"
    direction="rtl"
    size="1000px"
    :destroy-on-close="true"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
  >
    <div v-loading="loading" class="task-detail">
      <template v-if="task">
        <!-- 头部摘要 -->
        <div class="task-detail__header">
          <div>
            <div class="task-detail__no">
              {{ task.taskNo }}
              <el-tag
                :type="
                  (TASK_STATUS_MAP[task.status || 0]?.type as any) || 'info'
                "
                style="margin-left: 8px"
                size="small"
              >
                {{ TASK_STATUS_MAP[task.status || 0]?.label }}
              </el-tag>
              <el-tag
                :type="
                  (CARRIER_TYPE_MAP[task.carrierType || 1]?.type as any) ||
                  'info'
                "
                style="margin-left: 4px"
                size="small"
                effect="plain"
              >
                {{ CARRIER_TYPE_MAP[task.carrierType || 1]?.label }}
              </el-tag>
            </div>
            <div class="task-detail__name">{{ task.taskName || '--' }}</div>
          </div>
          <div class="task-detail__actions">
            <el-button
              v-if="primaryAction"
              :type="primaryAction.buttonType"
              size="small"
              v-permission="primaryAction.permission"
              @click="triggerAction(primaryAction)"
            >
              {{ primaryAction.label }}
            </el-button>
            <el-button
              v-if="showPlanRoute"
              :type="planRouteAction.buttonType"
              size="small"
              plain
              v-permission="planRouteAction.permission"
              @click="triggerAction(planRouteAction)"
            >
              {{ planRouteAction.label
              }}<span
                v-if="(task?.segmentCount ?? 0) === 0"
                style="margin-left: 4px"
                >·未规划</span
              >
            </el-button>
            <el-button
              v-for="act in secondaryActions"
              :key="act.key"
              :type="act.buttonType"
              size="small"
              plain
              v-permission="act.permission"
              @click="triggerAction(act)"
            >
              {{ act.label }}
            </el-button>
            <el-dropdown v-if="reverseActions.length" trigger="click">
              <el-button size="small" plain type="info">
                更多操作<el-icon style="margin-left: 2px"
                  ><ArrowDown
                /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="act in reverseActions"
                    :key="act.key"
                    v-permission="act.permission"
                    @click="triggerAction(act)"
                  >
                    {{ act.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button
              type="success"
              size="small"
              :icon="Plus"
              v-permission="'operation:task-finance:add'"
              @click="openFinanceEdit(null)"
            >
              新建费用单
            </el-button>
          </div>
        </div>

        <!-- 状态时间轴 -->
        <el-divider content-position="left">状态时间轴</el-divider>
        <el-steps
          :active="statusStep"
          align-center
          finish-status="success"
          class="task-detail__steps"
        >
          <el-step title="待分配" />
          <el-step title="待派车" />
          <el-step title="已派车" />
          <el-step title="已装车" />
          <el-step title="在途" />
          <el-step title="已到达" />
          <el-step title="已签收" />
        </el-steps>

        <!-- 基础信息 -->
        <el-divider content-position="left">基础信息</el-divider>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="承运资源">
            <div v-if="task.carrierType === CARRIER_TYPE.CARRIER">
              {{ task.carrierName || '--' }}
            </div>
            <div v-else>
              {{ task.mainDriverName || '--' }}
              <span v-if="task.plateNumber" class="ele-text-secondary">
                / {{ task.plateNumber }}
              </span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="主驾电话">
            {{ task.mainDriverPhone || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="挂车">
            {{ task.trailerPlateNumber || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划装车">
            {{ formatDateTime(task.plannedLoadTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际装车">
            {{ formatDateTime(task.actualLoadTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划到达">
            {{ formatDateTime(task.plannedArriveTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际到达">
            {{ formatDateTime(task.actualArriveTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="承运成本">
            {{ formatAmount(task.carrierCostAmount) }}
          </el-descriptions-item>
          <el-descriptions-item label="已预付/补款/结算">
            <span style="font-variant-numeric: tabular-nums">
              {{ formatAmount(task.prepaidAmount) }} /
              {{ formatAmount(task.supplementAmount) }} /
              {{ formatAmount(task.settledAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ task.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 关联单据状态（只读：计划/财务单据状态机独立于任务） -->
        <el-divider content-position="left">关联单据状态</el-divider>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="计划状态分布">
            <waybill-status-summary :summary="task.waybillStatusSummary" />
            <span
              v-if="(task.waybillStatusSummary?.total ?? 0) > 0"
              class="ele-text-secondary"
              style="margin-left: 8px"
            >
              共 {{ task.waybillStatusSummary?.total }} 张计划
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="财务单据状态">
            <span class="ele-text-secondary">（财务模块接入后展示）</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Tab: 调令 / 装卸记录 / 挂接货物 / 费用单 -->
        <el-divider />
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane name="segments" :label="`调令 (${segments.length})`">
            <el-table :data="segments" border size="small">
              <el-table-column
                label="段"
                prop="orderNo"
                width="60"
                align="center"
              >
                <template #default="{ row }">
                  {{ row.orderNo ?? row.segmentNo ?? '--' }}
                </template>
              </el-table-column>
              <el-table-column label="类型" width="80" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :type="
                      (DISPATCH_TYPE_MAP[
                        row.dispatchType ?? DISPATCH_TYPE_DEFAULT
                      ]?.type as any) || 'info'
                    "
                  >
                    {{
                      DISPATCH_TYPE_MAP[
                        row.dispatchType ?? DISPATCH_TYPE_DEFAULT
                      ]?.label || '--'
                    }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                label="起点"
                prop="fromLocation"
                min-width="180"
              />
              <el-table-column label="终点" prop="toLocation" min-width="180" />
              <el-table-column
                label="公里数"
                prop="mileage"
                width="100"
                align="right"
              />
              <el-table-column label="计划装车" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.plannedLoadTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="实际装车" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.actualLoadTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="实际到达" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.actualArriveTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="接收/出发/完成" min-width="200">
                <template #default="{ row }">
                  <div class="dispatch-time-cell">
                    <span class="ele-text-secondary">接</span>
                    {{ formatDateTime(row.acceptedAt) || '--' }}
                    <span class="ele-text-secondary">·发</span>
                    {{ formatDateTime(row.startedAt) || '--' }}
                    <span class="ele-text-secondary">·完</span>
                    {{ formatDateTime(row.completedAt) || '--' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small">
                    {{ SEGMENT_STATUS_MAP[row.status]?.label || row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane
            name="loading-records"
            :label="`装卸记录 (${loadingRecords.length})`"
          >
            <el-empty
              v-if="!loadingRecords.length"
              description="暂无装卸记录"
              :image-size="80"
            />
            <el-timeline v-else class="loading-records-timeline">
              <el-timeline-item
                v-for="rec in loadingRecords"
                :key="rec.id"
                :type="rec.eventType === 1 ? 'warning' : 'success'"
                :timestamp="formatDateTime(rec.happenedAt) || '--'"
                placement="top"
              >
                <div class="loading-rec-card">
                  <div class="loading-rec-card__head">
                    <el-tag
                      size="small"
                      :type="rec.eventType === 1 ? 'warning' : 'success'"
                    >
                      {{ rec.eventType === 1 ? '装车' : '卸车' }}
                    </el-tag>
                    <span class="loading-rec-card__loc">
                      {{ rec.location || '--' }}
                    </span>
                    <span class="ele-text-secondary loading-rec-card__qty">
                      {{ rec.quantity || 0 }} 台 ·
                      {{ rec.operatorName || '--' }}
                    </span>
                    <el-tag
                      v-if="rec.dispatchOrderId"
                      type="info"
                      effect="plain"
                      size="small"
                    >
                      调令 #{{ orderNoOf(rec.dispatchOrderId) }}
                    </el-tag>
                  </div>
                  <div
                    v-if="rec.items && rec.items.length"
                    class="loading-rec-card__items"
                  >
                    <span
                      v-for="it in rec.items"
                      :key="it.id"
                      class="ele-text-secondary"
                    >
                      {{ it.waybillNo || '--' }} · {{ it.vehicleBrand || '--' }}
                      {{ it.vehicleModel || '' }} ({{ it.quantity }} 台)
                    </span>
                  </div>
                  <div
                    v-if="rec.photoUrls && rec.photoUrls.length"
                    class="loading-rec-card__photos"
                  >
                    <el-image
                      v-for="(url, idx) in rec.photoUrls"
                      :key="url"
                      :src="url"
                      fit="cover"
                      class="loading-rec-card__photo"
                      :preview-src-list="rec.photoUrls"
                      :initial-index="idx"
                    />
                  </div>
                  <div v-if="rec.remark" class="loading-rec-card__remark">
                    备注：{{ rec.remark }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-tab-pane>

          <el-tab-pane name="cargoes" :label="`挂接货物 (${items.length})`">
            <el-table :data="items" border size="small">
              <el-table-column
                label="计划号"
                prop="waybillNo"
                min-width="140"
              />
              <el-table-column
                label="客户"
                prop="customerName"
                min-width="120"
              />
              <el-table-column label="品牌/车型" min-width="160">
                <template #default="{ row }">
                  {{ row.vehicleBrand || '--' }} /
                  {{ row.vehicleModel || '--' }}
                </template>
              </el-table-column>
              <el-table-column
                label="台数"
                prop="quantity"
                width="80"
                align="center"
              />
              <el-table-column
                label="归属调令"
                prop="dispatchOrderId"
                width="100"
                align="center"
              >
                <template #default="{ row }">
                  <span v-if="row.dispatchOrderId">
                    第 {{ orderNoOf(row.dispatchOrderId) }} 段
                  </span>
                  <span v-else>--</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small">
                    {{ ITEM_STATUS_MAP[row.status]?.label || row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="cost" label="应付成本">
            <div class="cost-tab-toolbar">
              <div class="cost-tab-summary">
                <template v-if="costResult">
                  <span class="cost-total">
                    合计应付：{{ formatAmount(costResult.totalCostAmount) }}
                  </span>
                  <el-tag
                    size="small"
                    :type="costStatusTag(costResult.calcStatus).type"
                    style="margin-left: 8px"
                  >
                    {{ costStatusTag(costResult.calcStatus).text }}
                  </el-tag>
                  <span
                    v-if="costResult.payeeName"
                    class="ele-text-secondary"
                    style="margin-left: 8px"
                  >
                    收款方：{{ costResult.payeeName }}
                  </span>
                </template>
                <span v-else class="ele-text-secondary">
                  暂无成本结果（可点击「重算成本」生成）
                </span>
              </div>
              <el-button
                type="primary"
                size="small"
                :loading="costLoading"
                @click="recalcCost"
              >
                重算成本
              </el-button>
            </div>
            <el-table
              :data="costResult?.items ?? []"
              border
              size="small"
              v-loading="costLoading"
            >
              <el-table-column label="费用项" min-width="110">
                <template #default="{ row }">
                  {{ row.feeName || row.feeType }}
                </template>
              </el-table-column>
              <el-table-column label="方向" width="70" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :type="row.direction === 1 ? 'success' : 'warning'"
                  >
                    {{ row.direction === 1 ? '加项' : '扣减' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                label="计价方式"
                prop="pricingMethod"
                width="100"
                align="center"
              />
              <el-table-column
                label="单价"
                prop="unitPrice"
                width="90"
                align="right"
              />
              <el-table-column
                label="数量"
                prop="quantity"
                width="80"
                align="right"
              />
              <el-table-column label="金额" width="100" align="right">
                <template #default="{ row }">
                  {{ formatAmount(row.amount) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="160">
                <template #default="{ row }">
                  <el-tag
                    v-if="row.calcStatus === 'success'"
                    type="success"
                    size="small"
                  >
                    成功
                  </el-tag>
                  <el-tooltip v-else :content="row.errorMessage || ''">
                    <el-tag type="danger" size="small">
                      {{ row.errorType || '异常' }}
                    </el-tag>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <div
              v-if="costResult?.calcTime"
              class="ele-text-secondary cost-tab-meta"
            >
              计算时间：{{ formatDateTime(costResult.calcTime) }}
              <span v-if="costResult.calcEngineVersion">
                · 引擎 {{ costResult.calcEngineVersion }}
              </span>
            </div>
          </el-tab-pane>

          <el-tab-pane
            v-if="task && task.carrierType === CARRIER_TYPE.CARRIER"
            name="carrierFreight"
            label="承运运费"
          >
            <div class="cost-tab-toolbar">
              <div class="cost-tab-summary">
                <template v-if="carrierFreightResult">
                  <span class="cost-total">
                    合计承运运费：{{
                      formatAmount(carrierFreightResult.totalAmount)
                    }}
                  </span>
                  <el-tag
                    size="small"
                    :type="costStatusTag(carrierFreightResult.calcStatus).type"
                    style="margin-left: 8px"
                  >
                    {{ costStatusTag(carrierFreightResult.calcStatus).text }}
                  </el-tag>
                  <span
                    v-if="carrierFreightResult.carrierName"
                    class="ele-text-secondary"
                    style="margin-left: 8px"
                  >
                    承运商：{{ carrierFreightResult.carrierName }}
                  </span>
                </template>
                <span v-else class="ele-text-secondary">
                  暂无承运运费结果（可点击「重算运费」生成）
                </span>
              </div>
              <el-button
                type="primary"
                size="small"
                :loading="carrierFreightLoading"
                @click="recalcCarrierFreight"
              >
                重算运费
              </el-button>
            </div>
            <el-table
              :data="carrierFreightResult?.items ?? []"
              border
              size="small"
              v-loading="carrierFreightLoading"
            >
              <el-table-column label="品牌/车型" min-width="150">
                <template #default="{ row }">
                  {{ carrierFreightBrandModel(row) }}
                </template>
              </el-table-column>
              <el-table-column
                label="台数"
                prop="quantity"
                width="70"
                align="center"
              />
              <el-table-column label="计费模式" width="90" align="center">
                <template #default="{ row }">
                  {{ carrierBillingModeText(row.billingMode) }}
                </template>
              </el-table-column>
              <el-table-column label="单价" width="110" align="right">
                <template #default="{ row }">
                  {{
                    row.unitPrice != null
                      ? Number(row.unitPrice).toFixed(2)
                      : '--'
                  }}
                </template>
              </el-table-column>
              <el-table-column label="金额" width="110" align="right">
                <template #default="{ row }">
                  {{ formatAmount(row.amount) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="160">
                <template #default="{ row }">
                  <el-tag
                    v-if="row.calcStatus === 'success'"
                    type="success"
                    size="small"
                  >
                    已匹配
                  </el-tag>
                  <el-tooltip v-else :content="row.errorMessage || ''">
                    <el-tag type="warning" size="small">
                      {{ row.errorType || '未匹配' }}
                    </el-tag>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <div
              v-if="carrierFreightResult?.calcTime"
              class="ele-text-secondary cost-tab-meta"
            >
              计算时间：{{ formatDateTime(carrierFreightResult.calcTime) }}
              <span v-if="carrierFreightResult.calcEngineVersion">
                · 引擎 {{ carrierFreightResult.calcEngineVersion }}
              </span>
            </div>
          </el-tab-pane>

          <el-tab-pane name="finance" :label="`费用单 (${financeDocs.length})`">
            <el-table :data="financeDocs" border size="small">
              <el-table-column label="单据号" prop="docNo" min-width="160" />
              <el-table-column label="类型" width="90" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :type="DOC_TYPE_LABEL[row.docType]?.type as any"
                  >
                    {{ DOC_TYPE_LABEL[row.docType]?.label }}
                  </el-tag>
                  <el-tag
                    v-if="row.isFinal === 1"
                    type="danger"
                    size="small"
                    effect="plain"
                    style="margin-left: 4px"
                  >
                    终结
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                label="收款人"
                prop="payeeName"
                min-width="140"
              />
              <el-table-column
                label="计划金额"
                prop="plannedAmount"
                width="120"
                align="right"
              />
              <el-table-column
                label="实际金额"
                prop="actualAmount"
                width="120"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatAmount(row.actualAmount) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :type="FIN_STATUS_LABEL[row.status]?.type as any"
                  >
                    {{ FIN_STATUS_LABEL[row.status]?.label }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="计划支付时间" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.plannedPayTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="{ row }">
                  <el-link
                    type="primary"
                    :underline="false"
                    @click="openFinanceEdit(row)"
                  >
                    详情/编辑
                  </el-link>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <!-- 语义化动作弹窗 -->
    <action-assign-carrier
      v-model:visible="actionVisible['assign-carrier']"
      :task="task"
      @done="onActionDone"
    />
    <action-dispatch
      v-model:visible="actionVisible.dispatch"
      :task="task"
      @done="onDispatchDone"
    />
    <action-plan-route
      v-model:visible="actionVisible['plan-route']"
      :task="task"
      @done="onActionDone"
    />
    <action-confirm-load
      v-model:visible="actionVisible['confirm-load']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />
    <action-confirm-arrive
      v-model:visible="actionVisible['confirm-arrive']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />
    <action-confirm-sign
      v-model:visible="actionVisible['confirm-sign']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />
    <action-revert
      v-if="task && revertActionKey"
      v-model:visible="actionVisible.revert"
      :tasks="[task]"
      :action-key="revertActionKey"
      @done="onActionDone"
    />
    <action-revert-sign
      v-model:visible="actionVisible['revert-sign']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />
    <action-force-cancel
      v-model:visible="actionVisible['force-cancel']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />

    <!-- 费用单创建/编辑 -->
    <finance-edit
      v-if="task"
      v-model:visible="financeEditVisible"
      :task="task"
      :doc-id="editingFinanceId"
      :init-doc-type="financeInitDocType"
      :init-is-final="financeInitIsFinal"
      @done="onFinanceDone"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { ArrowDown, Plus } from '@element-plus/icons-vue';
  import {
    getTask,
    listTaskFinanceSummary,
    listTaskSegments,
    listTaskWaybillItems,
    updateTaskStatus
  } from '@/api/operation/task';
  import { listLoadingRecords } from '@/api/operation/task/loading-record';
  import {
    getTaskCostResult,
    recalculateTaskCost
  } from '@/api/billing/cost-policy';
  import type { TaskCostResult } from '@/api/billing/cost-policy/model';
  import {
    getTaskCarrierFreightResult,
    recalculateTaskCarrierFreight
  } from '@/api/billing/carrier-contract';
  import type {
    CarrierFreightItem,
    CarrierFreightResult
  } from '@/api/billing/carrier-contract/model';
  import type {
    Task,
    TaskSegment,
    TaskWaybillItem,
    TaskFinanceSummaryItem,
    TaskLoadingRecord
  } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    CARRIER_TYPE,
    CARRIER_TYPE_MAP,
    DISPATCH_TYPE_DEFAULT,
    DISPATCH_TYPE_MAP,
    ITEM_STATUS_MAP,
    SEGMENT_STATUS_MAP,
    TASK_STATUS,
    TASK_STATUS_MAP
  } from '../status-config';
  import {
    TASK_ACTION_CONFIGS,
    getPrimaryTaskAction,
    getReverseTaskActions,
    getSecondaryTaskActions,
    shouldShowPlanRoute
  } from '../task-actions';
  import type { TaskActionConfig, TaskActionKey } from '../task-actions';
  import FinanceEdit from '../../task-finance/components/finance-edit.vue';
  import ActionAssignCarrier from '../../task-workbench/components/action-assign-carrier.vue';
  import ActionDispatch from '../../task-workbench/components/action-dispatch.vue';
  import ActionPlanRoute from '../../task-workbench/components/action-plan-route.vue';
  import ActionConfirmLoad from '../../task-workbench/components/action-confirm-load.vue';
  import ActionConfirmArrive from '../../task-workbench/components/action-confirm-arrive.vue';
  import ActionConfirmSign from '../../task-workbench/components/action-confirm-sign.vue';
  import ActionRevert from '../../task-workbench/components/action-revert.vue';
  import ActionRevertSign from '../../task-workbench/components/action-revert-sign.vue';
  import ActionForceCancel from '../../task-workbench/components/action-force-cancel.vue';
  import WaybillStatusSummary from './waybill-status-summary.vue';

  const props = defineProps<{ visible: boolean; taskId: number | null }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const task = ref<Task | null>(null);
  const segments = ref<TaskSegment[]>([]);
  const items = ref<TaskWaybillItem[]>([]);
  const loadingRecords = ref<TaskLoadingRecord[]>([]);
  const financeDocs = ref<TaskFinanceSummaryItem[]>([]);
  const activeTab = ref('segments');

  const costResult = ref<TaskCostResult | null>(null);
  const costLoading = ref(false);

  const costStatusTag = (
    s?: string
  ): { type: 'success' | 'warning' | 'info' | 'danger'; text: string } => {
    switch (s) {
      case 'success':
        return { type: 'success', text: '计算成功' };
      case 'partial':
        return { type: 'warning', text: '部分成功' };
      case 'locked':
        return { type: 'info', text: '已锁定' };
      default:
        return { type: 'danger', text: '异常' };
    }
  };

  const loadCostResult = async (id: number) => {
    try {
      costResult.value = await getTaskCostResult(id);
    } catch (_) {
      costResult.value = null;
    }
  };

  const recalcCost = async () => {
    if (!task.value?.id) return;
    costLoading.value = true;
    try {
      costResult.value = await recalculateTaskCost(task.value.id);
      EleMessage.success({ message: '成本已重算', plain: true });
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '重算失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      costLoading.value = false;
    }
  };

  const carrierFreightResult = ref<CarrierFreightResult | null>(null);
  const carrierFreightLoading = ref(false);

  const carrierBillingModeText = (m?: number | null) => {
    if (m === 1) return '单公里';
    if (m === 2) return '整单价';
    return '台单价';
  };

  const carrierFreightBrandModel = (row: CarrierFreightItem) => {
    const b = row.vehicleBrand?.trim();
    const m = row.vehicleModel?.trim();
    if (!b && !m) return '不限';
    return `${b || '不限'}/${m || '不限'}`;
  };

  const loadCarrierFreightResult = async (id: number) => {
    try {
      carrierFreightResult.value =
        (await getTaskCarrierFreightResult(id)) ?? null;
    } catch (_) {
      carrierFreightResult.value = null;
    }
  };

  const recalcCarrierFreight = async () => {
    if (!task.value?.id) return;
    carrierFreightLoading.value = true;
    try {
      carrierFreightResult.value =
        (await recalculateTaskCarrierFreight(task.value.id)) ?? null;
      EleMessage.success({ message: '承运运费已重算', plain: true });
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '重算失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      carrierFreightLoading.value = false;
    }
  };

  const orderNoOf = (orderId?: number | null): string | number => {
    if (!orderId) return '--';
    const seg = segments.value.find((s) => s.id === orderId);
    return seg?.orderNo ?? seg?.segmentNo ?? '--';
  };
  const DOC_TYPE_LABEL: Record<number, { label: string; type: string }> = {
    1: { label: '预付单', type: 'primary' },
    2: { label: '补款单', type: 'warning' },
    3: { label: '结算单', type: 'success' }
  };
  const FIN_STATUS_LABEL: Record<number, { label: string; type: string }> = {
    0: { label: '草稿', type: 'info' },
    1: { label: '待审批', type: 'warning' },
    2: { label: '已审批', type: 'primary' },
    3: { label: '已支付', type: 'success' },
    4: { label: '已撤销', type: 'danger' }
  };

  const formatAmount = (v?: number | null) => {
    if (v === null || v === undefined) return '--';
    return Number(v).toFixed(2);
  };

  watch(
    () => [props.visible, props.taskId] as const,
    async ([v, id]) => {
      if (v && id) {
        await load(id);
      }
    }
  );

  const load = async (id: number) => {
    loading.value = true;
    try {
      const [t, segs, its, fins, recs] = await Promise.all([
        getTask(id),
        listTaskSegments(id),
        listTaskWaybillItems(id),
        listTaskFinanceSummary(id),
        listLoadingRecords(id).catch(() => [] as TaskLoadingRecord[])
      ]);
      task.value = t;
      segments.value = segs;
      items.value = its;
      financeDocs.value = fins;
      loadingRecords.value = recs;
      loadCostResult(id);
      if (t?.carrierType === CARRIER_TYPE.CARRIER) {
        loadCarrierFreightResult(id);
      } else {
        carrierFreightResult.value = null;
      }
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const statusStep = computed(() => {
    const s = task.value?.status ?? TASK_STATUS.PENDING_DISPATCH;
    if (s === TASK_STATUS.CANCELLED) return 0;
    // 7 步：待分配 / 待派车 / 已派车 / 已装车 / 在途 / 已到达 / 已签收
    // 已关闭：超过已签收，整条时间轴标 finish
    const map: Record<number, number> = {
      [TASK_STATUS.PENDING_ASSIGN]: 0,
      [TASK_STATUS.PENDING_DISPATCH]: 1,
      [TASK_STATUS.DISPATCHED]: 2,
      [TASK_STATUS.LOADED]: 3,
      [TASK_STATUS.ON_WAY]: 4,
      [TASK_STATUS.ARRIVED]: 5,
      [TASK_STATUS.SIGNED]: 6,
      [TASK_STATUS.CLOSED]: 7
    };
    return map[s] ?? 0;
  });

  // ============================================
  // 语义化动作
  // ============================================
  const primaryAction = computed(() =>
    getPrimaryTaskAction(task.value?.status)
  );
  const secondaryActions = computed(() =>
    getSecondaryTaskActions(task.value?.status)
  );
  const reverseActions = computed(() =>
    getReverseTaskActions(task.value?.status)
  );

  const actionVisible = reactive({
    'assign-carrier': false,
    dispatch: false,
    'plan-route': false,
    'confirm-load': false,
    'confirm-arrive': false,
    'confirm-sign': false,
    revert: false,
    'revert-sign': false,
    'force-cancel': false
  });
  const revertActionKey = ref<TaskActionKey | null>(null);

  const planRouteAction = TASK_ACTION_CONFIGS['plan-route'];
  const showPlanRoute = computed(() =>
    task.value ? shouldShowPlanRoute(task.value) : false
  );

  const financeInitDocType = ref<number | undefined>(undefined);
  const financeInitIsFinal = ref<number | undefined>(undefined);

  const triggerAction = async (act: TaskActionConfig) => {
    if (!task.value?.id) return;
    if (act.dialog === 'revert') {
      revertActionKey.value = act.key;
      actionVisible.revert = true;
      return;
    }
    if (act.dialog) {
      actionVisible[act.dialog] = true;
      return;
    }
    if (act.openSettlement) {
      // 生成结算单 → 打开费用单创建并预填类型=结算单 + is_final=1
      financeInitDocType.value = 3;
      financeInitIsFinal.value = 1;
      editingFinanceId.value = null;
      financeEditVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction(act);
    }
  };

  const runConfirmAction = async (act: TaskActionConfig) => {
    if (!task.value?.id) return;
    const confirmMessages: Record<string, string> = {
      depart: `确认任务单「${task.value.taskNo}」已出发？将推进到「在途」状态。`,
      close: `确认关闭任务单「${task.value.taskNo}」？关闭后不可再变更状态。`
    };
    try {
      await ElMessageBox.confirm(
        confirmMessages[act.key] || `确认执行「${act.label}」？`,
        '操作确认',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    const targetStatus =
      act.key === 'depart' ? 3 : act.key === 'close' ? 7 : null;
    if (targetStatus === null) return;
    try {
      const updated = await updateTaskStatus(task.value.id, {
        status: targetStatus
      });
      task.value = updated;
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      await reload();
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const reload = async () => {
    if (task.value?.id) await load(task.value.id);
  };

  const onActionDone = async () => {
    await reload();
    emit('done');
  };

  /** 派车成功后：若自有车且尚未规划路线，引导立即规划 */
  const onDispatchDone = async () => {
    await reload();
    emit('done');
    if (!task.value) return;
    const t = task.value;
    if (t.carrierType === CARRIER_TYPE.SELF && (t.segmentCount ?? 0) === 0) {
      try {
        await ElMessageBox.confirm(
          '已派车成功。该任务是自有车且尚未规划运输路线，建议立即规划（含起终点、里程）。',
          '继续规划路线？',
          {
            type: 'info',
            confirmButtonText: '立即规划',
            cancelButtonText: '稍后再说'
          }
        );
        actionVisible['plan-route'] = true;
      } catch {
        // 用户选择稍后再说，忽略
      }
    }
  };

  // ============================================
  // 费用单创建/编辑
  // ============================================
  const financeEditVisible = ref(false);
  const editingFinanceId = ref<number | null>(null);

  const openFinanceEdit = (row: TaskFinanceSummaryItem | null) => {
    editingFinanceId.value = row?.id ?? null;
    financeInitDocType.value = undefined;
    financeInitIsFinal.value = undefined;
    financeEditVisible.value = true;
  };

  const onFinanceDone = async () => {
    if (task.value?.id) {
      await load(task.value.id);
    }
    emit('done');
  };
</script>

<style lang="scss" scoped>
  .task-detail {
    padding: 0 4px;
    &__header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }
    &__no {
      font-size: 18px;
      font-weight: 600;
    }
    &__name {
      color: #666;
      margin-top: 4px;
    }
    &__actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    &__steps {
      margin: 8px 0 16px;
    }
  }

  .dispatch-time-cell {
    line-height: 1.6;
    font-size: 12px;
  }

  .cost-tab-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }

  .cost-total {
    font-weight: 600;
    font-size: 15px;
  }

  .cost-tab-meta {
    margin-top: 8px;
    font-size: 12px;
  }

  .loading-records-timeline {
    padding: 8px 0;
  }

  .loading-rec-card {
    background: var(--el-fill-color-light);
    padding: 8px 12px;
    border-radius: 4px;

    &__head {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    &__loc {
      font-weight: 500;
    }

    &__qty {
      flex: 1;
    }

    &__items {
      margin-top: 6px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      font-size: 12px;
    }

    &__photos {
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    &__photo {
      width: 64px;
      height: 64px;
      border-radius: 4px;
      overflow: hidden;
      border: 1px solid var(--el-border-color);
    }

    &__remark {
      margin-top: 6px;
      font-size: 12px;
      color: var(--el-text-color-regular);
    }
  }
</style>
