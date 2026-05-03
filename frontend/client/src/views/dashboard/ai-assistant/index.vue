<template>
  <div class="ai-assistant">
    <!-- 左栏 -->
    <aside class="ai-assistant__aside">
      <employee-list
        :employees="employees"
        v-model="currentEmployeeCode"
        @update:modelValue="onEmployeeChange"
      />
      <el-divider style="margin: 8px 0" />
      <session-list
        :sessions="sessions"
        v-model="currentSessionId"
        @update:modelValue="loadSessionMessages"
        @new="startNewSession"
        @delete="handleDeleteSession"
        @rename="handleRenameSession"
      />
    </aside>

    <!-- 中栏：对话 -->
    <main class="ai-assistant__main">
      <header class="ai-assistant__header">
        <div class="ai-assistant__title">
          <el-avatar
            :size="28"
            :src="employeeAvatarSrc"
            style="margin-right: 8px"
          >
            <el-icon><chat-line-square /></el-icon>
          </el-avatar>
          <span>{{ currentEmployee?.name || '请选择数字员工' }}</span>
          <el-tag v-if="currentEmployee" size="small" effect="plain" style="margin-left: 8px">
            {{ empTypeText(currentEmployee.employeeType) }}
          </el-tag>
        </div>
        <div class="ai-assistant__sub">
          {{ currentEmployee?.description || '企业数字员工 · 高级版' }}
        </div>
      </header>

      <div ref="scrollerRef" class="ai-assistant__scroll">
        <!-- 欢迎语 + 建议提问 -->
        <div v-if="!turns.length && currentEmployee" class="ai-welcome">
          <el-card shadow="never" class="ai-welcome__card">
            <div class="ai-welcome__title">
              你好，我是「{{ currentEmployee.name }}」
            </div>
            <div v-if="currentEmployee.welcomeMessage" class="ai-welcome__msg">
              {{ currentEmployee.welcomeMessage }}
            </div>
            <div
              v-if="currentEmployee.suggestedQuestions?.length"
              class="ai-welcome__chips"
            >
              <el-tag
                v-for="(q, idx) in currentEmployee.suggestedQuestions"
                :key="idx"
                effect="plain"
                style="cursor: pointer; margin: 4px 6px 0 0"
                @click="sendQuick(q)"
              >
                {{ q }}
              </el-tag>
            </div>
          </el-card>
        </div>

        <message-bubble
          v-for="t in turns"
          :key="t.id"
          :turn="t"
          @confirm="handleToolConfirm"
        />

        <div v-if="streaming" class="ai-streaming-tip">
          <el-icon class="is-loading"><loading /></el-icon>
          数字员工正在思考…
          <el-button text size="small" type="danger" @click="handleAbort">中止</el-button>
        </div>
      </div>

      <chat-input
        :disabled="streaming || !currentEmployee"
        :placeholder="
          !currentEmployee ? '请先在左侧选择数字员工' : '描述你的需求…（支持上传 Excel/CSV）'
        "
        @send="handleSend"
      />
    </main>

    <!-- 右栏：可用工具 -->
    <aside class="ai-assistant__rightside">
      <div class="ai-aside-section">
        <div class="ai-aside-section__title">可用工具</div>
        <div v-if="!employeeTools.length" class="ai-aside-section__empty">
          该数字员工尚未绑定工具
        </div>
        <div v-for="t in employeeTools" :key="t.code" class="ai-tool-item">
          <div class="ai-tool-item__header">
            <span class="ai-tool-item__name">{{ t.name }}</span>
            <el-tag
              v-if="t.riskLevel === 'high'"
              size="small"
              type="warning"
              effect="light"
            >高风险</el-tag>
          </div>
          <div v-if="t.description" class="ai-tool-item__desc">
            {{ t.description }}
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, reactive, ref } from 'vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import {
    ChatLineSquare,
    Loading
  } from '@element-plus/icons-vue';
  import {
    deleteAiSession,
    listAiEmployees,
    listEmployeeTools,
    listSessionMessages,
    pageAiSessions,
    renameAiSession
  } from '@/api/ai';
  import {
    postChatConfirm,
    postChatStream
  } from '@/api/ai/chat-stream';
  import type {
    AiAttachment,
    AiEmployee,
    AiEmployeeTool,
    AiMessage,
    AiSession,
    AiSseEvent,
    ChatTurn,
    ToolCallEntry
  } from '@/api/ai/model';
  import EmployeeList from './components/employee-list.vue';
  import SessionList from './components/session-list.vue';
  import MessageBubble from './components/message-bubble.vue';
  import ChatInput from './components/chat-input.vue';

  defineOptions({ name: 'DashboardAiAssistant' });

  const employees = ref<AiEmployee[]>([]);
  const sessions = ref<AiSession[]>([]);
  const employeeTools = ref<AiEmployeeTool[]>([]);
  const currentEmployeeCode = ref<string>('');
  const currentSessionId = ref<number | null>(null);
  const turns = ref<ChatTurn[]>([]);
  const streaming = ref(false);
  const scrollerRef = ref<HTMLElement | null>(null);

  let abortCtrl: AbortController | null = null;

  // ============ 打字机平滑层 ============
  // 后端推下来的 delta chunk 粒度参差不齐（Kimi 常常一次半句话）。
  // 这里把每个字符塞进一个队列，按固定节奏输出到 turn.content；
  // 队列堆积越多吐字越快，避免长回复也"卡顿"。
  interface TyperState {
    buffer: string;
    timer: any;
    finished: boolean;
    onFlush?: () => void;
  }
  const typerMap = new WeakMap<ChatTurn, TyperState>();

  function getTyper(turn: ChatTurn): TyperState {
    let st = typerMap.get(turn);
    if (!st) {
      st = { buffer: '', timer: null, finished: false };
      typerMap.set(turn, st);
    }
    return st;
  }

  function pushDelta(turn: ChatTurn, text: string) {
    if (!text) return;
    const st = getTyper(turn);
    st.buffer += text;
    startTyper(turn, st);
  }

  function startTyper(turn: ChatTurn, st: TyperState) {
    if (st.timer) return;
    const tick = () => {
      if (st.buffer.length === 0) {
        st.timer = null;
        st.onFlush?.();
        return;
      }
      // 缓冲越多每帧吐越多字符，保持节奏感（>200 时近乎一次吐完）
      const len = st.buffer.length;
      let take = 1;
      if (len > 200) take = Math.min(len, 16);
      else if (len > 80) take = 6;
      else if (len > 30) take = 3;
      else if (len > 10) take = 2;
      const piece = st.buffer.slice(0, take);
      st.buffer = st.buffer.slice(take);
      turn.content += piece;
      scrollToBottomThrottled();
      st.timer = setTimeout(tick, 24); // ~42fps，对 CJK 视觉就很顺
    };
    st.timer = setTimeout(tick, 0);
  }

  /** 当后端流结束时调用：等队列吐完后再触发 cb */
  function flushTyper(turn: ChatTurn, cb?: () => void) {
    const st = getTyper(turn);
    st.finished = true;
    if (st.buffer.length === 0 && !st.timer) {
      cb?.();
      return;
    }
    st.onFlush = cb;
  }

  const currentEmployee = computed<AiEmployee | undefined>(() =>
    employees.value.find((e) => e.code === currentEmployeeCode.value)
  );
  const employeeAvatarSrc = computed(() => {
    const p = (currentEmployee.value?.avatar || '').trim();
    if (!p) return '';
    if (p.startsWith('http://') || p.startsWith('https://') || p.startsWith('data:')) {
      return p;
    }
    return p.startsWith('/') ? p : `/${p}`;
  });

  function empTypeText(t?: string): string {
    switch (t) {
      case 'form_recorder':
        return '录单员';
      case 'data_analyst':
        return '数据分析员';
      case 'archivist':
        return '档案管理员';
      default:
        return '数字员工';
    }
  }

  onMounted(async () => {
    await loadEmployees();
    await loadSessions();
  });

  async function loadEmployees() {
    try {
      employees.value = await listAiEmployees();
      if (employees.value.length && !currentEmployeeCode.value) {
        await onEmployeeChange(employees.value[0].code);
      }
    } catch (e: any) {
      ElMessage.error(e?.message || '加载数字员工失败');
    }
  }

  async function loadSessions() {
    try {
      const data = await pageAiSessions({
        page: 1,
        limit: 50,
        employeeCode: currentEmployeeCode.value || undefined
      });
      sessions.value = data?.list ?? [];
    } catch (e: any) {
      ElMessage.error(e?.message || '加载会话列表失败');
    }
  }

  async function onEmployeeChange(code: string) {
    currentEmployeeCode.value = code;
    currentSessionId.value = null;
    turns.value = [];
    try {
      employeeTools.value = await listEmployeeTools(code);
    } catch (e: any) {
      employeeTools.value = [];
    }
    await loadSessions();
  }

  function startNewSession() {
    currentSessionId.value = null;
    turns.value = [];
  }

  async function handleRenameSession(id: number, title: string) {
    try {
      await renameAiSession(id, title);
      const target = sessions.value.find((x) => x.id === id);
      if (target) target.title = title;
      ElMessage.success('已更新会话名称');
    } catch (e: any) {
      ElMessage.error(e?.message || '重命名失败');
    }
  }

  async function handleDeleteSession(id: number) {
    try {
      await ElMessageBox.confirm('确定删除该会话？', '提示', { type: 'warning' });
    } catch {
      return;
    }
    try {
      await deleteAiSession(id);
      ElMessage.success('已删除');
      if (currentSessionId.value === id) startNewSession();
      await loadSessions();
    } catch (e: any) {
      ElMessage.error(e?.message || '删除失败');
    }
  }

  async function loadSessionMessages(id: number) {
    if (!id) return;
    currentSessionId.value = id;
    try {
      const msgs = await listSessionMessages(id, 200);
      turns.value = mergeMessagesToTurns(msgs);
      await scrollToBottom();
    } catch (e: any) {
      ElMessage.error(e?.message || '加载消息失败');
    }
  }

  /** 把 DB 消息列表聚合成前端 turns（按 user / assistant 切分；tool 归到上一个 assistant） */
  function mergeMessagesToTurns(msgs: AiMessage[]): ChatTurn[] {
    const out: ChatTurn[] = [];
    let lastAssistant: ChatTurn | null = null;

    for (const m of msgs) {
      if (m.role === 'user') {
        out.push({
          id: `u-${m.id}`,
          role: 'user',
          content: m.content || '',
          attachments: m.attachments || [],
          toolCalls: [],
          createdAt: m.createdAt || ''
        });
        lastAssistant = null;
      } else if (m.role === 'assistant') {
        const turn: ChatTurn = {
          id: `a-${m.id}`,
          role: 'assistant',
          content: m.content || '',
          toolCalls: (m.toolCalls || []).map((tc: any) => ({
            toolCallId: tc.id || '',
            toolCode: tc.function?.name || tc.name || '',
            status: 'success'
          })),
          createdAt: m.createdAt || ''
        };
        out.push(turn);
        lastAssistant = turn;
      } else if (m.role === 'tool' && lastAssistant) {
        // 找到对应的 toolCall 项，写入摘要
        const target = lastAssistant.toolCalls.find(
          (x) => x.toolCallId === m.toolCallId
        );
        if (target) {
          target.summary = m.content || '';
        } else {
          lastAssistant.toolCalls.push({
            toolCallId: m.toolCallId || '',
            toolCode: m.toolName || '',
            toolName: m.toolName,
            status: 'success',
            summary: m.content || ''
          });
        }
      }
    }
    return out;
  }

  function sendQuick(q: string) {
    handleSend({ content: q, attachments: [] });
  }

  async function handleSend(payload: { content: string; attachments: AiAttachment[] }) {
    if (!currentEmployeeCode.value) {
      ElMessage.warning('请先选择数字员工');
      return;
    }
    if (!payload.content && !payload.attachments.length) return;

    // 必须用 reactive() 显式包装，再 push 进 turns；
    // 否则后续 SSE 回调里通过原始引用（如 assistantTurn.content += ...）
    // 修改的是非响应式对象，UI 不会更新。
    const userTurn = reactive<ChatTurn>({
      id: `u-tmp-${Date.now()}`,
      role: 'user',
      content: payload.content,
      attachments: payload.attachments,
      toolCalls: [],
      createdAt: nowText()
    });
    const assistantTurn = reactive<ChatTurn>({
      id: `a-tmp-${Date.now()}`,
      role: 'assistant',
      content: '',
      pending: true,
      toolCalls: [],
      createdAt: nowText()
    });
    turns.value.push(userTurn, assistantTurn);
    await scrollToBottom();

    streaming.value = true;
    abortCtrl = new AbortController();

    await postChatStream(
      {
        employeeCode: currentEmployeeCode.value,
        sessionId: currentSessionId.value || undefined,
        content: payload.content,
        attachments: payload.attachments
      },
      {
        signal: abortCtrl.signal,
        onEvent: (evt) => handleSseEvent(evt, assistantTurn),
        onError: (err) => {
          assistantTurn.pending = false;
          streaming.value = false;
          assistantTurn.content +=
            (assistantTurn.content ? '\n\n' : '') + `[错误] ${err.message}`;
        },
        onDone: async () => {
          // 等打字机把队列吐完再关 streaming 状态
          flushTyper(assistantTurn, async () => {
            streaming.value = false;
            assistantTurn.pending = false;
            await loadSessions();
            await scrollToBottom();
          });
        }
      }
    );
  }

  function handleSseEvent(evt: AiSseEvent, assistantTurn: ChatTurn) {
    switch (evt.event) {
      case 'session':
        if (evt.data?.sessionId) currentSessionId.value = evt.data.sessionId;
        break;
      case 'delta':
        if (evt.data?.content) pushDelta(assistantTurn, evt.data.content);
        break;
      case 'tool.call': {
        const entry: ToolCallEntry = {
          toolCallId: evt.data.tool_call_id,
          toolCode: evt.data.tool_code,
          toolName: evt.data.tool_name,
          status: 'calling',
          riskLevel: evt.data.risk_level,
          params: evt.data.params
        };
        assistantTurn.toolCalls.push(entry);
        break;
      }
      case 'tool.result': {
        const entry = assistantTurn.toolCalls.find(
          (x) => x.toolCallId === evt.data.tool_call_id
        );
        if (entry) {
          entry.status = (evt.data.status || 'success') as ToolCallEntry['status'];
          entry.summary = evt.data.summary;
          entry.error = evt.data.error;
          entry.latencyMs = evt.data.latency_ms;
        }
        break;
      }
      case 'confirm.required': {
        const entry: ToolCallEntry = {
          toolCallId: evt.data.tool_call_id,
          toolCode: evt.data.tool_code,
          toolName: evt.data.tool_name,
          status: 'pending_confirm',
          riskLevel: evt.data.risk_level,
          params: evt.data.params,
          confirmToken: evt.data.confirm_token
        };
        assistantTurn.toolCalls.push(entry);
        break;
      }
      case 'done':
        // 等打字机吐完队列后再清 pending
        flushTyper(assistantTurn, () => {
          assistantTurn.pending = false;
        });
        break;
      case 'error':
        assistantTurn.pending = false;
        assistantTurn.content +=
          (assistantTurn.content ? '\n\n' : '') +
          `[错误] ${evt.data?.message || '服务异常'}`;
        break;
    }
  }

  async function handleToolConfirm(entry: ToolCallEntry, approved: boolean) {
    if (!entry.confirmToken || !currentSessionId.value) return;
    entry.status = approved ? 'calling' : 'cancelled';

    const lastAssistant = [...turns.value]
      .reverse()
      .find((t) => t.role === 'assistant');
    const followUpAssistant = reactive<ChatTurn>({
      id: `a-tmp-${Date.now()}`,
      role: 'assistant',
      content: '',
      pending: true,
      toolCalls: [],
      createdAt: nowText()
    });
    turns.value.push(followUpAssistant);

    streaming.value = true;
    abortCtrl = new AbortController();

    await postChatConfirm(
      {
        sessionId: currentSessionId.value,
        confirmToken: entry.confirmToken,
        approved
      },
      {
        signal: abortCtrl.signal,
        onEvent: (evt) => {
          // tool.result 事件可能针对老的 entry，也可能产生新工具调用
          if (
            evt.event === 'tool.result' &&
            evt.data.tool_call_id === entry.toolCallId &&
            lastAssistant
          ) {
            const target = lastAssistant.toolCalls.find(
              (x) => x.toolCallId === entry.toolCallId
            );
            if (target) {
              target.status = (evt.data.status ||
                'success') as ToolCallEntry['status'];
              target.summary = evt.data.summary;
              target.error = evt.data.error;
              target.latencyMs = evt.data.latency_ms;
            }
            return;
          }
          handleSseEvent(evt, followUpAssistant);
        },
        onError: (err) => {
          followUpAssistant.pending = false;
          streaming.value = false;
          followUpAssistant.content +=
            (followUpAssistant.content ? '\n\n' : '') + `[错误] ${err.message}`;
        },
        onDone: async () => {
          flushTyper(followUpAssistant, async () => {
            streaming.value = false;
            followUpAssistant.pending = false;
            await loadSessions();
            await scrollToBottom();
          });
        }
      }
    );
  }

  function handleAbort() {
    abortCtrl?.abort();
    streaming.value = false;
  }

  async function scrollToBottom() {
    await nextTick();
    if (scrollerRef.value) {
      scrollerRef.value.scrollTop = scrollerRef.value.scrollHeight;
    }
  }
  let _scrollTimer: any = null;
  function scrollToBottomThrottled() {
    if (_scrollTimer) return;
    _scrollTimer = setTimeout(() => {
      _scrollTimer = null;
      scrollToBottom();
    }, 80);
  }

  function nowText(): string {
    const d = new Date();
    const pad = (n: number) => `${n}`.padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }
