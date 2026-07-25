<!-- 生态运营 - 敏感词库 -->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: '0' }">
      <el-form inline @submit.prevent="() => reload(1)">
        <el-form-item label="关键字">
          <el-input
            clearable
            v-model="where.keyword"
            placeholder="按词或备注搜索"
            style="width: 180px"
            @keyup.enter="() => reload(1)"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            clearable
            v-model="where.category"
            placeholder="全部"
            style="width: 130px"
          >
            <el-option
              v-for="c in options.categories"
              :key="c.value"
              :label="c.label"
              :value="c.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="命中后">
          <el-select
            clearable
            v-model="where.action"
            placeholder="全部"
            style="width: 140px"
          >
            <el-option
              v-for="a in options.actions"
              :key="a.value"
              :label="a.label"
              :value="a.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="适用范围">
          <el-select
            clearable
            v-model="where.scope"
            placeholder="全部"
            style="width: 150px"
          >
            <el-option
              v-for="s in options.scopes"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            clearable
            v-model="where.status"
            placeholder="全部"
            style="width: 110px"
          >
            <el-option label="启用中" :value="1" />
            <el-option label="已停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="() => reload(1)">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 12px"
      >
        词库用于货源、运力大厅的发布检查。「禁止发布」的词会让企业当场提交失败，
        建议只用于明确违规的内容；把握不大的词先设成「转人工审核」。 改动最多 5
        分钟后全面生效。
      </el-alert>

      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        v-model:selections="selections"
        :show-overflow-tooltip="true"
        cache-key="EcoSensitiveWordTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '添加敏感词', onClick: () => openEdit() },
              { title: '批量导入', onClick: openImport },
              { title: '试测一段话', onClick: openTest }
            ]"
          />
        </template>

        <template #category="{ row }">
          <el-tag size="small" :disable-transitions="true">
            {{ labelOf(options.categories, row.category) }}
          </el-tag>
        </template>

        <template #action_col="{ row }">
          <el-tag
            size="small"
            :disable-transitions="true"
            :type="row.action === 1 ? 'danger' : 'warning'"
          >
            {{ labelOf(options.actions, row.action) }}
          </el-tag>
        </template>

        <template #scope="{ row }">
          {{ labelOf(options.scopes, row.scope) }}
        </template>

        <template #status="{ row }">
          <el-tag
            size="small"
            :disable-transitions="true"
            :type="row.status === 1 ? 'success' : 'info'"
          >
            {{ row.status === 1 ? '启用中' : '已停用' }}
          </el-tag>
        </template>

        <template #hit="{ row }">
          <span v-if="row.hitCount > 0">
            {{ row.hitCount }} 次
            <el-tooltip
              v-if="row.lastHitAt"
              :content="`最近一次 ${row.lastHitAt}`"
            >
              <el-icon style="vertical-align: -2px"><InfoFilled /></el-icon>
            </el-tooltip>
          </span>
          <span v-else style="color: var(--el-text-color-placeholder)">
            还没拦到过
          </span>
        </template>

        <template #operate="{ row }">
          <btn-items :divider="true" type="link" :items="rowActions(row)" />
        </template>
      </ele-pro-table>

      <div v-if="selections.length" class="eco-batch-bar">
        已选 {{ selections.length }} 个
        <el-divider direction="vertical" />
        <el-link type="primary" :underline="false" @click="batchStatus(1)">
          批量启用
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="warning" :underline="false" @click="batchStatus(0)">
          批量停用
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="danger" :underline="false" @click="batchRemove">
          批量删除
        </el-link>
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { InfoFilled } from '@element-plus/icons-vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type { ButtonItem } from 'ele-admin-plus/es/ele-buttons/types';
  import {
    getWordOptions,
    pageSensitiveWords,
    removeSensitiveWords,
    setSensitiveWordStatus
  } from '@/api/ecosystem/sensitive-word';
  import type {
    SensitiveWord,
    SensitiveWordOptions,
    SensitiveWordParam,
    WordOption
  } from '@/api/ecosystem/sensitive-word/model';

  defineOptions({ name: 'EcoSensitiveWord' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<SensitiveWord[]>([]);

  const options = reactive<SensitiveWordOptions>({
    categories: [],
    actions: [],
    scopes: []
  });

  const where = reactive<SensitiveWordParam>({
    keyword: '',
    category: undefined,
    action: undefined,
    scope: undefined,
    status: undefined
  });

  const columns = ref<Columns>([
    { type: 'selection', columnKey: 'selection', width: 46, align: 'center' },
    { prop: 'word', label: '敏感词', minWidth: 160 },
    {
      prop: 'category',
      label: '分类',
      width: 110,
      align: 'center',
      slot: 'category'
    },
    {
      prop: 'action',
      label: '命中后',
      width: 120,
      align: 'center',
      slot: 'action_col'
    },
    {
      prop: 'scope',
      label: '适用范围',
      width: 140,
      align: 'center',
      slot: 'scope'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'hitCount',
      label: '拦下过',
      width: 130,
      align: 'center',
      slot: 'hit'
    },
    { prop: 'remark', label: '备注', minWidth: 160 },
    {
      columnKey: 'operate',
      label: '操作',
      width: 190,
      align: 'center',
      slot: 'operate',
      fixed: 'right'
    }
  ]);

  const labelOf = (list: WordOption[], value: number | string) =>
    list.find((i) => i.value === value)?.label ?? value;

  const datasource: DatasourceFunction = ({ pages }) =>
    pageSensitiveWords({
      page: pages?.page,
      limit: pages?.limit,
      keyword: where.keyword || undefined,
      category: where.category,
      action: where.action,
      scope: where.scope,
      status: where.status
    });

  const reload = (page?: number) => {
    selections.value = [];
    tableRef.value?.reload?.({ page: page ?? 1 });
  };

  const resetSearch = () => {
    where.keyword = '';
    where.category = undefined;
    where.action = undefined;
    where.scope = undefined;
    where.status = undefined;
    reload(1);
  };

  const rowActions = (row: SensitiveWord): ButtonItem[] => [
    { preset: 'edit', onClick: () => openEdit(row) },
    {
      title: row.status === 1 ? '停用' : '启用',
      onClick: () => toggleStatus(row)
    },
    { preset: 'del', onClick: () => removeOne(row) }
  ];

  const openEdit = (row?: SensitiveWord) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/word-edit.vue'),
      componentProps: {
        data: row,
        options,
        onDone: () => reload()
      }
    });
  };

  const openImport = () => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/word-import.vue'),
      componentProps: { options, onDone: () => reload(1) }
    });
  };

  const openTest = () => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/word-test.vue'),
      componentProps: { options }
    });
  };

  const toggleStatus = (row: SensitiveWord) => {
    const next = row.status === 1 ? 0 : 1;
    const acting = next === 1 ? '正在启用' : '正在停用';
    const loading = EleMessage.loading({
      message: `${acting}「${row.word}」，请稍候…`,
      plain: true
    });
    setSensitiveWordStatus([row.id], next)
      .then((msg) => {
        loading.close();
        EleMessage.success({ message: msg as string, plain: true });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const batchStatus = (status: number) => {
    const ids = selections.value.map((i) => i.id);
    const acting = status === 1 ? '正在批量启用' : '正在批量停用';
    const loading = EleMessage.loading({
      message: `${acting}，请稍候…`,
      plain: true
    });
    setSensitiveWordStatus(ids, status)
      .then((msg) => {
        loading.close();
        EleMessage.success({ message: msg as string, plain: true });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const removeOne = (row: SensitiveWord) => {
    ElMessageBox.confirm(
      `删除后「${row.word}」不再参与发布检查。如果只是想先观察一段时间，建议改用「停用」。`,
      '确定删除这个敏感词吗？',
      { type: 'warning', draggable: true, confirmButtonText: '确定删除' }
    )
      .then(() => doRemove([row.id]))
      .catch(() => {});
  };

  const batchRemove = () => {
    const ids = selections.value.map((i) => i.id);
    ElMessageBox.confirm(
      `删除后这些词不再参与发布检查。如果只是想先观察一段时间，建议改用「批量停用」。`,
      `确定删除选中的 ${ids.length} 个敏感词吗？`,
      { type: 'warning', draggable: true, confirmButtonText: '确定删除' }
    )
      .then(() => doRemove(ids))
      .catch(() => {});
  };

  const doRemove = (ids: number[]) => {
    const loading = EleMessage.loading({
      message: '正在删除，请稍候…',
      plain: true
    });
    removeSensitiveWords(ids)
      .then((msg) => {
        loading.close();
        EleMessage.success({ message: msg as string, plain: true });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  onMounted(() => {
    getWordOptions()
      .then((data) => {
        options.categories = data.categories;
        options.actions = data.actions;
        options.scopes = data.scopes;
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  });
</script>

<style lang="scss" scoped>
  .eco-batch-bar {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 6px;
    background: var(--el-fill-color-light);
    font-size: 13px;
    color: var(--el-text-color-regular);
  }
</style>
