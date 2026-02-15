<template>
  <ele-page>
    <file-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        :export-config="{ fileName: '文件数据', datasource: exportSource }"
        :print-config="{ datasource: exportSource }"
        cache-key="SystemFileTable"
      >
        <template #toolbar>
          <el-upload
            action=""
            :show-file-list="false"
            :before-upload="handleUpload"
            style="
              display: inline-block;
              vertical-align: middle;
              margin: 0 12px 0 0;
            "
          >
            <btn-items :items="[{ preset: 'upload' }]" />
          </el-upload>
          <btn-items :items="[{ preset: 'del', onClick: () => remove() }]" />
        </template>
        <template #path="{ row }">
          <el-link
            type="primary"
            :href="row.url"
            target="_blank"
            underline="never"
          >
            {{ row.path }}
          </el-link>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[
              {
                preset: 'download',
                props: { href: row.downloadUrl, target: '_blank' }
              },
              { preset: 'del', onClick: () => remove(row) }
            ]"
          />
        </template>
      </ele-pro-table>
    </ele-card>
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
  import FileSearch from './components/file-search.vue';
  import {
    pageFiles,
    removeFiles,
    uploadFile,
    listFiles
  } from '@/api/system/file';
  import type { FileRecord, FileRecordParam } from '@/api/system/file/model';

  defineOptions({ name: 'SystemFile' });

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center'
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'name',
      label: '文件名称',
      sortable: 'custom',
      minWidth: 140
    },
    {
      prop: 'path',
      label: '文件路径',
      sortable: 'custom',
      minWidth: 140,
      slot: 'path'
    },
    {
      prop: 'length',
      label: '文件大小',
      width: 120,
      align: 'center',
      sortable: 'custom',
      formatter: (row) => {
        if (row.length < 1024) {
          return row.length + 'B';
        } else if (row.length < 1024 * 1024) {
          return (row.length / 1024).toFixed(1) + 'KB';
        } else if (row.length < 1024 * 1024 * 1024) {
          return (row.length / 1024 / 1024).toFixed(1) + 'M';
        } else {
          return (row.length / 1024 / 1024 / 1024).toFixed(1) + 'G';
        }
      }
    },
    {
      prop: 'createNickname',
      label: '上传人',
      width: 120,
      align: 'center',
      sortable: 'custom'
    },
    {
      prop: 'createTime',
      label: '上传时间',
      width: 180,
      align: 'center',
      sortable: 'custom'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 190,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格选中数据 */
  const selections = ref<FileRecord[]>([]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageFiles({ ...where, ...orders, ...pages });
  };

  /** 搜索 */
  const reload = (where?: FileRecordParam, page?: number) => {
    selections.value = [];
    tableRef.value?.reload?.({ where, page });
  };

  /** 删除 */
  const remove = (row?: FileRecord) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `确定要删除“${rows.map((d) => d.name).join(', ')}”吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeFiles(rows.map((d) => d.id))
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  /** 上传 */
  const handleUpload = (file: File) => {
    if (file.size / 1024 / 1024 > 100) {
      EleMessage.error({ message: '大小不能超过 100MB', plain: true });
      return false;
    }
    const loading = EleMessage.loading({
      message: '上传中..',
      plain: true,
      mask: true
    });
    uploadFile(file)
      .then(() => {
        loading.close();
        EleMessage.success({ message: '上传成功', plain: true });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
    return false;
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ where, orders }) => {
    return listFiles({ ...where, ...orders });
  };
</script>
