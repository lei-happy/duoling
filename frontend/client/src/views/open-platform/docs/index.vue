<template>
  <ele-page>
    <el-row :gutter="16">
      <el-col :md="17" :xs="24">
        <!-- 场景一：AI 工具 -->
        <ele-card class="op-doc-card">
          <div class="op-scene-head op-scene-head--ai">
            <div class="op-scene-badge">场景一</div>
            <div>
              <div class="op-scene-title">让 AI 办公工具连接智途</div>
              <div class="op-scene-sub"
                >推荐给非技术同事，三步搞定，无需写代码</div
              >
            </div>
          </div>

          <ol class="op-steps">
            <li>
              <span class="op-step-no">1</span>
              <span>到「接入应用」新建一个应用（例如「AI 助手」）。</span>
            </li>
            <li>
              <span class="op-step-no">2</span>
              <span
                >进入应用的「MCP 连接」，点「新建连接」，起个名字并勾选允许 AI
                使用的能力。</span
              >
            </li>
            <li>
              <span class="op-step-no">3</span>
              <span
                >创建后弹出一段配置，点「复制配置」，粘贴到 AI 工具的 MCP
                设置里保存即可。</span
              >
            </li>
          </ol>

          <div class="op-code-block">
            <div class="op-code-block__bar">
              <span class="op-code-block__name"
                >MCP 配置示例（以实际生成为准）</span
              >
              <el-button link type="primary" @click="copy(mcpExample)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="mcpExample" language="json" />
          </div>

          <div class="op-hint">
            配置好后，直接对 AI 说「帮我查一下最近的运单」「看看客户 XX
            的信息」，它就会通过智途读取数据。
          </div>
        </ele-card>

        <!-- 场景二：系统对接 -->
        <ele-card class="op-doc-card">
          <div class="op-scene-head op-scene-head--api">
            <div class="op-scene-badge op-scene-badge--api">场景二</div>
            <div>
              <div class="op-scene-title">让其他系统对接智途接口</div>
              <div class="op-scene-sub">
                交给开发同事，把 AppKey / AppSecret 与下面说明一起给他
              </div>
            </div>
          </div>

          <div class="op-block-title">1. 请求地址</div>
          <div class="op-code-block">
            <div class="op-code-block__bar">
              <span class="op-code-block__name">Endpoint</span>
              <el-button
                link
                type="primary"
                @click="copy(baseUrl + '/openapi/v1/')"
              >
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="endpointExample" language="bash" />
          </div>

          <div class="op-block-title">2. 鉴权（HMAC-SHA256 签名）</div>
          <p class="op-p">每次请求带上以下请求头，服务端用同样算法校验：</p>
          <div class="op-code-block">
            <div class="op-code-block__bar">
              <span class="op-code-block__name">请求头</span>
              <el-button link type="primary" @click="copy(headerExample)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="headerExample" language="bash" />
          </div>
          <p class="op-p"
            >待签名字符串按行拼接后用 AppSecret 计算 HMAC-SHA256：</p
          >
          <div class="op-code-block">
            <div class="op-code-block__bar">
              <span class="op-code-block__name">签名算法</span>
              <el-button link type="primary" @click="copy(signExample)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="signExample" language="bash" />
          </div>

          <div class="op-block-title">3. 返回格式</div>
          <div class="op-code-block">
            <div class="op-code-block__bar">
              <span class="op-code-block__name">Response</span>
              <el-button link type="primary" @click="copy(respExample)">
                <el-icon><CopyDocument /></el-icon>复制
              </el-button>
            </div>
            <code-viewer :code="respExample" language="json" />
          </div>
          <div class="op-hint">
            code 为 0 表示成功；非 0 时 message 为可读的错误说明，error_code
            为稳定错误码，便于程序判断。
          </div>
        </ele-card>
      </el-col>

      <el-col :md="7" :xs="24">
        <ele-card header="常见疑问" class="op-doc-card op-faq-card">
          <div class="op-faq">
            <div class="op-faq__item">
              <div class="op-faq__q">什么是 MCP？</div>
              <div class="op-faq__a">
                一种让 AI
                工具安全连接外部系统的「通用插头」。你不用懂原理，复制配置就能用。
              </div>
            </div>
            <div class="op-faq__item">
              <div class="op-faq__q">什么是 API 密钥？</div>
              <div class="op-faq__a">
                一把「钥匙」，代表某个系统有权访问你授权的能力。密钥泄露有风险，请妥善保管。
              </div>
            </div>
            <div class="op-faq__item">
              <div class="op-faq__q">密钥忘了怎么办？</div>
              <div class="op-faq__a">
                密钥只在创建时显示一次，忘记只能到应用里「重置密钥」，旧的会立即失效。
              </div>
            </div>
            <div class="op-faq__item">
              <div class="op-faq__q">担心数据安全？</div>
              <div class="op-faq__a">
                每把钥匙只能访问你勾选的能力，敏感字段（如手机号）自动打码，所有调用都可在「调用记录」追溯。
              </div>
            </div>
          </div>
        </ele-card>
      </el-col>
    </el-row>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { CopyDocument } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import CodeViewer from '@/components/CodeViewer/index.vue';
  import { copyText } from '../constants';

  defineOptions({ name: 'OpenPlatformDocs' });

  const baseUrl = computed(() => `${window.location.origin}`);

  const mcpExample = `{
  "mcpServers": {
    "智途运输助手": {
      "url": "https://你的地址/mcp/xxxxxxxx",
      "headers": { "Authorization": "Bearer mcp_xxx.mcpt_xxx" }
    }
  }
}`;

  const endpointExample = computed(
    () =>
      `POST ${baseUrl.value}/openapi/v1/{能力编码}\n例如：${baseUrl.value}/openapi/v1/customer.query`
  );

  const headerExample = `X-Zt-Key:        AppKey
X-Zt-Timestamp:  当前秒级时间戳（与服务器相差不超过 5 分钟）
X-Zt-Nonce:      一次性随机串（防重放）
X-Zt-Sign:       见下方签名算法`;

  const signExample = `stringToSign =
  HTTP方法 + "\\n" +
  请求路径 + "\\n" +
  规范化Query（按 key 升序，urlencode）+ "\\n" +
  sha256Hex(请求体) + "\\n" +
  时间戳 + "\\n" +
  Nonce

X-Zt-Sign = HMAC_SHA256(stringToSign, AppSecret) 的十六进制`;

  const respExample = `{
  "code": 0,
  "message": "ok",
  "data": {
    "list": [ { "customer_name": "示例客户", "contact_phone": "138****5678" } ],
    "total": 1,
    "page": 1,
    "pageSize": 20
  }
}`;

  const copy = async (text: string) => {
    const ok = await copyText(text);
    if (ok) {
      EleMessage.success({ message: '已复制到剪贴板', plain: true });
    } else {
      EleMessage.error({ message: '复制失败，请手动选中复制', plain: true });
    }
  };
