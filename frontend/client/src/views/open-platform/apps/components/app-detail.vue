<template>
  <el-dialog
    v-model="visible"
    width="880px"
    :destroy-on-close="true"
    :align-center="true"
    append-to-body
    class="op-detail-dialog"
    @closed="onClosed"
  >
    <template #header>
      <div class="op-detail-head">
        <div class="op-detail-head__avatar">
          {{ (app?.name || '应').slice(0, 1) }}
        </div>
        <div class="op-detail-head__info">
          <div class="op-detail-head__title">
            <span class="op-detail-head__name">{{
              app?.name || '接入应用'
            }}</span>
            <el-tag
              v-if="app"
              size="small"
              round
              :type="statusTagType(app.status)"
              :disable-transitions="true"
            >
              {{ statusText(app.status) }}
            </el-tag>
          </div>
          <div class="op-detail-head__desc">
            {{ app?.description || '管理该应用的 API 密钥与 MCP 连接' }}
          </div>
        </div>
      </div>
    </template>

    <div class="op-detail-body">
      <el-tabs v-model="activeTab" class="op-detail-tabs">
        <!-- API 密钥 -->
        <el-tab-pane name="api">
          <template #label>
            <span class="op-tab-label">
              API 密钥
              <el-badge
                v-if="credentials.length"
                :value="credentials.length"
                type="primary"
                class="op-tab-badge"
              />
            </span>
          </template>
          <div class="op-pane-head">
            <div class="op-pane-tip">
              <el-icon><InfoFilled /></el-icon>
              <span
                >给你的其他系统对接使用，创建后得到 AppKey /
                AppSecret，交给开发同事即可。</span
              >
            </div>
            <el-button
              type="primary"
              round
              v-permission="'open-platform:credential:create'"
              @click="openCredentialCreate"
            >
              <el-icon class="op-btn-icon"><Plus /></el-icon>创建密钥
            </el-button>
          </div>
          <div class="op-table-card">
            <el-table
              :data="credentials"
              v-loading="loadingCred"
              row-key="id"
              class="op-table"
            >
              <el-table-column label="AppKey" min-width="220">
                <template #default="{ row }">
                  <span class="op-code-inline">{{ row.access_key }}</span>
                </template>
              </el-table-column>
              <el-table-column label="授权能力" width="110" align="center">
                <template #default="{ row }">
                  <span class="op-count">{{ (row.scope || []).length }}</span>
                  项
                </template>
              </el-table-column>
              <el-table-column label="状态" width="90" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    round
                    :type="statusTagType(row.status)"
                    :disable-transitions="true"
                  >
                    {{ statusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="160" align="center">
                <template #default="{ row }">{{
                  row.created_at || '—'
                }}</template>
              </el-table-column>
              <el-table-column label="操作" width="196" align="center">
                <template #default="{ row }">
                  <el-button
                    link
                    type="primary"
                    v-permission="'open-platform:app:edit'"
                    @click="openCredentialScope(row)"
                  >
                    授权
                  </el-button>
                  <el-button
                    link
                    type="primary"
                    v-permission="'open-platform:credential:reset'"
                    :disabled="row.status !== 'enabled'"
                    @click="resetCred(row)"
                  >
                    重置
                  </el-button>
                  <el-button
                    link
                    type="danger"
                    v-permission="'open-platform:credential:revoke'"
                    :disabled="row.status !== 'enabled'"
                    @click="revokeCred(row)"
                  >
                    停用
                  </el-button>
                </template>
              </el-table-column>
              <template #empty>
                <div class="op-empty"
                  >还没有密钥，点击右上角「创建密钥」开始接入</div
                >
              </template>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- MCP 连接 -->
        <el-tab-pane name="mcp">
          <template #label>
            <span class="op-tab-label">
              MCP 连接
              <el-badge
                v-if="mcpConfigs.length"
                :value="mcpConfigs.length"
                type="primary"
                class="op-tab-badge"
              />
            </span>
          </template>
          <div class="op-pane-head">
            <div class="op-pane-tip">
              <el-icon><InfoFilled /></el-icon>
              <span
                >给 Trae、WorkBuddy 等 AI
                工具使用，创建后复制配置粘贴即可，无需懂技术。</span
              >
            </div>
            <el-button
              type="primary"
              round
              v-permission="'open-platform:mcp:create'"
              @click="openMcpCreate"
            >
              <el-icon class="op-btn-icon"><Plus /></el-icon>新建连接
            </el-button>
          </div>
          <div class="op-table-card">
            <el-table
              :data="mcpConfigs"
              v-loading="loadingMcp"
              row-key="id"
              class="op-table"
            >
              <el-table-column
                prop="display_name"
                label="连接名称"
                min-width="170"
              />
              <el-table-column label="开放能力" width="110" align="center">
                <template #default="{ row }">
                  <span class="op-count">{{
                    (row.enabled_capabilities || []).length
                  }}</span>
                  项
                </template>
              </el-table-column>
              <el-table-column label="状态" width="90" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    round
                    :type="statusTagType(row.status)"
                    :disable-transitions="true"
                  >
                    {{ statusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="160" align="center">
                <template #default="{ row }">
                  <el-button
                    link
                    type="primary"
                    v-permission="'open-platform:mcp:edit'"
                    @click="openMcpEdit(row)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    link
                    type="danger"
                    v-permission="'open-platform:mcp:delete'"
                    @click="removeMcp(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
              <template #empty>
                <div class="op-empty">
                  还没有 MCP 连接，点击右上角「新建连接」给 AI 工具授权
                </div>
              </template>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { InfoFilled, Plus } from '@element-plus/icons-vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    listCredentials,
    resetCredential,
    revokeCredential,
    listMcpConfigs,
    deleteMcpConfig
  } from '@/api/open-platform';
  import type {
    OpenApp,
    Credential,
    McpConfig
  } from '@/api/open-platform/model';
  import { statusTagType, statusText } from '../../constants';

  const { openModal } = useModal();

  const visible = ref(false);
  const activeTab = ref('api');
  const app = ref<OpenApp | null>(null);

  const credentials = ref<Credential[]>([]);
  const mcpConfigs = ref<McpConfig[]>([]);
  const loadingCred = ref(false);
  const loadingMcp = ref(false);

  const open = (row: OpenApp) => {
    app.value = row;
    activeTab.value = 'api';
    visible.value = true;
    loadCredentials();
    loadMcp();
  };

  const onClosed = () => {
    app.value = null;
    credentials.value = [];
    mcpConfigs.value = [];
  };

  const loadCredentials = async () => {
    if (!app.value?.id) return;
    loadingCred.value = true;
    try {
      credentials.value = await listCredentials(app.value.id);
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载密钥失败，请稍后重试',
        plain: true
      });
    } finally {
      loadingCred.value = false;
    }
  };

  const loadMcp = async () => {
    if (!app.value?.id) return;
    loadingMcp.value = true;
    try {
      mcpConfigs.value = await listMcpConfigs(app.value.id);
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载 MCP 连接失败，请稍后重试',
        plain: true
      });
    } finally {
      loadingMcp.value = false;
    }
  };

  // ---- 密钥 ----
  const revealCredential = (cred: Credential) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./secret-reveal.vue'),
      componentProps: {
        mode: 'credential',
        accessKey: cred.access_key,
        secret: cred.secret
      }
    });
  };

  const openCredentialCreate = () => {
    if (!app.value?.id) return;
    openModal({
      custom: true,
      asyncComponent: () => import('./credential-edit.vue'),
      componentProps: {
        appId: app.value.id,
        onDone: () => loadCredentials(),
        onReveal: (cred: Credential) => revealCredential(cred)
      }
    });
  };

  const openCredentialScope = (row: Credential) => {
    if (!app.value?.id) return;
    openModal({
      custom: true,
      asyncComponent: () => import('./credential-edit.vue'),
      componentProps: {
        appId: app.value.id,
        data: row,
        onDone: () => loadCredentials()
      }
    });
  };

  const resetCred = (row: Credential) => {
    ElMessageBox.confirm(
      '重置后旧密钥会立即失效，使用旧密钥的系统需要更换为新密钥。确定继续吗？',
      '重置密钥',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在重置密钥，请稍候…',
          plain: true
        });
        resetCredential(row.id)
          .then((cred) => {
            loading.close();
            loadCredentials();
            if (cred) revealCredential(cred);
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({
              message: e.message || '重置失败，请稍后重试',
              plain: true
            });
          });
      })
      .catch(() => {});
  };

  const revokeCred = (row: Credential) => {
    ElMessageBox.confirm(
      '停用后这把密钥将无法再调用接口，且不可恢复。确定停用吗？',
      '停用密钥',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在停用，请稍候…',
          plain: true
        });
        revokeCredential(row.id)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg || '已停用', plain: true });
            loadCredentials();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({
              message: e.message || '停用失败，请稍后重试',
              plain: true
            });
          });
      })
      .catch(() => {});
  };

  // ---- MCP ----
  const revealMcp = (cfg: McpConfig) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./secret-reveal.vue'),
      componentProps: {
        mode: 'mcp',
        url: cfg.url,
        token: cfg.token,
        configJson: cfg.config_json
      }
    });
  };

  const openMcpCreate = () => {
    if (!app.value?.id) return;
    openModal({
      custom: true,
      asyncComponent: () => import('./mcp-edit.vue'),
      componentProps: {
        appId: app.value.id,
        onDone: () => loadMcp(),
        onReveal: (cfg: McpConfig) => revealMcp(cfg)
      }
    });
  };

  const openMcpEdit = (row: McpConfig) => {
    if (!app.value?.id) return;
    openModal({
      custom: true,
      asyncComponent: () => import('./mcp-edit.vue'),
      componentProps: {
        appId: app.value.id,
        data: row,
        onDone: () => loadMcp()
      }
    });
  };

  const removeMcp = (row: McpConfig) => {
    ElMessageBox.confirm(
      `删除后「${row.display_name}」将立即失效，已配置该连接的 AI 工具将无法再使用。确定删除吗？`,
      '删除 MCP 连接',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在删除，请稍候…',
          plain: true
        });
        deleteMcpConfig(row.id)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg || '已删除', plain: true });
            loadMcp();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({
              message: e.message || '删除失败，请稍后重试',
              plain: true
            });
          });
      })
      .catch(() => {});
  };

  defineExpose({ open });
