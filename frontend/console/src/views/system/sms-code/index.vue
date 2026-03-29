<template>
  <ele-page>
    <sms-code-search
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
        :export-config="{ fileName: '短信验证码数据' }"
        :where="defaultWhere"
        cache-key="SystemSmsCodeTable"
      >
        <template #purpose="{ row }">
          <el-tag
            v-if="row.purpose === 1"
            size="small"
            type="primary"
            :disable-transitions="true"
          >
            验证码登录
          </el-tag>
          <el-tag
            v-else-if="row.purpose === 2"
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            重置密码
          </el-tag>
          <span v-else>{{ row.purpose }}</span>
        </template>
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 0"
            size="small"
            type="info"
            :disable-transitions="true"
          >
            未使用
          </el-tag>
          <el-tag
            v-else-if="row.status === 1"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            已使用
          </el-tag>
          <el-tag
            v-else-if="row.status === 2"
            size="small"
            type="danger"
            :disable-transitions="true"
          >
            已过期
          </el-tag>
          <span v-else>{{ row.status }}</span>
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
  import SmsCodeSearch from './components/sms-code-search.vue';
  import { pageSmsCodes, listSmsCodes } from '@/api/system/sms-code';
  import type { SmsCodeParam } from '@/api/system/sms-code/model';

  defineOptions({ name: 'SystemSmsCode' });

  const defaultWhere = reactive({
    phone: '',
    purpose: undefined as number | undefined,
    status: undefined as number | undefined
  });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const purposeText = (p: number) =>
    p === 1 ? '验证码登录' : p === 2 ? '重置密码' : String(p);
  const statusText = (s: number) =>
    s === 0 ? '未使用' : s === 1 ? '已使用' : s === 2 ? '已过期' : String(s);

  const columns = ref<Columns>([
    {
      prop: 'phone',
      label: '手机号',
      minWidth: 120
    },
    {
      prop: 'code',
      label: '验证码',
      minWidth: 90,
      align: 'center'
    },
    {
      prop: 'purpose',
      label: '用途',
      width: 120,
      slot: 'purpose',
      align: 'center',
      formatter: (row) => purposeText(row.purpose)
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      slot: 'status',
      align: 'center',
      formatter: (row) => statusText(row.status)
    },
    {
      prop: 'expireAt',
      label: '过期时间',
      width: 180,
      align: 'center'
    },
    {
      prop: 'clientIp',
      label: '请求IP',
      minWidth: 120
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 180,
      align: 'center'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where, orders, filters }) => {
    return pageSmsCodes({ ...where, ...orders, ...filters, ...pages });
  };

  const reload = (where?: SmsCodeParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const exportData = () => {
    const loading = EleMessage.loading({
      message: '请求中..',
      plain: true
    });
    tableRef.value?.fetch?.(({ where, orders, filters }) => {
      listSmsCodes({ ...where, ...orders, ...filters })
        .then((data) => {
          const workbook = new ExcelJS.Workbook();
          const sheet = workbook.addWorksheet('Sheet1');
          sheet.addRow([
            '手机号',
            '验证码',
            '用途',
            '状态',
            '过期时间',
            '请求IP',
            '创建时间'
          ]);
          data.forEach((d) => {
            sheet.addRow([
              d.phone,
              d.code,
              purposeText(d.purpose),
              statusText(d.status),
              d.expireAt,
              d.clientIp ?? '',
              d.createdAt
            ]);
          });
          [14, 10, 14, 10, 20, 16, 20].forEach((width, index) => {
            sheet.getColumn(index + 1).width = width;
          });
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
          workbook.xlsx.writeBuffer().then((buf) => {
            download(buf, '短信验证码.xlsx');
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
