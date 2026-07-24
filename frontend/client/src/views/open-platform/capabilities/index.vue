<template>
  <ele-page>
    <ele-card :body-style="{ padding: '16px 20px' }">
      <div class="op-tip">
        能力目录是开放平台对外提供的“能做哪些事”的清单。创建密钥或 MCP 连接时，
        你可以从这里挑选要授权的能力，未勾选的能力对外一律不可访问。
      </div>
      <div class="op-toolbar">
        <el-input
          v-model="keyword"
          placeholder="搜索能力名称 / 编码"
          clearable
          class="op-search"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="category"
          placeholder="全部分类"
          clearable
          class="op-category"
        >
          <el-option
            v-for="c in categoryOptions"
            :key="c"
            :label="c"
            :value="c"
          />
        </el-select>
        <el-radio-group v-model="channel" @change="load">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="api">API 接口</el-radio-button>
          <el-radio-button value="mcp">MCP 工具</el-radio-button>
        </el-radio-group>
      </div>
      <el-table
        :data="filtered"
        v-loading="loading"
        row-key="code"
        stripe
        class="op-cap-table"
        @row-click="showDetail"
      >
        <el-table-column label="能力名称" min-width="160">
          <template #default="{ row }">
            <div class="op-cap__name">{{ row.name }}</div>
            <div class="op-cap__code">{{ row.code }}</div>
          </template>
        </el-table-column>
        <el-table-column
          prop="category"
          label="分类"
          width="110"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              size="small"
              type="info"
              effect="plain"
              :disable-transitions="true"
            >
              {{ row.category || '未分类' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="支持通道" width="150" align="center">
          <template #default="{ row }">
            <el-tag
              v-for="c in row.channels"
              :key="c"
              size="small"
              round
              class="op-field-tag"
              :type="c === 'api' ? 'primary' : 'success'"
              :disable-transitions="true"
            >
              {{ c === 'api' ? 'API' : 'MCP' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="只读" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              size="small"
              round
              type="success"
              v-if="row.read_only"
              :disable-transitions="true"
            >
              只读
            </el-tag>
            <el-tag
              size="small"
              round
              type="warning"
              v-else
              :disable-transitions="true"
              >写</el-tag
            >
          </template>
        </el-table-column>
        <el-table-column
          prop="description"
          label="说明"
          min-width="240"
          show-overflow-tooltip
        >
          <template #default="{ row }">{{ row.description || '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="showDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>

    <capability-detail ref="detailRef" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted } from 'vue';
  import { Search } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { listCapabilities } from '@/api/open-platform';
  import type { Capability } from '@/api/open-platform/model';
  import CapabilityDetail from './components/capability-detail.vue';

  defineOptions({ name: 'OpenPlatformCapabilities' });

  const loading = ref(false);
  const channel = ref('');
  const keyword = ref('');
  const category = ref('');
  const list = ref<Capability[]>([]);
  const detailRef = ref<InstanceType<typeof CapabilityDetail>>();

  /** 分类下拉选项：从能力清单去重得到 */
  const categoryOptions = computed(() => {
    const set = new Set<string>();
    list.value.forEach((c) => c.category && set.add(c.category));
    return Array.from(set);
  });

  const filtered = computed(() => {
    const kw = keyword.value.trim().toLowerCase();
    return list.value.filter((c) => {
      if (category.value && c.category !== category.value) return false;
      if (!kw) return true;
      return (
        c.name.toLowerCase().includes(kw) || c.code.toLowerCase().includes(kw)
      );
    });
  });

  const showDetail = (row: Capability) => {
    detailRef.value?.open(row);
  };

  const load = async () => {
    loading.value = true;
    try {
      list.value = await listCapabilities(channel.value || undefined);
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载能力目录失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  onMounted(load);
</script>

<style lang="scss" scoped>
  .op-tip {
    color: var(--el-text-color-secondary);
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 12px;
  }
  .op-toolbar {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
    flex-wrap: wrap;
  }
  .op-search {
    width: 260px;
  }
  .op-category {
    width: 160px;
  }
  .op-cap__name {
    font-weight: 500;
  }
  .op-cap__code {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    font-family: 'Consolas', 'Monaco', monospace;
  }
  .op-field-tag {
    margin: 2px 4px 2px 0;
  }
  .op-cap-table {
    :deep(.el-table__row) {
      cursor: pointer;
    }
  }
</style>
