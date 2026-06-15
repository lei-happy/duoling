<template>
  <ele-page>
    <!-- 合规看板汇总 -->
    <el-row :gutter="12" class="compliance-stats">
      <el-col :lg="6" :md="12" :xs="12">
        <ele-card>
          <div class="stat-item">
            <div class="stat-label">待处理合计</div>
            <div class="stat-value">{{ summary.total }}</div>
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="6" :md="12" :xs="12">
        <ele-card>
          <div class="stat-item">
            <div class="stat-label">已过期</div>
            <div class="stat-value danger">{{ summary.expired }}</div>
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="6" :md="12" :xs="12">
        <ele-card>
          <div class="stat-item">
            <div class="stat-label">临界（7天内）</div>
            <div class="stat-value warning">{{ summary.critical }}</div>
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="6" :md="12" :xs="12">
        <ele-card>
          <div class="stat-item">
            <div class="stat-label">预警</div>
            <div class="stat-value primary">{{ summary.warning }}</div>
          </div>
        </ele-card>
      </el-col>
    </el-row>

    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="级别">
          <el-select
            v-model="where.level"
            placeholder="全部"
            clearable
            style="width: 130px"
          >
            <el-option label="已过期" value="expired" />
            <el-option label="临界" value="critical" />
            <el-option label="预警" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item label="主体">
          <el-select
            v-model="where.subjectType"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="自有驾驶员" value="driver" />
            <el-option label="自有车辆" value="vehicle" />
            <el-option label="社会运力-司机" value="social_driver" />
            <el-option label="社会运力-车辆" value="social_vehicle" />
          </el-select>
        </el-form-item>
        <el-form-item label="证照">
          <el-select
            v-model="where.docType"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="驾驶证" value="driver_license" />
            <el-option label="从业资格证" value="qualification" />
            <el-option label="保险" value="insurance" />
            <el-option label="年检" value="inspection" />
            <el-option label="道路运输证" value="transport_license" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="where.status" style="width: 120px">
            <el-option label="待处理" value="open" />
            <el-option label="已忽略" value="dismissed" />
            <el-option label="已消除" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键字">
          <el-input
            v-model="where.keyword"
            placeholder="姓名/车牌"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        cache-key="ComplianceAlertTable"
      >
        <template #subjectName="{ row }">
          <span>{{ row.subjectName }}</span>
          <span v-if="row.subjectRef" class="subject-ref">
            （{{ row.subjectRef }}）
          </span>
        </template>
        <template #daysLeft="{ row }">
          <span v-if="row.daysLeft < 0" class="days danger">
            已过期 {{ -row.daysLeft }} 天
          </span>
          <span v-else :class="['days', row.daysLeft <= 7 ? 'warning' : '']">
            剩 {{ row.daysLeft }} 天
          </span>
        </template>
        <template #level="{ row }">
          <el-tag v-if="row.level === 'expired'" type="danger" size="small">
            已过期
          </el-tag>
          <el-tag
            v-else-if="row.level === 'critical'"
            type="warning"
            size="small"
          >
            临界
          </el-tag>
          <el-tag v-else type="info" size="small">预警</el-tag>
        </template>
        <template #action="{ row }">
          <el-button
            v-if="row.status === 'open'"
            type="primary"
            link
            @click="onDismiss(row)"
          >
            忽略
          </el-button>
          <span v-else style="color: var(--el-text-color-secondary)">-</span>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { formatDate } from '@/utils/date-util';
  import {
    pageComplianceAlerts,
    getComplianceSummary,
    dismissComplianceAlert
  } from '@/api/capacity/compliance';
  import type {
    ComplianceAlertParam,
    ComplianceSummary
  } from '@/api/capacity/compliance/model';

  defineOptions({ name: 'CapacityCompliance' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const summary = reactive<ComplianceSummary>({
    total: 0,
    expired: 0,
    critical: 0,
    warning: 0,
    bySubjectType: {},
    byDocType: {}
  });

  const where = reactive<
    Pick<
      ComplianceAlertParam,
      'level' | 'subjectType' | 'docType' | 'status' | 'keyword'
    >
  >({
    level: void 0,
    subjectType: void 0,
    docType: void 0,
    status: 'open',
    keyword: ''
  });

  const columns = ref<Columns>([
    { prop: 'subjectTypeLabel', label: '主体类型', width: 120 },
    { prop: 'subjectName', label: '名称', minWidth: 150, slot: 'subjectName' },
    { prop: 'docTypeLabel', label: '证照类型', width: 120 },
    {
      prop: 'docNo',
      label: '证照号',
      minWidth: 140,
      formatter: (row) => row.docNo ?? '-'
    },
    {
      prop: 'expireDate',
      label: '到期日',
      width: 120,
      align: 'center',
      formatter: (row) => formatDate(row.expireDate)
    },
    {
      prop: 'daysLeft',
      label: '剩余',
      width: 120,
      align: 'center',
      slot: 'daysLeft'
    },
    { prop: 'level', label: '级别', width: 90, align: 'center', slot: 'level' },
    {
      prop: 'action',
      label: '操作',
      width: 90,
      align: 'center',
      slot: 'action'
    }
  ]);

  const loadSummary = async () => {
    try {
      const res = await getComplianceSummary();
      if (res) {
        summary.total = res.total ?? 0;
        summary.expired = res.expired ?? 0;
        summary.critical = res.critical ?? 0;
        summary.warning = res.warning ?? 0;
        summary.bySubjectType = res.bySubjectType ?? {};
        summary.byDocType = res.byDocType ?? {};
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageComplianceAlerts({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? res?.total ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.({ page: 1 });
    loadSummary();
  };

  const resetSearch = () => {
    where.level = void 0;
    where.subjectType = void 0;
    where.docType = void 0;
    where.status = 'open';
    where.keyword = '';
    reload();
  };

  const onDismiss = (row: any) => {
    ElMessageBox.confirm(
      `确定忽略「${row.subjectName} - ${row.docTypeLabel}」的到期预警吗？`,
      '系统提示',
      { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
    )
      .then(async () => {
        const loading = EleMessage.loading({
          message: '请稍后..',
          plain: true
        });
        try {
          await dismissComplianceAlert(row.id);
          loading.close();
          EleMessage.success({ message: '已忽略', plain: true });
          reload();
        } catch (e: any) {
          loading.close();
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => void 0);
  };

  onMounted(() => {
    loadSummary();
  });
</script>

<style scoped>
  .compliance-stats {
    margin-bottom: 12px;
  }

  .stat-item {
    text-align: center;
    padding: 6px 0;
  }

  .stat-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
  }

  .stat-value {
    font-size: 26px;
    font-weight: 600;
  }

  .stat-value.danger {
    color: var(--el-color-danger);
  }

  .stat-value.warning {
    color: var(--el-color-warning);
  }

  .stat-value.primary {
    color: var(--el-color-primary);
  }

  .subject-ref {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .days.danger {
    color: var(--el-color-danger);
    font-weight: 600;
  }

  .days.warning {
    color: var(--el-color-warning);
    font-weight: 600;
  }
</style>
