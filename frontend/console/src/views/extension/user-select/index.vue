<template>
  <ele-page>
    <ele-card header="基础用法">
      <div style="margin: 0 0 8px 0">单选：</div>
      <div style="max-width: 260px">
        <user-select clearable v-model="userId" placeholder="请选择用户" />
      </div>
      <div style="margin: 22px 0 8px 0">多选：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <user-select
          multiple
          clearable
          v-model="userId2"
          placeholder="请选择用户"
        />
      </div>
    </ele-card>
    <ele-card header="头像模式">
      <div style="margin: 0 0 8px 0">单选：</div>
      <div style="max-width: 260px">
        <user-select
          clearable
          v-model="userId3"
          placeholder="请选择用户"
          view-type="avatar"
        />
      </div>
      <div style="margin: 22px 0 8px 0">多选：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <user-select
          multiple
          clearable
          v-model="userId4"
          placeholder="请选择用户"
          view-type="avatar"
        />
      </div>
    </ele-card>
    <ele-card header="选择器模式">
      <div style="margin: 0 0 8px 0">单选：</div>
      <el-button type="primary" @click="handleClick">打开用户选择器</el-button>
      <div v-if="selected" style="margin: 8px 0 0 0">
        <div>已选择：</div>
        <div style="word-break: break-all">{{
          JSON.stringify({
            userId: selected.userId,
            username: selected.username,
            nickname: selected.nickname,
            sexName: selected.sexName,
            phone: selected.phone,
            organizationName: selected.organizationName
          })
        }}</div>
      </div>
      <user-select
        v-model:visible="showUserSelect"
        view-type="picker"
        :beforeConfirm="beforeConfirm"
        @select="handleSelect"
      />
      <div style="margin: 22px 0 8px 0">多选：</div>
      <el-button type="primary" @click="handleClick2">打开用户选择器</el-button>
      <div v-if="selected2" style="margin: 8px 0 0 0">
        <div>已选择：</div>
        <div style="word-break: break-all; white-space: pre-wrap">{{
          `[\n${selected2
            .map(
              (d) =>
                `  ${JSON.stringify({
                  userId: d.userId,
                  username: d.username,
                  nickname: d.nickname,
                  sexName: d.sexName,
                  phone: d.phone,
                  organizationName: d.organizationName
                })}`
            )
            .join(',\n')}\n]`
        }}</div>
      </div>
      <user-select
        multiple
        v-model:visible="showUserSelect2"
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
        <user-select
          multiple
          clearable
          v-model="userId5"
          placeholder="请选择用户"
          popper-type="drawer"
        />
      </div>
      <div style="margin: 22px 0 8px 0">下拉模式：</div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <user-select
          multiple
          clearable
          v-model="userId6"
          placeholder="请选择用户"
          popper-type="popper"
          :popper-width="1030"
          :popper-height="580"
          :popper-options="{ strategy: 'fixed' }"
          :table-props="{ pagination: { teleported: false } }"
        />
      </div>
      <div style="padding-bottom: 28px">
        <div style="margin: 32px 0 12px 0">选择器抽屉模式：</div>
        <el-button type="primary" @click="handleClick4">
          打开用户选择器
        </el-button>
        <div v-if="selected4" style="margin: 8px 0 0 0">
          <div>已选择：</div>
          <div style="word-break: break-all; white-space: pre-wrap">{{
            selected4.length
              ? `[\n${selected4
                  .map(
                    (d) =>
                      `  ${JSON.stringify({
                        userId: d.userId,
                        username: d.username,
                        nickname: d.nickname,
                        sexName: d.sexName,
                        phone: d.phone,
                        organizationName: d.organizationName
                      })}`
                  )
                  .join(',\n')}\n]`
              : '[]'
          }}</div>
        </div>
        <user-select
          popper-type="drawer"
          multiple
          v-model:visible="showUserSelect4"
          view-type="picker"
          @select="handleSelect4"
          v-model="userId7"
        />
      </div>
    </ele-card>
    <ele-card header="自定义数据">
      <div style="margin: 0 0 18px 0">
        用户选择组件基于表格选择组件开发，支持 EleTableSelect
        的全部属性，意味着可以当成是一个带有分割面板的表格选择组件：
      </div>
      <div style="max-width: 260px; margin-bottom: 8px">
        <user-select
          multiple
          clearable
          v-model="userId8"
          placeholder="请选择字典"
          popper-title="字典选择"
          value-key="dictDataId"
          label-key="dictDataName"
          :table-props="{ datasource, columns }"
          :componentLang="{
            searchPlaceholder: '输入字典分类名搜索',
            labelNickname: '数据名',
            labelPhone: '数据值'
          }"
          :tree-list-api="treeListApi"
          :item-icon="BookOutlined"
          :max-tag-text-length="20"
        />
      </div>
      <div style="padding-bottom: 72px">
        <div style="margin: 32px 0 12px 0">选择器模式：</div>
        <el-button type="primary" @click="handleClick3">
          打开字典选择器
        </el-button>
        <div v-if="selected3" style="margin: 8px 0 0 0">
          <div>已选择：</div>
          <div style="word-break: break-all; white-space: pre-wrap">{{
            selected3.length
              ? `[\n${selected3
                  .map(
                    (d) =>
                      `  ${JSON.stringify({
                        dictDataId: d.dictDataId,
                        dictDataName: d.dictDataName,
                        dictDataCode: d.dictDataCode,
                        sortNumber: d.sortNumber,
                        createTime: d.createTime
                      })}`
                  )
                  .join(',\n')}\n]`
              : '[]'
          }}</div>
        </div>
        <user-select
          multiple
          v-model:visible="showUserSelect3"
          view-type="picker"
          @select="handleSelect3"
          v-model="userId9"
          popper-title="字典选择"
          value-key="dictDataId"
          label-key="dictDataName"
          :table-props="{ datasource, columns }"
          :componentLang="{
            searchPlaceholder: '输入字典分类名搜索',
            labelNickname: '数据名',
            labelPhone: '数据值'
          }"
          :tree-list-api="treeListApi"
          :item-icon="BookOutlined"
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
  import { BookOutlined } from '@/components/icons';
  import type { User } from '@/api/system/user/model';
  import { pageDictionaryData } from '@/api/system/dictionary-data';
  import type { DictionaryData } from '@/api/system/dictionary-data/model';
  import { listDictionaries } from '@/api/system/dictionary';

  defineOptions({ name: 'ExtensionUserSelect' });

  /** 选中用户的id */
  const userId = ref();

  /** 2选中用户的id */
  const userId2 = ref();

  /** 3选中用户的id */
  const userId3 = ref();

  /** 4选中用户的id */
  const userId4 = ref();

  /** 是否打开用户选择器 */
  const showUserSelect = ref(false);

  /** 用户选择器选中的数据 */
  const selected = ref<User>();

  /** 打开用户选择器 */
  const handleClick = () => {
    showUserSelect.value = true;
  };

  /** 用户选择器选择完成事件 */
  const handleSelect = (result: User) => {
    selected.value = result;
  };

  /** 用户选择器确认按钮点击事件 */
  const beforeConfirm = (result?: User) => {
    if (!result) {
      EleMessage.error({ message: '请选择一个用户', plain: true });
      return false;
    }
  };

  /** 用户选择器2选中的数据 */
  const selected2 = ref<User[]>();

  /** 是否打开用户选择器2 */
  const showUserSelect2 = ref(false);

  /** 打开用户选择器2 */
  const handleClick2 = () => {
    showUserSelect2.value = true;
  };

  /** 用户选择器2选择完成事件 */
  const handleSelect2 = (result: User[]) => {
    selected2.value = result;
  };

  /** 用户选择器2确认按钮点击事件 */
  const beforeConfirm2 = (result?: User[]) => {
    if (!result?.length) {
      EleMessage.error({ message: '请至少选择一个用户', plain: true });
      return false;
    }
  };

  /** 5选中用户的id */
  const userId5 = ref();

  /** 6选中用户的id */
  const userId6 = ref();

  /** 7选中用户的id */
  const userId7 = ref();

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageDictionaryData({
      dictDataName: where.nickname,
      dictDataCode: where.phone,
      dictId: where.organizationId,
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
      prop: 'dictDataName',
      label: '字典数据名',
      sortable: 'custom',
      minWidth: 120
    },
    {
      prop: 'dictDataCode',
      label: '字典数据值',
      sortable: 'custom',
      minWidth: 120
    },
    {
      prop: 'sortNumber',
      label: '排序号',
      sortable: 'custom',
      width: 100,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      width: 180,
      align: 'center'
    }
  ]);

  const treeListApi = async (): Promise<any> => {
    const data = await listDictionaries();
    return (data || []).map((d) => ({
      ...d,
      organizationId: d.dictId,
      organizationName: d.dictName
    }));
  };

  /** 8选中用户的id */
  const userId8 = ref();

  /** 用户选择器3选中的数据 */
  const selected3 = ref<DictionaryData[]>();

  /** 是否打开用户选择器3 */
  const showUserSelect3 = ref(false);

  /** 打开用户选择器3 */
  const handleClick3 = () => {
    showUserSelect3.value = true;
  };

  /** 用户选择器3选择完成事件 */
  const handleSelect3 = (result: DictionaryData[]) => {
    selected3.value = result;
  };

  /** 9选中用户的id */
  const userId9 = ref();

  /** 用户选择器4选中的数据 */
  const selected4 = ref<User[]>();

  /** 是否打开用户选择器4 */
  const showUserSelect4 = ref(false);

  /** 打开用户选择器4 */
  const handleClick4 = () => {
    showUserSelect4.value = true;
  };

  /** 用户选择器4选择完成事件 */
  const handleSelect4 = (result: User[]) => {
    selected4.value = result;
  };
</script>
