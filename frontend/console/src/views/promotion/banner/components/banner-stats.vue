<!-- Banner 数据统计弹窗：聚合概览 + 按租户 + 用户明细 -->
<template>
  <ele-modal
    :width="820"
    :title="`推广数据 - ${banner.title || ''}`"
    v-bind="modalProps"
  >
    <div class="stats-summary">
      <div class="stats-cell">
        <div class="stats-cell__value">{{ summary.view_pv }}</div>
        <div class="stats-cell__label">曝光 PV</div>
      </div>
      <div class="stats-cell">
        <div class="stats-cell__value">{{ summary.view_uv }}</div>
        <div class="stats-cell__label">曝光 UV</div>
      </div>
      <div class="stats-cell">
        <div class="stats-cell__value">{{ summary.click_pv }}</div>
        <div class="stats-cell__label">点击 PV</div>
      </div>
      <div class="stats-cell">
        <div class="stats-cell__value">{{ summary.click_uv }}</div>
        <div class="stats-cell__label">点击 UV</div>
      </div>
      <div class="stats-cell">
        <div class="stats-cell__value"
          >{{ (summary.ctr * 100).toFixed(2) }}%</div
        >
        <div class="stats-cell__label">点击率 CTR</div>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="按租户聚合" name="tenant">
        <el-table :data="byTenant" size="small" max-height="360" border>
          <el-table-column type="index" label="#" width="50" align="center" />
          <el-table-column prop="tenant_name" label="租户" min-width="160">
            <template #default="{ row }">
              {{ row.tenant_name || row.tenant_code }}
            </template>
          </el-table-column>
          <el-table-column
            prop="view_pv"
            label="曝光PV"
            width="90"
            align="center"
          />
          <el-table-column
            prop="view_uv"
            label="曝光UV"
            width="90"
            align="center"
          />
          <el-table-column
            prop="click_pv"
            label="点击PV"
            width="90"
            align="center"
          />
          <el-table-column
            prop="click_uv"
            label="点击UV"
            width="90"
            align="center"
          />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用户明细" name="events">
        <div class="events-filter">
          <el-radio-group
            v-model="eventType"
            size="small"
            @change="loadEvents(1)"
          >
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="view">曝光</el-radio-button>
            <el-radio-button value="click">点击</el-radio-button>
          </el-radio-group>
        </div>
        <el-table
          v-loading="eventLoading"
          :data="events"
          size="small"
          max-height="320"
          border
        >
          <el-table-column prop="tenant_name" label="租户" min-width="140">
            <template #default="{ row }">
              {{ row.tenant_name || row.tenant_code }}
            </template>
          </el-table-column>
          <el-table-column prop="user_phone" label="用户" width="140">
            <template #default="{ row }">
              {{ row.user_phone || row.user_id }}
            </template>
          </el-table-column>
          <el-table-column
            prop="event_type"
            label="行为"
            width="90"
            align="center"
          >
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="row.event_type === 'click' ? 'success' : 'info'"
                :disable-transitions="true"
              >
                {{ row.event_type === 'click' ? '点击' : '曝光' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="occurred_at"
            label="时间"
            width="180"
            align="center"
          />
        </el-table>
        <div class="events-pager">
          <el-pagination
            layout="total, prev, pager, next"
            :total="eventTotal"
            :current-page="eventPage"
            :page-size="eventLimit"
            @current-change="loadEvents"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', text: '关闭', onClick: () => closeModal() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { getBannerStats, pageBannerEvents } from '@/api/promotion';
  import type {
    Banner,
    BannerStatsSummary,
    BannerTenantStat,
    BannerEvent
  } from '@/api/promotion/model';

  const props = defineProps<{ banner: Banner }>();

  const { modalProps, closeModal } = useModal();

  const activeTab = ref('tenant');

  const summary = ref<BannerStatsSummary>({
    view_pv: 0,
    view_uv: 0,
    click_pv: 0,
    click_uv: 0,
    ctr: 0
  });
  const byTenant = ref<BannerTenantStat[]>([]);

  const events = ref<BannerEvent[]>([]);
  const eventLoading = ref(false);
  const eventType = ref('');
  const eventPage = ref(1);
  const eventLimit = ref(10);
  const eventTotal = ref(0);

  const loadStats = () => {
    getBannerStats(props.banner.id!)
      .then((data) => {
        if (!data) return;
        summary.value = data.summary;
        byTenant.value = data.by_tenant;
      })
      .catch((e) => EleMessage.error({ message: e.message, plain: true }));
  };

  const loadEvents = (page = 1) => {
    eventPage.value = page;
    eventLoading.value = true;
    pageBannerEvents(props.banner.id!, {
      page,
      limit: eventLimit.value,
      event_type: eventType.value || undefined
    })
      .then((res) => {
        events.value = res.list;
        eventTotal.value = res.count;
      })
      .catch((e) => EleMessage.error({ message: e.message, plain: true }))
      .finally(() => {
        eventLoading.value = false;
      });
  };

  loadStats();
  loadEvents(1);
</script>

<style lang="scss" scoped>
  .stats-summary {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .stats-cell {
    flex: 1;
    text-align: center;
    padding: 14px 8px;
    border-radius: 8px;
    background: var(--el-fill-color-light);

    &__value {
      font-size: 22px;
      font-weight: 700;
      color: var(--el-color-primary);
    }

    &__label {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }

  .events-filter {
    margin-bottom: 10px;
  }

  .events-pager {
    margin-top: 12px;
    display: flex;
    justify-content: flex-end;
  }
</style>
