<!-- 生态运营 - 免审白名单 -->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: '0' }">
      <el-form inline @submit.prevent="() => reload(1)">
        <el-form-item label="关键字">
          <el-input
            clearable
            v-model="where.keyword"
            placeholder="按企业名或编码搜索"
            style="width: 220px"
            @keyup.enter="() => reload(1)"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="() => reload(1)">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 12px"
      >
        白名单里的企业发布挂牌后直接上架，只在 24 小时内抽检。
        发现「已被强制下架多次却还在名单里」的，请及时移出——只下架单条挂牌，
        下一条照样会直通上架。
      </el-alert>

      <ele-pro-table
        ref="tableRef"
        row-key="tenantCode"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        cache-key="EcoAuditWhitelistTable"
      >
        <template #toolbar>
          <btn-items
            :items="[{ preset: 'add', title: '授予免审', onClick: openGrant }]"
          />
        </template>

        <template #source="{ row }">
          <el-tag
            size="small"
            :disable-transitions="true"
            :type="row.whitelistSource === 2 ? 'warning' : 'info'"
          >
            {{ row.whitelistSourceLabel || '—' }}
          </el-tag>
        </template>

        <template #publish="{ row }">
          {{ row.publishCount ?? 0 }} 条
          <span class="eco-wl-sub">在架 {{ row.listedCount ?? 0 }}</span>
        </template>

        <template #deal="{ row }">
          {{ row.dealCount ?? 0 }} 笔
          <span class="eco-wl-sub">完成 {{ row.dealCompletedCount ?? 0 }}</span>
        </template>

        <template #risk="{ row }">
          <span :class="hasRisk(row) ? 'eco-wl-risk' : ''">
            强制下架 {{ row.forceDelistCount ?? 0 }} · 举报成立
            {{ row.reportValidCount ?? 0 }}
          </span>
        </template>

        <template #operate="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="[
              { title: '查看档案', onClick: () => openProfile(row) },
              {
                title: '移出',
                props: { type: 'danger' },
                onClick: () => revokeOne(row)
              }
            ]"
          />
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { reactive, ref } from 'vue';
  import { useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageWhitelist } from '@/api/ecosystem/audit-whitelist';
  import type { WhitelistMember } from '@/api/ecosystem/audit/model';
  import { useWhitelistActions } from '@/views/ecosystem/components/use-whitelist-actions';

  defineOptions({ name: 'EcoAuditWhitelist' });

  const { openModal } = useModal();
  const { revoke } = useWhitelistActions();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const where = reactive<{ keyword?: string }>({ keyword: '' });

  const columns = ref<Columns>([
    { prop: 'tenantName', label: '企业', minWidth: 180 },
    { prop: 'tenantCode', label: '企业编码', width: 130 },
    {
      prop: 'whitelistSource',
      label: '授予方式',
      width: 110,
      align: 'center',
      slot: 'source'
    },
    { prop: 'whitelistAt', label: '授予时间', width: 170, align: 'center' },
    {
      prop: 'publishCount',
      label: '累计发布',
      width: 140,
      align: 'center',
      slot: 'publish'
    },
    {
      prop: 'dealCount',
      label: '成交',
      width: 130,
      align: 'center',
      slot: 'deal'
    },
    {
      columnKey: 'risk',
      label: '违规记录',
      width: 200,
      align: 'center',
      slot: 'risk'
    },
    {
      columnKey: 'operate',
      label: '操作',
      width: 150,
      align: 'center',
      slot: 'operate',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) =>
    pageWhitelist({
      page: pages?.page,
      limit: pages?.limit,
      keyword: where.keyword || undefined
    });

  const reload = (page?: number) => {
    tableRef.value?.reload?.({ page: page ?? 1 });
  };

  const resetSearch = () => {
    where.keyword = '';
    reload(1);
  };

  const hasRisk = (row: WhitelistMember) =>
    (row.forceDelistCount ?? 0) > 0 || (row.reportValidCount ?? 0) > 0;

  const openGrant = () => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/profile-modal.vue'),
      componentProps: { onDone: () => reload(1) }
    });
  };

  const openProfile = (row: WhitelistMember) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/profile-modal.vue'),
      componentProps: {
        tenantCode: row.tenantCode,
        onDone: () => reload()
      }
    });
  };

  const revokeOne = (row: WhitelistMember) => {
    revoke(row.tenantCode, () => reload());
  };
</script>

<style lang="scss" scoped>
  .eco-wl-sub {
    margin-left: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-wl-risk {
    color: var(--el-color-danger);
  }
</style>
