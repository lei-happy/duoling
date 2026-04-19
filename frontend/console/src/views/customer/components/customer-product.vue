<!-- 客户产品授权弹窗 -->
<template>
  <ele-modal
    :width="780"
    title=""
    position="center"
    :body-style="{
      padding: '16px 20px',
      minHeight: '200px'
    }"
    v-bind="modalProps"
  >
    <template #header>
      <span style="color: var(--el-color-primary); font-weight: 600">{{ data?.tenantName }}</span>
      <span style="color: var(--el-text-color-secondary); font-size: 13px; margin: 0 4px">（{{ data?.tenantCode }}）</span>
      <span>授权管理</span>
    </template>
    <!-- 已授权的产品列表 -->
    <el-table
      :data="productList"
      border
      stripe
      :loading="listLoading"
      size="small"
      style="width: 100%"
    >
      <el-table-column label="产品版本" min-width="120">
        <template #default="{ row }">
          {{ getVersionName(row.versionCode) || row.versionCode }}
          <span style="color: var(--el-text-color-placeholder); margin-left: 4px; font-size: 12px">{{ row.versionCode }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="startTime" label="授权开始" min-width="140"/>
      <el-table-column prop="endTime" label="授权到期" min-width="140" />
      <el-table-column label="开通类型" min-width="100" align="center">
        <template #default="{ row }">
          <dict-data
            v-if="row.grantType"
            code="grant_type"
            type="tag"
            v-model="row.grantType"
          />
          <span v-else style="color: var(--el-text-color-placeholder)">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="grantRemark" label="开通备注" min-width="120" show-overflow-tooltip />
      <el-table-column label="操作" width="80" align="center" fixed="right">
        <template #default="{ row }">
          <el-popconfirm
            v-if="canRemove(row)"
            title="确定要取消此授权吗？"
            @confirm="handleRemove(row)"
          >
            <template #reference>
              <el-button type="danger" link size="small">取消</el-button>
            </template>
          </el-popconfirm>
          <span v-else style="color: var(--el-text-color-placeholder)">-</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增授权：折叠交互 -->
    <div v-if="!showForm" style="margin-top: 16px; text-align: center">
      <el-button type="primary" plain @click="handleShowForm">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>新增授权
      </el-button>
    </div>
    <template v-else>
      <el-divider content-position="left">开通新授权</el-divider>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        @submit.prevent=""
        size="default"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="产品版本" prop="versionId">
              <el-select
                v-model="form.versionId"
                placeholder="请选择产品版本"
                style="width: 100%"
                @change="handleVersionChange"
              >
                <el-option
                  v-for="v in versionList"
                  :key="v.id"
                  :label="`${v.versionName}（${v.versionCode}）`"
                  :value="v.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开通类型" prop="grantType">
              <dict-data
                code="grant_type"
                type="select"
                v-model="form.grantType"
                placeholder="请选择开通类型"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授权开始" prop="startTime">
              <el-date-picker
                v-model="form.startTime"
                type="datetime"
                placeholder="选择开始时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
                :disabled="startTimeLocked"
              />
              <div
                v-if="startTimeLocked"
                style="font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.4"
              >
                时间闭环：自动衔接上一条授权的到期时间，避免空档
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授权到期" prop="endTime">
              <el-date-picker
                v-model="form.endTime"
                type="datetime"
                placeholder="选择到期时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="开通备注">
              <el-input
                v-model="form.grantRemark"
                type="textarea"
                :rows="2"
                placeholder="请输入开通备注（选填）"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <div style="text-align: right">
          <el-button @click="handleCollapseForm">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            开通授权
          </el-button>
        </div>
      </el-form>
    </template>

  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Plus } from '@element-plus/icons-vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    listCustomerProducts,
    assignCustomerProduct,
    removeCustomerProduct,
    listProductVersions
  } from '@/api/customer';
  import type { Customer, CustomerProduct } from '@/api/customer/model';

  const props = defineProps<{
    data?: Customer | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps } = useModal();

  const formRef = ref<FormInstance | null>(null);
  const productList = ref<CustomerProduct[]>([]);
  const listLoading = ref(false);
  const versionList = ref<any[]>([]);
  const submitLoading = ref(false);
  const showForm = ref(false);
  // 仅当存在「未来到期」的有效授权时才锁定开始时间为时间闭环；
  // 否则（无任何授权 / 历史全部过期）允许运营手工选择开始时间。
  const startTimeLocked = ref(false);

  const createEmptyForm = () => ({
    versionId: undefined as number | undefined,
    versionCode: '',
    startTime: undefined as string | undefined,
    endTime: undefined as string | undefined,
    grantType: undefined as string | undefined,
    grantRemark: undefined as string | undefined
  });

  const form = reactive(createEmptyForm());

  const rules = reactive<FormRules>({
    versionId: [
      { required: true, message: '请选择产品版本', trigger: 'change' }
    ],
    grantType: [
      { required: true, message: '请选择开通类型', trigger: 'change' }
    ],
    startTime: [
      { required: true, message: '请选择授权开始时间', trigger: 'change' }
    ],
    endTime: [
      { required: true, message: '请选择授权到期时间', trigger: 'change' }
    ]
  });

  const getVersionName = (code?: string) => {
    if (!code) return '';
    const found = versionList.value.find((v) => v.versionCode === code);
    return found?.versionName || '';
  };

  const loadProducts = () => {
    if (!props.data?.id) return;
    listLoading.value = true;
    listCustomerProducts(props.data.id)
      .then((list) => {
        listLoading.value = false;
        productList.value = list || [];
      })
      .catch((e) => {
        listLoading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const loadVersions = () => {
    listProductVersions()
      .then((list) => {
        versionList.value = list || [];
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const handleVersionChange = (val: number) => {
    const found = versionList.value.find((v) => v.id === val);
    if (found) {
      form.versionCode = found.versionCode;
    }
  };

  const canRemove = (row: CustomerProduct) => {
    if (!row.endTime || !productList.value.length) return true;
    const maxEndTime = productList.value.reduce((latest, p) => {
      if (!p.endTime) return latest;
      return p.endTime > latest ? p.endTime : latest;
    }, '');
    return row.endTime === maxEndTime;
  };

  const handleRemove = (row: CustomerProduct) => {
    if (!props.data?.id || !row.id) return;
    removeCustomerProduct(props.data.id, row.id)
      .then((msg) => {
        EleMessage.success({ message: msg, plain: true });
        loadProducts();
        emit('done');
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const addDays = (dateStr: string, days: number) => {
    const d = new Date(dateStr.replace(/-/g, '/'));
    d.setDate(d.getDate() + days);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  };

  const formatNow = () => {
    const d = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  };

  /**
   * 取「当前时间之后到期」的最大 endTime；如果不存在则返回空串。
   * 历史已过期 / 已取消的记录不再纳入时间闭环计算，避免运营被锁在过去时间无法新建授权。
   */
  const findActiveLatestEndTime = (): string => {
    const nowStr = formatNow();
    return productList.value.reduce((latest, p) => {
      if (!p.endTime) return latest; // 永久授权不参与闭环
      if (p.endTime <= nowStr) return latest; // 已过期不参与闭环
      return p.endTime > latest ? p.endTime : latest;
    }, '');
  };

  const handleShowForm = () => {
    const latestEndTime = findActiveLatestEndTime();
    Object.assign(form, createEmptyForm());
    if (latestEndTime) {
      // 时间闭环：从上一条有效授权的到期时间开始
      form.startTime = latestEndTime;
      form.endTime = addDays(latestEndTime, 10);
      startTimeLocked.value = true;
    } else {
      // 无有效授权（取消全部 / 历史全部过期 / 全新客户）
      // 默认从当前时间开始，且开放编辑
      form.startTime = formatNow();
      form.endTime = addDays(form.startTime, 10);
      startTimeLocked.value = false;
    }
    showForm.value = true;
  };

  const handleCollapseForm = () => {
    showForm.value = false;
    Object.assign(form, createEmptyForm());
  };

  const handleSubmit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid || !props.data?.id) return;
      submitLoading.value = true;
      assignCustomerProduct(props.data.id, {
        versionId: form.versionId!,
        versionCode: form.versionCode,
        startTime: form.startTime,
        endTime: form.endTime,
        grantType: form.grantType,
        grantRemark: form.grantRemark
      })
        .then((msg) => {
          submitLoading.value = false;
          EleMessage.success({ message: msg, plain: true });
          showForm.value = false;
          Object.assign(form, createEmptyForm());
          loadProducts();
          emit('done');
        })
        .catch((e) => {
          submitLoading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  onMounted(() => {
    loadProducts();
    loadVersions();
  });
</script>
