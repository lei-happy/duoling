<template>
  <el-dialog
    v-model="visible"
    width="760px"
    :align-center="true"
    append-to-body
    class="op-cap-dialog"
    @closed="onClosed"
  >
    <template #header>
      <div class="op-cap-head" v-if="cap">
        <div class="op-cap-head__title">
          <span class="op-cap-head__name">{{ cap.name }}</span>
          <el-tag
            v-for="c in cap.channels"
            :key="c"
            size="small"
            round
            :type="c === 'api' ? 'primary' : 'success'"
            :disable-transitions="true"
          >
            {{ c === 'api' ? 'API' : 'MCP' }}
          </el-tag>
          <el-tag
            size="small"
            round
            :type="cap.read_only ? 'success' : 'warning'"
            :disable-transitions="true"
          >
            {{ cap.read_only ? '只读' : '写操作' }}
          </el-tag>
        </div>
        <div class="op-cap-head__code">{{ cap.code }}</div>
      </div>
    </template>

    <div class="op-cap-body" v-if="cap">
      <p class="op-cap-desc">{{ cap.description || '暂无说明' }}</p>

      <el-tabs v-model="activeTab" class="op-cap-tabs">
        <!-- API 请求 -->
        <el-tab-pane v-if="hasApi" label="API 请求" name="api">
          <div class="op-cap-section">
            <div class="op-cap-section__head">
              <span class="op-cap-section__title">请求示例</span>
              <el-button link type="primary" @click="copy(curlExample)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="curlExample" language="bash" class="op-code" />
          </div>

          <div class="op-cap-section" v-if="requestBody">
            <div class="op-cap-section__head">
              <span class="op-cap-section__title">请求参数（body）</span>
              <el-button link type="primary" @click="copy(requestBody)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="requestBody" language="json" class="op-code" />
          </div>
        </el-tab-pane>

        <!-- MCP 工具 -->
        <el-tab-pane v-if="hasMcp" label="MCP 工具" name="mcp">
          <div class="op-cap-fields">
            <div class="op-cap-field">
              <span class="op-cap-field__label">工具名</span>
              <span class="op-code-inline">{{ mcpToolName }}</span>
            </div>
            <div class="op-cap-field">
              <span class="op-cap-field__label">显示名称</span>
              <span>{{ cap.name }}</span>
            </div>
            <div class="op-cap-field">
              <span class="op-cap-field__label">描述</span>
              <span>{{ cap.description || '暂无描述' }}</span>
            </div>
          </div>
          <div class="op-cap-section">
            <div class="op-cap-section__head">
              <span class="op-cap-section__title">入参 Schema</span>
              <el-button link type="primary" @click="copy(inputSchemaText)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer
              :code="inputSchemaText"
              language="json"
              class="op-code"
            />
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- 返回字段 -->
      <div class="op-cap-section op-cap-section--return">
        <div class="op-cap-section__title">返回字段</div>
        <div class="op-cap-return">
          <template v-if="(cap.output_fields || []).length">
            <el-tag
              v-for="f in cap.output_fields"
              :key="f"
              size="small"
              type="info"
              class="op-return-tag"
              :disable-transitions="true"
            >
              {{ f }}
            </el-tag>
          </template>
          <span v-else class="op-cap-muted">按能力默认返回全部字段</span>
        </div>
        <div class="op-cap-note">
          敏感字段（如手机号、身份证）会自动脱敏后返回，无需额外处理。
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { CopyDocument } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import CodeViewer from '@/components/CodeViewer/index.vue';
  import type { Capability } from '@/api/open-platform/model';
  import { copyText } from '../../constants';

  defineOptions({ name: 'CapabilityDetail' });

  const visible = ref(false);
  const activeTab = ref('api');
  const cap = ref<Capability | null>(null);

  const hasApi = computed(() => (cap.value?.channels || []).includes('api'));
  const hasMcp = computed(() => (cap.value?.channels || []).includes('mcp'));

  const mcpToolName = computed(() =>
    (cap.value?.code || '').replace(/\./g, '_')
  );

  /** 从 input_schema 推导示例入参；无 schema 时按查询类给通用参数 */
  const sampleBody = computed<Record<string, any>>(() => {
    const c = cap.value;
    if (!c) return {};
    const schema = c.input_schema;
    if (schema && schema.properties) {
      const out: Record<string, any> = {};
      Object.keys(schema.properties).forEach((k) => {
        const t = schema.properties[k]?.type;
        out[k] =
          t === 'integer' || t === 'number'
            ? 1
            : t === 'boolean'
              ? true
              : t === 'array'
                ? []
                : '示例值';
      });
      return out;
    }
    if (c.code.endsWith('.query')) {
      return { keyword: '示例', page: 1, pageSize: 20 };
    }
    return {};
  });

  const requestBody = computed(() => {
    const body = sampleBody.value;
    if (!Object.keys(body).length) return '';
    return JSON.stringify(body, null, 2);
  });

  const inputSchemaText = computed(() => {
    const schema = cap.value?.input_schema || {
      type: 'object',
      properties: cap.value?.code.endsWith('.query')
        ? {
            keyword: { type: 'string', description: '关键字（可选）' },
            page: { type: 'integer', description: '页码，默认 1' },
            pageSize: { type: 'integer', description: '每页条数，默认 20' }
          }
        : {}
    };
    return JSON.stringify(schema, null, 2);
  });

  const curlExample = computed(() => {
    const c = cap.value;
    if (!c) return '';
    const bodyStr = requestBody.value || '{}';
    const indented = bodyStr
      .split('\n')
      .map((l, i) => (i === 0 ? l : '  ' + l))
      .join('\n');
    return [
      `curl -X POST "https://<开放平台域名>/openapi/v1/${c.code}" \\`,
      `  -H "X-Zt-Key: <你的 AppKey>" \\`,
      `  -H "X-Zt-Timestamp: 1710000000" \\`,
      `  -H "X-Zt-Nonce: 8f3a1c9d" \\`,
      `  -H "X-Zt-Sign: <HMAC-SHA256 签名>" \\`,
      `  -H "Content-Type: application/json" \\`,
      `  -d '${indented}'`
    ].join('\n');
  });

  const copy = async (text: string) => {
    const ok = await copyText(text);
    if (ok) {
      EleMessage.success({ message: '已复制到剪贴板', plain: true });
    } else {
      EleMessage.error({ message: '复制失败，请手动选择复制', plain: true });
    }
  };

  const open = (row: Capability) => {
    cap.value = row;
    activeTab.value = (row.channels || []).includes('api') ? 'api' : 'mcp';
    visible.value = true;
  };

  const onClosed = () => {
    cap.value = null;
  };

  defineExpose({ open });