</script>

<style lang="scss" scoped>
  .op-doc-card {
    margin-bottom: 16px;
  }

  .op-scene-head {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 18px;
    margin-bottom: 16px;
    border-radius: 12px;
  }
  .op-scene-head--ai {
    background: linear-gradient(135deg, #e6fffb, #f0f5ff);
  }
  .op-scene-head--api {
    background: linear-gradient(135deg, #eef2ff, #f5f7ff);
  }
  .op-scene-badge {
    flex-shrink: 0;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #2ed3c0, #12b8a6);
  }
  .op-scene-badge--api {
    background: linear-gradient(135deg, #5b8cff, #3b5bdb);
  }
  .op-scene-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .op-scene-sub {
    margin-top: 3px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .op-steps {
    list-style: none;
    margin: 0 0 16px;
    padding: 0;

    li {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      line-height: 1.8;
      color: var(--el-text-color-regular);
      margin-bottom: 10px;
    }
  }
  .op-step-no {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    margin-top: 2px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .op-block-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 18px 0 8px;
  }
  .op-p {
    line-height: 1.8;
    color: var(--el-text-color-regular);
    margin: 6px 0;
    font-size: 13.5px;
  }

  .op-code-block {
    margin: 8px 0 4px;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #2b2b2b;
  }
  .op-code-block__bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: #252526;
    border-bottom: 1px solid #000;
  }
  .op-code-block__name {
    font-size: 12px;
    color: #c9d1d9;
  }
  .op-code-block :deep(.ele-code-viewer) {
    border-radius: 0;
  }
  .op-code-block :deep(.el-button) {
    color: #79b8ff;
  }

  .op-hint {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.7;
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
  }

  .op-faq-card {
    position: sticky;
    top: 12px;
  }
  .op-faq__item + .op-faq__item {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px dashed var(--el-border-color);
  }
  .op-faq__q {
    font-weight: 600;
    color: var(--el-text-color-primary);
    font-size: 14px;
  }
  .op-faq__a {
    color: var(--el-text-color-secondary);
    font-size: 13px;
    line-height: 1.7;
    margin-top: 6px;
  }

  :deep(.el-icon) {
    margin-right: 4px;
    vertical-align: -2px;
  }
</style>
