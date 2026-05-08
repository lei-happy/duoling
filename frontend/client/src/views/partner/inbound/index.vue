<!--
  合作客户（反向视角）
  B 视角：本企业作为承运商被哪些 A 公司纳入了合作。
  数据来源：GET /api/client/partner/inbound（基于平台库 sys_carrier_link 反查）
-->
<template>
  <ele-page>
    <ele-card>
      <el-form
        :inline="true"
        :model="where"
        @submit.prevent="reload(1)"
      >
        <el-form-item>
          <el-input
            v-model.trim="where.keyword"
            placeholder="企业名称/承运商名"
            clearable
            style="width: 220px"
            @keyup.enter="reload(1)"
            @clear="reload(1)"
          />
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="where.linkStatus"
            placeholder="互联状态"
            clearable
            style="width: 140px"
          >
            <el-option label="已互联" :value="1" />
            <el-option label="A 端已删除" :value="2" />
            <el-option label="B 端已退出" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="reload(1)">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="onReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
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
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="PartnerInboundTable"
      >
        <template #sourceTenantName="{ row }">
          <div class="cell-tenant">
            <b>{{ row.sourceTenantName || row.sourceTenantCode }}</b>
            <span v-if="row.sourceTenantShortName" class="short">
              ({{ row.sourceTenantShortName }})
            </span>
          </div>
          <div class="sub" v-if="row.sourceCarrierName">
            对方称我为：<span>{{ row.sourceCarrierName }}</span>
          </div>
        </template>
        <template #sourceContact="{ row }">
          <div v-if="row.sourceContactPerson || row.sourceContactPhone">
            <div>{{ row.sourceContactPerson || '—' }}</div>
            <div class="sub">{{ row.sourceContactPhone || '—' }}</div>
          </div>
          <span v-else class="placeholder">—</span>
        </template>
        <template #sourceLocation="{ row }">
          <span v-if="row.sourceProvince || row.sourceCity || row.sourceAddress">
            {{ row.sourceProvince || '' }}{{ row.sourceCity ? ' / ' + row.sourceCity : '' }}
            <div v-if="row.sourceAddress" class="sub">{{ row.sourceAddress }}</div>
          </span>
          <span v-else class="placeholder">—</span>
        </template>
        <template #linkStatus="{ row }">
          <el-tag
            :type="statusTagType(row.linkStatus)"
            size="small"
            :disable-transitions="true"
          >
            {{ INBOUND_STATUS_TEXT[row.linkStatus] || '未知' }}
          </el-tag>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { reactive, ref } from 'vue';
  import { Search, Refresh } from '@element-plus/icons-vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    pageInbound,
    INBOUND_STATUS_TEXT,
    type CarrierInboundParam
  } from '@/api/partner/inbound';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'PartnerInbound' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<CarrierInboundParam>({
    keyword: undefined,
    linkStatus: undefined
  });

  const columns = ref<Columns>([
    {
      prop: 'sourceTenantName',
      label: '邀请方企业',
      minWidth: 240,
      slot: 'sourceTenantName'
    },
    {
      prop: 'sourceContact',
      label: '联系人 / 电话',
      width: 150,
      slot: 'sourceContact'
    },
    {
      prop: 'sourceLocation',
      label: '所在地',
      minWidth: 180,
      slot: 'sourceLocation'
    },
    {
      prop: 'cooperationStart',
      label: '合作起始',
      width: 130,
      align: 'center',
      formatter: (row) =>
        row.cooperationStart ? row.cooperationStart : '—'
    },
    {
      prop: 'linkStatus',
      label: '互联状态',
      width: 110,
      align: 'center',
      slot: 'linkStatus'
    },
    {
      prop: 'createdAt',
      label: '建立时间',
      sortable: 'custom',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where: w, orders }) => {
    return pageInbound({ ...w, ...orders, ...pages });
  };

  const reload = (page?: number) => {
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const onReset = () => {
    where.keyword = undefined;
    where.linkStatus = undefined;
    reload(1);
  };

  function statusTagType(s: number): any {
    if (s === 1) return 'success';
    if (s === 2 || s === 3) return 'info';
    return 'warning';
  }
</script>

<style scoped>
  .cell-tenant {
    line-height: 1.4;
  }
  .cell-tenant .short {
    margin-left: 6px;
    color: var(--el-text-color-secondary);
    font-weight: normal;
    font-size: 12px;
  }
  .sub {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    margin-top: 2px;
  }
  .placeholder {
    color: var(--el-text-color-placeholder);
  }
</style>
