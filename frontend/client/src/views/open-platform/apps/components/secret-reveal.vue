<template>
  <ele-modal
    :width="620"
    :title="title"
    :close-on-click-modal="false"
    v-bind="modalProps"
  >
    <el-alert
      type="warning"
      :closable="false"
      show-icon
      title="以下信息仅显示这一次"
      description="关闭后将无法再次查看，请立即复制并妥善保存。若遗失只能重新生成。"
      style="margin-bottom: 16px"
    />

    <template v-if="mode === 'credential'">
      <div class="op-field">
        <div class="op-field__label">AppKey（公开标识）</div>
        <div class="op-field__value">
          <span class="op-code">{{ accessKey }}</span>
          <el-button link type="primary" @click="copy(accessKey)"
            >复制</el-button
          >
        </div>
      </div>
      <div class="op-field">
        <div class="op-field__label">AppSecret（密钥，务必保密）</div>
        <div class="op-field__value">
          <span class="op-code">{{ secret }}</span>
          <el-button link type="primary" @click="copy(secret)">复制</el-button>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="op-field">
        <div class="op-field__label">连接地址</div>
        <div class="op-field__value">
          <span class="op-code">{{ url }}</span>
          <el-button link type="primary" @click="copy(url)">复制</el-button>
        </div>
      </div>
      <div class="op-field">
        <div class="op-field__label">访问 Token</div>
        <div class="op-field__value">
          <span class="op-code">{{ token }}</span>
          <el-button link type="primary" @click="copy(token)">复制</el-button>
        </div>
      </div>
      <div class="op-field">
        <div class="op-field__label">
          一键配置（把下面整段复制到你的 AI 工具的 MCP 配置里）
        </div>
        <div class="op-json-wrap">
          <pre class="op-json">{{ configText }}</pre>
          <el-button
            class="op-json-copy"
            size="small"
            type="primary"
            @click="copy(configText)"
          >
            复制配置
          </el-button>
        </div>
      </div>
    </template>

    <template #footer>
      <el-button type="primary" @click="closeModal()">我已保存，关闭</el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { copyText } from '../../constants';

  const props = defineProps<{
    mode: 'credential' | 'mcp';
    /** credential 模式 */
    accessKey?: string;
    secret?: string;
    /** mcp 模式 */
    url?: string;
    token?: string;
    configJson?: Record<string, any>;
  }>();

  const { modalProps, closeModal } = useModal();

  const title = computed(() =>
    props.mode === 'credential' ? '密钥已生成' : 'MCP 连接已创建'
  );

  const configText = computed(() =>
    props.configJson ? JSON.stringify(props.configJson, null, 2) : ''
  );

  const copy = async (text?: string) => {
    if (!text) return;
    const ok = await copyText(text);
    if (ok) {
      EleMessage.success({ message: '已复制到剪贴板', plain: true });
    } else {
      EleMessage.error({ message: '复制失败，请手动选中复制', plain: true });
    }
  };
</script>

<style lang="scss" scoped>
  .op-field {
    margin-bottom: 16px;
  }
  .op-field__label {
    color: var(--el-text-color-secondary);
    font-size: 13px;
    margin-bottom: 6px;
  }
  .op-field__value {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .op-code {
    flex: 1;
    background: var(--el-fill-color-light);
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'Consolas', 'Monaco', monospace;
    word-break: break-all;
  }
  .op-json-wrap {
    position: relative;
  }
  .op-json {
    background: var(--el-fill-color-light);
    border-radius: 6px;
    padding: 12px;
    margin: 0;
    font-size: 12px;
    max-height: 260px;
    overflow: auto;
  }
  .op-json-copy {
    position: absolute;
    top: 8px;
    right: 8px;
  }
</style>
