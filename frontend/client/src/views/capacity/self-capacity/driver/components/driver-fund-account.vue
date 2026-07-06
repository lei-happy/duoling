<template>
  <el-drawer
    v-model="visible"
    :title="`资金账户 - ${driver?.name ?? ''}`"
    size="720px"
    append-to-body
    :destroy-on-close="true"
    @open="onOpen"
  >
    <div v-loading="loading" class="fund-account">
      <!-- 余额卡片 -->
      <div class="fund-account__cards">
        <div class="fund-account__card fund-account__card--main">
          <div class="fund-account__label">当前余额</div>
          <div
            class="fund-account__balance"
            :class="{
              'is-positive': balanceNum > 0,
              'is-negative': balanceNum < 0
            }"
          >
            {{ formatMoney(account?.balance) }}
          </div>
          <div class="fund-account__hint">{{ balanceHint }}</div>
        </div>
        <div class="fund-account__card">
          <div class="fund-account__label">累计入账</div>
          <div class="fund-account__num is-positive">
            +{{ formatMoney(account?.totalIn) }}
          </div>
        </div>
        <div class="fund-account__card">
          <div class="fund-account__label">累计出账</div>
          <div class="fund-account__num is-negative">
            -{{ formatMoney(account?.totalOut) }}
          </div>
        </div>
        <div class="fund-account__card">
          <div class="fund-account__label">账户状态</div>
          <div class="fund-account__num">
            <el-tag
              :type="
                account?.status === FUND_ACCOUNT_STATUS.NORMAL
                  ? 'success'
                  : 'danger'
              "
              size="small"
              :disable-transitions="true"
            >
              {{
                account?.status === FUND_ACCOUNT_STATUS.NORMAL ? '正常' : '冻结'
              }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="fund-account__toolbar">
        <div>
          <el-button
            v-if="canPost"
            type="primary"
            :disabled="account?.status !== FUND_ACCOUNT_STATUS.NORMAL"
            @click="openPost"
          >
            记账
          </el-button>
          <template v-if="canFreeze">
            <el-button
              v-if="account?.status === FUND_ACCOUNT_STATUS.NORMAL"
              @click="toggleStatus(FUND_ACCOUNT_STATUS.FROZEN)"
            >
              冻结账户
            </el-button>
            <el-button
              v-else
              type="warning"
              @click="toggleStatus(FUND_ACCOUNT_STATUS.NORMAL)"
            >
              解冻账户
            </el-button>
          </template>
        </div>
        <el-select
          v-model="filterBizType"
          placeholder="全部类型"
          clearable
          style="width: 150px"
          @change="loadTransactions(1)"
        >
          <el-option
            v-for="opt in bizTypeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>

      <!-- 流水表格 -->
      <el-table :data="transactions" size="small" border stripe>
        <el-table-column prop="createdAt" label="时间" width="150">
          <template #default="{ row }">
            {{ formatDateTime(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="bizType" label="类型" width="90">
          <template #default="{ row }">
            {{ bizTypeLabel(row.bizType) }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">
            <span :class="row.delta >= 0 ? 'is-positive' : 'is-negative'">
              {{ row.delta >= 0 ? '+' : '-' }}{{ formatMoney(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="变动后余额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.balanceAfter) }}
          </template>
        </el-table-column>
        <el-table-column prop="operatorName" label="操作人" width="90">
          <template #default="{ row }">
            {{ row.operatorName || '—' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="remark"
          label="备注"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>
      <div class="fund-account__pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          background
          small
          @current-change="loadTransactions"
        />
      </div>
    </div>

    <!-- 记账弹窗 -->
    <el-dialog
      v-model="postVisible"
      title="资金账户记账"
      width="460px"
      append-to-body
      align-center
      :close-on-click-modal="false"
    >
      <el-form
        ref="postFormRef"
        :model="postForm"
        :rules="postRules"
        label-width="90px"
      >
        <el-form-item label="业务类型" prop="bizType">
          <el-select v-model="postForm.bizType" style="width: 100%">
            <el-option
              v-for="opt in bizTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="postForm.bizType === FUND_BIZ_TYPE.ADJUST"
          label="方向"
          prop="direction"
        >
          <el-radio-group v-model="postForm.direction">
            <el-radio :value="FUND_DIRECTION.IN">入账（+）</el-radio>
            <el-radio :value="FUND_DIRECTION.OUT">出账（-）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="postForm.amount"
            :min="0.01"
            :precision="2"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="postForm.remark"
            type="textarea"
            :rows="2"
            placeholder="人工调整必填，且不少于 5 字"
          />
        </el-form-item>
      </el-form>
      <div class="fund-account__effect">
        本次将使余额
        <strong :class="postDelta >= 0 ? 'is-positive' : 'is-negative'">
          {{ postDelta >= 0 ? '增加' : '减少' }} {{ formatMoney(postAmountAbs) }}
        </strong>
      </div>
      <template #footer>
        <el-button @click="postVisible = false">取消</el-button>
        <el-button type="primary" :loading="posting" @click="submitPost">
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, computed, reactive } from 'vue';
  import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus';
  import {
    getDriverFundAccount,
    listDriverFundTransactions,
    postDriverFundTransaction,
    toggleFundAccountStatus
  } from '@/api/capacity/self-capacity/driver';
  import type {
    Driver,
    DriverFundAccount,
    DriverFundTransaction
  } from '@/api/capacity/self-capacity/driver/model';
  import { formatDateTime } from '@/utils/date-util';
  import { usePermission } from '@/utils/use-permission';
  import {
    FUND_ACCOUNT_STATUS,
    FUND_BIZ_TYPE,
    FUND_DIRECTION,
    MANUAL_BIZ_TYPE_OPTIONS,
    MANUAL_REMARK_MIN_LEN,
    fundBizTypeLabel,
    resolveManualSign
  } from '../fund-account.constants';

  const { hasPermission } = usePermission();
  const canPost = computed(() =>
    hasPermission('capacity:self_capacity:driver:fund-post')
  );
  const canFreeze = computed(() =>
    hasPermission('capacity:self_capacity:driver:fund-freeze')
  );

  const props = defineProps<{
    visible: boolean;
    driver: Driver | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  const visible = computed({
    get: () => props.visible,
    set: (v) => emit('update:visible', v)
  });

  const bizTypeOptions = MANUAL_BIZ_TYPE_OPTIONS;
  const bizTypeLabel = fundBizTypeLabel;

  const loading = ref(false);
  const account = ref<DriverFundAccount | null>(null);
  const transactions = ref<DriverFundTransaction[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = 15;
  const filterBizType = ref<number | undefined>(undefined);

  const balanceNum = computed(() => Number(account.value?.balance ?? 0));
  const balanceHint = computed(() => {
    if (balanceNum.value > 0) return '公司欠司机（司机可提取）';
    if (balanceNum.value < 0) return '司机欠公司（预付未核销）';
    return '两清';
  });

  const formatMoney = (v: number | string | undefined) => {
    const n = Math.abs(Number(v ?? 0));
    return n.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const loadAccount = async () => {
    if (!props.driver?.id) return;
    account.value = await getDriverFundAccount(props.driver.id);
  };

  const loadTransactions = async (p?: number) => {
    if (!props.driver?.id) return;
    if (p) page.value = p;
    const res = await listDriverFundTransactions(props.driver.id, {
      page: page.value,
      limit: pageSize,
      bizType: filterBizType.value
    });
    transactions.value = res.list ?? [];
    total.value = res.total ?? 0;
  };

  const onOpen = async () => {
    loading.value = true;
    page.value = 1;
    filterBizType.value = undefined;
    try {
      await loadAccount();
      await loadTransactions(1);
    } catch (e: any) {
      ElMessage.error(e?.message ?? '加载资金账户失败');
    } finally {
      loading.value = false;
    }
  };

  const toggleStatus = async (status: number) => {
    if (!account.value?.id) return;
    const label = status === FUND_ACCOUNT_STATUS.FROZEN ? '冻结' : '解冻';
    try {
      await ElMessageBox.confirm(`确定${label}该资金账户吗？`, '系统提示', {
        type: 'warning'
      });
    } catch {
      return;
    }
    try {
      account.value = await toggleFundAccountStatus(account.value.id, status);
      ElMessage.success(`${label}成功`);
    } catch (e: any) {
      ElMessage.error(e?.message ?? '操作失败');
    }
  };

  // 记账
  const postVisible = ref(false);
  const posting = ref(false);
  const postFormRef = ref<FormInstance>();
  const postForm = reactive<{
    bizType: number;
    amount: number | undefined;
    direction: number | undefined;
    remark: string;
  }>({
    bizType: FUND_BIZ_TYPE.PREPAY_REGISTER,
    amount: undefined,
    direction: FUND_DIRECTION.IN,
    remark: ''
  });

  const postRules = {
    bizType: [{ required: true, message: '请选择业务类型', trigger: 'change' }],
    amount: [{ required: true, message: '请输入金额', trigger: 'blur' }]
  };

  const postAmountAbs = computed(() => Number(postForm.amount ?? 0));
  const postDelta = computed(
    () =>
      resolveManualSign(postForm.bizType, postForm.direction) *
      postAmountAbs.value
  );

  const openPost = () => {
    postForm.bizType = FUND_BIZ_TYPE.PREPAY_REGISTER;
    postForm.amount = undefined;
    postForm.direction = FUND_DIRECTION.IN;
    postForm.remark = '';
    postVisible.value = true;
  };

  const submitPost = async () => {
    if (!props.driver?.id) return;
    await postFormRef.value?.validate().catch(() => Promise.reject());
    if (!postForm.amount || postForm.amount <= 0) {
      ElMessage.warning('金额必须大于 0');
      return;
    }
    if (
      postForm.bizType === FUND_BIZ_TYPE.ADJUST &&
      postForm.remark.trim().length < MANUAL_REMARK_MIN_LEN
    ) {
      ElMessage.warning(`人工调整必须填写不少于 ${MANUAL_REMARK_MIN_LEN} 字的备注`);
      return;
    }
    posting.value = true;
    try {
      await postDriverFundTransaction(props.driver.id, {
        bizType: postForm.bizType,
        amount: postForm.amount,
        direction:
          postForm.bizType === FUND_BIZ_TYPE.ADJUST
            ? postForm.direction
            : undefined,
        remark: postForm.remark || undefined
      });
      ElMessage.success('记账成功');
      postVisible.value = false;
      await loadAccount();
      await loadTransactions(1);
    } catch (e: any) {
      ElMessage.error(e?.message ?? '记账失败');
    } finally {
      posting.value = false;
    }
  };
</script>

<style scoped>
  .fund-account__cards {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 16px;
  }
  .fund-account__card {
    padding: 12px 14px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background: var(--el-fill-color-lighter);
  }
  .fund-account__card--main {
    background: var(--el-color-primary-light-9);
  }
  .fund-account__label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
  }
  .fund-account__balance {
    font-size: 24px;
    font-weight: 600;
  }
  .fund-account__num {
    font-size: 16px;
    font-weight: 600;
  }
  .fund-account__hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
  }
  .fund-account__toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .fund-account__pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
  .fund-account__effect {
    margin-top: 4px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
  .is-positive {
    color: var(--el-color-success);
  }
  .is-negative {
    color: var(--el-color-danger);
  }
</style>
