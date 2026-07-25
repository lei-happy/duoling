<!--
  发布方档案：认证、历史发布、通过率、成交、违规记录 + 免审资格与一键授予/移出

  审核详情与白名单页问的是同一个问题「这家企业靠不靠得住」，后端也给了同一份
  数据结构（tenant + eligibility），所以两处共用这个组件，连授予/移出的确认
  文案都一致——同一个动作在两个页面有两套说法，是运营最容易误操作的地方。
-->
<template>
  <div v-loading="loading" class="eco-tenant">
    <template v-if="profile">
      <div class="eco-tenant__head">
        <div class="eco-tenant__name">
          {{ tenant.tenantName || tenant.tenantCode }}
        </div>
        <div class="eco-tenant__code">{{ tenant.tenantCode }}</div>
        <div class="eco-tenant__tags">
          <el-tag
            size="small"
            :disable-transitions="true"
            :type="tenant.licenseVerified === 1 ? 'success' : 'danger'"
          >
            {{ tenant.licenseVerified === 1 ? '已企业认证' : '未企业认证' }}
          </el-tag>
          <el-tag
            v-if="tenant.transportLicenseVerified === 1"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            道路运输许可已核验
          </el-tag>
          <el-tag
            size="small"
            :disable-transitions="true"
            :type="tenant.hallEnabled === 1 ? 'info' : 'warning'"
          >
            {{ tenant.hallEnabled === 1 ? '大厅正常' : '大厅已关停' }}
          </el-tag>
          <el-tag
            v-if="tenant.auditWhitelist === 1"
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            免审直通
          </el-tag>
        </div>
        <div v-if="restrictedText" class="eco-tenant__warn">
          {{ restrictedText }}
        </div>
      </div>

      <div class="eco-tenant__grid">
        <div v-for="m in metrics" :key="m.label" class="eco-tenant__metric">
          <div class="eco-tenant__metric-value">{{ m.value }}</div>
          <div class="eco-tenant__metric-label">{{ m.label }}</div>
        </div>
      </div>

      <div class="eco-tenant__section">
        <div class="eco-tenant__section-title"
          >违规记录（括号内为近 90 天）</div
        >
        <div class="eco-tenant__violations">
          <span>
            驳回 {{ tenant.rejectCount ?? 0 }}（{{
              tenant.rejectCountRecent ?? 0
            }}）
          </span>
          <span>
            强制下架 {{ tenant.forceDelistCount ?? 0 }}（{{
              tenant.forceDelistCountRecent ?? 0
            }}）
          </span>
          <span>抽检不通过 {{ tenant.spotCheckFailCount ?? 0 }}</span>
          <span>
            举报成立 {{ tenant.reportValidCount ?? 0 }}（{{
              tenant.reportValidCountRecent ?? 0
            }}）
          </span>
        </div>
        <div v-if="tenant.whitelistRevokedAt" class="eco-tenant__revoked">
          {{ tenant.whitelistRevokedAt }} 被移出过免审：{{
            tenant.whitelistRevokeReason || '未填写原因'
          }}
        </div>
      </div>

      <div
        v-if="tenant.recentPosts && tenant.recentPosts.length"
        class="eco-tenant__section"
      >
        <div class="eco-tenant__section-title">最近发布</div>
        <div
          v-for="p in tenant.recentPosts"
          :key="p.id"
          class="eco-tenant__recent"
        >
          <span class="eco-tenant__recent-title">{{ p.title }}</span>
          <el-tag size="small" :disable-transitions="true">
            {{ p.statusLabel }}
          </el-tag>
          <span class="eco-tenant__recent-time">{{ p.createdAt }}</span>
        </div>
      </div>

      <div class="eco-tenant__section">
        <div class="eco-tenant__section-title">免审白名单资格</div>
        <eligibility-items :data="eligibility" />
      </div>

      <div class="eco-tenant__actions">
        <template v-if="tenant.auditWhitelist === 1">
          <el-button type="warning" plain @click="revoke">
            移出免审白名单
          </el-button>
        </template>
        <template v-else>
          <el-tooltip
            :disabled="eligibility.manualAllowed"
            content="企业认证与大厅能力是参与大厅的门槛，不满足时人工也不能授予"
          >
            <span>
              <el-button
                type="primary"
                plain
                :disabled="!eligibility.manualAllowed"
                @click="grant"
              >
                {{ eligibility.eligible ? '授予免审' : '仍然授予免审' }}
              </el-button>
            </span>
          </el-tooltip>
        </template>
      </div>
    </template>

    <el-empty
      v-else-if="!loading"
      :image-size="72"
      description="点一条挂牌，这里显示发布方的档案"
    />
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getTenantProfile } from '@/api/ecosystem/audit-whitelist';
  import type { AuditTenantProfile } from '@/api/ecosystem/audit/model';
  import EligibilityItems from './eligibility-items.vue';
  import { useWhitelistActions } from './use-whitelist-actions';

  const props = defineProps<{
    /** 只给编码时组件自己去取档案 */
    tenantCode?: string | null;
    /** 已经有档案数据时直接传进来，避免为同一份数据再发一次请求 */
    profile?: AuditTenantProfile | null;
  }>();

  const emit = defineEmits<{ (e: 'changed'): void }>();

  const loading = ref(false);
  const loaded = ref<AuditTenantProfile | null>(null);

  const profile = computed(() => props.profile ?? loaded.value);

  const tenant = computed(() => profile.value?.tenant ?? ({} as any));
  const eligibility = computed(
    () => profile.value?.eligibility ?? ({ items: [] } as any)
  );

  const metrics = computed(() => {
    const t = tenant.value;
    const rate = t.passRate == null ? '—' : `${Math.round(t.passRate * 100)}%`;
    return [
      { label: '累计发布', value: t.publishCount ?? 0 },
      { label: '在架中', value: t.listedCount ?? 0 },
      { label: '待审核', value: t.pendingCount ?? 0 },
      { label: '审核通过率', value: rate },
      { label: '成交', value: t.dealCount ?? 0 },
      { label: '完成成交', value: t.dealCompletedCount ?? 0 }
    ];
  });

  const restrictedText = computed(() => {
    const t = tenant.value;
    const parts: string[] = [];
    if (t.publishRestrictedUntil) {
      parts.push(`发布受限至 ${t.publishRestrictedUntil}`);
    }
    if (t.intentRestrictedUntil) {
      parts.push(`洽谈受限至 ${t.intentRestrictedUntil}`);
    }
    return parts.join('；');
  });

  const load = (code?: string | null) => {
    if (!code) {
      loaded.value = null;
      return;
    }
    loading.value = true;
    getTenantProfile(code)
      .then((data) => {
        loading.value = false;
        loaded.value = data;
      })
      .catch((e) => {
        loading.value = false;
        loaded.value = null;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  watch(
    () => props.tenantCode,
    (code) => {
      if (!props.profile) {
        load(code);
      }
    },
    { immediate: true }
  );

  /** 档案由外部传入时，刷新的责任也在外部：这里只负责喊一声 */
  const refresh = () => {
    if (!props.profile) {
      load(props.tenantCode);
    }
  };

  const { grant: doGrant, revoke: doRevoke } = useWhitelistActions();

  const onChanged = () => {
    refresh();
    emit('changed');
  };

  const grant = () => doGrant(tenant.value.tenantCode, onChanged);

  const revoke = () => doRevoke(tenant.value.tenantCode, onChanged);

  defineExpose({ refresh });
</script>

<style lang="scss" scoped>
  .eco-tenant {
    min-height: 160px;
  }

  .eco-tenant__name {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.5;
    color: var(--el-text-color-primary);
  }

  .eco-tenant__code {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-tenant__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
  }

  .eco-tenant__warn {
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-color-danger);
  }

  .eco-tenant__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 14px;
  }

  .eco-tenant__metric {
    padding: 8px 4px;
    border-radius: 6px;
    text-align: center;
    background: var(--el-fill-color-light);
  }

  .eco-tenant__metric-value {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .eco-tenant__metric-label {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-tenant__section {
    margin-top: 16px;
  }

  .eco-tenant__section-title {
    margin-bottom: 6px;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .eco-tenant__violations {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 14px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-tenant__revoked {
    margin-top: 6px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-color-warning);
  }

  .eco-tenant__recent {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
    font-size: 12px;
    color: var(--el-text-color-regular);
  }

  .eco-tenant__recent-title {
    flex: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .eco-tenant__recent-time {
    color: var(--el-text-color-secondary);
  }

  .eco-tenant__actions {
    margin-top: 16px;
    text-align: right;
  }
</style>
