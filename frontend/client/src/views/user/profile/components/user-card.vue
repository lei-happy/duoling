<template>
  <ele-card>
    <div class="info-user">
      <div class="info-user-avatar" @click="openCropper">
        <el-avatar :size="100" :src="data.avatar" style="background: none">
          <el-icon :size="40"><UserOutlined /></el-icon>
        </el-avatar>
        <el-icon class="info-user-avatar-icon">
          <CloudUploadOutlined style="stroke-width: 3" />
        </el-icon>
      </div>
      <ele-text size="xxl" style="margin-top: 5px">
        {{ data.nickname || '未设置昵称' }}
      </ele-text>
      <ele-text type="placeholder">
        {{ userTypeName }}
      </ele-text>
    </div>
    <div class="info-list">
      <div class="info-item">
        <el-icon><MobileOutlined /></el-icon>
        <div class="info-item-text">{{ data.phone || '-' }}</div>
      </div>
      <div class="info-item">
        <el-icon><MailOutlined /></el-icon>
        <div class="info-item-text">{{ data.email || '未设置' }}</div>
      </div>
      <div class="info-item" v-if="data.sex">
        <el-icon><UserOutlined /></el-icon>
        <div class="info-item-text">{{ data.sex }}</div>
      </div>
      <div class="info-item" v-if="data.tenantName">
        <el-icon>
          <CityOutlined style="transform: translateY(-1px)" />
        </el-icon>
        <div class="info-item-text">{{ data.tenantName }}</div>
      </div>
    </div>
    <!-- 头像裁剪弹窗 -->
    <ele-cropper-modal
      v-model="visible"
      :src="data.avatar"
      :options="{
        aspectRatio: 1,
        autoCropArea: 1,
        viewMode: 1,
        dragMode: 'move'
      }"
      :modal-props="{ destroyOnClose: true }"
      @done="handleCrop"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import {
    CloudUploadOutlined,
    UserOutlined,
    CityOutlined,
    MobileOutlined,
    MailOutlined
  } from '@/components/icons';
  import { EleMessage } from 'ele-admin-plus';
  import { updateUserInfo } from '@/api/layout';
  import { uploadFile } from '@/api/system/file';
  import type { User } from '@/api/system/user/model';

  const USER_TYPE_MAP: Record<number, string> = {
    1: '管理员',
    2: '普通员工',
    3: '驾驶员'
  };

  const props = defineProps<{
    data: User;
  }>();

  const emit = defineEmits<{
    (e: 'done', value: User): void;
  }>();

  const userTypeName = computed(() => {
    return USER_TYPE_MAP[props.data.userType ?? 0] || '';
  });

  const visible = ref(false);

  const openCropper = () => {
    visible.value = true;
  };

  const MAX_AVATAR_SIZE = 5 * 1024 * 1024;

  const compressImage = (base64: string, quality = 0.85): Promise<string> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('无法创建画布'));
          return;
        }
        ctx.drawImage(img, 0, 0);
        resolve(canvas.toDataURL('image/jpeg', quality));
      };
      img.onerror = () => reject(new Error('图片加载失败'));
      img.src = base64;
    });
  };

  const base64ToFile = (base64: string, fileName: string): File => {
    const arr = base64.split(',');
    const mime = arr[0]?.match(/:(.*?);/)?.[1] || 'image/png';
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], fileName, { type: mime });
  };

  const handleCrop = async (result: string) => {
    visible.value = false;
    const loading = EleMessage.loading({ message: '上传中..', plain: true });
    try {
      const compressed = await compressImage(result);
      const file = base64ToFile(compressed, 'avatar.jpg');
      if (file.size > MAX_AVATAR_SIZE) {
        loading.close();
        EleMessage.error({
          message: '图片过大，请选择较小的图片',
          plain: true
        });
        return;
      }
      const uploadRes = await uploadFile(
        file,
        undefined,
        'avatar.jpg',
        'avatar'
      );
      const avatarUrl = uploadRes.url;

      const userInfo = await updateUserInfo({ avatar: avatarUrl });
      loading.close();
      EleMessage.success({ message: '头像更新成功', plain: true });
      emit('done', userInfo);
    } catch (e: any) {
      loading.close();
      EleMessage.error({ message: e.message || '上传失败', plain: true });
    }
  };
</script>

<style lang="scss" scoped>
  .info-user {
    padding-top: 8px;
    box-sizing: border-box;
    text-align: center;

    .info-user-avatar {
      display: inline-block;
      position: relative;
      cursor: pointer;
      line-height: 0;

      .info-user-avatar-icon {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #fff;
        font-size: 30px;
        display: none;
        z-index: 2;
      }

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background-color: transparent;
        transition: background-color 0.3s;
      }

      &:hover {
        .info-user-avatar-icon {
          display: block;
        }

        &::after {
          background-color: rgba(0, 0, 0, 0.4);
        }
      }
    }
  }

  .info-list {
    margin: 28px 0 12px 0;

    .info-item {
      display: flex;
      align-items: center;

      & > .el-icon {
        font-size: 16px;
      }

      .info-item-text {
        flex: 1;
        padding-left: 8px;
        box-sizing: border-box;
      }

      & + .info-item {
        margin-top: 10px;
      }
    }
  }
</style>
