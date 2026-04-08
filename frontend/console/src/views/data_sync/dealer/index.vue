<template>
  <ele-page hide-footer :multi-card="false">
    <ele-card :body-style="{ paddingBottom: '4px' }">
      <template #header>
        <div class="card-head">
          <span>经销商数据同步</span>
          <span class="card-head__hint">
            从汽车之家抓取全国经销商信息（按城市遍历列表页与详情页），固定增量模式：已存在经销商不重复写入。
          </span>
        </div>
      </template>
      <el-form inline class="toolbar-form" @submit.prevent="">
        <el-form-item label="城市上限">
          <el-input-number
            v-model="maxCities"
            :min="0"
            :max="9999"
            :controls="true"
            controls-position="right"
          />
          <span class="inline-hint">0=不限制（内置约 150 个城市）</span>
        </el-form-item>
        <el-form-item label="请求间隔(ms)">
          <el-input-number
            v-model="delayMs"
            :min="200"
            :max="5000"
            :step="50"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="triggering"
            @click="onTriggerSync"
          >
            发起增量同步
          </el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="jobId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="OpsDealerSyncJobs"
      >
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 'success'"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            成功
          </el-tag>
          <el-tag
            v-else-if="row.status === 'failed'"
            size="small"
            type="danger"
            :disable-transitions="true"
          >
            失败
          </el-tag>
          <el-tag
            v-else-if="row.status === 'running'"
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            执行中
          </el-tag>
          <el-tag v-else size="small" type="info" :disable-transitions="true">
            {{ row.status }}
          </el-tag>
        </template>
        <template #toolbar>
          <el-button :icon="ReloadOutlined" circle @click="reload()" />
        </template>
        <template #action="{ row }">
          <el-button type="primary" link @click="openLog(row)"> 日志 </el-button>
        </template>
      </ele-pro-table>
    </ele-card>

    <el-dialog
      v-model="logVisible"
      title="任务日志"
      width="720px"
      destroy-on-close
    >
      <pre class="log-pre">{{ activeLog }}</pre>
      <template #footer>
        <el-button type="primary" @click="logVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { ReloadOutlined } from '@/components/icons';
  import {
    pageDealerSyncJobs,
    triggerDealerSync,
    getDealerSyncJob
  } from '@/api/ops/dealer-sync';
  import type { DealerSyncJob } from '@/api/ops/dealer-sync/model';

  defineOptions({ name: 'DataSyncDealer' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const maxCities = ref(0);
  const delayMs = ref(400);
  const triggering = ref(false);
  const logVisible = ref(false);
  const activeLog = ref('');

  const columns = ref<Columns>([
    { prop: 'jobId', label: '任务ID', width: 100, align: 'center' },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'progressPct',
      label: '进度',
      width: 80,
      align: 'center',
      formatter: (row) => `${row.progressPct}%`
    },
    { prop: 'createTime', label: '创建时间', minWidth: 170 },
    { prop: 'lastUpdateTime', label: '更新时间', minWidth: 170 },
    {
      columnKey: 'action',
      label: '操作',
      width: 100,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageDealerSyncJobs({
      page: pages.page,
      limit: pages.limit
    }).then((res) => ({
      list: res.list,
      count: res.count
    }));
  };

  const reload = (page?: number) => {
    tableRef.value?.reload?.({ page });
  };

  const onTriggerSync = async () => {
    try {
      await ElMessageBox.confirm(
        '将按「增量」同步经销商数据：已存在经销商不会重复写入，仅新增不存在的经销商记录。确认继续？',
        '经销商增量同步',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    triggering.value = true;
    try {
      await triggerDealerSync({
        maxCities: maxCities.value,
        delayMs: delayMs.value
      });
      EleMessage.success({
        message: '经销商同步任务已创建，请通过列表与日志查看进度',
        plain: true
      });
      reload(1);
    } catch (e: any) {
      EleMessage.error({ message: e.message ?? '触发失败', plain: true });
    } finally {
      triggering.value = false;
    }
  };

  const openLog = async (row: DealerSyncJob) => {
    try {
      const latest = await getDealerSyncJob(row.jobId);
      activeLog.value =
        latest.logText ||
        latest.errorMessage ||
        '（无日志）';
      if (latest.errorMessage && latest.logText) {
        activeLog.value += `\n\n[error]\n${latest.errorMessage}`;
      }
      logVisible.value = true;
    } catch (e: any) {
      EleMessage.error({ message: e.message ?? '加载失败', plain: true });
    }
  };
</script>

<style scoped>
  .card-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
  }
  .card-head__hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    font-weight: normal;
  }
  .toolbar-form {
    margin-bottom: 0;
  }
  .inline-hint {
    margin-left: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
  .log-pre {
    margin: 0;
    max-height: 50vh;
    overflow: auto;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
  }
</style>
