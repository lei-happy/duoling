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
        cache-key="BillingContractTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="合同编号/名称/客户名称"
                clearable
                @change="reload"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="合同状态"
                clearable
                @change="reload"
              >
                <el-option label="草稿" :value="0" />
                <el-option label="生效" :value="1" />
                <el-option label="已过期" :value="2" />
                <el-option label="已终止" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增合同
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 0" type="info" size="small">
            草稿
          </el-tag>
          <el-tag v-else-if="row.status === 1" type="success" size="small">
            生效
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            已过期
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="danger" size="small">
            已终止
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="openEdit(row)">
            编辑
          </el-link>
          <el-divider direction="vertical" />
          <el-link type="primary" :underline="false" @click="openDetail(row)">
            详情
          </el-link>
          <template v-if="row.status === 1">
            <el-divider direction="vertical" />
            <el-link
              type="warning"
              :underline="false"
              @click="terminate(row)"
            >
              终止
            </el-link>
          </template>
          <template v-if="row.status === 0">
            <el-divider direction="vertical" />
            <el-link
              type="success"
              :underline="false"
              @click="activate(row)"
            >
              激活
            </el-link>
            <el-divider direction="vertical" />
            <el-link type="danger" :underline="false" @click="remove(row)">
              删除
            </el-link>
          </template>
        </template>
      </ele-pro-table>
    </ele-card>
    <contract-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
    <contract-detail
      v-model:visible="detailVisible"
      :data="detailData"
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
  import ContractEdit from './components/contract-edit.vue';
  import ContractDetail from './components/contract-detail.vue';
  import {
    pageContracts,
    activateContract,
    terminateContract,
    removeContract
  } from '@/api/billing/contract';
  import type { FreightContract } from '@/api/billing/contract/model';

  defineOptions({ name: 'BillingContract' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<FreightContract[]>([]);
  const editVisible = ref(false);
  const editData = ref<FreightContract | null>(null);
  const detailVisible = ref(false);
  const detailData = ref<FreightContract | null>(null);
  const where = reactive({
    keyword: '',
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
    { prop: 'contractNo', label: '合同编号', minWidth: 140 },
    { prop: 'contractName', label: '合同名称', minWidth: 160 },
    { prop: 'customerName', label: '客户名称', minWidth: 140 },
    { prop: 'effectiveDate', label: '生效日期', minWidth: 120, align: 'center' },
    { prop: 'expiryDate', label: '失效日期', minWidth: 120, align: 'center' },
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
      width: 220,
      align: 'center',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageContracts({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.total ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: FreightContract) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openDetail = (row: FreightContract) => {
    detailData.value = row;
    detailVisible.value = true;
  };

  const activate = (row: FreightContract) => {
    ElMessageBox.confirm(
      `确定要激活合同"${row.contractName}"吗？激活后将参与运费匹配。`,
      '系统提示',
      { type: 'info', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        activateContract(row.id!)
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

  const terminate = (row: FreightContract) => {
    ElMessageBox.confirm(
      `确定要终止合同"${row.contractName}"吗？终止后不可恢复。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        terminateContract(row.id!)
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

  const remove = (row: FreightContract) => {
    ElMessageBox.confirm(
      `确定要删除合同"${row.contractName}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeContract(row.id!)
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
