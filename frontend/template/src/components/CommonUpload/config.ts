import { uploadFile } from '@/api/system/file';

/**
 * 组件文案
 */
export interface CommonUploadLocale {
  imageError: string;
  excelError: string;
  limitError: string;
}

/**
 * 上传文件接口
 */
export const uploadApi = uploadFile;
