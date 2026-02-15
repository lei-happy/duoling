<!-- 房屋租赁合同 -->
<template>
  <ele-printer
    v-model="printing"
    margin="0mm 12mm 10mm 12mm"
    :header-style="{
      padding: '26px 0 2px 0',
      fontSize: '13px',
      borderBottom: '1px solid #666',
      marginBottom: '26px'
    }"
    :body-style="{ padding: '0 14px', fontSize: '17px', lineHeight: 2.5 }"
    :target="target"
    :static="isStatic"
    @done="handlePrintDone"
  >
    <template #header>
      <div style="color: #444">
        <img
          src="/favicon.ico"
          style="height: 15px; width: 15px; vertical-align: -2px"
        />
        <span> XXX公寓房屋租赁合同</span>
      </div>
      <div style="color: #888">电话：027-987654321</div>
    </template>
    <div v-if="!!data" style="page-break-after: always">
      <div style="font-size: 35px; text-align: center">房屋租赁合同</div>
      <div style="margin-top: 12px">
        <span>甲方：</span>
        <span class="demo-input" style="min-width: 280px">
          {{ data.partyA }}
        </span>
      </div>
      <div>
        <span>乙方：</span>
        <span class="demo-input" style="min-width: 280px">
          {{ data.partyB }}
        </span>
      </div>
      <div>
        <span>房屋地址：</span>
        <span class="demo-input" style="min-width: 280px">
          {{ data.address }}
        </span>
      </div>
      <div>甲、乙双方就房屋租赁事宜，达成如下协议：</div>
      <div style="margin: 8px 0 4px 0">一、租赁期限</div>
      <div>
        1、租赁期限自______年______月______日起至______年______月______日止。
      </div>
      <div>
        2、租赁期满后，如果乙方需要继续租赁，则甲方有权优先考虑与乙方续签租赁合同。
      </div>
      <div style="margin: 8px 0 4px 0">二、房屋使用费用</div>
      <div>1、乙方承担租赁期间的水费、电费、燃气费、物业管理费等使用费用。</div>
      <div>
        2、乙方在入住前应一次性向甲方支付押金______元，用于租赁期内的房屋维修和卫生保洁。
      </div>
      <div>
        3、乙方在租赁期间应妥善保管房屋及其设备设施，不得人为损坏。
        如因乙方过错导致房屋设备设施损坏，乙方应承担维修或更换费用。
      </div>
      <div style="margin: 8px 0 4px 0">三、房屋使用要求</div>
      <div>1、乙方应遵守国家相关法律法规，不得将房屋用于违法活动。</div>
      <div>2、乙方应爱护房屋及其设备设施，不得随意改造和拆除。</div>
      <div>
        3、乙方不得将房屋转租他人，不得将房屋用于存放危险品和易燃易爆品。
      </div>
      <div style="margin: 8px 0 4px 0">四、支付方式</div>
      <div>1、乙方应按月支付租金，租金为______元/月。</div>
      <div>
        2、乙方应在每月______日前将租金支付给甲方，付款方式为（现金、银行转账等）。
      </div>
      <div style="margin: 8px 0 4px 0">五、合同解除和终止</div>
      <div>1、在租赁期内，如果乙方符合下列条件之一，则甲方有权解除合同：</div>
      <div>（1）乙方将房屋转租他人；</div>
      <div>（2）乙方将房屋用于违法活动；</div>
      <div>（3）乙方未按时支付租金达30天以上。</div>
      <div>2、在租赁期内，如果甲方符合下列条件之一，则乙方有权解除合同：</div>
      <div>（1）甲方将房屋擅自出租他人；</div>
      <div>（2）甲方将房屋用于违法活动；</div>
      <div>（3）甲方未按时提供房屋及其设备设施的正常使用。</div>
      <div>
        3、合同期满后，如果乙方不再续租，则甲方有权在3日内收回房屋。如果乙方需要继续租赁，
        则应在本合同期满前3个月内向甲方提出书面申请，并双方重新签订租赁合同。
      </div>
      <div style="margin: 8px 0 4px 0">六、其他事项</div>
      <div>1、本合同自双方签字盖章之日起生效。</div>
      <div>2、本合同一式两份，甲、乙双方各执一份，具有同等法律效力。</div>
      <div style="margin-top: 28px">
        <span>甲方：</span>
        <span class="demo-input" style="min-width: 220px">
          {{ data.partyA }}
        </span>
        <span>&emsp;&emsp;乙方：</span>
        <span class="demo-input" style="min-width: 220px">
          {{ data.partyB }}
        </span>
      </div>
      <div>
        <span>电话：</span>
        <span class="demo-input" style="min-width: 220px"></span>
        <span>&emsp;&emsp;电话：</span>
        <span class="demo-input" style="min-width: 220px"></span>
      </div>
      <div>
        <span>日期：</span>
        <span class="demo-input" style="min-width: 220px">{{ data.date }}</span>
        <span>&emsp;&emsp;日期：</span>
        <span class="demo-input" style="min-width: 220px">{{ data.date }}</span>
      </div>
    </div>
  </ele-printer>
</template>

<script lang="ts" setup>
  import { ref, nextTick } from 'vue';
  import type { MessageHandler as ElMessageHandler } from 'element-plus/es/components/message';
  import { EleMessage } from 'ele-admin-plus';
  import type { PrintTarget } from 'ele-admin-plus/es/ele-printer/types';
  import type { Contract } from '@/api/example/model';
  let loading: ElMessageHandler;

  const props = defineProps<{
    /** 合同数据 */
    data?: Contract | null;
    /** 始终显示 */
    isStatic: boolean;
    /** 打印位置 */
    target: PrintTarget;
  }>();

  /** 是否打印 */
  const printing = ref(false);

  /** 打印 */
  const print = () => {
    console.log('开始打印...');
    if (props.target !== '_iframe') {
      printing.value = true;
      return;
    }
    loading = EleMessage.loading({
      message: '正在打印中..',
      plain: true,
      centered: true,
      mask: true
    });
    nextTick(() => {
      printing.value = true;
    });
  };

  /** 打印结束事件 */
  const handlePrintDone = () => {
    console.log('打印结束.');
    loading && loading.close();
  };

  defineExpose({ print });
</script>

<style lang="scss" scoped>
  .demo-input {
    height: 24px;
    line-height: 24px;
    max-width: 80%;
    padding: 0 14px;
    display: inline-block;
    border-bottom: 1px solid #000;
    vertical-align: middle;
    box-sizing: border-box;
    overflow: hidden;
  }
</style>
