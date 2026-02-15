<template>
  <ele-card header="图片预览">
    <option-item label="可左右循环预览" :responsive="false">
      <el-radio-group v-model="infinite">
        <el-radio :value="false" label="否" />
        <el-radio :value="true" label="是" />
      </el-radio-group>
    </option-item>
    <option-item
      label="可点击遮罩关闭"
      :responsive="false"
      style="margin-top: 0"
    >
      <el-radio-group v-model="hideOnClickModal">
        <el-radio :value="false" label="否" />
        <el-radio :value="true" label="是" />
      </el-radio-group>
    </option-item>
    <option-item
      label="可按返回键关闭"
      :responsive="false"
      style="margin-top: 0"
    >
      <el-radio-group v-model="closeOnPressEscape">
        <el-radio :value="false" label="否" />
        <el-radio :value="true" label="是" />
      </el-radio-group>
    </option-item>
    <option-item
      label="初始打开的图片"
      :responsive="false"
      :label-style="{ textAlign: 'left', marginBottom: '8px' }"
      :body-style="{ padding: 0 }"
      style="margin-top: 4px; display: block"
    >
      <ele-check-card
        v-model="initialIndex"
        :items="checkCardItems"
        :row="{ gutter: 8 }"
        :item-style="{ display: 'flex', padding: '6px', marginBottom: '8px' }"
        style="max-width: 652px"
      >
        <template #item="{ item }">
          <img
            :src="item?.url"
            :style="{
              objectFit: 'contain',
              width: '100%',
              height: '38px',
              pointerEvents: 'none'
            }"
          />
        </template>
      </ele-check-card>
    </option-item>
    <div style="margin-top: 6px">
      <el-button type="primary" @click="openImageViewer">
        打开图片预览
      </el-button>
    </div>
    <EleImageViewer
      v-model="showImageViewer"
      :urlList="urlList"
      :infinite="infinite"
      :hideOnClickModal="hideOnClickModal"
      :closeOnPressEscape="closeOnPressEscape"
      :initialIndex="initialIndex"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  /** 是否打开图片预览组件 */
  const showImageViewer = ref(false);

  /** 图片列表 */
  const urlList = ref([
    'https://cdn.eleadmin.com/20200610/RZ8FQmZfHkcffMlTBCJllBFjEhEsObVo.jpg',
    'https://cdn.eleadmin.com/20200610/WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg',
    'https://cdn.eleadmin.com/20200610/4Z0QR2L0J1XStxBh99jVJ8qLfsGsOgjU.jpg',
    'https://cdn.eleadmin.com/20200610/ttkIjNPlVDuv4lUTvRX8GIlM2QqSe0jg.jpg',
    'https://cdn.eleadmin.com/20200610/fAenQ8nvRjL7x0i0jEfuDBZHvJfHf3v6.jpg',
    'https://cdn.eleadmin.com/20200610/LrCTN2j94lo9N7wEql7cBr1Ux4rHMvmZ.jpg',
    'https://cdn.eleadmin.com/20200610/yeKvhT20lMU0f1T3Y743UlGEOLLnZSnp.jpg',
    'https://cdn.eleadmin.com/20200610/CyrCNmTJfv7D6GFAg39bjT3eRkkRm5dI.jpg'
  ]);

  /** 打开图片预览组件 */
  const openImageViewer = () => {
    showImageViewer.value = true;
  };

  /** 循环预览 */
  const infinite = ref(false);

  /** 点击遮罩关闭 */
  const hideOnClickModal = ref(false);

  /** 返回键关闭 */
  const closeOnPressEscape = ref(true);

  /** 初始图片索引 */
  const initialIndex = ref(0);

  /** 可选卡片数据 */
  const checkCardItems = ref(
    urlList.value.map((url, value) => ({ value, url, col: { sm: 3, xs: 6 } }))
  );
</script>
