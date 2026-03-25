<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        cache-key="ResourceDriverTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="姓名/手机号"
                clearable
                @change="reload"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.licenseType"
                placeholder="驾照类型"
                clearable
                @change="reload"
              >
                <el-option label="A1" value="A1" />
                <el-option label="A2" value="A2" />
                <el-option label="B1" value="B1" />
                <el-option label="B2" value="B2" />
                <el-option label="C1" value="C1" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                @change="reload"
              >
                <el-option label="在岗" :value="1" />
                <el-option label="停用" :value="0" />
                <el-option label="休息" :value="2" />
                <el-option label="离职" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增司机
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            在岗
          </el-tag>
          <el-tag v-else-if="row.status === 0" type="info" size="small">
            停用
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            休息
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="danger" size="small">
            离职
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="openEdit(row)">
            编辑
          </el-link>
          <el-divider direction="vertical" />
          <el-link type="danger" :underline="false" @click="remove(row)">
            删除
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>
    <driver-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import DriverEdit from './components/driver-edit.vue';
  import { pageDrivers, removeDriver } from '@/api/resource/driver';
  import type { Driver } from '@/api/resource/driver/model';

  defineOptions({ name: 'ResourceDriver' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Driver[]>([]);
  const editVisible = ref(false);
  const editData = ref<Driver | null>(null);
  const where = reactive({
    keyword: '',
    licenseType: undefined as string | undefined,
    status: undefined as number | undefined
  });

  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center'
    },
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'name', label: '姓名', minWidth: 100 },
    { prop: 'phone', label: '手机号', minWidth: 120 },
    { prop: 'licenseType', label: '驾照类型', minWidth: 90, align: 'center' },
    { prop: 'licenseNo', label: '驾照号码', minWidth: 140 },
    {
      prop: 'licenseExpire',
      label: '驾照到期',
      minWidth: 110,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 130,
      align: 'center',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageDrivers({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Driver) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Driver) => {
    ElMessageBox.confirm(
      `确定要删除司机"${row.name}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeDriver(row.id!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
