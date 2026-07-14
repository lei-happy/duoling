<!-- 运营推广 - Banner 管理 -->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: '0' }">
      <el-form inline @submit.prevent="() => reload(1)">
        <el-form-item label="标题">
          <el-input
            clearable
            v-model="where.keyword"
            placeholder="按标题搜索"
            @keyup.enter="() => reload(1)"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            clearable
            v-model="where.status"
            placeholder="全部"
            style="width: 130px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已上线" value="published" />
            <el-option label="已下线" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item label="投放">
          <el-select
            clearable
            v-model="where.target_type"
            placeholder="全部"
            style="width: 130px"
          >
            <el-option label="全部客户" value="all" />
            <el-option label="按版本" value="version" />
            <el-option label="指定租户" value="tenant" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="() => reload(1)">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="PromotionBannerTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新建 Banner', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #image="{ row }">
          <el-image
            :src="row.image_url"
            fit="cover"
            style="width: 140px; height: 28px; border-radius: 4px"
            :preview-src-list="[row.image_url]"
            preview-teleported
          />
        </template>
        <template #link_type="{ row }">
          <el-tag size="small" :disable-transitions="true">
            {{ linkTypeLabel(row.link_type) }}
          </el-tag>
        </template>
        <template #target="{ row }">
          {{ targetLabel(row) }}
        </template>
        <template #status="{ row }">
          <el-tag
            size="small"
            :disable-transitions="true"
            :type="statusTagType(row.status)"
          >
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #schedule="{ row }">
          <span v-if="row.start_at || row.end_at">
            {{ row.start_at || '不限' }} ~ {{ row.end_at || '不限' }}
          </span>
          <span v-else>长期</span>
        </template>
        <template #action="{ row }">
          <btn-items :divider="true" type="link" :items="rowActions(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    pageBanners,
    removeBanner,
    publishBanner,
    offlineBanner
  } from '@/api/promotion';
  import type { Banner, BannerParam } from '@/api/promotion/model';

  defineOptions({ name: 'PromotionBanner' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const where = reactive<BannerParam>({
    keyword: '',
    status: undefined,
    target_type: undefined
  });

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    {
      prop: 'image_url',
      label: '图片',
      width: 160,
      align: 'center',
      slot: 'image'
    },
    { prop: 'title', label: '标题', minWidth: 160 },
    {
      prop: 'link_type',
      label: '跳转',
      width: 90,
      align: 'center',
      slot: 'link_type'
    },
    {
      prop: 'target',
      label: '投放',
      width: 120,
      align: 'center',
      slot: 'target'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    { prop: 'sort_order', label: '排序', width: 70, align: 'center' },
    {
      prop: 'schedule',
      label: '排期',
      minWidth: 200,
      align: 'center',
      slot: 'schedule'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 220,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return pageBanners({
      page: pages?.page,
      limit: pages?.limit,
      keyword: where.keyword || undefined,
      status: where.status,
      target_type: where.target_type
    });
  };

  const reload = (page?: number) => {
    tableRef.value?.reload?.({ page: page ?? 1 });
  };

  const resetSearch = () => {
    where.keyword = '';
    where.status = undefined;
    where.target_type = undefined;
    reload(1);
  };

  const linkTypeLabel = (t: string) =>
    ({ none: '不跳转', external: '外链', internal: '站内' })[t] || t;

  const statusLabel = (s: string) =>
    ({ draft: '草稿', published: '已上线', offline: '已下线' })[s] || s;

  const statusTagType = (s: string) =>
    ({ draft: 'info', published: 'success', offline: 'warning' })[s] as
      | 'info'
      | 'success'
      | 'warning';

  const targetLabel = (row: Banner) => {
    if (row.target_type === 'all') return '全部客户';
    const count = row.target_values?.length || 0;
    return row.target_type === 'version' ? `版本(${count})` : `租户(${count})`;
  };

  const rowActions = (row: Banner) => {
    const items: any[] = [
      { preset: 'edit', onClick: () => openEdit(row) },
      { title: '统计', onClick: () => openStats(row) }
    ];
    if (row.status === 'published') {
      items.push({
        title: '下线',
        danger: true,
        onClick: () => changeStatus(row, false)
      });
    } else {
      items.push({ title: '上线', onClick: () => changeStatus(row, true) });
    }
    items.push({ preset: 'del', onClick: () => remove(row) });
    return items;
  };

  const openEdit = (row?: Banner) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/banner-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  const openStats = (row: Banner) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/banner-stats.vue'),
      componentProps: { banner: row }
    });
  };

  const changeStatus = (row: Banner, publish: boolean) => {
    const loading = EleMessage.loading({ message: '请求中..', plain: true });
    const req = publish ? publishBanner(row.id!) : offlineBanner(row.id!);
    req
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

  const remove = (row: Banner) => {
    ElMessageBox.confirm(`确定要删除 Banner「${row.title}」吗？`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeBanner(row.id!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg as string, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
