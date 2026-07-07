import request from './request';

export interface UploadResult {
  url: string;
  name: string;
}

/**
 * 上传单张图片到司机端文件服务。
 * scene 见后端 ALLOWED_SCENES：task_loading（装卸车）/ task_receipt（回单）/ avatar 等。
 */
export async function uploadImage(
  file: File,
  scene = 'task_receipt'
): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('scene', scene);
  const res = await request.post<{ code: number; message?: string; data?: UploadResult }>(
    '/file/upload',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  const body = res.data;
  if (body?.data?.url) {
    return body.data;
  }
  return Promise.reject(new Error(body?.message || '上传失败'));
}
