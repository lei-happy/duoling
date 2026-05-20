<!--
  产品版本升级方案对比页
  - 公开页面（白名单），同时也支持已登录访问
  - 数据来源：GET /api/open/product/version-features
  - 当前生效版本（如 lite）会高亮"当前版本"标记
-->
<template>
  <div class="upgrade-plans">
    <div class="page-header">
      <div>
        <h1>选择最适合您的版本</h1>
        <p class="sub">从轻量版开始，按业务规模平滑升级到旗舰版</p>
      </div>
      <el-button @click="goBack">返回</el-button>
    </div>

    <div v-loading="loading" class="content-wrap">
      <!-- 版本卡片列 -->
      <div class="versions-row">
        <div
          v-for="v in matrix?.versions"
          :key="v.versionCode"
          class="version-card"
          :class="{ current: isCurrent(v.versionCode) }"
        >
          <div class="badge" v-if="isCurrent(v.versionCode)">当前版本</div>
          <div class="vname">{{ v.versionName }}</div>
          <div class="vcode">{{ v.versionCode }}</div>
          <div class="vprice">{{ formatPrice(v) }}</div>
          <div class="vmeta">
            <div
              >最大用户：<b>{{ v.maxUsers ?? '—' }}</b></div
            >
            <div
              >最大车辆：<b>{{ v.maxVehicles ?? '—' }}</b></div
            >
          </div>
          <div class="vdesc" v-if="v.description">{{ v.description }}</div>
          <el-button
            type="primary"
            class="vbtn"
            :disabled="isCurrent(v.versionCode)"
            @click="onSelect(v)"
          >
            {{ isCurrent(v.versionCode) ? '当前正在使用' : '选择此版本' }}
          </el-button>
        </div>
      </div>

      <!-- 功能矩阵 -->
      <div class="feature-matrix" v-if="matrix">
        <div class="matrix-title">功能对比</div>
        <table class="cmp-table">
          <thead>
            <tr>
              <th class="col-feat">功能</th>
              <th
                v-for="v in matrix.versions"
                :key="v.versionCode"
                :class="{ thCur: isCurrent(v.versionCode) }"
              >
                {{ v.versionName }}
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="m in matrix.modules" :key="m">
              <tr class="module-row">
                <td :colspan="matrix.versions.length + 1">
                  {{ MODULE_LABEL[m] || m }}
                </td>
              </tr>
              <tr v-for="f in featuresByModule(m)" :key="f.featureCode">
                <td class="col-feat">
                  <div class="fname">{{ f.featureName }}</div>
                  <div class="fdesc" v-if="f.description">
                    {{ f.description }}
                  </div>
                </td>
                <td
                  v-for="v in matrix.versions"
                  :key="v.versionCode"
                  :class="{ thCur: isCurrent(v.versionCode) }"
                >
                  <el-icon
                    v-if="f.includedIn.includes(v.versionCode)"
                    color="#52c41a"
                  >
                    <Check />
                  </el-icon>
                  <el-icon v-else color="#dcdcdc">
                    <Close />
                  </el-icon>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <p class="cs-hint">
        如需开通或升级，请联系商务（可在帮助中心获取联系方式），
        或将本页截图发送给您的客户经理。
      </p>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { Check, Close } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    getVersionFeaturesMatrix,
    type ProductVersionFeatureMatrix,
    type ProductVersionItem
  } from '@/api/open/product';
  import { useUserStore } from '@/store/modules/user';

  defineOptions({ name: 'UpgradePlans' });

  const router = useRouter();
  const userStore = useUserStore();
  const loading = ref(true);
  const matrix = ref<ProductVersionFeatureMatrix | null>(null);

  const MODULE_LABEL: Record<string, string> = {
    dashboard: '智能工作台',
    enterprise: '企业管理',
    operation: '运营调度',
    capacity: '运力中心',
    partner: '客商中心',
    billing: '计费中心',
    approval: '审批中心',
    finance: '财务结算',
    insight: '数据洞察',
    ecosystem: '生态平台'
  };

  const currentCode = computed(() => userStore.versionCode);

  const isCurrent = (code: string) => currentCode.value === code;

  const featuresByModule = (m: string) =>
    matrix.value?.features.filter((f) => f.module === m) ?? [];

  const formatPrice = (v: ProductVersionItem) => {
    if (!v.price) {
      if (v.versionCode === 'lite') return '免费';
      return '面议';
    }
    return v.price;
  };

  const onSelect = (v: ProductVersionItem) => {
    if (isCurrent(v.versionCode)) return;
    EleMessage.info({
      message: `请联系商务为您开通【${v.versionName}】`,
      plain: true
    });
  };

  const goBack = () => {
    if (window.history.length > 1) router.back();
    else router.push('/');
  };

  onMounted(async () => {
    try {
      matrix.value = await getVersionFeaturesMatrix();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载失败', plain: true });
    } finally {
      loading.value = false;
    }
  });
</script>

<style scoped>
  .upgrade-plans {
    min-height: 100vh;
    background: linear-gradient(180deg, #f0f4ff 0%, #ffffff 320px);
    padding: 24px 32px 40px;
  }
  .page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  .page-header h1 {
    margin: 0 0 6px;
    font-size: 26px;
  }
  .sub {
    margin: 0;
    color: #5a6477;
  }
  .content-wrap {
    max-width: 1280px;
    margin: 0 auto;
  }
  .versions-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
  }
  .version-card {
    position: relative;
    background: #fff;
    border: 1px solid #e6e8ef;
    border-radius: 10px;
    padding: 20px 18px 18px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .version-card.current {
    border-color: #4d7cff;
    box-shadow: 0 6px 24px rgba(77, 124, 255, 0.18);
  }
  .badge {
    position: absolute;
    top: 12px;
    right: 12px;
    background: #4d7cff;
    color: #fff;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 12px;
  }
  .vname {
    font-size: 18px;
    font-weight: 600;
  }
  .vcode {
    font-size: 12px;
    color: #98a0b3;
    text-transform: uppercase;
  }
  .vprice {
    font-size: 22px;
    color: #d46b08;
    font-weight: 700;
    margin-top: 2px;
  }
  .vmeta {
    font-size: 13px;
    color: #5a6477;
    line-height: 1.7;
  }
  .vdesc {
    font-size: 12px;
    color: #909399;
    line-height: 1.6;
    margin-top: 4px;
    min-height: 32px;
  }
  .vbtn {
    margin-top: auto;
  }

  .feature-matrix {
    background: #fff;
    border: 1px solid #ebeef5;
    border-radius: 10px;
    padding: 18px;
  }
  .matrix-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  .cmp-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  .cmp-table th,
  .cmp-table td {
    border-bottom: 1px solid #f1f3f6;
    padding: 10px 12px;
    text-align: center;
    vertical-align: middle;
  }
  .cmp-table th {
    background: #fafbff;
    color: #1d2433;
  }
  .cmp-table th.thCur,
  .cmp-table td.thCur {
    background: #eef3ff;
  }
  .col-feat {
    text-align: left;
    width: 32%;
  }
  .module-row td {
    background: #f5f7fb;
    color: #4d7cff;
    font-weight: 600;
    text-align: left;
  }
  .fname {
    color: #1d2433;
  }
  .fdesc {
    color: #98a0b3;
    font-size: 12px;
    margin-top: 2px;
  }
  .cs-hint {
    margin-top: 18px;
    color: #98a0b3;
    font-size: 13px;
    text-align: center;
  }
</style>
