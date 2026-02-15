<template>
  <ele-card header="导入 Excel">
    <el-space>
      <el-upload
        action=""
        accept=".xls,.xlsx"
        :show-file-list="false"
        :before-upload="importFile"
      >
        <el-button type="primary" class="ele-btn-icon">导入</el-button>
      </el-upload>
      <el-upload
        action=""
        accept=".xls,.xlsx"
        :show-file-list="false"
        :before-upload="importFile2"
      >
        <el-button type="primary" class="ele-btn-icon">
          导入拆分合并
        </el-button>
      </el-upload>
      <el-upload
        action=""
        accept=".xls,.xlsx"
        :show-file-list="false"
        :before-upload="importFile3"
      >
        <el-button type="primary" class="ele-btn-icon">
          导入保持合并
        </el-button>
      </el-upload>
    </el-space>
    <div style="overflow: auto; margin-top: 12px">
      <ele-table
        :border="true"
        style="min-width: max-content; table-layout: fixed"
      >
        <colgroup>
          <col width="52" />
          <col v-for="item in importTitle" :key="item" />
        </colgroup>
        <thead>
          <tr>
            <th></th>
            <th
              v-for="item in importTitle"
              :key="item"
              style="text-align: center"
            >
              {{ item }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in importData" :key="index">
            <td style="text-align: center">{{ index + 1 }}</td>
            <template v-for="key in importTitle">
              <td
                v-if="item[key]?.colspan !== 0 && item[key]?.rowspan !== 0"
                :key="key"
                :colspan="item[key]?.colspan"
                :rowspan="item[key]?.rowspan"
                style="text-align: center"
              >
                {{ item[key]?.value }}
              </td>
            </template>
          </tr>
          <tr v-if="!importData.length">
            <td
              :colspan="importTitle.length + 1"
              style="text-align: center; background: none"
            >
              暂无数据
            </td>
          </tr>
        </tbody>
      </ele-table>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import ExcelJS from 'exceljs';

  /** 导入数据的列 */
  const importTitle = ref<string[]>(['A', 'B', 'C', 'D', 'E', 'F', 'G']);

  /** 导入的数据 */
  const importData = ref<Record<string, any>[]>([]);

  /** 导入本地excel文件 */
  const importFile = (file: File) => {
    if (
      ![
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ].includes(file.type)
    ) {
      EleMessage.error({ message: '只能选择 excel 文件', plain: true });
      return false;
    }
    if (file.size / 1024 / 1024 > 20) {
      EleMessage.error({ message: '大小不能超过 20MB', plain: true });
      return false;
    }
    const loading = EleMessage.loading({ message: '加载中..', plain: true });
    const reader = new FileReader();
    reader.onload = (e) => {
      const workbook = new ExcelJS.Workbook();
      workbook.xlsx.load(e.target?.result as any).then(() => {
        const title: string[] = [];
        const list: Record<string, any>[] = [];
        workbook.eachSheet((sheet) => {
          list.splice(0, list.length);
          sheet.eachRow({ includeEmpty: true }, (row, rowIndex) => {
            title.splice(0, title.length);
            const item: Record<string, any> = {};
            row.eachCell({ includeEmpty: true }, (cell) => {
              const key = cell.address.slice(0, -String(rowIndex).length);
              title.push(key);
              const isMerged =
                cell.isMerged && cell.address !== cell.master.address;
              item[key] = {
                value: isMerged ? '' : cell.value,
                colspan: 1,
                rowspan: 1
              };
            });
            list.push(item);
          });
        });
        importTitle.value = title;
        importData.value = list;
        loading.close();
      });
    };
    reader.readAsArrayBuffer(file);
    return false;
  };

  /** 导入excel拆分合并单元格 */
  const importFile2 = (file: File) => {
    if (
      ![
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ].includes(file.type)
    ) {
      EleMessage.error({ message: '只能选择 excel 文件', plain: true });
      return false;
    }
    if (file.size / 1024 / 1024 > 20) {
      EleMessage.error({ message: '大小不能超过 20MB', plain: true });
      return false;
    }
    const loading = EleMessage.loading({ message: '加载中..', plain: true });
    const reader = new FileReader();
    reader.onload = (e) => {
      const workbook = new ExcelJS.Workbook();
      workbook.xlsx.load(e.target?.result as any).then(() => {
        const title: string[] = [];
        const list: Record<string, any>[] = [];
        workbook.eachSheet((sheet) => {
          list.splice(0, list.length);
          sheet.eachRow({ includeEmpty: true }, (row, rowIndex) => {
            title.splice(0, title.length);
            const item: Record<string, any> = {};
            row.eachCell({ includeEmpty: true }, (cell) => {
              const key = cell.address.slice(0, -String(rowIndex).length);
              title.push(key);
              item[key] = {
                value: cell.value,
                colspan: 1,
                rowspan: 1
              };
            });
            list.push(item);
          });
        });
        importTitle.value = title;
        importData.value = list;
        loading.close();
      });
    };
    reader.readAsArrayBuffer(file);
    return false;
  };

  /** 导入 excel 读取合并信息 */
  const importFile3 = (file: File) => {
    if (
      ![
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ].includes(file.type)
    ) {
      EleMessage.error({ message: '只能选择 excel 文件', plain: true });
      return false;
    }
    if (file.size / 1024 / 1024 > 20) {
      EleMessage.error({ message: '大小不能超过 20MB', plain: true });
      return false;
    }
    const loading = EleMessage.loading({ message: '加载中..', plain: true });
    const reader = new FileReader();
    reader.onload = (e) => {
      const workbook = new ExcelJS.Workbook();
      workbook.xlsx.load(e.target?.result as any).then(() => {
        const title: string[] = [];
        const list: Record<string, any>[] = [];
        workbook.eachSheet((sheet) => {
          list.splice(0, list.length);
          sheet.eachRow({ includeEmpty: true }, (row) => {
            title.splice(0, title.length);
            const item: Record<string, any> = {};
            row.eachCell({ includeEmpty: true }, (cell) => {
              const key = cell.address.slice(0, -String(cell.row).length);
              title.push(key);
              const isMerged =
                cell.isMerged && cell.address !== cell.master.address;
              item[key] = {
                value: cell.value,
                colspan: isMerged ? 0 : 1,
                rowspan: isMerged ? 0 : 1
              };
            });
            list.push(item);
          });
          // 生成表格的跨行跨列
          sheet.eachRow({ includeEmpty: true }, (row) => {
            row.eachCell({ includeEmpty: true }, (cell) => {
              const master = cell.master;
              if (cell.isMerged && cell.address !== master.address) {
                const mk = master.address.slice(0, -String(master.row).length);
                const mItem = list[Number(master.row) - 1][mk];
                const rs = Math.abs(Number(cell.row) - Number(master.row)) + 1;
                rs > mItem.rowspan && (mItem.rowspan = rs);
                const cs = Math.abs(Number(cell.col) - Number(master.col)) + 1;
                cs > mItem.colspan && (mItem.colspan = cs);
              }
            });
          });
        });
        importTitle.value = title;
        importData.value = list;
        loading.close();
      });
    };
    reader.readAsArrayBuffer(file);
    return false;
  };
</script>
