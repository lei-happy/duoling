<template>
  <ele-page>
    <login-record-search
      :where="defaultWhere"
      @search="(where) => reload(where, 1)"
    />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :export-config="{ fileName: '登录日志数据' }"
        :where="defaultWhere"
        cache-key="SystemLoginRecordTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'export',
                props: { type: 'primary' },
                onClick: () => exportData()
              }
            ]"
          />
        </template>
        <template #loginType="{ row }">
          <el-tag
            v-if="row.loginType === 0"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            登录成功
          </el-tag>
          <el-tag
            v-else-if="row.loginType === 1"
            size="small"
            type="danger"
            :disable-transitions="true"
          >
            登录失败
          </el-tag>
          <el-tag
            v-else-if="row.loginType === 2"
            size="small"
            type="info"
            :disable-transitions="true"
          >
            退出登录
          </el-tag>
          <el-tag
            v-else-if="row.loginType === 3"
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            刷新TOKEN
          </el-tag>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import ExcelJS from 'exceljs';
  import { download } from '@/utils/common';
  import LoginRecordSearch from './components/login-record-search.vue';
  import {
    pageLoginRecords,
    listLoginRecords
  } from '@/api/logcenter/login-record';
  import type { LoginRecordParam } from '@/api/logcenter/login-record/model';

  defineOptions({ name: 'SystemLoginRecord' });

  /** 默认搜索条件 */
  const defaultWhere = reactive({
    username: '',
    nickname: ''
  });

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'username',
      label: '账号',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'nickname',
      label: '用户名',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'ip',
      label: 'IP地址',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'device',
      label: '设备型号',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'os',
      label: '操作系统',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'browser',
      label: '浏览器',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'loginType',
      label: '操作类型',
      sortable: 'custom',
      width: 130,
      slot: 'loginType',
      filters: [
        {
          text: '登录成功',
          value: '0'
        },
        {
          text: '登录失败',
          value: '1'
        },
        {
          text: '退出登录',
          value: '2'
        },
        {
          text: '刷新TOKEN',
          value: '3'
        }
      ],
      filterMultiple: false,
      align: 'center',
      formatter: (row) =>
        ['登录成功', '登录失败', '退出登录', '刷新TOKEN'][row.loginType]
    },
    {
      prop: 'comments',
      label: '备注',
      sortable: 'custom',
      minWidth: 110,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '登录时间',
      sortable: 'custom',
      width: 180,
      align: 'center'
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({
    pages,
    where,
    orders,
    filters
  }) => {
    return pageLoginRecords({ ...where, ...orders, ...filters, ...pages });
  };

  /** 刷新表格 */
  const reload = (where?: LoginRecordParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  /** 导出数据 */
  const exportData = () => {
    // 请求查询全部接口
    const loading = EleMessage.loading({
      message: '请求中..',
      plain: true
    });
    tableRef.value?.fetch?.(({ where, orders, filters }) => {
      listLoginRecords({ ...where, ...orders, ...filters })
        .then((data) => {
          const workbook = new ExcelJS.Workbook();
          const sheet = workbook.addWorksheet('Sheet1');
          sheet.addRow([
            '账号',
            '用户名',
            'IP地址',
            '设备型号',
            '操作系统',
            '浏览器',
            '操作类型',
            '备注',
            '登录时间'
          ]);
          data.forEach((d) => {
            sheet.addRow([
              d.username,
              d.nickname,
              d.ip,
              d.device,
              d.os,
              d.browser,
              ['登录成功', '登录失败', '退出登录', '刷新TOKEN'][d.loginType],
              d.comments,
              d.createTime
            ]);
          });
          // 设置列宽
          [16, 16, 22, 22, 18, 20, 14, 16, 24].forEach((width, index) => {
            sheet.getColumn(index + 1).width = width;
          });
          // 设置样式
          sheet.eachRow({ includeEmpty: true }, (row, rowIndex) => {
            row.height = 20;
            row.eachCell({ includeEmpty: true }, (cell) => {
              cell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' }
              };
              cell.alignment = {
                vertical: 'middle',
                horizontal: 'center'
              };
              cell.font = { size: 12, bold: rowIndex === 1 };
            });
          });
          // 下载文件
          workbook.xlsx.writeBuffer().then((data) => {
            download(data, '登录日志.xlsx');
            loading.close();
          });
        })
        .catch((e) => {
          loading.close();
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };
</script>
