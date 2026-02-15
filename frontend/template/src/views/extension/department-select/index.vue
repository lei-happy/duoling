<template>
  <ele-page>
    <ele-card header="基础用法">
      <div style="margin: 0 0 8px 0">单选：</div>
      <div style="max-width: 260px">
        <department-select
          clearable
          v-model="deptId"
          placeholder="请选择部门"
        />
      </div>
      <div style="margin: 22px 0 8px 0">多选：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <department-select
          multiple
          clearable
          v-model="dept2"
          placeholder="请选择部门"
        />
      </div>
    </ele-card>
    <ele-card header="选择器模式">
      <div style="margin: 0 0 8px 0">单选：</div>
      <el-button type="primary" @click="handleClick">打开部门选择器</el-button>
      <div v-if="selected" style="margin: 8px 0 0 0">
        <div>已选择：</div>
        <div style="word-break: break-all">{{
          JSON.stringify({
            organizationId: selected.organizationId,
            organizationName: selected.organizationName,
            organizationTypeName: selected.organizationTypeName,
            sortNumber: selected.sortNumber,
            createTime: selected.createTime
          })
        }}</div>
      </div>
      <department-select
        v-model:visible="showDeptSelect"
        view-type="picker"
        :beforeConfirm="beforeConfirm"
        @select="handleSelect"
      />
      <div style="margin: 22px 0 8px 0">多选：</div>
      <el-button type="primary" @click="handleClick2">打开部门选择器</el-button>
      <div v-if="selected2" style="margin: 8px 0 0 0">
        <div>已选择：</div>
        <div style="word-break: break-all; white-space: pre-wrap">{{
          `[\n${selected2
            .map(
              (d) =>
                `  ${JSON.stringify({
                  organizationId: d.organizationId,
                  organizationName: d.organizationName,
                  organizationTypeName: d.organizationTypeName,
                  sortNumber: d.sortNumber,
                  createTime: d.createTime
                })}`
            )
            .join(',\n')}\n]`
        }}</div>
      </div>
      <department-select
        multiple
        v-model:visible="showDeptSelect2"
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
        <department-select
          multiple
          clearable
          v-model="deptId3"
          placeholder="请选择部门"
          popper-type="drawer"
          :popper-width="560"
        />
      </div>
      <div style="margin: 22px 0 8px 0">下拉模式：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <department-select
          multiple
          clearable
          v-model="deptId4"
          placeholder="请选择部门"
          popper-type="popper"
          :popper-width="560"
          popper-height="auto"
          :tree-props="{ height: 340 }"
        />
      </div>
      <div style="padding-bottom: 28px">
        <div style="margin: 32px 0 12px 0">选择器抽屉模式：</div>
        <el-button type="primary" @click="handleClick4">
          打开部门选择器
        </el-button>
        <div v-if="selected4" style="margin: 8px 0 0 0">
          <div>已选择：</div>
          <div style="word-break: break-all; white-space: pre-wrap">{{
            selected4.length
              ? `[\n${selected4
                  .map(
                    (d) =>
                      `  ${JSON.stringify({
                        organizationId: d.organizationId,
                        organizationName: d.organizationName,
                        organizationTypeName: d.organizationTypeName,
                        sortNumber: d.sortNumber,
                        createTime: d.createTime
                      })}`
                  )
                  .join(',\n')}\n]`
              : '[]'
          }}</div>
        </div>
        <department-select
          popper-type="drawer"
          multiple
          v-model:visible="showDeptSelect4"
          view-type="picker"
          @select="handleSelect4"
          v-model="deptId7"
        />
      </div>
    </ele-card>
    <ele-card header="自定义数据">
      <div style="margin: 0 0 18px 0">
        部门选择组件基于树选择组件开发，支持 EleTreeSelect
        的全部属性，意味着可以当成是一个带有右侧已选列表的树选择组件：
      </div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <department-select
          multiple
          clearable
          v-model="deptId5"
          placeholder="请选择菜单"
          popper-title="菜单选择"
          :list-api="listApi"
          :tree-props="{ props: { value: 'menuId', label: 'title' } }"
          :item-icon="AppstoreOutlined"
          :max-tag-text-length="20"
        />
      </div>
      <div style="padding-bottom: 38px">
        <div style="margin: 32px 0 12px 0">选择器模式：</div>
        <el-button type="primary" @click="handleClick3">
          打开菜单选择器
        </el-button>
        <div v-if="selected3" style="margin: 8px 0 0 0">
          <div>已选择：</div>
          <div style="word-break: break-all; white-space: pre-wrap">{{
            selected3.length
              ? `[\n${selected3
                  .map(
                    (d) =>
                      `  ${JSON.stringify({
                        menuId: d.menuId,
                        title: d.title,
                        path: d.path,
                        icon: d.icon,
                        createTime: d.createTime
                      })}`
                  )
                  .join(',\n')}\n]`
              : '[]'
          }}</div>
        </div>
        <department-select
          multiple
          v-model:visible="showDeptSelect3"
          view-type="picker"
          @select="handleSelect3"
          v-model="deptId6"
          popper-title="菜单选择"
          :list-api="listApi"
          :tree-props="{ props: { value: 'menuId', label: 'title' } }"
          :item-icon="AppstoreOutlined"
        />
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, toTree } from 'ele-admin-plus';
  import { AppstoreOutlined } from '@/components/icons';
  import type { Organization } from '@/api/system/organization/model';
  import { listMenus } from '@/api/system/menu';
  import type { Menu } from '@/api/system/menu/model';

  defineOptions({ name: 'ExtensionDepartmentSelect' });

  /** 选中部门的id */
  const deptId = ref();

  /** 2选中部门的id */
  const dept2 = ref();

  /** 是否打开部门选择器 */
  const showDeptSelect = ref(false);

  /** 部门选择器选中的数据 */
  const selected = ref<Organization>();

  /** 打开部门选择器 */
  const handleClick = () => {
    showDeptSelect.value = true;
  };

  /** 部门选择器选择完成事件 */
  const handleSelect = (result: Organization) => {
    selected.value = result;
  };

  /** 部门选择器确认按钮点击事件 */
  const beforeConfirm = (result?: Organization) => {
    if (!result) {
      EleMessage.error({ message: '请选择一个部门', plain: true });
      return false;
    }
  };

  /** 部门选择器2选中的数据 */
  const selected2 = ref<Organization[]>();

  /** 是否打开部门选择器2 */
  const showDeptSelect2 = ref(false);

  /** 打开部门选择器2 */
  const handleClick2 = () => {
    showDeptSelect2.value = true;
  };

  /** 部门选择器2选择完成事件 */
  const handleSelect2 = (result: Organization[]) => {
    selected2.value = result;
  };

  /** 部门选择器2确认按钮点击事件 */
  const beforeConfirm2 = (result?: Organization[]) => {
    if (!result?.length) {
      EleMessage.error({ message: '请至少选择一个部门', plain: true });
      return false;
    }
  };

  /** 3选中部门的id */
  const deptId3 = ref();

  /** 4选中部门的id */
  const deptId4 = ref();

  /** 5选中部门的id */
  const deptId5 = ref();

  /** 树数据源 */
  const listApi = async () => {
    const data = await listMenus();
    return toTree({
      data,
      idField: 'menuId',
      parentIdField: 'parentId'
    });
  };

  /** 6选中部门的id */
  const deptId6 = ref();

  /** 部门选择器3选中的数据 */
  const selected3 = ref<Menu[]>();

  /** 是否打开部门选择器3 */
  const showDeptSelect3 = ref(false);

  /** 打开部门选择器3 */
  const handleClick3 = () => {
    showDeptSelect3.value = true;
  };

  /** 部门选择器3选择完成事件 */
  const handleSelect3 = (result: Menu[]) => {
    selected3.value = result;
  };

  /** 7选中部门的id */
  const deptId7 = ref();

  /** 部门选择器4选中的数据 */
  const selected4 = ref<Organization[]>();

  /** 是否打开部门选择器4 */
  const showDeptSelect4 = ref(false);

  /** 打开部门选择器4 */
  const handleClick4 = () => {
    showDeptSelect4.value = true;
  };

  /** 部门选择器4选择完成事件 */
  const handleSelect4 = (result: Organization[]) => {
    selected4.value = result;
  };
</script>
