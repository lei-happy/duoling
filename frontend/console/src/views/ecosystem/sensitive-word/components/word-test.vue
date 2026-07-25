<!-- 敏感词 - 试测一段话 -->
<template>
  <ele-modal form :width="560" v-model="visible" title="试测一段话">
    <el-alert
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 14px"
    >
      把企业可能填写的内容粘进来，看看会不会被拦下。
      改完词库先在这里试一下，避免误伤真实货源。
    </el-alert>

    <el-form label-width="88px" @submit.prevent="run">
      <el-form-item label="适用范围">
        <el-select v-model="scope" style="width: 100%">
          <el-option
            v-for="s in options.scopes"
            :key="s.value"
            :label="s.label"
            :value="s.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="内容">
        <el-input
          type="textarea"
          :rows="5"
          v-model="text"
          placeholder="例如：杭州到成都商品车 8 台，需要封闭板运输，有货联系 138xxxxxxxx"
        />
      </el-form-item>
    </el-form>

    <div v-if="result" class="eco-result">
      <el-alert
        :type="result.blocked ? 'error' : 'success'"
        :closable="false"
        show-icon
        :title="
          result.blocked
            ? '这段内容会被拦下，企业无法提交'
            : '这段内容可以正常发布'
        "
      />

      <div v-if="result.contactHits.length" class="eco-result-row">
        <span class="eco-result-label">识别到联系方式</span>
        <el-tag
          v-for="c in result.contactHits"
          :key="c"
          type="danger"
          size="small"
          :disable-transitions="true"
          style="margin-right: 6px"
        >
          {{ c }}
        </el-tag>
        <div class="eco-tip">
          联系方式由系统固定拦截，与词库无关，不需要也无法在词库里配置。
        </div>
      </div>

      <div v-if="result.wordHits.length" class="eco-result-row">
        <span class="eco-result-label">命中词库</span>
        <el-tag
          v-for="w in result.wordHits"
          :key="w.word"
          :type="w.action === 1 ? 'danger' : 'warning'"
          size="small"
          :disable-transitions="true"
          style="margin-right: 6px"
        >
          {{ w.word }}（{{ w.action === 1 ? '禁止发布' : '转人工' }}）
        </el-tag>
      </div>

      <div
        v-if="!result.contactHits.length && !result.wordHits.length"
        class="eco-tip eco-result-row"
      >
        没有命中任何规则。
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!text.trim()"
        @click="run"
      >
        开始试测
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { testSensitiveText } from '@/api/ecosystem/sensitive-word';
  import type {
    SensitiveWordOptions,
    WordTestResult
  } from '@/api/ecosystem/sensitive-word/model';

  defineProps<{ options: SensitiveWordOptions }>();

  const visible = defineModel<boolean>({ default: false });

  const loading = ref(false);
  const text = ref('');
  const scope = ref<string>('ecosystem');
  const result = ref<WordTestResult | null>(null);

  const run = () => {
    if (!text.value.trim()) {
      EleMessage.warning({ message: '请先输入要试测的内容', plain: true });
      return;
    }
    loading.value = true;
    result.value = null;
    testSensitiveText(text.value, scope.value)
      .then(({ result: data }) => {
        loading.value = false;
        result.value = data;
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };
</script>

<style lang="scss" scoped>
  .eco-result {
    margin-top: 4px;
  }

  .eco-result-row {
    margin-top: 12px;
  }

  .eco-result-label {
    display: inline-block;
    margin-right: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-tip {
    margin-top: 6px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }
</style>