</script>

<style lang="scss" scoped>
  .op-detail-head {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .op-detail-head__avatar {
    width: 46px;
    height: 46px;
    flex-shrink: 0;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #5b8cff, #3b5bdb);
    box-shadow: 0 6px 14px rgba(59, 91, 219, 0.28);
  }
  .op-detail-head__title {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .op-detail-head__name {
    font-size: 17px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  .op-detail-head__desc {
    margin-top: 3px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    max-width: 620px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .op-detail-body {
    min-height: 360px;
  }

  .op-tab-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .op-tab-badge {
    transform: translateY(-1px);
  }

  .op-pane-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
  }
  .op-pane-tip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    flex: 1;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);

    .el-icon {
      flex-shrink: 0;
      font-size: 15px;
    }
  }
  .op-btn-icon {
    margin-right: 4px;
  }

  .op-table-card {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 12px;
    overflow: hidden;
  }
  .op-table {
    :deep(.el-table__header-wrapper th) {
      background: var(--el-fill-color-light);
      font-weight: 600;
    }
  }
  .op-count {
    font-weight: 600;
    color: var(--el-color-primary);
  }
  .op-code-inline {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12.5px;
    color: var(--el-text-color-regular);
    word-break: break-all;
  }
  .op-empty {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
</style>

<style lang="scss">
  .op-detail-dialog.el-dialog {
    border-radius: 16px;
    overflow: hidden;

    .el-dialog__header {
      padding: 20px 24px 16px;
      margin-right: 0;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }
    .el-dialog__body {
      padding: 18px 24px 24px;
    }
  }
</style>
