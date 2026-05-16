<template>
  <div>
    <ele-pro-table
      row-key="dictId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :tools="proTableToolsWithExport"
      :export-config="{ fileName: '字典数据' }"
    >
      <template #toolbar>
        <el-button
          type="primary"
          @click="getChildSelections"
          class="ele-btn-icon"
        >
          获取所有选中
        </el-button>
      </template>
      <template #action="{ row }">
        <el-link type="primary" underline="never" @click="editDict(row)">
          修改
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="danger" underline="never" @click="removeDict(row)">
          删除
        </el-link>
      </template>
      <template #expand="{ row }">
        <child-table
          :dictId="row.dictId"
          v-model:selections="childSelections[row.dictId]"
          @setDictionaryData="handleSetDictionaryData"
        />
      </template>
      <template #expandPrint="{ row }">
        <child-print-table :data="dictionaryDatas[row.dictId]" />
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExport } from '@/config/pro-table-tool-presets';
  import { pageDictionaries } from '@/api/system/dictionary';
  import type { Dictionary } from '@/api/system/dictionary/model';
  import ChildTable from './child-table.vue';
  import ChildPrintTable from './child-print-table.vue';
  import type { DictionaryData } from '@/api/system/dictionary-data/model';

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'expand',
      columnKey: 'expand',
      width: 50,
      align: 'center',
      slot: 'expand',
      // 用于打印
      printSlot: 'expandPrint',
      // 用于导出
      formatter: (row) => {
        const rows: (string | number)[][] = [
          ['#', '字典数据名称', '字典数据代码', '排序号', '创建时间']
        ];
        dictionaryDatas[row.dictId]?.forEach?.((d, i) => {
          rows.push([
            i + 1,
            d.dictDataName ?? '',
            d.dictDataCode ?? '',
            d.sortNumber ?? '',
            d.createTime ?? ''
          ]);
        });
        return rows.map((cells) => cells.join(',')).join('\n');
      }
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'dictName',
      label: '字典名称',
      sortable: 'custom',
      minWidth: 130
    },
    {
      prop: 'dictCode',
      label: '字典代码',
      sortable: 'custom',
      minWidth: 160
    },
    {
      prop: 'sortNumber',
      label: '排序号',
      sortable: 'custom',
      width: 120,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      minWidth: 180,
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 120,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, orders }) => {
    return pageDictionaries({ ...orders, ...pages });
  };

  /** 删除字典 */
  const removeDict = (row: Dictionary) => {
    EleMessage.error({ message: `删除: ${row.dictName}`, plain: true });
  };

  /** 修改字典 */
  const editDict = (row: Dictionary) => {
    EleMessage.info({ message: `修改: ${row.dictName}`, plain: true });
  };

  /** 子表格多选选中数据 */
  const childSelections = reactive({});

  /** 获取子表格多选选中数据 */
  const getChildSelections = () => {
    console.log(JSON.parse(JSON.stringify(childSelections)));
    const length = Object.keys(childSelections)
      .map((key) => childSelections[key].length)
      .reduce((a, b) => a + b, 0);
    EleMessage.success({
      message: `共选中 ${length} 条数据, 已打印在控制台`,
      plain: true
    });
  };

  /** 存储已加载的子表格数据 */
  const dictionaryDatas = reactive<Record<number, DictionaryData[]>>({});

  const handleSetDictionaryData = (dictId: number, data: DictionaryData[]) => {
    dictionaryDatas[dictId] = data;
  };
</script>
