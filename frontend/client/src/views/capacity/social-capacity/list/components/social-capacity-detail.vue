<template>
  <el-dialog
    title="社会运力详情"
    :model-value="visible"
    width="860px"
    draggable
    align-center
    class="sc-detail-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
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

        <el-tabs v-model="activeTab" class="sc-detail-tabs">
          <el-tab-pane label="基础信息" name="basic">
            <div class="sc-detail-tab-pane">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="社会运力编号">{{ detail.socialCode }}</el-descriptions-item>
                <el-descriptions-item label="来源">{{ detail.source || '—' }}</el-descriptions-item>
                <el-descriptions-item label="来源备注">{{ detail.sourceRemark || '—' }}</el-descriptions-item>
                <el-descriptions-item label="评级">
                  {{ detail.ratingLevel ? ratingLabel(detail.ratingLevel) : '未评级' }}
                </el-descriptions-item>
                <el-descriptions-item label="累计承运">
                  {{ detail.orderCount ?? 0 }} 次
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ detail.createdAt || '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="备注" :span="2">
                  {{ detail.remark || '—' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-tab-pane>

          <el-tab-pane label="车辆信息" name="vehicle">
            <div class="sc-detail-tab-pane">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="车牌号">
                  <plate-number-tag
                    :text="detail.plateNumber"
                    :category="detail.vehicle?.plateCategory"
                  />
                </el-descriptions-item>
                <el-descriptions-item label="车牌类型">
                  {{ plateCategoryLabel(detail.vehicle?.plateCategory) }}
                </el-descriptions-item>
                <el-descriptions-item label="车辆类型">{{ detail.vehicleTypeLabel || '—' }}</el-descriptions-item>
                <el-descriptions-item label="颜色">{{ detail.vehicle?.color || '—' }}</el-descriptions-item>
                <el-descriptions-item label="品牌型号">
                  {{ [detail.vehicle?.brand, detail.vehicle?.model].filter(Boolean).join(' / ') || '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="VIN">{{ detail.vehicle?.vin || '—' }}</el-descriptions-item>
                <el-descriptions-item label="发动机号">{{ detail.vehicle?.engineNo || '—' }}</el-descriptions-item>
                <el-descriptions-item label="轴数">{{ detail.vehicle?.axleCount ?? '—' }}</el-descriptions-item>
                <el-descriptions-item label="核定载重">
                  {{ detail.vehicle?.loadCapacity ? `${detail.vehicle.loadCapacity} 吨` : '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="核定容积">
                  {{ detail.vehicle?.volumeCapacity ? `${detail.vehicle.volumeCapacity} m³` : '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="车长">
                  {{ detail.vehicle?.length ? `${detail.vehicle.length} m` : '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="注册日期">{{ detail.vehicle?.registrationDate || '—' }}</el-descriptions-item>
                <el-descriptions-item label="年检到期">{{ detail.vehicle?.inspectionExpire || '—' }}</el-descriptions-item>
                <el-descriptions-item label="保险到期">{{ detail.vehicle?.insuranceExpire || '—' }}</el-descriptions-item>
                <el-descriptions-item label="道路运输证号">{{ detail.vehicle?.transportLicenseNo || '—' }}</el-descriptions-item>
                <el-descriptions-item label="道路运输证有效期">{{ detail.vehicle?.transportLicenseExpire || '—' }}</el-descriptions-item>
                <el-descriptions-item
                  v-if="detail.vehicle?.hasTrailer === 1"
                  label="挂车信息"
                  :span="2"
                >
                  {{ detail.vehicle.trailerPlate }} / {{ detail.vehicle.trailerType }} /
                  {{ detail.vehicle.trailerLoadCapacity }} 吨
                </el-descriptions-item>
              </el-descriptions>
              <div class="sc-detail-section-title">证件照片</div>
              <div class="sc-detail-doc-gallery">
                <div
                  v-for="doc in vehiclePhotoGallery"
                  :key="doc.key"
                  class="sc-detail-doc-gallery__card"
                >
                  <div class="sc-detail-doc-gallery__title">{{ doc.title }}</div>
                  <div class="sc-detail-doc-gallery__frame">
                    <el-image
                      v-if="detail.vehicle?.[doc.field]"
                      :src="resolveUploadUrl(detail.vehicle[doc.field])"
                      fit="cover"
                      class="sc-detail-doc-gallery__image"
                      :preview-src-list="[resolveUploadUrl(detail.vehicle[doc.field])]"
                    />
                    <div v-else class="sc-detail-doc-gallery__empty">暂无</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="驾驶员信息" name="driver">
            <div class="sc-detail-tab-pane">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="姓名">{{ detail.driver?.name || '—' }}</el-descriptions-item>
                <el-descriptions-item label="手机号">{{ detail.driver?.phone || '—' }}</el-descriptions-item>
                <el-descriptions-item label="身份证号">{{ detail.driver?.idCard || '—' }}</el-descriptions-item>
                <el-descriptions-item label="性别">
                  {{ detail.driver?.gender === 1 ? '男' : detail.driver?.gender === 2 ? '女' : '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="驾照类型">{{ detail.driver?.licenseType || '—' }}</el-descriptions-item>
                <el-descriptions-item label="驾照号码">{{ detail.driver?.licenseNo || '—' }}</el-descriptions-item>
                <el-descriptions-item label="驾照有效期">{{ detail.driver?.licenseExpire || '—' }}</el-descriptions-item>
                <el-descriptions-item label="从业资格证号">{{ detail.driver?.qualificationNo || '—' }}</el-descriptions-item>
                <el-descriptions-item label="从业资格证有效期">{{ detail.driver?.qualificationExpire || '—' }}</el-descriptions-item>
                <el-descriptions-item label="紧急联系人">{{ detail.driver?.emergencyContact || '—' }}</el-descriptions-item>
                <el-descriptions-item label="紧急联系电话">{{ detail.driver?.emergencyPhone || '—' }}</el-descriptions-item>
                <el-descriptions-item label="居住地址" :span="2">{{ detail.driver?.homeAddress || '—' }}</el-descriptions-item>
              </el-descriptions>
              <div class="sc-detail-section-title">证件照片</div>
              <div class="sc-detail-doc-gallery">
                <div
                  v-for="doc in driverPhotoGallery"
                  :key="doc.key"
                  class="sc-detail-doc-gallery__card"
                >
                  <div class="sc-detail-doc-gallery__title">{{ doc.title }}</div>
                  <div class="sc-detail-doc-gallery__frame">
                    <el-image
                      v-if="detail.driver?.[doc.field]"
                      :src="resolveUploadUrl(detail.driver[doc.field])"
                      fit="cover"
                      class="sc-detail-doc-gallery__image"
                      :preview-src-list="[resolveUploadUrl(detail.driver[doc.field])]"
                    />
                    <div v-else class="sc-detail-doc-gallery__empty">暂无</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="结算账户" name="account">
            <div class="sc-detail-tab-pane">
              <el-empty
                v-if="!detail.accounts?.length"
                description="暂无结算账户"
                :image-size="80"
              />
              <el-table
                v-else
                :data="detail.accounts"
                border
                size="small"
                class="sc-detail__table"
              >
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
          </el-tab-pane>

          <el-tab-pane label="审核流水" name="audit">
            <div class="sc-detail-tab-pane">
              <el-empty
                v-if="!auditList.length"
                description="暂无流水"
                :image-size="80"
              />
              <el-timeline v-else>
                <el-timeline-item
                  v-for="a in auditList"
                  :key="a.id"
                  :type="auditTimelineType(a.action)"
                  :timestamp="a.createdAt"
                >
                  <div class="sc-detail__audit">
                    <strong>{{ actionLabelForAudit(a) }}</strong>
                    <span v-if="a.operatorName"> · {{ a.operatorName }}</span>
                    <div v-if="a.remark" class="sc-detail__audit-remark">{{ a.remark }}</div>
                    <div
                      v-if="a.action === 1 && auditRequestType(a) === 'status_change'"
                      class="sc-detail__audit-changes"
                    >
                      <div class="sc-detail__audit-changes-title">申请启用状态变更</div>
                      <div class="sc-detail__audit-change-row">
                        <span class="sc-detail__audit-change-label">启用状态</span>
                        <span class="sc-detail__audit-change-values">
                          <span class="sc-detail__audit-change-before">
                            {{ auditStatusChange(a)?.fromLabel ?? '—' }}
                          </span>
                          <span class="sc-detail__audit-change-arrow">→</span>
                          <span class="sc-detail__audit-change-after">
                            {{ auditStatusChange(a)?.toLabel ?? '—' }}
                          </span>
                        </span>
                      </div>
                    </div>
                    <div
                      v-else-if="a.action === 1 && auditChangeType(a) === 'initial'"
                      class="sc-detail__audit-tag sc-detail__audit-tag--info"
                    >
                      首次提交审核
                    </div>
                    <div
                      v-else-if="a.action === 1 && auditChangeType(a) === 'unchanged'"
                      class="sc-detail__audit-tag"
                    >
                      本次无字段变更
                    </div>
                    <div
                      v-else-if="auditChanges(a).length"
                      class="sc-detail__audit-changes"
                    >
                      <div class="sc-detail__audit-changes-title">变更项</div>
                      <div
                        v-for="c in auditChanges(a)"
                        :key="`${c.group}-${c.field}`"
                        class="sc-detail__audit-change-row"
                      >
                        <span class="sc-detail__audit-change-label">
                          {{ c.group }} · {{ c.label }}
                        </span>
                        <span class="sc-detail__audit-change-values">
                          <span class="sc-detail__audit-change-before">{{ c.before }}</span>
                          <span class="sc-detail__audit-change-arrow">→</span>
                          <span class="sc-detail__audit-change-after">{{ c.after }}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>
        </el-tabs>
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
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import { resolveUploadUrl } from '@/utils/upload-url';
  import {
    getSocialCapacity,
    listAuditHistory
  } from '@/api/capacity/social-capacity/list';
  import type {
    SocialCapacityDetail,
    SocialCapacityAudit,
    SocialCapacityAuditChange,
    SocialCapacityVehicleInfo,
    SocialCapacityDriverInfo
  } from '@/api/capacity/social-capacity/list/model';

  type VehiclePhotoField = keyof Pick<
    SocialCapacityVehicleInfo,
    | 'vehicleLicensePhoto'
    | 'vehicleLicenseBackPhoto'
    | 'transportLicensePhoto'
    | 'vehiclePhoto'
  >;

  type DriverPhotoField = keyof Pick<
    SocialCapacityDriverInfo,
    | 'licensePhoto'
    | 'qualificationPhoto'
    | 'idCardFrontPhoto'
    | 'idCardBackPhoto'
  >;

  const props = defineProps<{
    visible: boolean;
    socialCapacityId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const activeTab = ref('basic');
  const detail = ref<SocialCapacityDetail | null>(null);
  const auditList = ref<SocialCapacityAudit[]>([]);
  const loading = ref(false);

  const vehiclePhotoGallery: Array<{
    key: string;
    title: string;
    field: VehiclePhotoField;
  }> = [
    { key: 'vehicleLicense', title: '行驶证主页', field: 'vehicleLicensePhoto' },
    { key: 'vehicleLicenseBack', title: '行驶证副页', field: 'vehicleLicenseBackPhoto' },
    { key: 'transportLicense', title: '道路运输证', field: 'transportLicensePhoto' },
    { key: 'vehicle', title: '车辆外观照', field: 'vehiclePhoto' }
  ];

  const driverPhotoGallery: Array<{
    key: string;
    title: string;
    field: DriverPhotoField;
  }> = [
    { key: 'license', title: '驾驶证', field: 'licensePhoto' },
    { key: 'qualification', title: '从业资格证', field: 'qualificationPhoto' },
    { key: 'idFront', title: '身份证人像面', field: 'idCardFrontPhoto' },
    { key: 'idBack', title: '身份证国徽面', field: 'idCardBackPhoto' }
  ];

  const onOpen = () => {
    activeTab.value = 'basic';
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

  const plateCategoryLabel = (cat?: string) => {
    if (cat === 'BLUE') return '蓝牌';
    if (cat === 'YELLOW') return '黄牌';
    if (cat === 'NEW_ENERGY') return '新能源';
    return cat || '—';
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

  const auditRequestType = (a: SocialCapacityAudit) => a.attachment?.requestType;

  const auditStatusChange = (a: SocialCapacityAudit) => a.attachment?.statusChange;

  const actionLabelForAudit = (a: SocialCapacityAudit) => {
    if (a.action === 1 && auditRequestType(a) === 'status_change') {
      return '提交状态变更审核';
    }
    return actionLabel(a.action);
  };

  const auditChangeType = (a: SocialCapacityAudit) => a.attachment?.changeType;

  const auditChanges = (a: SocialCapacityAudit): SocialCapacityAuditChange[] =>
    a.attachment?.changes ?? [];

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
    min-height: 120px;
  }

  .sc-detail__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }

  .sc-detail__head h3 {
    margin: 0;
    font-size: 16px;
  }

  .sc-detail__tags {
    display: flex;
    gap: 6px;
  }

  .sc-detail-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .sc-detail-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .sc-detail-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .sc-detail-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .sc-detail-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .sc-detail-tabs :deep(.el-tabs__item) {
    flex: 1;
    min-width: 0;
    margin: 0;
    padding: 0 6px;
    height: 36px;
    line-height: 36px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    transition:
      color 0.2s,
      background 0.2s,
      box-shadow 0.2s;
  }

  .sc-detail-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .sc-detail-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .sc-detail-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .sc-detail-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .sc-detail-tab-pane {
    max-height: min(420px, calc(100vh - 300px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .sc-detail-section-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 16px 0 10px;
    padding-left: 2px;
    border-left: 3px solid var(--el-color-primary);
    line-height: 1.2;
  }

  .sc-detail-doc-gallery {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
  }

  @media (max-width: 768px) {
    .sc-detail-doc-gallery {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .sc-detail-doc-gallery__card {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 10px;
    background: var(--el-fill-color-blank);
  }

  .sc-detail-doc-gallery__title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    text-align: center;
    margin-bottom: 8px;
  }

  .sc-detail-doc-gallery__frame {
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color-light);
  }

  .sc-detail-doc-gallery__image {
    width: 100%;
    height: 100%;
    display: block;
    cursor: pointer;
  }

  .sc-detail-doc-gallery__empty {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    font-size: 12px;
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

  .sc-detail__audit-tag {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
  }

  .sc-detail__audit-tag--info {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .sc-detail__audit-changes {
    margin-top: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid var(--el-color-warning-light-7);
    background: var(--el-color-warning-light-9);
  }

  .sc-detail__audit-changes-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-color-warning-dark-2);
    margin-bottom: 8px;
  }

  .sc-detail__audit-change-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 6px 0;
    border-bottom: 1px dashed var(--el-color-warning-light-5);
  }

  .sc-detail__audit-change-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .sc-detail__audit-change-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .sc-detail__audit-change-values {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    line-height: 1.5;
  }

  .sc-detail__audit-change-before {
    color: var(--el-text-color-secondary);
    text-decoration: line-through;
    padding: 1px 6px;
    border-radius: 4px;
    background: var(--el-fill-color);
  }

  .sc-detail__audit-change-arrow {
    color: var(--el-text-color-placeholder);
    font-weight: 600;
  }

  .sc-detail__audit-change-after {
    color: var(--el-color-primary);
    font-weight: 600;
    padding: 1px 6px;
    border-radius: 4px;
    background: var(--el-color-primary-light-9);
  }
</style>
