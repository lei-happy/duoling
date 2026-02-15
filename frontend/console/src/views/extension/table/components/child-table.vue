<template>
  <div style="padding: 0 16px">
    <ele-pro-table
      row-key="dictDataId"
      :columns="dictDataColumns"
      :datasource="dictDataDatasource"
      :show-overflow-tooltip="true"
      :toolbar="false"
      :pagination="false"
      :empty-props="false"
      :selections="selections || []"
      @update:selections="updateSelections"
      @done="handleTableDone"
    >
      <template #action="{ row: d }">
        <el-link type="primary" underline="never" @click="editDictData(d)">
          修改
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="danger" underline="never" @click="removeDictData(d)">
          删除
        </el-link>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns,
    DoneFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { listDictionaryData } from '@/api/system/dictionary-data';
  import type { DictionaryData } from '@/api/system/dictionary-data/model';

  const props = defineProps<{
    dictId: number;
    selections?: DictionaryData[];
  }>();

  const emit = defineEmits<{
    (e: 'update:selections', value: DictionaryData[]): void;
    (e: 'setDictionaryData', dictId: number, value: DictionaryData[]): void;
  }>();

  /** 字典数据列配置 */
  const dictDataColumns = ref<Columns>([
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
      prop: 'dictDataName',
      label: '字典数据名称',
      sortable: 'custom',
      minWidth: 140
    },
    {
      prop: 'dictDataCode',
      label: '字典数据代码',
      sortable: 'custom',
      minWidth: 140
    },
    {
      prop: 'sortNumber',
      label: '排序号',
      sortable: 'custom',
      width: 110,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      minWidth: 140,
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 120,
      align: 'center',
      slot: 'action'
    }
  ]);

  /** 字典数据数据源 */
  const dictDataDatasource: DatasourceFunction = ({ where, orders }) => {
    return listDictionaryData({ ...where, ...orders, dictId: props.dictId });
  };

  /** 删除字典数据 */
  const removeDictData = (row: DictionaryData) => {
    EleMessage.error({ message: `删除: ${row.dictDataName}`, plain: true });
  };

  /** 修改字典数据 */
  const editDictData = (row: DictionaryData) => {
    EleMessage.info({ message: `修改: ${row.dictDataName}`, plain: true });
  };

  /** 更新多选选中数据 */
  const updateSelections = (value: DictionaryData[]) => {
    emit('update:selections', value);
  };

  /** 表格数据请求完成事件 */
  const handleTableDone: DoneFunction<DictionaryData> = (result) => {
    emit('setDictionaryData', props.dictId, result.data);
  };
</script>