</script>

<style lang="scss" scoped>
  .op-cap-head__title {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .op-cap-head__name {
    font-size: 17px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .op-cap-head__code {
    margin-top: 4px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12.5px;
    color: var(--el-text-color-secondary);
  }

  .op-cap-desc {
    margin: 0 0 12px;
    color: var(--el-text-color-regular);
    font-size: 13.5px;
    line-height: 1.7;
  }

  .op-cap-section {
    margin-top: 14px;
  }
  .op-cap-section__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .op-cap-section__title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .op-code {
    max-height: 320px;
    font-size: 12.5px;
    line-height: 1.6;
  }

  .op-cap-fields {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px 16px;
    border-radius: 10px;
    background: var(--el-fill-color-light);
  }
  .op-cap-field {
    display: flex;
    gap: 12px;
    font-size: 13px;
  }
  .op-cap-field__label {
    flex-shrink: 0;
    width: 68px;
    color: var(--el-text-color-secondary);
  }
  .op-code-inline {
    font-family: 'Consolas', 'Monaco', monospace;
    color: var(--el-color-primary);
  }

  .op-cap-section--return {
    padding-top: 14px;
    border-top: 1px dashed var(--el-border-color);
  }
  .op-cap-return {
    margin: 8px 0;
  }
  .op-return-tag {
    margin: 2px 6px 2px 0;
  }
  .op-cap-muted {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
  .op-cap-note {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  :deep(.el-icon) {
    margin-right: 4px;
    vertical-align: -2px;
  }
</style>

<style lang="scss">
  .op-cap-dialog.el-dialog {
    border-radius: 16px;
    overflow: hidden;

    .el-dialog__header {
      padding: 20px 24px 14px;
      margin-right: 0;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }
    .el-dialog__body {
      padding: 18px 24px 22px;
    }
  }
</style>
