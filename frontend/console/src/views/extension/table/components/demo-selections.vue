<template>
  <div>
    <div class="option-wrapper">
      <option-item label="翻页保留多选" :responsive="false">
        <el-switch
          v-model="reserveSelection"
          size="small"
          @change="handleReserveSelectionChange"
        />
      </option-item>
      <option-item label="翻页保留单选" :responsive="false">
        <el-switch v-model="reserveCurrent" size="small" />
      </option-item>
    </div>
    <ele-pro-table
      ref="tableRef"
      row-key="pieceId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      v-model:selections="selections"
      v-model:current="current"
      highlight-current-row
      :reserveCurrent="reserveCurrent"
      :pagination="{
        pageSize: 10,
        pageSizes: [10, 20, 40]
      }"
      :export-config="{ fileName: '档案数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
    >
      <template #toolbar>
        <el-space :size="12" wrap>
          <el-button type="primary" class="ele-btn-icon" @click="getSelections">
            获取多选
          </el-button>
          <el-button type="warning" class="ele-btn-icon" @click="setSelections">
            修改多选
          </el-button>
          <el-button
            type="danger"
            class="ele-btn-icon"
            @click="clearSelections"
          >
            清空多选
          </el-button>
          <el-button
            plain
            type="primary"
            class="ele-btn-icon"
            @click="getCurrent"
          >
            获取单选
          </el-button>
          <el-button
            plain
            type="warning"
            class="ele-btn-icon"
            @click="setCurrent"
          >
            修改单选
          </el-button>
          <el-button
            plain
            type="danger"
            class="ele-btn-icon"
            @click="removeCurrent"
          >
            清空单选
          </el-button>
        </el-space>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, random } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Column
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';
  const data = Array.from({ length: 39 }).map((_, i) => {
    const pieceId = i + 1;
    const no = String(pieceId).padStart(3, '0');
    const secrets = ['机密', '秘密', '公开', '绝密', '内部'];
    const retentions = ['永久', '定期10年', '定期20年'];
    const retentionNos = ['Y', 'D10', 'D20'];
    const retentionRandom = random(0, retentions.length);
    const year = '2020';
    const item: Piece = {
      pieceId,
      title: `教学档案${no}`,
      pieceNo: `ELE101-${retentionNos[retentionRandom]}-ZM•JX-${year}-${no}`,
      secret: secrets[random(0, secrets.length)],
      retention: retentions[retentionRandom],
      year,
      amount: random(2, 10)
    };
    return item;
  });

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
    /** 保管期限 */
    retention?: string;
    /** 归档年度 */
    year?: string;
    /** 件数 */
    amount?: number;
  }

  /** 翻页保留多选 */
  const reserveSelection = ref(true);

  /** 翻页保留单选 */
  const reserveCurrent = ref(false);

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Column[]>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center',
      reserveSelection: reserveSelection.value,
      selectable: (row) => {
        return ![1, 5, 8].includes(row.pieceId);
      }
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
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
      count: list.length,
      list: list.slice(start, end > list.length ? list.length : end)
    };
  };

  /** 表格多选选中数据 */
  const selections = ref<Piece[]>([]);

  /** 表格单选选中数据 */
  const current = ref<Piece | null>(null);

  /** 获取多选 */
  const getSelections = () => {
    console.log(JSON.parse(JSON.stringify(selections.value)));
    EleMessage.success({
      message: `共 ${selections.value.length} 条数据已打印在控制台`,
      plain: true
    });
  };

  /** 修改多选 */
  const setSelections = () => {
    tableRef.value?.setSelectedRows?.(
      JSON.parse(JSON.stringify([data[1], data[2], data[5], data[11]]))
    );
  };

  /** 清空多选 */
  const clearSelections = () => {
    selections.value = [];
  };

  /** 获取单选 */
  const getCurrent = () => {
    if (!current.value) {
      EleMessage.success({ message: '未选中任何数据', plain: true });
    } else {
      console.log(JSON.parse(JSON.stringify(current.value)));
      EleMessage.success({
        message: current.value.pieceNo + '的数据已打印在控制台',
        plain: true
      });
    }
  };

  /** 修改单选 */
  const setCurrent = () => {
    tableRef.value?.setCurrentRow?.(data[3]);
  };

  /** 清空单选 */
  const removeCurrent = () => {
    current.value = null;
  };

  /** 翻页保留多选改变 */
  const handleReserveSelectionChange = () => {
    columns.value[0].reserveSelection = reserveSelection.value;
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = async ({ filter }) => {
    const res: any = await datasource({
      filter,
      pages: { page: 1, limit: 1000 }
    } as any);
    return res.list;
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
