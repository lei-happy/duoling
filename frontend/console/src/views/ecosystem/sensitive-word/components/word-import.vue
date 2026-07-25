<!-- 敏感词 - 批量导入 -->
<template>
  <ele-modal form :width="560" v-model="visible" title="批量导入敏感词">
    <el-form label-width="88px" @submit.prevent="submit">
      <el-form-item label="词列表">
        <el-input
          type="textarea"
          :rows="10"
          v-model="text"
          placeholder="一行一个词，也可以用逗号分隔&#10;例如：&#10;易燃易爆&#10;放射性&#10;管制刀具"
        />
        <div class="eco-tip">
          识别到 <b>{{ words.length }}</b> 个词（已去重）。一次最多 500 个。
          已经在词库里的词会自动跳过，不会重复添加。
        </div>
      </el-form-item>

      <el-form-item label="分类">
        <el-select v-model="category" style="width: 100%">
          <el-option
            v-for="c in options.categories"
            :key="c.value"
            :label="c.label"
            :value="c.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="命中后">
        <el-radio-group v-model="action">
          <el-radio
            v-for="a in options.actions"
            :key="a.value"
            :value="a.value"
            :label="a.value"
          >
            {{ a.label }}
          </el-radio>
        </el-radio-group>
        <div class="eco-tip">
          这一批词统一使用同一种处理方式，导入后可以单独调整。
        </div>
      </el-form-item>

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
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!words.length"
        @click="submit"
      >
        导入 {{ words.length ? `${words.length} 个词` : '' }}
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { importSensitiveWords } from '@/api/ecosystem/sensitive-word';
  import type { SensitiveWordOptions } from '@/api/ecosystem/sensitive-word/model';

  defineProps<{ options: SensitiveWordOptions }>();

  const emit = defineEmits<{ (e: 'done'): void }>();

  const visible = defineModel<boolean>({ default: false });

  const loading = ref(false);
  const text = ref('');
  const category = ref<number>(9);
  const action = ref<number>(1);
  const scope = ref<string>('all');

  /** 换行、逗号、分号、顿号都当分隔符——运营从各处复制来的格式不统一 */
  const words = computed(() =>
    Array.from(
      new Set(
        text.value
          .split(/[\n\r,，;；、]+/)
          .map((w) => w.trim())
          .filter((w) => w.length > 0)
      )
    )
  );

  const submit = () => {
    if (!words.value.length) {
      EleMessage.warning({ message: '请先填入要导入的词', plain: true });
      return;
    }
    loading.value = true;
    importSensitiveWords({
      words: words.value,
      category: category.value,
      action: action.value,
      scope: scope.value
    })
      .then(({ message }) => {
        loading.value = false;
        EleMessage.success({ message, plain: true });
        visible.value = false;
        text.value = '';
        emit('done');
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };
</script>

<style lang="scss" scoped>
  .eco-tip {
    margin-top: 4px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }
</style>