</script>

<style lang="scss" scoped>
  .ai-assistant {
    display: grid;
    grid-template-columns: 260px 1fr 280px;
    gap: 12px;
    height: calc(100vh - 120px);
    min-height: 500px;
    padding: 12px;

    &__aside {
      background: var(--el-bg-color);
      border-radius: 8px;
      padding: 8px;
      overflow-y: auto;
      box-shadow: var(--el-box-shadow-lighter);
    }
    &__rightside {
      background: var(--el-bg-color);
      border-radius: 8px;
      padding: 12px;
      overflow-y: auto;
      box-shadow: var(--el-box-shadow-lighter);
    }
    &__main {
      display: flex;
      flex-direction: column;
      background: var(--el-bg-color);
      border-radius: 8px;
      box-shadow: var(--el-box-shadow-lighter);
      overflow: hidden;
    }
    &__header {
      padding: 12px 16px;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }
    &__title {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 600;
    }
    &__sub {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
    &__scroll {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      background: var(--el-fill-color-blank);
    }
  }

  .ai-welcome {
    display: flex;
    justify-content: center;
    margin-top: 40px;
    &__card {
      width: 100%;
      max-width: 560px;
    }
    &__title {
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
    &__msg {
      margin-top: 8px;
      color: var(--el-text-color-secondary);
      line-height: 1.7;
    }
    &__chips {
      margin-top: 12px;
      display: flex;
      flex-wrap: wrap;
    }
  }

  .ai-streaming-tip {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
    margin-top: 8px;
  }

  .ai-aside-section {
    &__title {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-bottom: 8px;
    }
    &__empty {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }
  }
  .ai-tool-item {
    padding: 8px 10px;
    border-radius: 6px;
    background: var(--el-fill-color-light);
    margin-bottom: 6px;
    &__header {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    &__name {
      font-size: 13px;
      font-weight: 500;
    }
    &__desc {
      margin-top: 4px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      line-height: 1.6;
    }
  }

  @media (max-width: 1200px) {
    .ai-assistant {
      grid-template-columns: 240px 1fr;
    }
    .ai-assistant__rightside {
      display: none;
    }
  }
</style>
