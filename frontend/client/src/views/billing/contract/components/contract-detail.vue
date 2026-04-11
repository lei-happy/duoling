<template>
  <el-drawer
    title="合同详情"
    :model-value="visible"
    @update:model-value="updateVisible"
    :size="800"
    direction="rtl"
  >
    <template v-if="data">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="合同编号">
          {{ data.contractNo }}
        </el-descriptions-item>
        <el-descriptions-item label="合同名称">
          {{ data.contractName }}
        </el-descriptions-item>
        <el-descriptions-item label="客户名称">
          {{ data.customerName }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="data.status === 0" type="info" size="small">
            草稿
          </el-tag>
          <el-tag v-else-if="data.status === 1" type="success" size="small">
            生效
          </el-tag>
          <el-tag v-else-if="data.status === 2" type="warning" size="small">
            已过期
          </el-tag>
          <el-tag v-else-if="data.status === 3" type="danger" size="small">
            已终止
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="生效日期">
          {{ data.effectiveDate }}
        </el-descriptions-item>
        <el-descriptions-item label="失效日期">
          {{ data.expiryDate }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ data.remark || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">运价明细</el-divider>

      <div style="margin-bottom: 12px">
        <el-button type="primary" size="small" @click="openRateEdit()">
          新增运价
        </el-button>
      </div>

      <el-table :data="rates" border stripe size="small">
        <el-table-column type="index" width="50" align="center" />
        <el-table-column prop="origin" label="出发地" min-width="100" />
        <el-table-column prop="destination" label="目的地" min-width="100" />
        <el-table-column label="计费模式" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.billingMode === 1" size="small">单公里</el-tag>
            <el-tag
              v-else-if="row.billingMode === 2"
              type="warning"
              size="small"
              >整单价</el-tag
            >
            <el-tag v-else type="success" size="small">台单价</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vehicleBrand" label="品牌" min-width="80" />
        <el-table-column prop="vehicleModel" label="车型" min-width="80" />
        <el-table-column label="单价" min-width="120" align="right">
          <template #default="{ row }">
            {{ row.unitPrice }}
            <span style="color: #999; font-size: 12px">
              {{
                row.billingMode === 1
                  ? '元/台·km'
                  : row.billingMode === 2
                    ? '元/单'
                    : '元/台'
              }}
            </span>
            <div
              v-if="row.billingMode === 1 && row.distanceKm"
              style="color: #999; font-size: 12px"
            >
              {{ row.distanceKm }} km
            </div>
          </template>
        </el-table-column>
        <el-table-column label="运价类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.priceType === 1" type="warning" size="small">
              预估
            </el-tag>
            <el-tag v-else type="success" size="small">明确</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="effectiveDate"
          label="生效日期"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="expiryDate"
          label="失效日期"
          min-width="110"
          align="center"
        />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 1" type="success" size="small">
              生效
            </el-tag>
            <el-tag v-else type="info" size="small">停用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-link
              type="primary"
              :underline="false"
              @click="openRateEdit(row)"
            >
              编辑
            </el-link>
            <el-divider direction="vertical" />
            <el-link
              type="danger"
              :underline="false"
              @click="removeRateRow(row)"
            >
              删除
            </el-link>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <rate-edit
      v-model:visible="rateEditVisible"
      :contract-id="data?.id"
      :data="rateEditData"
      @done="loadRates"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import RateEdit from './rate-edit.vue';
  import { listRates, removeRate } from '@/api/billing/contract';
  import type {
    FreightContract,
    FreightRate
  } from '@/api/billing/contract/model';

  const props = defineProps<{
    visible: boolean;
    data: FreightContract | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const rates = ref<FreightRate[]>([]);
  const rateEditVisible = ref(false);
  const rateEditData = ref<FreightRate | null>(null);

  const loadRates = async () => {
    if (!props.data?.id) return;
    try {
      rates.value = (await listRates(props.data.id)) ?? [];
    } catch (_) {
      rates.value = [];
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val && props.data?.id) {
        loadRates();
      } else {
        rates.value = [];
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const openRateEdit = (row?: FreightRate) => {
    rateEditData.value = row ?? null;
    rateEditVisible.value = true;
  };

  const removeRateRow = (row: FreightRate) => {
    ElMessageBox.confirm('确定要删除该运价明细吗?', '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeRate(row.id!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            loadRates();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
