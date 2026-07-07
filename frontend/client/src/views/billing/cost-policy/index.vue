<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="成本政策" name="policy" />
        <el-tab-pane label="费用规则" name="fee" />
      </el-tabs>
    </ele-card>

    <template v-if="activeTab === 'policy'">
      <ele-card :body-style="{ paddingBottom: 0 }">
        <el-form :inline="true" @submit.prevent="">
          <el-form-item label="关键字">
            <el-input
              v-model="where.keyword"
              placeholder="政策编号/名称"
              clearable
              style="width: 180px"
              @keyup.enter="reload(1)"
            />
          </el-form-item>
          <el-form-item label="适用范围">
            <el-select
              v-model="where.scopeType"
              placeholder="全部"
              clearable
              style="width: 130px"
            >
              <el-option label="全局默认" :value="0" />
              <el-option label="指定承运商" :value="1" />
              <el-option label="指定司机" :value="2" />
              <el-option label="指定运力" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="where.status"
              placeholder="全部"
              clearable
              style="width: 110px"
            >
              <el-option label="草稿" :value="0" />
              <el-option label="生效" :value="1" />
              <el-option label="已过期" :value="2" />
              <el-option label="已终止" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="reload(1)">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </ele-card>

      <ele-card :body-style="{ paddingTop: '8px' }">
        <div class="toolbar">
          <el-button type="primary" @click="openEdit()">新增政策</el-button>
        </div>
        <el-table
          :data="list"
          v-loading="loading"
          border
          row-key="id"
          highlight-current-row
        >
          <el-table-column prop="policyNo" label="政策编号" min-width="140" />
          <el-table-column prop="policyName" label="政策名称" min-width="160" />
          <el-table-column label="适用范围" width="130" align="center">
            <template #default="{ row }">
              {{ scopeLabel(row.scopeType) }}
            </template>
          </el-table-column>
          <el-table-column label="承运类型" width="100" align="center">
            <template #default="{ row }">
              {{ carrierLabel(row.carrierType) }}
            </template>
          </el-table-column>
          <el-table-column label="规则数" width="90" align="center">
            <template #default="{ row }">
              {{ row.activeRuleCount ?? 0 }}/{{ row.ruleCount ?? 0 }}
            </template>
          </el-table-column>
          <el-table-column label="生效期" min-width="190" align="center">
            <template #default="{ row }">
              {{ row.effectiveDate }} ~ {{ row.expiryDate || '长期' }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTag(row.status).type" size="small">
                {{ statusTag(row.status).text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="230"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button link type="primary" @click="openDetail(row)">
                规则
              </el-button>
              <el-button link type="primary" @click="openEdit(row)">
                编辑
              </el-button>
              <el-button
                v-if="row.status === 0 || row.status === 3"
                link
                type="success"
                @click="doActivate(row)"
              >
                激活
              </el-button>
              <el-button
                v-if="row.status === 1"
                link
                type="warning"
                @click="doTerminate(row)"
              >
                终止
              </el-button>
              <el-button
                v-if="row.status !== 1"
                link
                type="danger"
                @click="doRemove(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pager">
          <el-pagination
            layout="total, prev, pager, next, sizes"
            :total="total"
            :current-page="page"
            :page-size="limit"
            :page-sizes="[10, 20, 50]"
            @current-change="onPageChange"
            @size-change="onSizeChange"
          />
        </div>
      </ele-card>
    </template>

    <ele-card v-else :body-style="{ paddingTop: '8px' }">
      <cost-rule-center :meta="meta" @open-policy="openPolicyFromRule" />
    </ele-card>

    <cost-policy-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload()"
    />
    <cost-policy-detail
      v-model:visible="detailVisible"
      :policy-id="detailPolicyId"
      :meta="meta"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import CostPolicyEdit from './components/cost-policy-edit.vue';
  import CostPolicyDetail from './components/cost-policy-detail.vue';
  import CostRuleCenter from './components/cost-rule-center.vue';
  import {
    pagePolicies,
    activatePolicy,
    terminatePolicy,
    removePolicy,
    getCostMeta
  } from '@/api/billing/cost-policy';
  import type {
    CostPolicy,
    CostPolicyParam,
    CostRuleWithPolicy,
    CostMeta
  } from '@/api/billing/cost-policy/model';

  defineOptions({ name: 'BillingCostPolicy' });

  const activeTab = ref<'policy' | 'fee'>('policy');

  const list = ref<CostPolicy[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(20);
  const loading = ref(false);
  const where = reactive<CostPolicyParam>({});

  const meta = ref<CostMeta>({ feeTypes: [], pricingMethods: [] });

  const editVisible = ref(false);
  const editData = ref<CostPolicy | null>(null);
  const detailVisible = ref(false);
  const detailPolicyId = ref<number | null>(null);

  const scopeLabel = (t: number) =>
    ({ 0: '全局默认', 1: '指定承运商', 2: '指定司机', 3: '指定运力' })[t] ??
    '-';
  const carrierLabel = (t?: number | null) =>
    t == null
      ? '不限'
      : ({ 1: '自有车', 2: '承运商', 3: '社会运力' }[t] ?? '-');
  const statusTag = (s?: number) => {
    switch (s) {
      case 1:
        return { type: 'success', text: '生效' };
      case 2:
        return { type: 'info', text: '已过期' };
      case 3:
        return { type: 'danger', text: '已终止' };
      default:
        return { type: 'warning', text: '草稿' };
    }
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      const res = await pagePolicies({
        ...where,
        page: page.value,
        limit: limit.value
      });
      const raw = res as {
        list?: CostPolicy[];
        total?: number;
        count?: number;
      };
      list.value = raw.list ?? [];
      total.value = raw.total ?? raw.count ?? 0;
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const reload = (toPage?: number) => {
    if (toPage) page.value = toPage;
    fetchData();
  };

  const resetSearch = () => {
    where.keyword = undefined;
    where.scopeType = undefined;
    where.status = undefined;
    reload(1);
  };

  const onPageChange = (p: number) => {
    page.value = p;
    fetchData();
  };
  const onSizeChange = (s: number) => {
    limit.value = s;
    page.value = 1;
    fetchData();
  };

  const openEdit = (row?: CostPolicy) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openDetail = (row: CostPolicy) => {
    detailPolicyId.value = row.id ?? null;
    detailVisible.value = true;
  };

  const openPolicyFromRule = (row: CostRuleWithPolicy) => {
    if (!row.policyId) return;
    detailPolicyId.value = row.policyId;
    detailVisible.value = true;
  };

  const doActivate = (row: CostPolicy) => {
    ElMessageBox.confirm(
      `确定激活政策「${row.policyName}」？激活后参与成本匹配。`,
      '系统提示',
      { type: 'info', draggable: true }
    )
      .then(async () => {
        const msg = await activatePolicy(row.id!);
        EleMessage.success({ message: msg, plain: true });
        reload();
      })
      .catch(() => {});
  };

  const doTerminate = (row: CostPolicy) => {
    ElMessageBox.confirm(`确定终止政策「${row.policyName}」？`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        const msg = await terminatePolicy(row.id!);
        EleMessage.success({ message: msg, plain: true });
        reload();
      })
      .catch(() => {});
  };

  const doRemove = (row: CostPolicy) => {
    ElMessageBox.confirm(`确定删除政策「${row.policyName}」？`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        const msg = await removePolicy(row.id!);
        EleMessage.success({ message: msg, plain: true });
        reload();
      })
      .catch(() => {});
  };

  onMounted(async () => {
    try {
      meta.value = await getCostMeta();
    } catch (_) {
      meta.value = { feeTypes: [], pricingMethods: [] };
    }
    fetchData();
  });
</script>

<style scoped>
  .toolbar {
    margin-bottom: 12px;
  }
  .pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
</style>
