<template>
  <ele-page>
    <el-row :gutter="16">
      <!-- 系统名称设置 -->
      <el-col :span="24">
        <ele-card header="系统名称设置">
          <el-form
            label-width="120px"
            style="max-width: 560px"
            @submit.prevent
          >
            <el-form-item label="企业名称">
              <span>{{ enterpriseInfo?.tenantName }}</span>
            </el-form-item>
            <el-form-item label="系统显示名称">
              <div style="display: flex; align-items: center; width: 100%">
                <template v-if="editingName">
                  <el-input
                    v-model="systemNameInput"
                    placeholder="为空则显示企业名称"
                    :maxlength="12"
                    show-word-limit
                    clearable
                    style="flex: 1"
                  />
                  <el-button
                    type="primary"
                    :loading="saving"
                    style="margin-left: 12px"
                    @click="handleSaveName"
                  >
                    保存
                  </el-button>
                  <el-button style="margin-left: 8px" @click="cancelEdit">
                    取消
                  </el-button>
                </template>
                <template v-else>
                  <span style="flex: 1">
                    {{ enterpriseInfo?.systemName || enterpriseInfo?.tenantName || '-' }}
                  </span>
                  <el-button
                    v-if="isAdmin"
                    type="primary"
                    link
                    @click="startEdit"
                  >
                    修改
                  </el-button>
                </template>
              </div>
            </el-form-item>
            <el-form-item>
              <el-text type="info" size="small">
                系统显示名称将展示在客户端左上角，最多12个字符，为空时默认显示企业名称
              </el-text>
            </el-form-item>
          </el-form>
        </ele-card>
      </el-col>

      <!-- 版本信息 -->
      <el-col :span="24">
        <ele-card header="版本信息">
          <template v-if="enterpriseInfo?.version">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="当前版本">
                <el-tag type="primary">
                  {{ enterpriseInfo.version.versionName }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="版本编码">
                {{ enterpriseInfo.version.versionCode }}
              </el-descriptions-item>
              <el-descriptions-item label="授权开始时间">
                {{ formatDate(enterpriseInfo.version.startTime) || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="授权到期时间">
                <template v-if="enterpriseInfo.version.endTime">
                  <span>{{ formatDate(enterpriseInfo.version.endTime) }}</span>
                  <el-tag
                    :type="isExpiringSoon ? 'warning' : 'success'"
                    size="small"
                    style="margin-left: 8px"
                  >
                    {{ remainingDaysText }}
                  </el-tag>
                </template>
                <span v-else>永久有效</span>
              </el-descriptions-item>
              <el-descriptions-item label="最大用户数">
                {{ enterpriseInfo.version.maxUsers ?? '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="最大车辆数">
                {{ enterpriseInfo.version.maxVehicles ?? '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </template>
          <el-empty v-else description="暂无版本信息" />
        </ele-card>
      </el-col>

      <!-- 企业邀请（预留） -->
      <el-col :span="24">
        <ele-card header="企业邀请">
          <el-empty description="敬请期待" />
        </ele-card>
      </el-col>
    </el-row>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted } from 'vue';
  import { ElMessage } from 'element-plus';
  import { useUserStore } from '@/store/modules/user';
  import {
    getEnterpriseInfo,
    updateSystemName
  } from '@/api/enterprise';
  import type { EnterpriseInfo } from '@/api/enterprise';

  defineOptions({ name: 'EnterpriseManage' });

  const userStore = useUserStore();
  const isAdmin = computed(() => userStore.isAdmin);

  const enterpriseInfo = ref<EnterpriseInfo>();
  const editingName = ref(false);
  const systemNameInput = ref('');
  const saving = ref(false);

  const loadInfo = async () => {
    try {
      enterpriseInfo.value = await getEnterpriseInfo();
    } catch (e: any) {
      ElMessage.error(e.message || '获取企业信息失败');
    }
  };

  const startEdit = () => {
    systemNameInput.value = enterpriseInfo.value?.systemName || '';
    editingName.value = true;
  };

  const cancelEdit = () => {
    editingName.value = false;
  };

  const handleSaveName = async () => {
    saving.value = true;
    try {
      await updateSystemName(systemNameInput.value || null);
      ElMessage.success('系统名称更新成功');
      editingName.value = false;
      await loadInfo();
      if (userStore.info) {
        userStore.setInfo({
          ...userStore.info,
          systemName: systemNameInput.value || undefined
        });
      }
    } catch (e: any) {
      ElMessage.error(e.message || '更新失败');
    } finally {
      saving.value = false;
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  };

  const remainingDays = computed(() => {
    const endTime = enterpriseInfo.value?.version?.endTime;
    if (!endTime) return null;
    const diff = new Date(endTime).getTime() - Date.now();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  });

  const isExpiringSoon = computed(() => {
    return remainingDays.value !== null && remainingDays.value <= 30;
  });

  const remainingDaysText = computed(() => {
    if (remainingDays.value === null) return '';
    if (remainingDays.value <= 0) return '已过期';
    return `剩余 ${remainingDays.value} 天`;
  });

  onMounted(loadInfo);
</script>
