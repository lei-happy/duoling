<template>
  <ele-page hide-footer :multi-card="false">
    <ele-card :body-style="{ paddingBottom: '4px' }">
      <template #header>
        <div class="card-head">
          <span>汽车之家同步</span>
          <span class="card-head__hint">
            探测：参配页连通性。下方「同步」固定为增量：已有品牌/车系不写库、不重下图片；
            仍会拉报价页发现新车系，仅对新增品牌/车系下载 Logo、车系图并写参配（默认开启）。
            全量刷新仅能通过接口传 incrementalOnly=false（会重下图片并改写路径）。
          </span>
        </div>
      </template>
      <el-form inline class="toolbar-form" @submit.prevent="">
        <el-form-item label="车系 ID（汽车之家）">
          <el-input-number
            v-model="seriesId"
            :min="1"
            :max="999999"
            :controls="true"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="triggering" @click="onTrigger">
            发起探测任务
          </el-button>
        </el-form-item>
        <el-form-item label="品牌上限">
          <el-input-number
            v-model="maxBrands"
            :min="0"
            :max="9999"
            :controls="true"
            controls-position="right"
          />
          <span class="inline-hint">0=不限制（可售品牌约 267 个；增量仍会逐品牌请求报价页）</span>
        </el-form-item>
        <el-form-item label="请求间隔(ms)">
          <el-input-number
            v-model="fullDelayMs"
            :min="200"
            :max="5000"
            :step="50"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            plain
            :loading="fullTriggering"
            @click="onTriggerFull"
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
        cache-key="OpsAutohomeSyncJobs"
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
    pageAutohomeSyncJobs,
    triggerAutohomeProbe,
    triggerAutohomeFullSync,
    getAutohomeSyncJob
  } from '@/api/ops/autohome-sync';
  import type { AutohomeSyncJob } from '@/api/ops/autohome-sync/model';

  defineOptions({ name: 'DataSyncAutohome' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const seriesId = ref(4851);
  const maxBrands = ref(0);
  const fullDelayMs = ref(400);
  const triggering = ref(false);
  const fullTriggering = ref(false);
  const logVisible = ref(false);
  const activeLog = ref('');

  const columns = ref<Columns>([
    { prop: 'jobId', label: '任务ID', width: 100, align: 'center' },
    { prop: 'jobType', label: '类型', width: 100, align: 'center' },
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
    return pageAutohomeSyncJobs({
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

  const onTrigger = async () => {
    triggering.value = true;
    try {
      await triggerAutohomeProbe({ autohomeSeriesId: seriesId.value });
      EleMessage.success({ message: '任务已创建，请稍后刷新列表查看结果', plain: true });
      reload(1);
    } catch (e: any) {
      EleMessage.error({ message: e.message ?? '触发失败', plain: true });
    } finally {
      triggering.value = false;
    }
  };

  const onTriggerFull = async () => {
    try {
      await ElMessageBox.confirm(
        '将按「增量」同步：已存在品牌/车系不会更新或重下图片；仍会请求各品牌报价页，并对新车系发起图片与参配请求。确认继续？',
        '增量同步',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    fullTriggering.value = true;
    try {
      await triggerAutohomeFullSync({
        maxBrands: maxBrands.value,
        delayMs: fullDelayMs.value
      });
      EleMessage.success({
        message: '增量同步任务已创建，请通过列表与日志查看进度',
        plain: true
      });
      reload(1);
    } catch (e: any) {
      EleMessage.error({ message: e.message ?? '触发失败', plain: true });
    } finally {
      fullTriggering.value = false;
    }
  };

  const openLog = async (row: AutohomeSyncJob) => {
    try {
      const latest = await getAutohomeSyncJob(row.jobId);
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
