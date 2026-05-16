<template>
  <ele-page :flex-table="fixedHeight">
    <!-- 搜索表单 -->
    <search-form @search="handleSearch" />
    <ele-card
      :flex-table="fixedHeight"
      :body-style="{ paddingBottom: '4px' }"
      :style="{
        minHeight: fixedHeight ? '380px' : void 0,
        marginBottom: fixedHeight ? '0px' : void 0
      }"
    >
      <!-- 提示信息 -->
      <ele-alert
        show-icon
        :closable="false"
        :style="{ marginBottom: toolDefault ? '12px' : '4px' }"
      >
        <template #title>
          <span>已选择&nbsp;</span>
          <ele-text strong type="primary" tag="span">
            {{ selections.length }}
          </ele-text>
          <span>&nbsp;项数据&emsp;</span>
          <span>其中冻结状态的用户有 </span>
          <b>{{ selections.filter((d) => d.status === 1).length }} 个 &emsp;</b>
          <el-link
            type="primary"
            underline="never"
            style="vertical-align: 0px"
            @click="clearChoose"
          >
            清空
          </el-link>
        </template>
      </ele-alert>
      <!-- 表格 -->
      <ele-pro-table
        ref="tableRef"
        row-key="userId"
        :columns="columns"
        :datasource="datasource"
        v-model:current="current"
        v-model:selections="selections"
        :show-overflow-tooltip="true"
        :tools="proTableToolsWithExportPrint"
        :export-config="exportConfig"
        :print-config="{ datasource: exportSource }"
        :border="bordered"
        :sticky="!fixedHeight"
        :toolbar="{ theme: toolDefault ? 'default' : 'plain' }"
        :default-sort="{ prop: 'createTime', order: 'ascending' }"
        :footer-style="{ paddingBottom: '12px' }"
        style="padding-bottom: 0"
        class="demo-table"
        cache-key="listBasicTable"
        @done="handleDone"
      >
        <template #toolbar>
          <el-button
            type="primary"
            :icon="PlusOutlined"
            class="ele-btn-icon"
            @click="openEdit()"
          >
            添加
          </el-button>
          <ele-dropdown
            :disabled="!selections.length"
            :items="[
              {
                title: '批量修改',
                command: 'edit',
                icon: EditOutlined
              },
              {
                title: '批量禁用',
                command: 'disabled',
                icon: MinusCircleOutlined
              },
              {
                title: '批量删除',
                command: 'del',
                icon: DeleteOutlined,
                danger: true,
                divided: true
              }
            ]"
            :icon-props="{ size: 15 }"
            placement="bottom-start"
            style="margin-left: 12px"
            @command="handleDropClick"
          >
            <el-button :disabled="!selections.length" class="ele-btn-icon">
              <span>批量操作</span>
              <el-icon :size="12" style="margin: 0 -4px 0 2px">
                <ArrowDown />
              </el-icon>
            </el-button>
          </ele-dropdown>
        </template>
        <!-- 表头工具按钮 -->
        <template #tools>
          <div style="display: flex; align-items: center; flex-wrap: wrap">
            <div>边框&nbsp;</div>
            <el-switch v-model="bordered" size="small" />
            <el-divider direction="vertical" />
            <div>表头背景&nbsp;</div>
            <el-switch v-model="toolDefault" size="small" />
            <el-divider direction="vertical" />
            <div>高度铺满&nbsp;</div>
            <el-switch v-model="fixedHeight" size="small" />
            <el-divider direction="vertical" />
          </div>
        </template>
        <!-- 头像列 -->
        <template #avatar="{ row }">
          <el-avatar
            v-if="row.avatar"
            :src="row.avatar"
            :size="32"
            @click.stop=""
            style="vertical-align: -16px"
          />
          <el-avatar
            v-else
            :size="32"
            style="background: var(--el-color-primary); vertical-align: -2px"
            @click.stop=""
          >
            {{
              row.nickname && row.nickname.length > 2
                ? row.nickname.substring(row.nickname.length - 2)
                : row.nickname
            }}
          </el-avatar>
        </template>
        <!-- 状态列 -->
        <template #status="{ row }">
          <ele-dot v-if="row.status === 0" text="正常" size="8px" />
          <ele-dot
            v-else-if="row.status === 1"
            text="冻结"
            type="danger"
            :ripple="false"
            size="8px"
          />
        </template>
        <!-- 角色列 -->
        <template #roles="{ row }">
          <el-tag
            v-for="item in row.roles"
            :key="item.roleId"
            size="small"
            :disable-transitions="true"
            style="margin-right: 6px"
          >
            {{ item.roleName }}
          </el-tag>
        </template>
        <!-- 操作列 -->
        <template #action="{ row }">
          <el-link type="primary" underline="never" @click.stop="openEdit(row)">
            修改
          </el-link>
          <el-divider direction="vertical" />
          <el-link type="danger" underline="never" @click.stop="remove(row)">
            删除
          </el-link>
        </template>
        <!-- 用户名表头 -->
        <template #nicknameHeader="{ column }">
          <div style="display: flex; align-items: center">
            <div style="flex: 1; overflow: hidden; text-overflow: ellipsis">
              {{ column.label }}
            </div>
            <nickname-filter @search="handleNicknameFilter" />
          </div>
        </template>
        <!-- 打印增加额外内容 -->
        <template #printTop>
          <h2 style="text-align: center">还可以自定义打印的顶部区域</h2>
        </template>
        <template #printBottom="{ data }">
          <h2 style="text-align: center">还可以自定义打印的底部区域</h2>
          <div style="text-align: center">
            共打印了 <b style="color: red">{{ data.length }}</b> 条数据
          </div>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns,
    DoneFunction,
    ExportConfig
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  import { useI18n } from 'vue-i18n';
  import {
    PlusOutlined,
    ArrowDown,
    EditOutlined,
    MinusCircleOutlined,
    DeleteOutlined
  } from '@/components/icons';
  import { getExportWorkbook } from 'ele-admin-plus/es/ele-pro-table/exceljs-plugin';
  import { download } from '@/utils/common';
  import request from '@/utils/request';
  import { usePageTab } from '@/utils/use-page-tab';
  import { useDictData } from '@/utils/use-dict-data';
  import SearchForm from './components/search-form.vue';
  import NicknameFilter from './components/nickname-filter.vue';
  import type { User, UserParam } from '@/api/system/user/model';
  import { pageUsers, listUsers } from '@/api/system/user';

  defineOptions({ name: 'ListBasic' });

  const { t } = useI18n();
  const { push } = useRouter();
  const { addPageTab } = usePageTab();

  /** 性别字典数据 */
  const [sexDicts] = useDictData(['sex']);

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 用户名筛选值 */
  const nicknameFilterValue = ref('');

  /** 表格搜索参数 */
  const lastWhere = reactive<UserParam>({});

  /** 表格列配置 */
  const columns = computed<Columns>(() => {
    return [
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
        columnKey: 'avatar',
        prop: 'avatar',
        label: t('list.basic.table.avatar'),
        width: 100,
        align: 'center',
        slot: 'avatar',
        className: 'demo-table-cell-avatar'
      },
      {
        prop: 'username',
        label: t('list.basic.table.username'),
        minWidth: 110,
        sortable: 'custom'
      },
      {
        prop: 'nickname',
        label: t('list.basic.table.nickname'),
        minWidth: 110,
        sortable: 'custom',
        headerSlot: 'nicknameHeader'
      },
      {
        columnKey: 'roles',
        label: t('list.basic.table.roles'),
        minWidth: 110,
        slot: 'roles',
        hideInTable: true,
        formatter: (row) => row.roles.map((d: any) => d.roleName).join(',')
      },
      {
        prop: 'organizationName',
        label: t('list.basic.table.organizationName'),
        minWidth: 110,
        sortable: 'custom'
      },
      {
        prop: 'phone',
        label: t('list.basic.table.phone'),
        minWidth: 120,
        align: 'center',
        sortable: 'custom',
        hideInTable: true
      },
      {
        prop: 'email',
        label: t('list.basic.table.email'),
        minWidth: 120,
        sortable: 'custom',
        hideInTable: true
      },
      {
        columnKey: 'sex',
        prop: 'sexName',
        label: t('list.basic.table.sexName'),
        width: 110,
        align: 'center',
        sortable: 'custom',
        filters: sexDicts.value.map((d) => {
          return { text: d.dictDataName, value: d.dictDataCode };
        }),
        filterMultiple: false
      },
      {
        prop: 'createTime',
        label: t('list.basic.table.createTime'),
        minWidth: 200,
        align: 'center',
        sortable: 'custom'
      },
      {
        prop: 'status',
        label: t('list.basic.table.status'),
        width: 110,
        sortable: 'custom',
        align: 'center',
        slot: 'status',
        filters: [
          { text: '正常', value: '0' },
          { text: '冻结', value: '1' }
        ],
        filterMultiple: false,
        formatter: (row) => (row.status == 0 ? '正常' : '冻结')
      },
      {
        columnKey: 'action',
        label: t('list.basic.table.action'),
        width: 130,
        align: 'center',
        showOverflowTooltip: false,
        resizable: false,
        slot: 'action',
        hideInPrint: true,
        hideInExport: true
      }
    ];
  });

  /** 表格选中数据 */
  const selections = ref<User[]>([]);

  /** 表格单选选中数据 */
  const current = ref<User | null>(null);

  /** 表格是否显示边框 */
  const bordered = ref(true);

  /** 表头工具栏风格 */
  const toolDefault = ref(true);

  /** 表格固定高度 */
  const fixedHeight = ref(false);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({
    pages,
    where,
    orders,
    filters
  }) => {
    return pageUsers({ ...where, ...orders, ...filters, ...pages });
  };

  /** 表格数据请求完成事件 */
  const handleDone: DoneFunction<User> = () => {
    // 回显 id 为 45、47、48 的数据的复选框
    nextTick(() => {
      const ids = [45, 47, 48];
      tableRef.value?.setSelectedRowKeys?.(ids);
    });
  };

  /** 搜索事件 */
  const handleSearch = (where: UserParam) => {
    Object.assign(lastWhere, where);
    doReload();
  };

  /** 刷新表格 */
  const reload = (where?: UserParam) => {
    tableRef.value?.reload?.({ page: 1, where });
  };

  /** 清空选择 */
  const clearChoose = () => {
    tableRef.value?.clearSelection?.();
  };

  /** 编辑 */
  const openEdit = (row?: User) => {
    const path = row ? `/list/basic/edit/${row.userId}` : '/list/basic/add';
    if (row) {
      addPageTab({
        title: `修改用户[${row.nickname}]`,
        key: path,
        closable: true,
        meta: { icon: 'LinkOutlined' }
      });
    }
    push(path);
  };

  /** 删除 */
  const remove = (row: User) => {
    ElMessageBox.confirm(`确定要删除“${row.username}”吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        EleMessage.success({ message: '点击了删除', plain: true });
      })
      .catch(() => {});
  };

  /** 下拉按钮点击 */
  const handleDropClick = (command: string) => {
    if (command === 'del') {
      EleMessage.error({ message: '点击了批量删除', plain: true });
    } else if (command === 'edit') {
      EleMessage.info({ message: '点击了批量修改', plain: true });
    } else if (command === 'disabled') {
      EleMessage.info({ message: '点击了批量禁用', plain: true });
    }
  };

  /** 表格搜索 */
  const doReload = () => {
    if (nicknameFilterValue.value) {
      reload({
        ...lastWhere,
        nickname: nicknameFilterValue.value
      });
    } else {
      reload(lastWhere);
    }
  };

  /** 用户名筛选事件 */
  const handleNicknameFilter = (nickname: string) => {
    nicknameFilterValue.value = nickname;
    doReload();
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ where, orders, filters }) => {
    return listUsers({ ...where, ...orders, ...filters });
  };

  /** 导出配置 */
  const exportConfig = reactive<ExportConfig>({
    fileName: '基础列表数据',
    datasource: exportSource,
    beforeExport: (params) => {
      const { fileName, closeModal, bodyCols, bodyData, headerData } = params;
      const workbook = getExportWorkbook(params);
      const sheet = workbook.getWorksheet('Sheet1');

      const getBuffer = async () => {
        // 添加头像列图片
        const avatarColIndex = bodyCols.findIndex(
          (c) => c.dataKey === 'avatar'
        );
        if (sheet != null && avatarColIndex !== -1) {
          const avatarBuffers = await Promise.all(
            bodyData.map(async (row) => {
              const url = row[avatarColIndex].text as string | undefined;
              if (!url) {
                return;
              }
              const res = await request({ url, responseType: 'arraybuffer' });
              return res.data;
            })
          );
          avatarBuffers.forEach((buffer, index) => {
            const rowIndex = index + headerData.length;
            if (buffer != null) {
              const imgId = workbook.addImage({ buffer, extension: 'png' });
              sheet.addImage(imgId, {
                tl: { col: avatarColIndex + 0.4, row: rowIndex + 0.2 },
                ext: { width: 48, height: 48 }
              });
              sheet.getCell(rowIndex + 1, avatarColIndex + 1).value = '';
            }
            sheet.getRow(rowIndex + 1).height = 42;
            sheet.getColumn(avatarColIndex + 1).width = 8;
          });
        }
        // 输出workbook
        const data = await workbook.xlsx.writeBuffer();
        return data;
      };

      getBuffer().then((data) => {
        download(data, `${fileName}.xlsx`);
        closeModal();
      });
      return false;
    }
  });
</script>

<style lang="scss" scoped>
  .demo-table :deep(td.demo-table-cell-avatar) {
    padding: 0;
    font-size: 0;
  }
</style>
