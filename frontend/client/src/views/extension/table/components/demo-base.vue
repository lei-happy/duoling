<template>
  <div>
    <div class="option-wrapper">
      <option-item label="表头背景" :responsive="false">
        <el-switch v-model="toolbarBg" size="small" />
      </option-item>
      <option-item label="边框" :responsive="false">
        <el-switch v-model="border" size="small" @change="handleConfigChange" />
      </option-item>
      <option-item label="斑马纹" :responsive="false">
        <el-switch v-model="stripe" size="small" @change="handleConfigChange" />
      </option-item>
      <option-item label="表头" :responsive="false">
        <el-switch v-model="showHeader" size="small" />
      </option-item>
      <option-item label="表尾合计行" :responsive="false">
        <el-switch v-model="showSummary" size="small" />
      </option-item>
      <option-item label="行点击高亮" :responsive="false">
        <el-switch v-model="highlightCurrentRow" size="small" />
      </option-item>
      <option-item label="行点击勾选" :responsive="false">
        <el-switch v-model="rowClickChecked" size="small" />
      </option-item>
      <option-item label="不返回总数" :responsive="false">
        <el-switch v-model="noCount" size="small" @change="reload()" />
      </option-item>
    </div>
    <ele-pro-table
      ref="tableRef"
      row-key="pieceId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :highlight-current-row="highlightCurrentRow"
      :row-click-checked="rowClickChecked"
      v-model:selections="selections"
      v-model:current="current"
      :pagination="{
        pageSize: 10,
        pageSizes: [10, 20, 40]
      }"
      :toolbar="{ theme: toolbarBg ? 'default' : 'plain' }"
      :border="border"
      :stripe="stripe"
      :show-header="showHeader"
      :show-summary="showSummary"
      :summary-method="getSummaries"
      :tools="proTableToolsWithExportPrint"
      :export-config="{ fileName: '档案数据', datasource: exportSource }"
      :print-config="printConfig"
    >
      <template #toolbar>
        <el-space :size="12" wrap>
          <el-button type="primary" class="ele-btn-icon" @click="openExport">
            打开导出弹窗
          </el-button>
          <el-button type="primary" class="ele-btn-icon" @click="openPrint">
            打开打印弹窗
          </el-button>
          <el-button type="primary" class="ele-btn-icon" @click="exportData">
            直接导出
          </el-button>
          <el-button type="primary" class="ele-btn-icon" @click="printData">
            直接打印
          </el-button>
        </el-space>
      </template>
      <template #action="{ row }">
        <template v-if="row">
          <el-link type="primary" underline="never" @click="openEdit(row)">
            修改
          </el-link>
          <el-divider direction="vertical" />
          <el-link type="danger" underline="never" @click="remove(row)">
            删除
          </el-link>
        </template>
      </template>
      <!-- 直接打印时自定义多选列复选框 -->
      <template #selectionPrint="{ row }">
        <div
          v-if="row"
          :style="{
            width: '14px',
            height: '14px',
            border: '1px solid #000',
            borderRadius: '2px'
          }"
        >
          <div
            v-if="selections.some((d) => d.pieceId === row.pieceId)"
            :style="{
              width: '8px',
              height: '4px',
              border: '2px solid transparent',
              borderLeftColor: '#000',
              borderBottomColor: '#000',
              transform: 'rotate(-45deg) translate(0px, 2px)'
            }"
          ></div>
        </div>
      </template>
      <!-- 直接打印时自定义多选列表头复选框 -->
      <template #selectionHeaderPrint>
        <div
          :style="{
            width: '14px',
            height: '14px',
            border: '1px solid #000',
            borderRadius: '2px'
          }"
        >
          <div
            v-if="isPrintCheckAll === 'indeterminate'"
            :style="{
              width: '8px',
              height: '0px',
              borderTop: '2px solid #000',
              margin: '6px auto 0 auto'
            }"
          ></div>
          <div
            v-else-if="isPrintCheckAll"
            :style="{
              width: '8px',
              height: '4px',
              border: '2px solid transparent',
              borderLeftColor: '#000',
              borderBottomColor: '#000',
              transform: 'rotate(-45deg) translate(0px, 2px)'
            }"
          ></div>
        </div>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, nextTick } from 'vue';
  import { EleMessage, random } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Column,
    BeforeExportParams
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  /** 案卷 */
  interface Piece {
    /** 案卷id */
    pieceId?: number;
    /** 案卷题名 */
    title?: string;
    /** 案卷档号 */
    pieceNo?: string;
    /** 密级 */
    secret?: string;
    /** 存放位置 */
    location?: string;
    /** 案卷类型 */
    type?: string;
    /** 保管期限 */
    retention?: string;
    /** 载体类型 */
    carrier?: string;
    /** 归档年度 */
    year?: string;
    /** 件数 */
    amount?: number;
  }

  const data = Array.from({ length: 39 }).map((_, i) => {
    const pieceId = i + 1;
    const no = String(pieceId).padStart(3, '0');
    const secrets = ['机密', '秘密', '公开', '绝密', '内部'];
    const retentions = ['永久', '定期10年', '定期20年'];
    const retentionNos = ['Y', 'D10', 'D20'];
    const retentionRandom = random(0, retentions.length);
    const carriers = ['纸张', '光盘'];
    const year = '2020';
    const item: Piece = {
      pieceId,
      title: `教学档案${no}`,
      pieceNo: `ELE101-${retentionNos[retentionRandom]}-ZM•JX-${year}-${no}`,
      secret: secrets[random(0, secrets.length)],
      location: `001-001-${Math.random() < 0.5 ? 'A' : 'B'}0${random(1, 7)}`,
      type: '教学组织',
      retention: retentions[retentionRandom],
      carrier: carriers[random(0, carriers.length)],
      year,
      amount: random(2, 10)
    };
    return item;
  });

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Column[]>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center',
      fixed: 'left',
      printSlot: 'selectionPrint',
      printHeaderSlot: 'selectionHeaderPrint'
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center',
      fixed: 'left'
    },
    {
      prop: 'pieceNo',
      label: '案卷档号',
      minWidth: 260
    },
    {
      prop: 'title',
      label: '案卷题名',
      minWidth: 160
    },
    {
      prop: 'retention',
      label: '保管期限',
      minWidth: 110,
      align: 'center',
      filters: [
        { text: '永久', value: '永久' },
        { text: '定期10年', value: '定期10年' },
        { text: '定期20年', value: '定期20年' }
      ],
      filterMultiple: false
    },
    {
      prop: 'amount',
      label: '件数',
      minWidth: 110,
      align: 'center'
    },
    {
      prop: 'secret',
      label: '密级',
      minWidth: 110,
      align: 'center',
      filters: [
        { text: '机密', value: '机密' },
        { text: '秘密', value: '秘密' },
        { text: '公开', value: '公开' },
        { text: '绝密', value: '绝密' },
        { text: '内部', value: '内部' }
      ],
      filterMultiple: true
    },
    {
      prop: 'year',
      label: '归档年度',
      minWidth: 110,
      align: 'center'
    },
    {
      prop: 'type',
      label: '案卷类型',
      minWidth: 140,
      align: 'center'
    },
    {
      prop: 'location',
      label: '存放位置',
      minWidth: 140,
      align: 'center'
    },
    {
      prop: 'carrier',
      label: '载体类型',
      minWidth: 110,
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = async ({ pages, filter }) => {
    await new Promise((resolve) => setTimeout(resolve, 100));
    const secretFilter = filter.secret?.length ? filter.secret : null;
    const retentFilter = filter.retention?.length ? filter.retention : null;
    const list = data.filter((d) => {
      if (secretFilter != null) {
        if (!d.secret || !secretFilter.includes(d.secret)) {
          return false;
        }
      }
      if (retentFilter != null) {
        if (!d.retention || !retentFilter.includes(d.retention)) {
          return false;
        }
      }
      return true;
    });
    const start = ((pages.page || 1) - 1) * (pages.limit || 10);
    const end = start + (pages.limit || 10);
    return {
      count: noCount.value ? '*' : list.length,
      list: list.slice(start, end > list.length ? list.length : end)
    };
  };

  /** 表格多选选中数据 */
  const selections = ref<Piece[]>([]);

  /** 表格单选选中数据 */
  const current = ref<Piece | null>(null);

  /** 更多配置 */
  const toolbarBg = ref(false);
  const border = ref(false);
  const stripe = ref(false);
  const showHeader = ref(true);
  const showSummary = ref(true);
  const highlightCurrentRow = ref(false);
  const rowClickChecked = ref(false);
  const noCount = ref(false);

  /** 打开编辑弹窗 */
  const openEdit = (row: Piece) => {
    EleMessage.success({ message: `编辑: ${row.pieceNo}`, plain: true });
  };

  /** 删除单个 */
  const remove = (row: Piece) => {
    EleMessage.error({ message: `删除: ${row.pieceNo}`, plain: true });
  };

  /** 表格合计行 */
  const getSummaries = ({ columns, data }) => {
    const sums: string[] = [];
    let labelFlag = false;
    columns.forEach((column: Column, index: number) => {
      if (column.property === 'amount') {
        sums[index] = data
          .map((item: Piece) => Number(item[column.property as string]))
          .reduce((prev: number, curr: number) => {
            const value = Number(curr);
            if (!isNaN(value)) {
              return prev + curr;
            } else {
              return prev;
            }
          }, 0);
        labelFlag = true;
      } else if (
        !labelFlag &&
        column?.type !== 'selection' &&
        column?.type !== 'index'
      ) {
        sums[index] = '合计';
        labelFlag = true;
      }
    });
    return sums;
  };

  /** 获取多选行数据 */
  /* const getSelections = () => {
    console.log(JSON.parse(JSON.stringify(selections.value)));
  }; */

  /** 获取选中行数据 */
  /* const getCurrent = () => {
    if (!current.value) {
      EleMessage.success({ message: '未选中任何数据', plain: true });
    } else {
      console.log(JSON.parse(JSON.stringify(current.value)));
    }
  }; */

  /** 搜索 */
  const reload = () => {
    selections.value = [];
    tableRef.value?.reload?.({ page: 1 });
  };

  /** 表格属性改变 */
  const handleConfigChange = () => {
    nextTick(() => {
      tableRef.value && tableRef.value.doLayout();
    });
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = async ({ filter }) => {
    const res: any = await datasource({
      filter,
      pages: { page: 1, limit: data.length }
    } as any);
    return res.list;
  };

  /** 打印配置 */
  const printConfig = reactive({
    datasource: exportSource,
    printerProps: {
      direction: 'landscape'
    },
    beforePrint: (params: BeforeExportParams) => {
      params.footerData.forEach((fRow) => {
        params.bodyData.push(fRow);
      });
      params.footerData.splice(0, params.footerData.length);
    }
  });

  /** 打开导出 */
  const openExport = () => {
    tableRef.value?.openExportModal?.();
  };

  /** 打开打印 */
  const openPrint = () => {
    tableRef.value?.openPrintModal?.();
  };

  /** 直接打印时表格是否全选状态 */
  const isPrintCheckAll = ref<boolean | 'indeterminate'>(false);

  /** 直接打印 */
  const printData = () => {
    const printData = tableRef.value?.getData?.() || [];
    isPrintCheckAll.value = selections.value.length
      ? printData.length === selections.value.length
        ? true
        : 'indeterminate'
      : false;
    tableRef.value?.printData?.({
      data: printData,
      columns: columns.value,
      showHeader: showHeader.value,
      showFooter: showSummary.value,
      dataType: 'pageData'
    });
  };

  /** 直接导出 */
  const exportData = () => {
    const printData = tableRef.value?.getData?.() || [];
    isPrintCheckAll.value = selections.value.length
      ? printData.length === selections.value.length
        ? true
        : 'indeterminate'
      : false;
    tableRef.value?.exportData?.({
      data: printData,
      columns: [
        {
          type: 'selection',
          columnKey: 'selection',
          width: 50,
          align: 'center',
          formatter: (row) =>
            selections.value.some((d) => d.pieceId === row.pieceId) ? '☑' : '☐',
          label:
            isPrintCheckAll.value === 'indeterminate'
              ? '☐'
              : isPrintCheckAll.value
                ? '☑'
                : '☐'
        },
        ...columns.value.filter(
          (c) => c.columnKey !== 'action' && c.columnKey !== 'selection'
        )
      ],
      showHeader: showHeader.value,
      showFooter: showSummary.value,
      fileName: '档案数据',
      dataType: 'pageData'
    });
  };
</script>

<style lang="scss" scoped>
  .option-wrapper {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    padding-top: 12px;

    :deep(.option-item) {
      margin: 0 20px 8px 0;

      .option-item-label + .option-item-body {
        padding-left: 4px;
      }
    }
  }
</style>
