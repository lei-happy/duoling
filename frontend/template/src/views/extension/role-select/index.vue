<template>
  <ele-page>
    <ele-card header="基础用法">
      <div style="margin: 0 0 8px 0">单选：</div>
      <div style="max-width: 260px">
        <role-select clearable v-model="roleId" placeholder="请选择角色" />
      </div>
      <div style="margin: 22px 0 8px 0">多选：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <role-select
          multiple
          clearable
          v-model="roleId2"
          placeholder="请选择角色"
        />
      </div>
    </ele-card>
    <ele-card header="选择器模式">
      <div style="margin: 0 0 8px 0">单选：</div>
      <el-button type="primary" @click="handleClick">打开角色选择器</el-button>
      <div v-if="selected" style="margin: 8px 0 0 0">
        <div>已选择：</div>
        <div style="word-break: break-all">{{
          JSON.stringify({
            roleId: selected.roleId,
            roleCode: selected.roleCode,
            roleName: selected.roleName,
            comments: selected.comments,
            createTime: selected.createTime
          })
        }}</div>
      </div>
      <role-select
        v-model:visible="showRoleSelect"
        view-type="picker"
        :beforeConfirm="beforeConfirm"
        @select="handleSelect"
      />
      <div style="margin: 22px 0 8px 0">多选：</div>
      <el-button type="primary" @click="handleClick2">打开角色选择器</el-button>
      <div v-if="selected2" style="margin: 8px 0 0 0">
        <div>已选择：</div>
        <div style="word-break: break-all; white-space: pre-wrap">{{
          `[\n${selected2
            .map(
              (d) =>
                `  ${JSON.stringify({
                  roleId: d.roleId,
                  roleCode: d.roleCode,
                  roleName: d.roleName,
                  comments: d.comments,
                  createTime: d.createTime
                })}`
            )
            .join(',\n')}\n]`
        }}</div>
      </div>
      <role-select
        multiple
        v-model:visible="showRoleSelect2"
        view-type="picker"
        :beforeConfirm="beforeConfirm2"
        @select="handleSelect2"
      />
      <div style="margin: 22px 0 0 0">
        选择器模式是通过 v-model:visible 控制打开状态，监听 “确定按钮”
        事件获取选中数据。
      </div>
    </ele-card>
    <ele-card header="更多示例">
      <div style="margin: 0 0 8px 0">抽屉模式：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <role-select
          multiple
          clearable
          v-model="roleId3"
          placeholder="请选择角色"
          popper-type="drawer"
        />
      </div>
      <div style="margin: 22px 0 8px 0">下拉模式：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <role-select
          multiple
          clearable
          v-model="roleId4"
          placeholder="请选择角色"
          popper-type="popper"
          :popper-width="880"
          :popper-height="460"
          :popper-options="{ strategy: 'fixed' }"
          :table-props="{ pagination: { teleported: false } }"
        />
      </div>
      <div style="padding-bottom: 28px">
        <div style="margin: 32px 0 12px 0">选择器抽屉模式：</div>
        <el-button type="primary" @click="handleClick4">
          打开角色选择器
        </el-button>
        <div v-if="selected4" style="margin: 8px 0 0 0">
          <div>已选择：</div>
          <div style="word-break: break-all; white-space: pre-wrap">{{
            selected4.length
              ? `[\n${selected4
                  .map(
                    (d) =>
                      `  ${JSON.stringify({
                        roleId: d.roleId,
                        roleCode: d.roleCode,
                        roleName: d.roleName,
                        comments: d.comments,
                        createTime: d.createTime
                      })}`
                  )
                  .join(',\n')}\n]`
              : '[]'
          }}</div>
        </div>
        <role-select
          popper-type="drawer"
          multiple
          v-model:visible="showRoleSelect4"
          view-type="picker"
          @select="handleSelect4"
          v-model="roleId7"
        />
      </div>
    </ele-card>
    <ele-card header="自定义数据">
      <div style="margin: 0 0 18px 0">
        角色选择组件基于表格选择组件开发，支持 EleTableSelect
        的全部属性，意味着可以当成是一个带有右侧已选列表的表格选择组件：
      </div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <role-select
          multiple
          clearable
          v-model="roleId5"
          placeholder="请选择文件"
          popper-title="文件选择"
          value-key="id"
          label-key="name"
          :table-props="{ datasource, columns }"
          :componentLang="{
            labelRoleName: '文件名称',
            labelRoleCode: '上传人'
          }"
          :item-icon="FileOutlined"
          :max-tag-text-length="20"
        />
      </div>
      <div style="padding-bottom: 38px">
        <div style="margin: 32px 0 12px 0">选择器模式：</div>
        <el-button type="primary" @click="handleClick3">
          打开文件选择器
        </el-button>
        <div v-if="selected3" style="margin: 8px 0 0 0">
          <div>已选择：</div>
          <div style="word-break: break-all; white-space: pre-wrap">{{
            selected3.length
              ? `[\n${selected3
                  .map(
                    (d) =>
                      `  ${JSON.stringify({
                        id: d.id,
                        name: d.name,
                        length: d.length,
                        createNickname: d.createNickname,
                        createTime: d.createTime
                      })}`
                  )
                  .join(',\n')}\n]`
              : '[]'
          }}</div>
        </div>
        <role-select
          multiple
          v-model:visible="showRoleSelect3"
          view-type="picker"
          @select="handleSelect3"
          v-model="roleId6"
          popper-title="文件选择"
          value-key="id"
          label-key="name"
          :table-props="{ datasource, columns }"
          :componentLang="{
            labelRoleName: '文件名称',
            labelRoleCode: '上传人'
          }"
          :item-icon="FileOutlined"
        />
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { FileOutlined } from '@/components/icons';
  import type { Role } from '@/api/system/role/model';
  import { pageFiles } from '@/api/system/file';
  import type { FileRecord } from '@/api/system/file/model';

  defineOptions({ name: 'ExtensionRoleSelect' });

  /** 选中角色的id */
  const roleId = ref();

  /** 2选中角色的id */
  const roleId2 = ref();

  /** 是否打开角色选择器 */
  const showRoleSelect = ref(false);

  /** 角色选择器选中的数据 */
  const selected = ref<Role>();

  /** 打开角色选择器 */
  const handleClick = () => {
    showRoleSelect.value = true;
  };

  /** 角色选择器选择完成事件 */
  const handleSelect = (result: Role) => {
    selected.value = result;
  };

  /** 角色选择器确认按钮点击事件 */
  const beforeConfirm = (result?: Role) => {
    if (!result) {
      EleMessage.error({ message: '请选择一个角色', plain: true });
      return false;
    }
  };

  /** 角色选择器2选中的数据 */
  const selected2 = ref<Role[]>();

  /** 是否打开角色选择器2 */
  const showRoleSelect2 = ref(false);

  /** 打开角色选择器2 */
  const handleClick2 = () => {
    showRoleSelect2.value = true;
  };

  /** 角色选择器2选择完成事件 */
  const handleSelect2 = (result: Role[]) => {
    selected2.value = result;
  };

  /** 角色选择器2确认按钮点击事件 */
  const beforeConfirm2 = (result?: Role[]) => {
    if (!result?.length) {
      EleMessage.error({ message: '请至少选择一个角色', plain: true });
      return false;
    }
  };

  /** 3选中角色的id */
  const roleId3 = ref();

  /** 4选中角色的id */
  const roleId4 = ref();

  /** 5选中角色的id */
  const roleId5 = ref();

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageFiles({
      name: where.roleName,
      createNickname: where.roleCode,
      ...orders,
      ...pages
    });
  };

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center',
      showOverflowTooltip: false,
      reserveSelection: true
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
    }
  ]);

  /** 6选中角色的id */
  const roleId6 = ref();

  /** 角色选择器3选中的数据 */
  const selected3 = ref<FileRecord[]>();

  /** 是否打开角色选择器3 */
  const showRoleSelect3 = ref(false);

  /** 打开角色选择器3 */
  const handleClick3 = () => {
    showRoleSelect3.value = true;
  };

  /** 角色选择器3选择完成事件 */
  const handleSelect3 = (result: FileRecord[]) => {
    selected3.value = result;
  };

  /** 7选中角色的id */
  const roleId7 = ref();

  /** 角色选择器4选中的数据 */
  const selected4 = ref<Role[]>();

  /** 是否打开角色选择器4 */
  const showRoleSelect4 = ref(false);

  /** 打开角色选择器4 */
  const handleClick4 = () => {
    showRoleSelect4.value = true;
  };

  /** 角色选择器4选择完成事件 */
  const handleSelect4 = (result: Role[]) => {
    selected4.value = result;
  };
</script>
