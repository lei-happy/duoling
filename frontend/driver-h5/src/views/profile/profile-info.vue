<template>
  <PageContainer title="个人信息">
    <div v-if="profile" class="info-page">
      <van-cell-group inset>
        <van-cell title="姓名" :value="profile.name" />
        <van-cell title="司机编号" :value="profile.driverCode" />
        <van-cell title="手机号" :value="profile.phone" />
        <van-cell title="性别" :value="genderLabel(profile.gender)" />
        <van-cell title="身份证号" :value="profile.idCard || '-'" />
      </van-cell-group>

      <van-cell-group inset class="mt">
        <van-field
          v-model="form.emergencyContact"
          label="紧急联系人"
          placeholder="请输入"
        />
        <van-field
          v-model="form.emergencyPhone"
          label="联系人电话"
          placeholder="请输入"
          type="tel"
        />
        <van-field
          v-model="form.homeAddress"
          label="家庭住址"
          placeholder="请输入"
        />
      </van-cell-group>

      <div class="actions">
        <van-button block round type="primary" :loading="saving" @click="onSave">
          保存修改
        </van-button>
      </div>
    </div>
    <van-loading v-else class="loading" type="spinner" />
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { showToast } from 'vant';
import PageContainer from '@/components/PageContainer.vue';
import { getMyProfile, updateMyProfile, type DriverProfile } from '@/api/profile';

const profile = ref<DriverProfile | null>(null);
const saving = ref(false);
const form = reactive({
  emergencyContact: '',
  emergencyPhone: '',
  homeAddress: ''
});

function genderLabel(g?: number) {
  return { 0: '未知', 1: '男', 2: '女' }[g ?? 0];
}

async function load() {
  profile.value = await getMyProfile();
  form.emergencyContact = profile.value.emergencyContact || '';
  form.emergencyPhone = profile.value.emergencyPhone || '';
  form.homeAddress = profile.value.homeAddress || '';
}

async function onSave() {
  if (saving.value) return;
  saving.value = true;
  try {
    profile.value = await updateMyProfile({ ...form });
    showToast({ message: '保存成功', type: 'success' });
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>

<style lang="scss" scoped>
.info-page {
  padding-top: $spacing-md;
  padding-bottom: $spacing-xl;
}
.mt {
  margin-top: $spacing-md;
}
.actions {
  margin: $spacing-xl $spacing-lg;
}
.loading {
  text-align: center;
  padding: 80px 0;
}
</style>
