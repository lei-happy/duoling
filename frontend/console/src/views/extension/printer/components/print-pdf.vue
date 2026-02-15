<template>
  <ele-card header="更多功能" :body-style="{ padding: 0 }">
    <div style="padding: 20px">
      <el-button :disabled="printing" type="primary" @click="handlePrintPdf">
        {{ printing ? '打印中...' : '打印pdf' }}
      </el-button>
      <el-button type="primary" @click="handleViewPdf">预览pdf</el-button>
    </div>
    <div v-if="pdfUrl">
      <iframe
        :src="pdfUrl"
        style="width: 100%; height: 880px; border: none; display: block"
      ></iframe>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { printPdf } from 'ele-admin-plus/es/ele-printer/util';
  const fileUrl = 'https://cdn.eleadmin.com/20200610/20200708224450.pdf';

  /** 是否打印中 */
  const printing = ref(false);

  /** 打印 */
  const handlePrintPdf = () => {
    printing.value = true;
    printPdf({
      url: fileUrl,
      done: () => {
        printing.value = false;
      }
    });
  };

  /** 预览地址 */
  const pdfUrl = ref('');

  /** 预览 */
  const handleViewPdf = () => {
    if (pdfUrl.value) {
      return;
    }
    //pdfUrl.value = `/pdfjs/web/viewer.html?file=${fileUrl}`;
    pdfUrl.value = `https://plus.eleadmin.com/pdfjs-legacy/web/viewer.html?file=${fileUrl}`;
  };
</script>
