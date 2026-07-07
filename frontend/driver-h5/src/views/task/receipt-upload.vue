<template>
  <PageContainer title="上传回单">
    <div class="receipt-upload">
      <div class="section card">
        <div class="section-title">回单图片（最多 9 张）</div>
        <van-uploader
          v-model="fileList"
          :max-count="9"
          :after-read="onAfterRead"
          :before-delete="onBeforeDelete"
          multiple
          upload-text="上传回单"
        />
      </div>

      <div class="section card">
        <div class="section-title">备注</div>
        <van-field
          v-model="remark"
          rows="2"
          autosize
          type="textarea"
          maxlength="255"
          show-word-limit
          placeholder="备注（选填）"
        />
      </div>

      <div v-if="receipts.length" class="section card">
        <div class="section-title">已上传回单（{{ receipts.length }}）</div>
        <div class="receipt-history">
          <div v-for="r in receipts" :key="r.id" class="history-item">
            <van-image
              v-for="(u, i) in r.fileUrls"
              :key="i"
              width="56"
              height="56"
              radius="6"
              fit="cover"
              :src="resolveUrl(u)"
              @click="preview(r.fileUrls, i)"
            />
            <van-icon
              name="delete-o"
              class="del"
              @click="onRemoveReceipt(r.id)"
            />
          </div>
        </div>
      </div>

      <div class="action-bar">
        <van-button
          type="primary"
          round
          block
          :loading="submitting"
          :disabled="!uploadedUrls.length"
          @click="onSubmit"
        >
          提交回单
        </van-button>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { showImagePreview, showToast, type UploaderFileListItem } from 'vant';
import PageContainer from '@/components/PageContainer.vue';
import { uploadImage } from '@/api/file';
import {
  deleteReceipt,
  listMyReceipts,
  uploadReceipt,
  type ReceiptItem
} from '@/api/task-receipt';

const route = useRoute();

const taskId = Number(route.params.id);
const fileList = ref<UploaderFileListItem[]>([]);
const uploadedUrls = ref<string[]>([]);
const remark = ref('');
const submitting = ref(false);
const receipts = ref<ReceiptItem[]>([]);

const baseUrl = (import.meta.env.VITE_UPLOAD_BASE as string) || '';
function resolveUrl(u: string) {
  if (!u) return '';
  if (/^https?:\/\//.test(u)) return u;
  return baseUrl + u;
}

async function loadReceipts() {
  if (!taskId) return;
  try {
    const res = await listMyReceipts({ taskId, page: 1, pageSize: 50 });
    receipts.value = res.list;
  } catch (e) {
    console.error(e);
  }
}

onMounted(loadReceipts);

async function onAfterRead(item: UploaderFileListItem | UploaderFileListItem[]) {
  const items = Array.isArray(item) ? item : [item];
  for (const it of items) {
    if (!it.file) continue;
    it.status = 'uploading';
    it.message = '上传中';
    try {
      const res = await uploadImage(it.file, 'task_receipt');
      it.status = 'done';
      it.message = '';
      it.url = resolveUrl(res.url);
      // 记录服务器相对路径用于提交
      (it as UploaderFileListItem & { serverUrl?: string }).serverUrl = res.url;
      uploadedUrls.value.push(res.url);
    } catch (e) {
      it.status = 'failed';
      it.message = '上传失败';
      console.error(e);
    }
  }
}

function onBeforeDelete(item: UploaderFileListItem) {
  const serverUrl = (item as UploaderFileListItem & { serverUrl?: string })
    .serverUrl;
  if (serverUrl) {
    uploadedUrls.value = uploadedUrls.value.filter((u) => u !== serverUrl);
  }
  return true;
}

function preview(urls: string[], start: number) {
  showImagePreview({ images: urls.map(resolveUrl), startPosition: start });
}

async function onSubmit() {
  if (!uploadedUrls.value.length) {
    showToast('请先上传回单图片');
    return;
  }
  submitting.value = true;
  try {
    await uploadReceipt({
      taskId,
      fileUrls: uploadedUrls.value,
      remark: remark.value.trim() || undefined
    });
    showToast({ message: '提交成功', type: 'success' });
    fileList.value = [];
    uploadedUrls.value = [];
    remark.value = '';
    await loadReceipts();
  } catch (e) {
    console.error(e);
  } finally {
    submitting.value = false;
  }
}

async function onRemoveReceipt(id: number) {
  try {
    await deleteReceipt(id);
    showToast({ message: '已删除', type: 'success' });
    await loadReceipts();
  } catch (e) {
    console.error(e);
  }
}
</script>

<style lang="scss" scoped>
.receipt-upload {
  padding-bottom: 90px;
}
.section {
  margin: $spacing-md;
  padding: $spacing-md;
  background: $bg-card;
  border-radius: $border-radius-md;
  box-shadow: $shadow-card;
  .section-title {
    font-size: $font-size-md;
    font-weight: 600;
    margin-bottom: $spacing-md;
  }
}
.receipt-history {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  .history-item {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    .del {
      margin-left: auto;
      color: $brand-danger;
      font-size: 20px;
    }
  }
}
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: $spacing-md $spacing-lg calc(#{$spacing-md} + #{$safe-area-bottom});
  background: #fff;
  box-shadow: 0 -2px 8px rgba(15, 23, 42, 0.06);
}
</style>
