<template>
  <ele-page style="position: relative; z-index: 1">
    <ele-card header="省市区级联选择">
      <div style="max-width: 280px">
        <regions-select
          v-model="city"
          placeholder="请选择省市区"
          :teleported="false"
          :filterable="!mobileDevice"
        />
      </div>
      <div style="margin-top: 12px">
        <el-button type="primary" @click="setCity">回显数据</el-button>
      </div>
    </ele-card>
    <ele-card header="省市级联选择">
      <div style="max-width: 280px">
        <regions-select
          v-model="provinceCity"
          placeholder="请选择省市"
          type="provinceCity"
          :teleported="false"
          :filterable="!mobileDevice"
        />
      </div>
      <div style="margin-top: 12px">
        <el-button type="primary" @click="setProvinceCity">回显数据</el-button>
      </div>
    </ele-card>
    <ele-card header="省选择">
      <div style="max-width: 280px">
        <regions-select
          v-model="province"
          :filterable="false"
          placeholder="请选择省"
          type="province"
          :teleported="false"
        />
      </div>
      <div style="margin-top: 12px">
        <el-button type="primary" @click="setProvince">回显数据</el-button>
      </div>
    </ele-card>
    <ele-card header="可多选">
      <div style="max-width: 280px">
        <regions-select
          v-model="citys"
          :filterable="false"
          placeholder="请选择省市区"
          :cascader-props="cascaderProps"
          :teleported="false"
        />
      </div>
      <div style="margin-top: 12px">
        <el-button type="primary" @click="setCitys">回显数据</el-button>
      </div>
      <div style="margin-top: 28px">省市多选：</div>
      <div style="max-width: 280px; margin-top: 12px">
        <regions-select
          v-model="provinceCitys"
          :filterable="false"
          placeholder="请选择省市"
          type="provinceCity"
          :cascader-props="cascaderProps"
          :teleported="false"
        />
      </div>
      <div style="margin-top: 28px">省多选：</div>
      <div style="max-width: 280px; margin-top: 12px">
        <regions-select
          v-model="provinces"
          :filterable="false"
          placeholder="请选择省"
          type="province"
          :cascader-props="cascaderProps"
          :teleported="false"
        />
      </div>
    </ele-card>
    <ele-card header="翻译">
      <div style="margin: 0 0 16px 0; opacity: 0.6">单选值翻译</div>
      <regions-select
        component="text"
        :model-value="['42', '4201', '420103']"
      />
      <div style="margin: 32px 0 16px 0; opacity: 0.6">多选值翻译</div>
      <regions-select
        component="text"
        :model-value="[
          ['42', '4201', '420103'],
          ['42', '4201', '420106'],
          ['42', '4201', '420111']
        ]"
      />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { useMobileDevice } from '@/utils/use-mobile';
  import RegionsSelect from '@/components/RegionsSelect/index.vue';

  defineOptions({ name: 'ExtensionRegions' });

  const { mobileDevice } = useMobileDevice();

  /** 选中的省市区 */
  const city = ref<string[]>([]);

  /** 回显 */
  const setCity = () => {
    city.value = ['42', '4201', '420103'];
  };

  /** 选中的省市 */
  const provinceCity = ref<string[]>([]);

  /** 回显 */
  const setProvinceCity = () => {
    provinceCity.value = ['42', '4201'];
  };

  /** 选中的省 */
  const province = ref<string[]>([]);

  /** 回显 */
  const setProvince = () => {
    province.value = ['42'];
  };

  /** 选中的省市区 */
  const citys = ref<string[][]>([]);

  /** 回显 */
  const setCitys = () => {
    citys.value = [
      ['42', '4201', '420103'],
      ['42', '4201', '420106'],
      ['42', '4201', '420111']
    ];
  };

  /** 级联属性 */
  const cascaderProps = reactive({ multiple: true });

  /** 选中的省市 */
  const provinceCitys = ref<string[][]>([]);

  /** 选中的省 */
  const provinces = ref<string[][]>([]);
</script>
