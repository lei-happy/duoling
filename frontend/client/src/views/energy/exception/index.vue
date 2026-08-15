<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <div class="stats">
        待处理 {{ stats.pending || 0 }} · 已处理 {{ stats.processed || 0 }} · 已忽略
        {{ stats.ignored || 0 }}
      </div>
      <el-form :inline="true" @submit.prevent="">
        <el-form-item label="状态">
          <el-select v-model="status" clearable placeholder="全部" style="width: 130px">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="processed" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card>
      <el-table :data="list" v-loading="loading" border>
        <el-table-column label="类型" width="160">
          <template #default="{ row }">
            {{ EXCEPTION_TYPES[row.exceptionType] || row.exceptionType }}
          </template>
        </el-table-column>
        <el-table-column prop="riskLevel" label="等级" width="90" />
        <el-table-column prop="exceptionMessage" label="说明" min-width="280" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            {{ { pending: '待处理', processed: '已处理', ignored: '已忽略' }[row.status] || row.status }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              link
              type="primary"
              @click="openResolve(row, 'processed')"
            >
              已核实
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              @click="openResolve(row, 'ignored')"
            >
              忽略
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>

    <el-dialog
      v-model="visible"
      :title="resolveForm.status === 'ignored' ? '忽略异常' : '核实异常'"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="resolveForm" :rules="rules" label-width="80px">
        <el-form-item label="处理说明" prop="remark">
          <el-input
            v-model.trim="resolveForm.remark"
            type="textarea"
            :rows="3"
            placeholder="写下核实结论，方便以后复查"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">确认</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { exceptionStats, pageExceptions, resolveException } from '@/api/energy';
  import { EXCEPTION_TYPES, asPage } from '../_shared/options';

  defineOptions({ name: 'EnergyException' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const stats = ref<any>({});
  const status = ref<string>();
  const visible = ref(false);
  const formRef = ref<FormInstance>();
  const resolveForm = reactive<any>({ id: 0, status: 'processed', remark: '' });
  const rules: FormRules = {
    remark: [{ required: true, message: '请填写处理说明', trigger: 'blur' }]
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      stats.value = await exceptionStats();
      list.value = asPage(await pageExceptions({ page: 1, limit: 50, status: status.value })).list;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载异常失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };

  const openResolve = (row: any, next: string) => {
    Object.assign(resolveForm, { id: row.id, status: next, remark: '' });
    visible.value = true;
  };

  const save = async () => {
    await formRef.value?.validate();
    saving.value = true;
    try {
      await resolveException(resolveForm.id, {
        status: resolveForm.status,
        remark: resolveForm.remark
      });
      EleMessage.success({
        message: resolveForm.status === 'ignored' ? '已忽略这条异常' : '已标记为处理完成',
        plain: true
      });
      visible.value = false;
      fetchData();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '处理失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  onMounted(fetchData);
</script>
<style scoped>
  .stats {
    margin-bottom: 8px;
    color: var(--el-text-color-secondary);
  }
</style>
