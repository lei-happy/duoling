<!-- 企业产品授权弹窗 -->
<template>
  <ele-modal
    :width="680"
    title="产品授权管理"
    position="center"
    :body-style="{
      padding: '16px 20px',
      minHeight: '200px'
    }"
    v-bind="modalProps"
  >
    <div style="margin-bottom: 16px">
      <ele-text type="placeholder">
        企业：{{ data?.tenantName }}（{{ data?.tenantCode }}）
      </ele-text>
    </div>
    <!-- 已授权的产品列表 -->
    <el-table :data="productList" border stripe :loading="listLoading" size="small">
      <el-table-column prop="versionCode" label="版本编码" width="120" />
      <el-table-column label="生效状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag v-if="isActive(row)" type="success" size="small">生效中</el-tag>
          <el-tag v-else type="info" size="small">已结束</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="startTime" label="授权开始" width="160" />
      <el-table-column prop="endTime" label="授权到期" width="160" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="{ row }">
          <el-popconfirm
            title="确定要取消此授权吗？取消后客户端菜单会自动刷新。"
            @confirm="handleRemove(row)"
          >
            <template #reference>
              <el-button type="danger" link size="small">取消</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-alert
      v-if="activeCount > 1"
      :title="`当前有 ${activeCount} 条生效授权，客户端菜单为多版本叠加。如需切换版本，请勾选下方「替换其他生效授权」。`"
      type="warning"
      :closable="false"
      show-icon
      style="margin-top: 12px"
    />

    <!-- 新增授权表单 -->
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
        <el-col :span="24">
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
          <el-form-item label="授权开始">
            <el-date-picker
              v-model="form.startTime"
              type="datetime"
              placeholder="选择开始时间"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="授权到期">
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
          <el-form-item label="替换语义">
            <el-checkbox v-model="form.replaceActive">
              替换其他生效授权（先取消已有授权再开通本次授权，跳过时间冲突/空档期校验）
            </el-checkbox>
            <div style="font-size: 12px; color: #999; line-height: 1.5">
              勾选后客户端菜单将仅按本次授权版本展示；不勾选则按"叠加"语义生效（多版本菜单合并）。
            </div>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { title: '开通授权', type: 'primary', loading: submitLoading, onClick: () => handleSubmit() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, onMounted } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    listTenantProducts,
    assignTenantProduct,
    removeTenantProduct,
    listProductVersions
  } from '@/api/customer';
  import type { Tenant, TenantProduct, TenantProductCreate } from '@/api/customer/model';

  const props = defineProps<{
    /** 当前企业数据 */
    data?: Tenant | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  /** 表单组件 */
  const formRef = ref<FormInstance | null>(null);

  /** 已授权产品列表 */
  const productList = ref<TenantProduct[]>([]);
  const listLoading = ref(false);

  /** 可选产品版本列表 */
  const versionList = ref<any[]>([]);

  /** 提交状态 */
  const submitLoading = ref(false);

  /** 新增授权表单 */
  const form = reactive<TenantProductCreate & { versionId: number | undefined }>({
    versionId: undefined,
    versionCode: '',
    startTime: undefined,
    endTime: undefined,
    replaceActive: false
  });

  /** 判断授权记录当前是否生效 */
  const isActive = (row: TenantProduct) => {
    if (row.status !== 1) return false;
    if (!row.endTime) return true;
    return new Date(row.endTime).getTime() > Date.now();
  };

  /** 当前生效授权数量 */
  const activeCount = computed(
    () => productList.value.filter((p) => isActive(p)).length
  );

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    versionId: [
      { required: true, message: '请选择产品版本', trigger: 'change' }
    ]
  });

  /** 加载已授权产品列表 */
  const loadProducts = () => {
    if (!props.data?.id) return;
    listLoading.value = true;
    listTenantProducts(props.data.id)
      .then((list) => {
        listLoading.value = false;
        productList.value = list || [];
      })
      .catch((e) => {
        listLoading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 加载可选产品版本 */
  const loadVersions = () => {
    listProductVersions()
      .then((list) => {
        versionList.value = list || [];
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 版本选择变更 */
  const handleVersionChange = (val: number) => {
    const found = versionList.value.find((v) => v.id === val);
    if (found) {
      form.versionCode = found.versionCode;
    }
  };

  /** 取消授权 */
  const handleRemove = (row: TenantProduct) => {
    if (!props.data?.id || !row.id) return;
    removeTenantProduct(props.data.id, row.id)
      .then((msg) => {
        EleMessage.success({ message: msg, plain: true });
        loadProducts();
        emit('done');
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 提交开通授权 */
  const handleSubmit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid || !props.data?.id) return;
      submitLoading.value = true;
      assignTenantProduct(props.data.id, {
        versionId: form.versionId!,
        versionCode: form.versionCode,
        startTime: form.startTime,
        endTime: form.endTime,
        replaceActive: form.replaceActive
      })
        .then((msg) => {
          submitLoading.value = false;
          EleMessage.success({ message: msg, plain: true });
          // 重置表单
          form.versionId = undefined;
          form.versionCode = '';
          form.startTime = undefined;
          form.endTime = undefined;
          form.replaceActive = false;
          formRef.value?.clearValidate?.();
          loadProducts();
          emit('done');
        })
        .catch((e) => {
          submitLoading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  /** 初始化 */
  onMounted(() => {
    loadProducts();
    loadVersions();
  });
</script>
