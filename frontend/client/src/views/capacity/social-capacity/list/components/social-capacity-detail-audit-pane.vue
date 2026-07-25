<template>
  <el-empty
    v-if="!auditList.length"
    description="暂无审批记录"
    :image-size="80"
  />
  <el-timeline v-else>
    <el-timeline-item
      v-for="a in auditList"
      :key="a.id"
      :type="auditTimelineType(a.action)"
      :timestamp="formatDateTime(a.createdAt, '—')"
    >
      <div class="sc-detail__audit">
        <strong>{{ actionLabelForAudit(a) }}</strong>
        <span v-if="a.operatorName"> · {{ a.operatorName }}</span>
        <div v-if="a.remark" class="sc-detail__audit-remark">{{
          a.remark
        }}</div>
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
</template>

<script lang="ts" setup>
  import { formatDateTime } from '@/utils/date-util';
  import type {
    SocialCapacityAudit,
    SocialCapacityAuditChange
  } from '@/api/capacity/social-capacity/list/model';

  defineProps<{
    auditList: SocialCapacityAudit[];
  }>();

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
  const actionLabel = (a?: number) => (a ? (ACTION_LABEL[a] ?? '—') : '—');

  const auditRequestType = (a: SocialCapacityAudit) =>
    a.attachment?.requestType;

  const auditStatusChange = (a: SocialCapacityAudit) =>
    a.attachment?.statusChange;

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
</script>

<style scoped>
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
