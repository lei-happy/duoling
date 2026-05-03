<template>
  <ele-page>
    <ele-card>
      <!-- 顶部：租户切换 + 统计大盘（两个 Tab 共享） -->
      <div class="ai-toolbar">
        <el-select
          v-model="tenantCode"
          placeholder="选择租户"
          style="width: 220px"
          @change="onTenantChange"
        >
          <el-option v-for="t in tenants" :key="t" :label="t" :value="t" />
        </el-select>
      </div>

      <el-row :gutter="12" style="margin-top: 12px">
        <el-col :span="6">
          <ele-card class="ai-stat-card">
            <div class="ai-stat-card__title">近 {{ statsDays }} 天 Prompt Tokens</div>
            <div class="ai-stat-card__value">{{ stats?.total_prompt_tokens ?? 0 }}</div>
          </ele-card>
        </el-col>
        <el-col :span="6">
          <ele-card class="ai-stat-card">
            <div class="ai-stat-card__title">近 {{ statsDays }} 天 Completion Tokens</div>
            <div class="ai-stat-card__value">{{ stats?.total_completion_tokens ?? 0 }}</div>
          </ele-card>
        </el-col>
        <el-col :span="12">
          <ele-card class="ai-stat-card">
            <div class="ai-stat-card__title">工具调用 Top</div>
            <el-table
              :data="stats?.tool_stats ?? []"
              size="small"
              max-height="120"
              border
            >
              <el-table-column prop="tool_code" label="工具" />
              <el-table-column prop="total" label="总数" width="70" />
              <el-table-column prop="success" label="成功" width="70" />
              <el-table-column prop="failed" label="失败" width="70" />
              <el-table-column prop="denied" label="拒绝" width="70" />
              <el-table-column prop="avg_latency_ms" label="平均延迟(ms)" width="120" />
            </el-table>
          </ele-card>
        </el-col>
      </el-row>

      <el-tabs v-model="activeTab" style="margin-top: 16px">
        <!-- ============ Tab 1：工具调用日志 ============ -->
        <el-tab-pane label="工具调用日志" name="tools">
          <div class="ai-toolbar" style="margin-bottom: 8px">
            <el-select
              v-model="searchForm.status"
              clearable
              placeholder="状态"
              style="width: 160px"
            >
              <el-option label="success" value="success" />
              <el-option label="failed" value="failed" />
              <el-option label="denied" value="denied" />
              <el-option label="pending_confirm" value="pending_confirm" />
              <el-option label="cancelled" value="cancelled" />
            </el-select>
            <el-input
              v-model="searchForm.toolCode"
              clearable
              placeholder="工具编码"
              style="width: 200px"
              @keyup.enter="loadList"
            />
            <el-input
              v-model.number="(searchForm as any).sessionId"
              clearable
              placeholder="会话ID"
              style="width: 120px"
              @keyup.enter="loadList"
            />
            <el-button type="primary" @click="loadList">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </div>

          <el-table
            v-loading="loading"
            :data="list"
            row-key="id"
            border
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="sessionId" label="会话ID" width="100" />
            <el-table-column prop="userId" label="用户ID" width="100" />
            <el-table-column prop="toolCode" label="工具" width="180" />
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag size="small" :type="statusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="latencyMs" label="延迟(ms)" width="100" />
            <el-table-column prop="createdAt" label="时间" width="170" />
            <el-table-column label="详情">
              <template #default="{ row }">
                <el-popover trigger="click" :width="500">
                  <template #reference>
                    <el-button text type="primary" size="small">查看</el-button>
                  </template>
                  <div>
                    <div style="font-weight: 500; margin-bottom: 4px">参数</div>
                    <pre class="ai-pre">{{ formatJson(row.params) }}</pre>
                    <div style="font-weight: 500; margin: 8px 0 4px">结果摘要</div>
                    <pre class="ai-pre">{{ row.resultSummary || '-' }}</pre>
                    <div v-if="row.errorMessage" style="font-weight: 500; margin: 8px 0 4px">错误</div>
                    <pre v-if="row.errorMessage" class="ai-pre is-error">{{ row.errorMessage }}</pre>
                  </div>
                </el-popover>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            style="margin-top: 12px; justify-content: flex-end"
            @size-change="loadList"
            @current-change="loadList"
          />
        </el-tab-pane>

        <!-- ============ Tab 2：会话浏览 ============ -->
        <el-tab-pane label="会话浏览" name="sessions">
          <div class="ai-toolbar" style="margin-bottom: 8px">
            <el-input
              v-model="sessionSearch.keyword"
              clearable
              placeholder="标题 / 会话号"
              style="width: 220px"
              @keyup.enter="loadSessions"
            />
            <el-input
              v-model="sessionSearch.employeeCode"
              clearable
              placeholder="数字员工编码"
              style="width: 200px"
              @keyup.enter="loadSessions"
            />
            <el-input
              v-model.number="(sessionSearch as any).userId"
              clearable
              placeholder="用户ID"
              style="width: 120px"
              @keyup.enter="loadSessions"
            />
            <el-button type="primary" @click="loadSessions">查询</el-button>
            <el-button @click="resetSessionSearch">重置</el-button>
          </div>

          <el-table
            v-loading="sessionLoading"
            :data="sessions"
            row-key="id"
            border
            highlight-current-row
            @row-click="openSessionDetail"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="employeeName" label="数字员工" width="160" />
            <el-table-column prop="userId" label="用户ID" width="100" />
            <el-table-column prop="messageCount" label="消息数" width="90" />
            <el-table-column label="Tokens (P/C)" width="160">
              <template #default="{ row }">
                {{ row.totalPromptTokens }} / {{ row.totalCompletionTokens }}
              </template>
            </el-table-column>
            <el-table-column prop="lastMessageAt" label="最后消息" width="170" />
            <el-table-column prop="createdAt" label="创建时间" width="170" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click.stop="openSessionDetail(row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="sessionPage"
            v-model:page-size="sessionPageSize"
            :total="sessionTotal"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            style="margin-top: 12px; justify-content: flex-end"
            @size-change="loadSessions"
            @current-change="loadSessions"
          />
        </el-tab-pane>
      </el-tabs>
    </ele-card>

    <!-- ============ 会话详情抽屉 ============ -->
    <el-drawer
      v-model="detailVisible"
      :title="`会话回放：${detailSession?.title || detailSession?.sessionNo || ''}`"
      direction="rtl"
      size="50%"
    >
      <div v-if="detailLoading" style="padding: 24px; text-align: center">加载中…</div>
      <div v-else>
        <div v-if="detailSession" class="ai-detail-meta">
          <div><span class="ai-detail-meta__k">租户：</span>{{ tenantCode }}</div>
          <div><span class="ai-detail-meta__k">数字员工：</span>{{ detailSession.employeeName }} ({{ detailSession.employeeCode }})</div>
          <div><span class="ai-detail-meta__k">用户ID：</span>{{ detailSession.userId }}</div>
          <div><span class="ai-detail-meta__k">消息数：</span>{{ detailSession.messageCount }}</div>
          <div><span class="ai-detail-meta__k">Tokens：</span>{{ detailSession.totalPromptTokens }} / {{ detailSession.totalCompletionTokens }}</div>
        </div>

        <div v-if="!detailMessages.length" style="padding: 24px; color: #999; text-align: center">
          暂无消息
        </div>
        <div v-else class="ai-msg-stream">
          <div
            v-for="m in detailMessages"
            :key="m.id"
            class="ai-msg"
            :class="`ai-msg--${m.role}`"
          >
            <div class="ai-msg__header">
              <el-tag size="small" :type="roleTagType(m.role)">{{ m.role }}</el-tag>
              <span v-if="m.toolName" class="ai-msg__tool">{{ m.toolName }}</span>
              <span v-if="m.modelUsed" class="ai-msg__model">{{ m.modelUsed }}</span>
              <span v-if="m.finishReason" class="ai-msg__finish">{{ m.finishReason }}</span>
              <span class="ai-msg__time">{{ m.createdAt }}</span>
            </div>
            <div v-if="m.content" class="ai-msg__body">{{ m.content }}</div>
            <div v-if="m.toolCalls?.length" class="ai-msg__toolcalls">
              <div v-for="(tc, idx) in m.toolCalls" :key="idx" class="ai-msg__tc">
                <div class="ai-msg__tc-title">
                  <el-icon><tools /></el-icon>
                  {{ tc.function?.name || tc.name }}
                </div>
                <pre class="ai-pre">{{ tc.function?.arguments || tc.arguments }}</pre>
              </div>
            </div>
            <div v-if="m.errorMessage" class="ai-msg__error">{{ m.errorMessage }}</div>
          </div>
        </div>
      </div>
    </el-drawer>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessage } from 'element-plus';
  import { Tools } from '@element-plus/icons-vue';
  import {
    getObserveSessionMessages,
    getTenantStats,
    listAuditTenants,
    pageObserveSessions,
    pageToolLogs
  } from '@/api/ai';
  import type {
    AiMessageRow,
    AiSessionRow,
    AiStats,
    AiToolLog
  } from '@/api/ai/model';

  defineOptions({ name: 'AiObserveDashboard' });

  const tenants = ref<string[]>([]);
  const tenantCode = ref<string>('');
  const activeTab = ref<'tools' | 'sessions'>('tools');

  // ============ 工具调用日志 ============
  const loading = ref(false);
  const list = ref<AiToolLog[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(20);
  const searchForm = reactive<{
    sessionId?: number;
    toolCode?: string;
    status?: string;
  }>({});

  const stats = ref<AiStats | null>(null);
  const statsDays = ref(7);

  function statusType(s: string) {
    switch (s) {
      case 'success':
        return 'success';
      case 'failed':
      case 'denied':
        return 'danger';
      case 'pending_confirm':
        return 'warning';
      default:
        return 'info';
    }
  }

  function formatJson(v: any): string {
    try {
      return JSON.stringify(v, null, 2);
    } catch {
      return String(v);
    }
  }

  async function loadTenants() {
    try {
      tenants.value = await listAuditTenants();
      if (!tenantCode.value && tenants.value.length) {
        tenantCode.value = tenants.value[0];
        await loadAll();
      }
    } catch (e: any) {
      ElMessage.error(e?.message || '加载租户列表失败');
    }
  }

  async function loadStats() {
    if (!tenantCode.value) return;
    try {
      stats.value = await getTenantStats(tenantCode.value, statsDays.value);
    } catch {
      stats.value = null;
    }
  }

  async function loadList() {
    if (!tenantCode.value) {
      ElMessage.warning('请选择租户');
      return;
    }
    loading.value = true;
    try {
      const data = await pageToolLogs({
        tenantCode: tenantCode.value,
        page: page.value,
        limit: pageSize.value,
        ...searchForm
      });
      list.value = (data?.list ?? []) as AiToolLog[];
      total.value = data?.total ?? 0;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载失败');
    } finally {
      loading.value = false;
    }
  }

  function resetSearch() {
    searchForm.sessionId = undefined;
    searchForm.toolCode = '';
    searchForm.status = undefined;
    page.value = 1;
    loadList();
  }

  // ============ 会话浏览 ============
  const sessionLoading = ref(false);
  const sessions = ref<AiSessionRow[]>([]);
  const sessionTotal = ref(0);
  const sessionPage = ref(1);
  const sessionPageSize = ref(20);
  const sessionSearch = reactive<{
    keyword?: string;
    employeeCode?: string;
    userId?: number;
  }>({});

  const detailVisible = ref(false);
  const detailLoading = ref(false);
  const detailSession = ref<AiSessionRow | null>(null);
  const detailMessages = ref<AiMessageRow[]>([]);

  async function loadSessions() {
    if (!tenantCode.value) {
      ElMessage.warning('请选择租户');
      return;
    }
    sessionLoading.value = true;
    try {
      const data = await pageObserveSessions({
        tenantCode: tenantCode.value,
        page: sessionPage.value,
        limit: sessionPageSize.value,
        ...sessionSearch
      });
      sessions.value = (data?.list ?? []) as AiSessionRow[];
      sessionTotal.value = data?.total ?? 0;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载会话失败');
    } finally {
      sessionLoading.value = false;
    }
  }

  function resetSessionSearch() {
    sessionSearch.keyword = '';
    sessionSearch.employeeCode = '';
    sessionSearch.userId = undefined;
    sessionPage.value = 1;
    loadSessions();
  }

  async function openSessionDetail(row: AiSessionRow) {
    detailVisible.value = true;
    detailLoading.value = true;
    detailSession.value = row;
    detailMessages.value = [];
    try {
      const data = await getObserveSessionMessages(row.id, tenantCode.value);
      detailMessages.value = (data?.messages ?? []) as AiMessageRow[];
      if (data?.session) detailSession.value = data.session as AiSessionRow;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载消息失败');
    } finally {
      detailLoading.value = false;
    }
  }

  function roleTagType(role: string) {
    switch (role) {
      case 'user':
        return 'info';
      case 'assistant':
        return 'success';
      case 'tool':
        return 'warning';
      default:
        return 'primary';
    }
  }

  // ============ 公共 ============

  async function onTenantChange() {
    page.value = 1;
    sessionPage.value = 1;
    await loadAll();
  }

  async function loadAll() {
    await Promise.all([loadStats(), loadList(), loadSessions()]);
  }

  onMounted(loadTenants);
</script>

<style lang="scss" scoped>
  .ai-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .ai-stat-card {
    text-align: left;
    &__title {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__value {
      font-size: 24px;
      font-weight: 600;
      margin-top: 4px;
    }
  }
  .ai-pre {
    margin: 0;
    padding: 8px;
    background: var(--el-fill-color-light);
    border-radius: 4px;
    font-size: 12px;
    max-height: 240px;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-all;
    &.is-error {
      color: var(--el-color-danger);
    }
  }

  .ai-detail-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 24px;
    padding: 12px 16px;
    background: var(--el-fill-color-light);
    border-radius: 6px;
    margin: 0 16px 12px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    &__k {
      color: var(--el-text-color-secondary);
      margin-right: 4px;
    }
  }

  .ai-msg-stream {
    padding: 0 16px 24px;
  }
  .ai-msg {
    border-left: 3px solid transparent;
    padding: 10px 12px;
    margin-bottom: 12px;
    border-radius: 4px;
    background: var(--el-bg-color);
    box-shadow: var(--el-box-shadow-lighter);
    &--user {
      border-left-color: var(--el-color-info);
    }
    &--assistant {
      border-left-color: var(--el-color-success);
    }
    &--tool {
      border-left-color: var(--el-color-warning);
      background: var(--el-fill-color-light);
    }
    &__header {
      display: flex;
      gap: 8px;
      align-items: center;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-bottom: 6px;
      flex-wrap: wrap;
    }
    &__tool,
    &__model,
    &__finish {
      padding: 0 6px;
      border-radius: 3px;
      background: var(--el-fill-color);
    }
    &__time {
      margin-left: auto;
    }
    &__body {
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.7;
      color: var(--el-text-color-primary);
    }
    &__toolcalls {
      margin-top: 8px;
    }
    &__tc {
      margin-top: 6px;
    }
    &__tc-title {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-bottom: 4px;
    }
    &__error {
      margin-top: 6px;
      padding: 6px 8px;
      background: var(--el-color-danger-light-9);
      color: var(--el-color-danger);
      border-radius: 4px;
      font-size: 12px;
    }
  }
</style>
