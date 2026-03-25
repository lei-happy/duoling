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
        cache-key="ResourceCustomerTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="客户名称/联系人"
                clearable
                @change="reload"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.customerType"
                placeholder="客户类型"
                clearable
                @change="reload"
              >
                <el-option label="托运方" :value="0" />
                <el-option label="收货方" :value="1" />
                <el-option label="两者兼具" :value="2" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                @change="reload"
              >
                <el-option label="正常" :value="1" />
                <el-option label="停用" :value="0" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增客户
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #customerType="{ row }">
          <el-tag v-if="row.customerType === 0" size="small">托运方</el-tag>
          <el-tag v-else-if="row.customerType === 1" type="success" size="small">
            收货方
          </el-tag>
          <el-tag v-else-if="row.customerType === 2" type="warning" size="small">
            两者兼具
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            正常
          </el-tag>
          <el-tag v-else-if="row.status === 0" type="info" size="small">
            停用
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
    <customer-edit
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
  import CustomerEdit from './components/customer-edit.vue';
  import { pageCustomers, removeCustomer } from '@/api/resource/customer';
  import type { Customer } from '@/api/resource/customer/model';

  defineOptions({ name: 'ResourceCustomer' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Customer[]>([]);
  const editVisible = ref(false);
  const editData = ref<Customer | null>(null);
  const where = reactive({
    keyword: '',
    customerType: undefined as number | undefined,
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
    { prop: 'customerName', label: '客户名称', minWidth: 160 },
    { prop: 'shortName', label: '简称', minWidth: 100 },
    {
      prop: 'customerType',
      label: '客户类型',
      minWidth: 100,
      align: 'center',
      slot: 'customerType'
    },
    { prop: 'contactPerson', label: '联系人', minWidth: 100 },
    { prop: 'contactPhone', label: '联系电话', minWidth: 120 },
    { prop: 'address', label: '地址', minWidth: 180 },
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
    const res = await pageCustomers({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Customer) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Customer) => {
    ElMessageBox.confirm(
      `确定要删除客户"${row.customerName}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeCustomer(row.id!)
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
