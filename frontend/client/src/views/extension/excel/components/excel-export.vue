<template>
  <ele-card header="导出 Excel" :body-style="{ padding: '18px 20px' }">
    <ele-pro-table
      row-key="key"
      :columns="columns"
      :datasource="data"
      :show-overflow-tooltip="true"
      :pagination="false"
      v-model:selections="selections"
      :tools="['export', 'print', 'size', 'columns', 'maximized']"
      :toolbar="{ theme: 'default' }"
      :border="true"
    >
      <template #toolbar>
        <el-space :size="12" wrap>
          <el-button type="primary" class="ele-btn-icon" @click="exportBas">
            导出
          </el-button>
          <el-button type="primary" class="ele-btn-icon" @click="exportAdv">
            导出带表头合并
          </el-button>
          <el-button type="primary" class="ele-btn-icon" @click="exportSel">
            导出选中
          </el-button>
        </el-space>
      </template>
    </ele-pro-table>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
  import ExcelJS from 'exceljs';
  import { download } from '@/utils/common';

  interface User {
    key: number;
    username: string;
    amount: number;
    province: string;
    city: string;
    zone: string;
    street: string;
    address: string;
  }

  /** 表格数据 */
  const data = ref<User[]>([
    {
      key: 1,
      username: '张小三',
      amount: 18,
      province: '浙江',
      city: '杭州',
      zone: '西湖区',
      street: '西溪街道',
      address: '西溪花园30栋1单元'
    },
    {
      key: 2,
      username: '李小四',
      amount: 39,
      province: '江苏',
      city: '苏州',
      zone: '姑苏区',
      street: '丝绸路',
      address: '天墅之城9幢2单元'
    },
    {
      key: 3,
      username: '王小五',
      amount: 8,
      province: '江西',
      city: '南昌',
      zone: '青山湖区',
      street: '艾溪湖办事处',
      address: '中兴和园1幢3单元'
    },
    {
      key: 4,
      username: '赵小六',
      amount: 16,
      province: '福建',
      city: '泉州',
      zone: '丰泽区',
      street: '南洋街道',
      address: '南洋村6幢1单元'
    },
    {
      key: 5,
      username: '孙小七',
      amount: 12,
      province: '湖北',
      city: '武汉',
      zone: '武昌区',
      street: '武昌大道',
      address: '两湖花园16幢2单元'
    },
    {
      key: 6,
      username: '周小八',
      amount: 11,
      province: '安徽',
      city: '黄山',
      zone: '黄山区',
      street: '汤口镇',
      address: '温泉村21号'
    }
  ]);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 56,
      align: 'center'
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 56,
      align: 'center'
    },
    {
      prop: 'username',
      label: '用户名',
      align: 'center',
      minWidth: 110
    },
    {
      columnKey: 'cityAddress',
      label: '地址',
      align: 'center',
      children: [
        {
          prop: 'province',
          label: '省',
          align: 'center',
          minWidth: 100
        },
        {
          prop: 'city',
          label: '市',
          align: 'center',
          minWidth: 100
        },
        {
          prop: 'zone',
          label: '区',
          align: 'center',
          minWidth: 120
        },
        {
          prop: 'street',
          label: '街道',
          align: 'center',
          minWidth: 120
        },
        {
          prop: 'address',
          label: '详细地址',
          align: 'center',
          minWidth: 160
        }
      ]
    },
    {
      prop: 'amount',
      label: '金额',
      align: 'center',
      minWidth: 80
    }
  ]);

  /** 选中数据 */
  const selections = ref<User[]>([]);

  /** 导出excel */
  const exportBas = () => {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Sheet1');
    sheet.addRow(['用户名', '省', '市', '区', '街道', '详细地址', '金额']);
    data.value.forEach((d) => {
      sheet.addRow([
        d.username,
        d.province,
        d.city,
        d.zone,
        d.street,
        d.address,
        d.amount
      ]);
    });
    // 设置列宽
    [16, 16, 16, 16, 20, 30, 12].forEach((width, index) => {
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
      download(data, '用户数据.xlsx');
    });
  };

  /** 导出带单元格合并 */
  const exportAdv = () => {
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Sheet1');
    sheet.addRow(['用户名', '地址', null, null, null, null, '金额']);
    sheet.addRow([null, '省', '市', '区', '街道', '详细地址', null]);
    data.value.forEach((d) => {
      sheet.addRow([
        d.username,
        d.province,
        d.city,
        d.zone,
        d.street,
        d.address,
        d.amount
      ]);
    });
    // 设置列宽
    [16, 16, 16, 16, 20, 30, 12].forEach((width, index) => {
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
        cell.font = { size: 12, bold: rowIndex < 3 };
      });
    });
    // 合并单元格
    sheet.mergeCells(1, 2, 1, 6);
    sheet.mergeCells(1, 1, 2, 1);
    sheet.mergeCells(1, 7, 2, 7);
    // 下载文件
    workbook.xlsx.writeBuffer().then((data) => {
      download(data, '用户数据.xlsx');
    });
  };

  /** 导出选中数据 */
  const exportSel = () => {
    if (selections.value.length === 0) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    //
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Sheet1');
    sheet.addRow(['用户名', '省', '市', '区', '街道', '详细地址', '金额']);
    selections.value.forEach((d) => {
      sheet.addRow([
        d.username,
        d.province,
        d.city,
        d.zone,
        d.street,
        d.address,
        d.amount
      ]);
    });
    // 设置列宽
    [16, 16, 16, 16, 20, 30, 12].forEach((width, index) => {
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
      download(data, '用户数据.xlsx');
    });
  };
</script>
