<template>
  <el-dialog
    title="社会运力详情"
    :model-value="visible"
    width="860px"
    draggable
    align-center
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <div v-loading="loading" class="sc-detail">
      <template v-if="detail">
        <div class="sc-detail__head">
          <h3>{{ detail.socialCode }} · {{ detail.driverName }}</h3>
          <div class="sc-detail__tags">
            <el-tag size="small" :type="approvalTagType(detail.approvalStatus)">
              {{ approvalLabel(detail.approvalStatus) }}
            </el-tag>
            <el-tag
              v-if="detail.approvalStatus === 2"
              size="small"
              :type="statusTagType(detail.status)"
            >
              {{ statusLabel(detail.status) }}
            </el-tag>
          </div>
        </div>

        <el-descriptions title="基础信息" :column="2" border size="small">
          <el-descriptions-item label="社会运力编号">{{ detail.socialCode }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ detail.source || '—' }}</el-descriptions-item>
          <el-descriptions-item label="来源备注">{{ detail.sourceRemark || '—' }}</el-descriptions-item>
          <el-descriptions-item label="评级">
            {{ detail.ratingLevel ? ratingLabel(detail.ratingLevel) : '未评级' }}
          </el-descriptions-item>
          <el-descriptions-item label="累计承运" :span="2">
            {{ detail.orderCount ?? 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detail.remark || '—' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-descriptions
          title="车辆信息"
          :column="2"
          border
          size="small"
          class="sc-detail__block"
        >
          <el-descriptions-item label="车牌号">{{ detail.plateNumber }}</el-descriptions-item>
          <el-descriptions-item label="车辆类型">{{ detail.vehicleTypeLabel || '—' }}</el-descriptions-item>
          <el-descriptions-item label="品牌型号">
            {{ [detail.vehicle?.brand, detail.vehicle?.model].filter(Boolean).join(' / ') || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="VIN">{{ detail.vehicle?.vin || '—' }}</el-descriptions-item>
          <el-descriptions-item label="核定载重">
            {{ detail.vehicle?.loadCapacity ? `${detail.vehicle.loadCapacity} 吨` : '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="核定容积">
            {{ detail.vehicle?.volumeCapacity ? `${detail.vehicle.volumeCapacity} m³` : '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="年检到期">{{ detail.vehicle?.inspectionExpire || '—' }}</el-descriptions-item>
          <el-descriptions-item label="保险到期">{{ detail.vehicle?.insuranceExpire || '—' }}</el-descriptions-item>
          <el-descriptions-item label="道路运输证号">{{ detail.vehicle?.transportLicenseNo || '—' }}</el-descriptions-item>
          <el-descriptions-item label="道路运输证有效期">{{ detail.vehicle?.transportLicenseExpire || '—' }}</el-descriptions-item>
          <el-descriptions-item v-if="detail.vehicle?.hasTrailer === 1" label="挂车信息" :span="2">
            {{ detail.vehicle.trailerPlate }} / {{ detail.vehicle.trailerType }} /
            {{ detail.vehicle.trailerLoadCapacity }} 吨
          </el-descriptions-item>
        </el-descriptions>

        <el-descriptions
          title="司机信息"
          :column="2"
          border
          size="small"
          class="sc-detail__block"
        >
          <el-descriptions-item label="姓名">{{ detail.driver?.name }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ detail.driver?.phone }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ detail.driver?.idCard || '—' }}</el-descriptions-item>
          <el-descriptions-item label="性别">
            {{ detail.driver?.gender === 1 ? '男' : detail.driver?.gender === 2 ? '女' : '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="驾驶证号">
            {{ detail.driver?.licenseNo || '—' }}（{{ detail.driver?.licenseType || '—' }}）
          </el-descriptions-item>
          <el-descriptions-item label="驾驶证有效期">{{ detail.driver?.licenseExpire || '—' }}</el-descriptions-item>
          <el-descriptions-item label="从业资格证号">{{ detail.driver?.qualificationNo || '—' }}</el-descriptions-item>
          <el-descriptions-item label="从业资格证有效期">{{ detail.driver?.qualificationExpire || '—' }}</el-descriptions-item>
          <el-descriptions-item label="紧急联系人">{{ detail.driver?.emergencyContact || '—' }}</el-descriptions-item>
          <el-descriptions-item label="紧急联系电话">{{ detail.driver?.emergencyPhone || '—' }}</el-descriptions-item>
          <el-descriptions-item label="居住地址" :span="2">{{ detail.driver?.homeAddress || '—' }}</el-descriptions-item>
        </el-descriptions>

        <div class="sc-detail__block">
          <h4>结算账户</h4>
          <el-table :data="detail.accounts ?? []" border size="small" class="sc-detail__table">
            <el-table-column label="默认" width="70" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.isDefault === 1" size="small" type="success">默认</el-tag>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column label="账户类型" width="100">
              <template #default="{ row }">{{ accountTypeLabel(row.accountType) }}</template>
            </el-table-column>
            <el-table-column prop="accountName" label="户名" min-width="120" />
            <el-table-column prop="accountNo" label="账号" min-width="140" />
            <el-table-column prop="bankName" label="开户行" min-width="120" />
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.status === 1" size="small" type="success">启用</el-tag>
                <el-tag v-else size="small" type="info">停用</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="sc-detail__block">
          <h4>审核 / 状态流水</h4>
          <el-empty
            v-if="!auditList.length"
            description="暂无流水"
            :image-size="60"
          />
          <el-timeline v-else>
            <el-timeline-item
              v-for="a in auditList"
              :key="a.id"
              :type="auditTimelineType(a.action)"
              :timestamp="a.createdAt"
            >
              <div class="sc-detail__audit">
                <strong>{{ actionLabel(a.action) }}</strong>
                <span v-if="a.operatorName"> · {{ a.operatorName }}</span>
                <div v-if="a.remark" class="sc-detail__audit-remark">{{ a.remark }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </template>
    </div>

    <template #footer>
      <slot name="footer" :detail="detail">
        <el-button @click="updateVisible(false)">关闭</el-button>
      </slot>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    getSocialCapacity,
    listAuditHistory
  } from '@/api/capacity/social-capacity/list';
  import type {
    SocialCapacityDetail,
    SocialCapacityAudit
  } from '@/api/capacity/social-capacity/list/model';

  const props = defineProps<{
    visible: boolean;
    socialCapacityId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const detail = ref<SocialCapacityDetail | null>(null);
  const auditList = ref<SocialCapacityAudit[]>([]);
  const loading = ref(false);

  const onOpen = () => {
    if (props.socialCapacityId) reload(props.socialCapacityId);
  };

  watch(
    () => props.socialCapacityId,
    (id) => {
      if (id && props.visible) reload(id);
    }
  );

  const reload = async (id: number) => {
    loading.value = true;
    try {
      const [d, h] = await Promise.all([
        getSocialCapacity(id),
        listAuditHistory(id)
      ]);
      detail.value = d;
      auditList.value = h ?? [];
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '加载失败', plain: true });
      detail.value = null;
      auditList.value = [];
    } finally {
      loading.value = false;
    }
  };

  const approvalLabel = (s?: number) =>
    s === 0
      ? '草稿'
      : s === 1
        ? '待审核'
        : s === 2
          ? '已通过'
          : s === 3
            ? '已驳回'
            : '—';
  const approvalTagType = (
    s?: number
  ): 'info' | 'primary' | 'success' | 'danger' =>
    s === 1 ? 'primary' : s === 2 ? 'success' : s === 3 ? 'danger' : 'info';

  const statusLabel = (s?: number) =>
    s === 0
      ? '未生效'
      : s === 1
        ? '正常'
        : s === 2
          ? '停用'
          : s === 3
            ? '黑名单'
            : '—';
  const statusTagType = (
    s?: number
  ): 'info' | 'success' | 'warning' | 'danger' =>
    s === 1 ? 'success' : s === 2 ? 'warning' : s === 3 ? 'danger' : 'info';

  const ratingLabel = (level?: number) =>
    level === 1 ? 'A' : level === 2 ? 'B' : level === 3 ? 'C' : level === 4 ? 'D' : '—';

  const accountTypeLabel = (t?: number) =>
    t === 1
      ? '银行卡'
      : t === 2
        ? '支付宝'
        : t === 3
          ? '微信'
          : t === 4
            ? '其他'
            : '—';

  const ACTION_LABEL: Record<number, string> = {
    1: '提交审核',
    2: '审核通过',
    3: '审核驳回',
    4: '启用',
    5: '停用',
    6: '加入黑名单',
    7: '移出黑名单',
    8: '撤回审核'
  };
  const actionLabel = (a?: number) => (a ? ACTION_LABEL[a] ?? '—' : '—');

  const auditTimelineType = (
    a?: number
  ): 'primary' | 'success' | 'warning' | 'danger' | 'info' =>
    a === 2 || a === 4 || a === 7
      ? 'success'
      : a === 3 || a === 6
        ? 'danger'
        : a === 5 || a === 8
          ? 'warning'
          : 'primary';

  defineExpose({ reload });
</script>

<style scoped>
  .sc-detail {
    min-height: 200px;
  }
  .sc-detail__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }
  .sc-detail__head h3 {
    margin: 0;
    font-size: 16px;
  }
  .sc-detail__tags {
    display: flex;
    gap: 6px;
  }
  .sc-detail__block {
    margin-top: 16px;
  }
  .sc-detail__block h4 {
    margin: 0 0 8px;
    font-size: 14px;
    color: var(--el-color-info-dark-2);
  }
  .sc-detail__table {
    width: 100%;
  }
  .sc-detail__audit {
    line-height: 1.6;
  }
  .sc-detail__audit-remark {
    color: var(--el-text-color-regular);
    font-size: 12px;
    margin-top: 4px;
  }
</style>
